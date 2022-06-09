"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""

import base64
import datetime
import os
import smtplib
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itertools import tee
from typing import Optional, Union

import jinja2
import pdfkit  # type: ignore
from document.config import settings
from document.domain import (
    assembly_strategies,
    bible_books,
    model,
    parsing,
    resource_lookup,
)
from document.utils import file_utils
from more_itertools import partition
from pydantic import BaseModel

logger = settings.logger(__name__)

COMMASPACE = ", "
HYPHEN = "-"
UNDERSCORE = "_"

MAX_FILENAME_LENGTH = 240


def resource_book_content_units(
    found_resource_lookup_dtos: Iterable[model.ResourceLookupDto],
    resource_dirs: Iterable[str],
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
) -> Sequence[Union[model.BookContent, model.ResourceLookupDto]]:
    """
    Initialize the resources from their found assets and
    parse their content for later typesetting. If any of the
    found resources could not be loaded then return them for later
    reporting.
    """
    book_content_or_unloaded_resource_lookup_dtos: list[
        Union[model.BookContent, model.ResourceLookupDto]
    ] = []
    for resource_lookup_dto, resource_dir in zip(
        found_resource_lookup_dtos, resource_dirs
    ):
        # usfm_tools parser can throw a MalformedUsfmError parse error if the
        # USFM for the resource is malformed (from the perspective of the
        # parser). If that happens keep track of said USFM resource for
        # reporting on the cover page of the generated PDF and log the issue,
        # but continue handling other resources in the document request.
        try:
            book_content_or_unloaded_resource_lookup_dtos.append(
                parsing.book_content(
                    resource_lookup_dto,
                    resource_dir,
                    resource_requests,
                    layout_for_print,
                )
            )
        except Exception:
            # Yield the resource that failed to be loaded by the USFM parser likely
            # due to an exceptions.MalformedUsfmError. These unloaded resources are
            # reported later on the cover page of the PDF.
            book_content_or_unloaded_resource_lookup_dtos.append(resource_lookup_dto)
            logger.exception("Caught exception: ")
    return book_content_or_unloaded_resource_lookup_dtos


def document_request_key(
    resource_requests: Sequence[model.ResourceRequest],
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    assembly_layout_kind: model.AssemblyLayoutEnum,
    max_filename_len: int = MAX_FILENAME_LENGTH,
) -> str:
    """
    Create and return the document_request_key. The
    document_request_key uniquely identifies a document request.

    If the document request key is max_filename_len or more characters
    in length, then switch to using a shorter string that is based on the
    current time. The reason for this is that the document request key is
    used as the file name (with suffix appended) and each OS has a limit
    to how long a file name may be. max_filename_len should make room for
    the a file suffix, e.g., ".html", to be appended.

    It is really useful to have filenames with semantic meaning and so
    those are preferred when possible, i.e., when the file name is not
    too long.
    """
    resource_request_keys = UNDERSCORE.join(
        [
            HYPHEN.join(
                [
                    resource_request.lang_code,
                    resource_request.resource_type,
                    resource_request.resource_code,
                ]
            )
            for resource_request in resource_requests
        ]
    )
    document_request_key = "{}_{}_{}".format(
        resource_request_keys, assembly_strategy_kind, assembly_layout_kind
    )
    if len(document_request_key) >= max_filename_len:
        # Likely the generated filename was too long for the OS where this is
        # running. In that case, use the current time as a document_request_key
        # value as doing so results in an acceptably short length.
        import time

        timestamp_components = str(time.time()).split(".")
        return "{}_{}".format(timestamp_components[0], timestamp_components[1])
    else:
        # Use the semantic filename which declaratively describes the
        # document request components.
        return document_request_key


def template_path(
    key: str, template_paths_map: Mapping[str, str] = settings.TEMPLATE_PATHS_MAP
) -> str:
    """
    Return the path to the requested template give a lookup key.
    Return a different path if the code is running inside the Docker
    container.
    """
    return template_paths_map[key]


def template(template_lookup_key: str) -> str:
    """Return template as string."""
    with open(template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    return template


def instantiated_template(template_lookup_key: str, dto: BaseModel) -> str:
    """
    Instantiate Jinja2 template with dto BaseModel instance. Return
    instantiated template as string.
    """
    with open(template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    env = jinja2.Environment(autoescape=True).from_string(template)
    return env.render(data=dto)


def enclose_html_content(
    content: str,
    document_html_header: str,
    document_html_footer: str = template("footer_enclosing"),
) -> str:
    """
    Write the enclosing HTML header and footer elements around the
    HTML body content for the document.
    """
    return "{}{}{}".format(document_html_header, content, document_html_footer)


def document_html_header(
    assembly_layout_kind: Optional[model.AssemblyLayoutEnum],
) -> str:
    """
    Choose the appropriate HTML header given the
    assembly_layout_kind. The HTML header, naturally, contains the CSS
    definitions and they in turn can be used to affect visual
    compactness.
    """
    if assembly_layout_kind and assembly_layout_kind in [
        model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
        model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
    ]:
        return template("header_compact_enclosing")
    else:
        return template("header_enclosing")


def assemble_content(
    document_request_key: str,
    document_request: model.DocumentRequest,
    book_content_units: Iterable[model.BookContent],
    output_dir: str = settings.output_dir(),
) -> None:
    """
    Assemble the content from all requested resources according to the
    assembly_strategy requested and write out to a single HTML file
    for subsequent use.
    """
    # Get the assembly strategy function appropriate given the users
    # choice of document_request.assembly_strategy_kind
    assembly_strategy = assembly_strategies.assembly_strategy_factory(
        document_request.assembly_strategy_kind
    )
    # Now, actually do the actual assembly given the additional
    # information of the document_request.assembly_layout_kind and
    # return it as a string.
    content = "".join(
        assembly_strategy(book_content_units, document_request.assembly_layout_kind)
    )
    # Get the appropriate HTML template header content given the
    # document_request.assembly_layout_kind the user has chosen.
    header = document_html_header(document_request.assembly_layout_kind)
    # Finally compose the HTML document into one string that includes
    # the header template content.
    content = enclose_html_content(content, document_html_header=header)
    html_file_path = "{}.html".format(os.path.join(output_dir, document_request_key))
    logger.debug("About to write HTML to %s", html_file_path)
    file_utils.write_file(
        html_file_path,
        content,
    )


def should_send_email(
    # NOTE: email_address comes in as pydantic.EmailStr and leaves
    # the pydantic class validator as a str.
    email_address: Optional[str],
    send_email: bool = settings.SEND_EMAIL,
) -> bool:
    """
    Return True if configuration is set to send email and the user
    has supplied an email address.
    """
    return send_email and email_address is not None


def send_email_with_pdf_attachment(
    # NOTE: email_address comes in as pydantic.EmailStr and leaves
    # the pydantic class validator as a str.
    email_address: Optional[str],
    output_filename: str,
    document_request_key: str,
    from_email_address: str = settings.FROM_EMAIL_ADDRESS,
    smtp_password: str = settings.SMTP_PASSWORD,
    email_send_subject: str = settings.EMAIL_SEND_SUBJECT,
    smtp_host: str = settings.SMTP_HOST,
    smtp_port: int = settings.SMTP_PORT,
) -> None:
    """
    If PDF exists, and environment configuration allows sending of
    email, then send an email to the document request
    recipient's email with the PDF attached.
    """
    if email_address:
        sender = from_email_address
        email_password = smtp_password
        recipients = [email_address]

        logger.debug("Email sender %s, recipients: %s", sender, recipients)

        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer["Subject"] = email_send_subject
        outer["To"] = COMMASPACE.join(recipients)
        outer["From"] = sender
        # outer.preamble = "You will not see this in a MIME-aware mail reader.\n"

        # List of attachments
        attachments = [output_filename]

        # Add the attachments to the message
        for file in attachments:
            try:
                with open(file, "rb") as fp:
                    msg = MIMEBase("application", "octet-stream")
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(file),
                )
                outer.attach(msg)
            except Exception:
                logger.exception(
                    "Unable to open one of the attachments. Caught exception: "
                )

        # Get the email body
        message_body = instantiated_template(
            "email",
            model.EmailPayload(
                document_request_key=document_request_key,
            ),
        )
        logger.debug("instantiated email template: %s", message_body)

        outer.attach(MIMEText(message_body, "plain"))

        composed = outer.as_string()

        # Send the email
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(sender, email_password)
                smtp.sendmail(sender, recipients, composed)
                smtp.close()
            logger.info("Email sent!")
        except Exception:
            logger.exception("Unable to send the email. Caught exception: ")


def convert_html_to_pdf(
    document_request_key: str,
    book_content_units: Iterable[model.BookContent],
    unfound_resource_lookup_dtos: Iterable[model.ResourceLookupDto],
    unloaded_resource_lookup_dtos: Iterable[model.ResourceLookupDto],
    output_dir: str = settings.output_dir(),
    logo_image_path: str = settings.LOGO_IMAGE_PATH,
    working_dir: str = settings.working_dir(),
    wkhtmltopdf_options: Mapping[str, Optional[str]] = settings.WKHTMLTOPDF_OPTIONS,
    docker_container_pdf_output_dir: str = settings.DOCKER_CONTAINER_PDF_OUTPUT_DIR,
    in_container: bool = settings.IN_CONTAINER,
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
) -> None:
    """Generate PDF from HTML."""
    now = datetime.datetime.now()
    revision_date = "Generated on: {}-{}-{}".format(now.year, now.month, now.day)
    title = "{}".format(
        COMMASPACE.join(
            sorted(
                {
                    "{}: {}".format(
                        book_content_unit.lang_name,
                        book_names[book_content_unit.resource_code],
                    )
                    for book_content_unit in book_content_units
                }
            )
        )
    )
    unfound = "{}".format(
        COMMASPACE.join(
            sorted(
                {
                    "{}-{}-{}".format(
                        unfound_resource_lookup_dto.lang_code,
                        unfound_resource_lookup_dto.resource_type,
                        unfound_resource_lookup_dto.resource_code,
                    )
                    for unfound_resource_lookup_dto in unfound_resource_lookup_dtos
                }
            )
        )
    )
    unloaded = "{}".format(
        COMMASPACE.join(
            sorted(
                {
                    "{}-{}-{}".format(
                        unloaded_resource_lookup_dto.lang_code,
                        unloaded_resource_lookup_dto.resource_type,
                        unloaded_resource_lookup_dto.resource_code,
                    )
                    for unloaded_resource_lookup_dto in unloaded_resource_lookup_dtos
                }
            )
        )
    )
    if unloaded:
        logger.debug("Resource requests that could not be loaded: %s", unloaded)
    html_file_path = "{}.html".format(os.path.join(output_dir, document_request_key))
    assert os.path.exists(html_file_path)
    output_pdf_file_path = pdf_output_filename(document_request_key)
    with open(logo_image_path, "rb") as fin:
        base64_encoded_logo_image = base64.b64encode(fin.read())
        images: dict[str, str | bytes] = {
            "logo": base64_encoded_logo_image,
        }
    # Use Jinja2 to instantiate the cover page.
    cover = instantiated_template(
        "cover",
        model.CoverPayload(
            title=title,
            unfound=unfound,
            unloaded=unloaded,
            revision_date=revision_date,
            images=images,
        ),
    )
    cover_filepath = os.path.join(working_dir, "cover.html")
    with open(cover_filepath, "w") as fout:
        fout.write(cover)
    pdfkit.from_file(
        html_file_path,
        output_pdf_file_path,
        options=wkhtmltopdf_options,
        cover=cover_filepath,
    )
    assert os.path.exists(output_pdf_file_path)
    copy_command = "cp {} {}".format(
        output_pdf_file_path,
        docker_container_pdf_output_dir,
    )
    logger.debug("IN_CONTAINER: {}".format(in_container))
    if in_container:
        logger.info("About to cp PDF to from Docker volume to host")
        logger.debug("Copy PDF command: %s", copy_command)
        subprocess.call(copy_command, shell=True)


def generate_pdf(
    output_filename: str,
    document_request_key: str,
    document_request: model.DocumentRequest,
    book_content_units: Iterable[model.BookContent],
    unfound_resource_lookup_dtos: Iterable[model.ResourceLookupDto],
    unloaded_resource_lookup_dtos: Iterable[model.ResourceLookupDto],
) -> None:
    """
    If the PDF doesn't yet exist, go ahead and generate it
    using the content for each resource.
    """
    if not os.path.isfile(output_filename):
        assemble_content(document_request_key, document_request, book_content_units)
        logger.info("Generating PDF %s...", output_filename)
        convert_html_to_pdf(
            document_request_key,
            book_content_units,
            unfound_resource_lookup_dtos,
            unloaded_resource_lookup_dtos,
        )


def pdf_output_filename(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the PDF output file path."""
    return os.path.join(output_dir, "{}.pdf".format(document_request_key))


def select_assembly_layout_kind(
    document_request: model.DocumentRequest,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    book_language_order: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
    print_layout: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
    # NOTE Could also have default value of
    # model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT
    # or model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT
    non_print_layout_for_multiple_usfm: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
    default_print_layout: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN,
) -> model.AssemblyLayoutEnum:
    """
    Make an intelligent choice of what layout to use given the
    DocumentRequest instance the user has requested. Why? Because we
    don't want to bother the user with having to choose a layout which
    would require them to understand what layouts could work well for
    their particular document request. Instead, we make the choice for
    them.
    """
    if not document_request.layout_for_print:
        document_request.layout_for_print = False
    if document_request.layout_for_print:
        return print_layout

    number_of_usfm_languages = len(
        set(
            [
                resource_request.lang_code
                for resource_request in document_request.resource_requests
                if resource_request.resource_type in usfm_resource_types
            ]
        )
    )

    if (
        document_request.assembly_strategy_kind == book_language_order
        and number_of_usfm_languages > 1
    ):
        return non_print_layout_for_multiple_usfm

    return default_print_layout


def main(document_request: model.DocumentRequest) -> tuple[str, str]:
    """
    This is the main entry point for this module and the
    backend system as a whole.
    """
    document_request.resource_requests = coalesce_english_tn_requests(
        document_request.resource_requests
    )
    # If an assembly_layout_kind has been chosen in the document request,
    # then we know that the request originated from a unit test. The UI does
    # not provide a way to choose an arbitrary layout, but unit tests can
    # specify a layout arbitrarily. We must handle both situations.
    if not document_request.assembly_layout_kind:
        document_request.assembly_layout_kind = select_assembly_layout_kind(
            document_request
        )
    logger.debug(
        "document_request: %s",
        document_request,
    )
    # Generate the document request key that identifies this and identical document requests.
    document_request_key_ = document_request_key(
        document_request.resource_requests,
        document_request.assembly_strategy_kind,
        document_request.assembly_layout_kind,
    )
    output_filename = pdf_output_filename(document_request_key_)

    # Immediately return pre-built PDF if the document has previously been
    # generated and is fresh enough. In that case, front run all requests to
    # the cloud including the more low level resource asset caching
    # mechanism for comparatively immediate return of PDF.
    if file_utils.asset_file_needs_update(output_filename):
        resource_lookup_dtos = [
            resource_lookup.resource_lookup_dto(
                resource_request.lang_code,
                resource_request.resource_type,
                resource_request.resource_code,
            )
            for resource_request in document_request.resource_requests
        ]

        # Determine which resources were actually found and which were
        # not.
        (
            unfound_resource_lookup_dtos_iter,
            found_resource_lookup_dtos_iter,
        ) = partition(
            lambda resource_lookup_dto: resource_lookup_dto.url is not None,
            resource_lookup_dtos,
        )

        # Save results for more than one use (generators exhaust on
        # first use).
        found_resource_lookup_dtos = list(found_resource_lookup_dtos_iter)
        unfound_resource_lookup_dtos = list(unfound_resource_lookup_dtos_iter)

        # For each found resource lookup DTO, now actually provision
        # to disk the assets associated with the resources and return
        # the resource directory paths.
        resource_dirs = [
            resource_lookup.provision_asset_files(resource_lookup_dto)
            for resource_lookup_dto in found_resource_lookup_dtos
        ]

        # Initialize found resources from their provisioned assets. If
        # any could not be initialized return those in the second
        # iterator via tee.
        book_content_units_iter, unloaded_resource_lookup_dtos_iter = tee(
            resource_book_content_units(
                found_resource_lookup_dtos,
                resource_dirs,
                document_request.resource_requests,
                document_request.layout_for_print,
            )
        )
        # A little further processing is needed on tee objects to get
        # the types separated. This first list is of successfully
        # initialized book content units.
        book_content_units = [
            book_content_unit
            for book_content_unit in book_content_units_iter
            if not isinstance(book_content_unit, model.ResourceLookupDto)
        ]
        # This second list is of resource lookup DTOs whose assets
        # could not be successfully loaded.
        unloaded_resource_lookup_dtos = [
            resource_lookup_dto
            for resource_lookup_dto in unloaded_resource_lookup_dtos_iter
            if isinstance(resource_lookup_dto, model.ResourceLookupDto)
        ]

        generate_pdf(
            output_filename,
            document_request_key_,
            document_request,
            book_content_units,
            unfound_resource_lookup_dtos,
            unloaded_resource_lookup_dtos,
        )

    if should_send_email(document_request.email_address):
        send_email_with_pdf_attachment(
            document_request.email_address, output_filename, document_request_key_
        )
    return document_request_key_, output_filename


def coalesce_english_tn_requests(
    resource_requests: Sequence[model.ResourceRequest],
) -> Sequence[model.ResourceRequest]:
    """
    Ensure only one English translation notes resource request per
    document request.

    translations.json offers URLs for English translation notes in repo form,
    en-tn, or in downloadable zip form, tn. They are the same resource
    provided in two different ways, thus only allow one per document
    request. Prefer the repo as once it is cloned subsequent accesses
    will be fast. Downloadable zip would be faster the first time, but
    eventually someone would request en-tn and not tn and then you'd
    have to wait for the repo to be cloned. I'd rather initialize
    resources early after initial launch.
    """
    if [
        resource_request
        for resource_request in resource_requests
        if resource_request.lang_code == "en" and resource_request.resource_type == "tn"
    ] and [
        resource_request
        for resource_request in resource_requests
        if resource_request.lang_code == "en"
        and resource_request.resource_type == "tn-wa"
    ]:  # Both tn and tn-wa requested for en.

        # Return the Sequence of resource_requests
        # with the English tn resource request removed but leave the
        # English tn-wa resouce request in the Sequence.
        return [
            resource_request
            for resource_request in resource_requests
            if not (
                resource_request.lang_code == "en"
                and resource_request.resource_type == "tn"
            )
        ]
    # Special case did not apply, thus return the unaltered
    # resource_requests Sequence.
    return resource_requests
