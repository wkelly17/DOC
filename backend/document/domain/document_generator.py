"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""

import base64
import datetime
import more_itertools
import os
import requests
import smtplib
import subprocess
import toolz  # type: ignore
from collections.abc import Iterable, Mapping, Sequence
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException, status
from itertools import tee
from requests.exceptions import HTTPError
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
from document.utils import file_utils, number_utils

# from document.domain import exceptions
from more_itertools import partition
from pydantic import BaseModel

logger = settings.logger(__name__)

COMMASPACE = ", "
HYPHEN = "-"
UNDERSCORE = "_"

MAX_FILENAME_LENGTH = 240

NUM_ZEROS = 3


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
            # due to a USFM-Tools.exceptions.MalformedUsfmError. These unloaded resources are
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


def uses_section(
    uses: Sequence[model.TWUse],
    translation_word_verse_section_header_str: str = settings.TRANSLATION_WORD_VERSE_SECTION_HEADER_STR,
    unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
    translation_word_verse_ref_item_fmt_str: str = settings.TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR,
    unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
    book_numbers: Mapping[str, str] = bible_books.BOOK_NUMBERS,
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
    num_zeros: int = NUM_ZEROS,
) -> model.HtmlContent:
    """
    Construct and return the 'Uses:' section which comes at the end of
    a translation word definition and wherein each item points to
    verses (as targeted by lang_code, book_id, chapter_num, and
    verse_num) wherein the word occurs.
    """
    html: list[model.HtmlContent] = []
    html.append(translation_word_verse_section_header_str)
    html.append(unordered_list_begin_str)
    for use in uses:
        html_content_str = model.HtmlContent(
            translation_word_verse_ref_item_fmt_str.format(
                use.lang_code,
                book_numbers[use.book_id].zfill(num_zeros),
                str(use.chapter_num).zfill(num_zeros),
                str(use.verse_num).zfill(num_zeros),
                book_names[use.book_id],
                use.chapter_num,
                use.verse_num,
            )
        )
        html.append(html_content_str)
    html.append(unordered_list_end_str)
    return model.HtmlContent("\n".join(html))


def translation_words_section(
    book_content_unit: model.TWBook,
    include_uses_section: bool = True,
    resource_type_name_fmt_str: str = settings.RESOURCE_TYPE_NAME_FMT_STR,
    opening_h3_fmt_str: str = settings.OPENING_H3_FMT_STR,
    opening_h3_with_id_fmt_str: str = settings.OPENING_H3_WITH_ID_FMT_STR,
) -> Iterable[model.HtmlContent]:
    """
    Build and return the translation words definition section, i.e.,
    the list of all translation words for this language, book
    combination. Include a 'Uses:' section that points from the
    translation word back to the verses which include the translation
    word if include_uses_section is True.
    """
    if book_content_unit.name_content_pairs:
        yield model.HtmlContent(
            resource_type_name_fmt_str.format(book_content_unit.resource_type_name)
        )

    for name_content_pair in book_content_unit.name_content_pairs:
        # NOTE Another approach to including all translation words would be to
        # only include words in the translation section which occur in current
        # lang_code, book verses. The problem with this is that translation note
        # 'See also' sections often refer to translation words that are not part
        # of the lang_code/book content and thus those links are dead unless we
        # include them even if they don't have any 'Uses' section. In other
        # words, by limiting the translation words we limit the ability of those
        # using the interleaved document to gain deeper understanding of the
        # interrelationships of words.

        # Make linking work: have to add ID to tags for anchor
        # links to work.
        name_content_pair.content = model.HtmlContent(
            name_content_pair.content.replace(
                opening_h3_fmt_str.format(name_content_pair.localized_word),
                opening_h3_with_id_fmt_str.format(
                    book_content_unit.lang_code,
                    name_content_pair.localized_word,
                    name_content_pair.localized_word,
                ),
            )
        )
        uses_section_ = model.HtmlContent("")

        # See comment above.
        if (
            include_uses_section
            and name_content_pair.localized_word in book_content_unit.uses
        ):
            uses_section_ = uses_section(
                book_content_unit.uses[name_content_pair.localized_word]
            )
            name_content_pair.content = model.HtmlContent(
                name_content_pair.content + uses_section_
            )
        yield name_content_pair.content


def assemble_content(
    document_request_key: str,
    document_request: model.DocumentRequest,
    book_content_units: Iterable[model.BookContent],
) -> str:
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
    tw_book_content_units = (
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.TWBook)
    )
    # Don't allow duplicate languages for tw words. We'd use list(set()) or
    # toolz.itertoolz.unique, but model.TWWord is not hashable and therefore
    # cannot be put in a set.
    unique_tw_book_content_units = []
    for tw_book_content_unit in tw_book_content_units:
        if tw_book_content_unit not in unique_tw_book_content_units:
            unique_tw_book_content_units.append(tw_book_content_unit)

    # We need to see if the document request included any usfm because
    # if it did we'll generate not only the tw word defs but also the
    # links to them from the notes area that exists adjacent to the
    # scripture versees themselves.
    usfm_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.USFMBook)
    ]
    # Add the translation words definition section for each language requested.
    for tw_book_content_unit in unique_tw_book_content_units:
        if usfm_book_content_units:
            # There is usfm content in this document request so we can
            # include the uses section in notes which links to individual word
            # definitions. The uses section will be incorporated by
            # assembly_strategies module if print layout is not chosen and
            # ignored otherwise.
            content = "{}{}".format(
                content, "".join(translation_words_section(tw_book_content_unit))
            )
        else:
            # There is no usfm content in this document request so
            # there is no need for the uses section.
            content = "{}{}".format(
                content,
                "".join(
                    translation_words_section(
                        tw_book_content_unit, include_uses_section=False
                    )
                ),
            )

    # Get the appropriate HTML template header content given the
    # document_request.assembly_layout_kind the user has chosen.
    header = document_html_header(document_request.assembly_layout_kind)
    # Finally compose the HTML document into one string that includes
    # the header template content.
    content = enclose_html_content(content, document_html_header=header)
    return content


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


def send_email_with_attachment(
    # NOTE: email_address comes in as pydantic.EmailStr and leaves
    # the pydantic class validator as a str.
    email_address: Optional[str],
    attachments: list[model.Attachment],
    document_request_key: str,
    content_disposition: str = "attachment",
    from_email_address: str = settings.FROM_EMAIL_ADDRESS,
    smtp_password: str = settings.SMTP_PASSWORD,
    email_send_subject: str = settings.EMAIL_SEND_SUBJECT,
    smtp_host: str = settings.SMTP_HOST,
    smtp_port: int = settings.SMTP_PORT,
    comma_space: str = COMMASPACE,
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
        outer["To"] = comma_space.join(recipients)
        outer["From"] = sender
        # outer.preamble = "You will not see this in a MIME-aware mail reader.\n"

        # List of attachments

        # Add the attachments to the message
        for attachment in attachments:
            try:
                with open(attachment.filepath, "rb") as fp:
                    msg = MIMEBase(attachment.mime_type[0], attachment.mime_type[1])
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header(
                    "Content-Disposition",
                    content_disposition,
                    filename=os.path.basename(attachment.filepath),
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
    html_filepath: str,
    pdf_filepath: str,
    wkhtmltopdf_options: dict[str, Optional[str]] = settings.WKHTMLTOPDF_OPTIONS,
) -> None:
    """Generate PDF from HTML."""
    assert os.path.exists(html_filepath)
    # Create generated on string for use in PDF document header.
    wkhtmltopdf_options["header-center"] = "generated on {}".format(
        datetime.datetime.now().strftime("%b %d, %Y at %H:%M:%S")
    )
    pdfkit.from_file(
        html_filepath,
        pdf_filepath,
        options=wkhtmltopdf_options,
    )


def convert_html_to_epub(
    html_filepath: str,
    epub_filepath: str,
    pandoc_options: str = settings.PANDOC_OPTIONS,
) -> None:
    """Generate ePub from HTML."""
    assert os.path.exists(html_filepath)
    pandoc_command = "pandoc {} {} -o {}".format(
        pandoc_options,
        html_filepath,
        epub_filepath,
    )
    logger.debug("Generate ePub command: %s", pandoc_command)
    subprocess.call(pandoc_command, shell=True)


# FIXME Use cover page...or should we? Maybe we should integrate what
# used to be presented on cover page inside the HTML document instead.
def convert_html_to_docx(
    html_filepath: str,
    docx_filepath: str,
    pandoc_options: str = settings.PANDOC_OPTIONS,
) -> None:
    """Generate Docx from HTML."""
    assert os.path.exists(html_filepath)
    pandoc_command = "pandoc {} {} -o {}".format(
        pandoc_options,
        html_filepath,
        docx_filepath,
    )
    logger.debug("Generate Docx command: %s", pandoc_command)
    subprocess.call(pandoc_command, shell=True)


def html_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the HTML output file path."""
    return os.path.join(output_dir, "{}.html".format(document_request_key))


def pdf_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the PDF output file path."""
    return os.path.join(output_dir, "{}.pdf".format(document_request_key))


def epub_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the ePub output file path."""
    return os.path.join(output_dir, "{}.epub".format(document_request_key))


def docx_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the docx output file path."""
    return os.path.join(output_dir, "{}.docx".format(document_request_key))


def cover_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the HTML cover output file path."""
    return os.path.join(output_dir, "{}_cover.html".format(document_request_key))


def select_assembly_layout_kind(
    document_request: model.DocumentRequest,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    book_language_order: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
    print_layout: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
    # NOTE Could also have default value for non_print_layout_for_multiple_usfm of
    # model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT
    # or model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT
    non_print_layout_for_multiple_usfm: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
    default_layout: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN,
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

    # Partition ulb resource requests by language.
    language_groups = toolz.itertoolz.groupby(
        lambda r: r.lang_code,
        filter(
            lambda r: r.resource_type in usfm_resource_types,
            document_request.resource_requests,
        ),
    )
    # Get a list of the sorted set of books for each language for later
    # comparison.
    sorted_book_set_for_each_language = [
        sorted({item.resource_code for item in value})
        for key, value in language_groups.items()
    ]

    # Get the unique number of languages
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
        # Because book content for different languages will be side by side for
        # the scripture left scripture right layout, we make sure there are a non-zero
        # even number of languages so that we can display them left and right in
        # pairs.
        and number_of_usfm_languages > 1
        and number_utils.is_even(number_of_usfm_languages)
        # Each language must have the same set of books in order to
        # use the scripture left scripture right layout strategy. As an example,
        # you wouldn't want to allow the sl-sr layout if the document request
        # asked for swahili ulb for lamentations and spanish ulb for nahum -
        # the set of books in each language are not the same and so do not make
        # sense to be displayed side by side.
        and more_itertools.all_equal(sorted_book_set_for_each_language)
    ):
        return non_print_layout_for_multiple_usfm

    return default_layout


def write_html_content_to_file(
    content: str,
    output_filename: str,
) -> None:
    """
    Write HTML content to file.
    """
    logger.debug("About to write HTML to %s", output_filename)
    # Write the HTML file to disk.
    file_utils.write_file(
        output_filename,
        content,
    )


def copy_pdf_to_docker_output_dir(
    pdf_filepath: str,
    docker_container_document_output_dir: str = settings.DOCKER_CONTAINER_DOCUMENT_OUTPUT_DIR,
    in_container: bool = settings.IN_CONTAINER,
) -> None:
    """
    Copy PDF file to docker_container_document_output_dir.
    """
    assert os.path.exists(pdf_filepath)
    copy_command = "cp {} {}".format(
        pdf_filepath,
        docker_container_document_output_dir,
    )
    logger.debug("IN_CONTAINER: {}".format(in_container))
    if in_container:
        logger.info("About to cp PDF to from Docker volume to host")
        logger.debug("Copy PDF command: %s", copy_command)
        subprocess.call(copy_command, shell=True)


def copy_epub_to_docker_output_dir(
    epub_filepath: str,
    docker_container_document_output_dir: str = settings.DOCKER_CONTAINER_DOCUMENT_OUTPUT_DIR,
    in_container: bool = settings.IN_CONTAINER,
) -> None:
    """
    Copy ePub file to docker_container_document_output_dir.
    """
    assert os.path.exists(epub_filepath)
    copy_command = "cp {} {}".format(
        epub_filepath,
        docker_container_document_output_dir,
    )
    logger.debug("IN_CONTAINER: {}".format(in_container))
    if in_container:
        logger.info(
            "About to cp ePub from output directory to from Docker volume for fileserver in production and for file viewing on host in development."
        )
        logger.debug("Copy ePub command: %s", copy_command)
        subprocess.call(copy_command, shell=True)


def copy_docx_to_docker_output_dir(
    docx_filepath: str,
    docker_container_document_output_dir: str = settings.DOCKER_CONTAINER_DOCUMENT_OUTPUT_DIR,
    in_container: bool = settings.IN_CONTAINER,
) -> None:
    """
    Copy Docx file to docker_container_document_output_dir.
    """
    assert os.path.exists(docx_filepath)
    copy_command = "cp {} {}".format(
        docx_filepath,
        docker_container_document_output_dir,
    )
    logger.debug("IN_CONTAINER: {}".format(in_container))
    if in_container:
        logger.info(
            "About to cp Docx from output directory to from Docker volume for fileserver in production and for file viewing on host in development."
        )
        logger.debug("Copy Docx command: %s", copy_command)
        subprocess.call(copy_command, shell=True)


def verify_resource_assets_available(
    resource_lookup_dto: model.ResourceLookupDto,
    # FIXME For some reason mypy and Python runtime don't believe
    # settings.NOT_FOUND_MESSAGE_FMT_STR is defined? So I am
    # hardcoding the format string instead as a default argument value.
    # failure_message: str = settings.NOT_FOUND_MESSAGE_FMT_STR,
    failure_message: str = "Book {} and resource type {} for language {} is not available.",
) -> bool:
    """
    We've got a non-None URL, but now let's check that the URL
    actually exists in the cloud because this URL points to assets
    associated with the resource that we need to build our document.
    If it doesn't response ok to an HTTP GET request then raise an
    InvalidDocumentRequestException to notify the front end there was a
    problem and otherwise return true if the URL returned an ok reponse.
    """
    if resource_lookup_dto.url:
        try:
            response = requests.get(resource_lookup_dto.url)
            response.raise_for_status()
        except HTTPError as http_err:
            logger.debug(http_err)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=failure_message.format(
                    resource_lookup_dto.resource_code,
                    resource_lookup_dto.resource_type_name,
                    resource_lookup_dto.lang_name,
                ),
            )

            return False  # This won't ever execute, this is also not needed by mypy. Just being consistent with types for self-documentation purposes.
        except Exception as err:
            logger.debug(f"Other error occurred: {err}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=failure_message.format(
                    resource_lookup_dto.resource_code,
                    resource_lookup_dto.resource_type,
                    resource_lookup_dto.lang_name,
                ),
            )
            return False
        else:
            return True
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=failure_message.format(
                resource_lookup_dto.resource_code,
                resource_lookup_dto.resource_type,
                resource_lookup_dto.lang_name,
            ),
        )
        return False


def main(document_request: model.DocumentRequest) -> str:
    """
    This is the main entry point for this module.
    """
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
    html_filepath_ = html_filepath(document_request_key_)
    pdf_filepath_ = pdf_filepath(document_request_key_)
    epub_filepath_ = epub_filepath(document_request_key_)
    docx_filepath_ = docx_filepath(document_request_key_)

    if file_utils.asset_file_needs_update(html_filepath_):
        # HTML didn't exist in cache so go ahead and start by getting the
        # resource lookup DTOs for each resource request in the document
        # request.
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
        _, found_resource_lookup_dtos_iter = partition(
            lambda resource_lookup_dto: resource_lookup_dto.url is not None
            and verify_resource_assets_available(resource_lookup_dto),
            resource_lookup_dtos,
        )

        found_resource_lookup_dtos = list(found_resource_lookup_dtos_iter)

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
        content = assemble_content(
            document_request_key_, document_request, book_content_units
        )
        write_html_content_to_file(
            content,
            html_filepath_,
        )

    # Immediately return pre-built PDF if the document has previously been
    # generated and is fresh enough. In that case, front run all requests to
    # the cloud including the more low level resource asset caching
    # mechanism for comparatively immediate return of PDF.
    if document_request.generate_pdf and file_utils.asset_file_needs_update(
        pdf_filepath_
    ):
        logger.info("Generating PDF %s...", pdf_filepath_)
        convert_html_to_pdf(
            html_filepath_,
            pdf_filepath_,
        )
        copy_pdf_to_docker_output_dir(pdf_filepath_)

    if document_request.generate_epub and file_utils.asset_file_needs_update(
        epub_filepath_
    ):
        convert_html_to_epub(
            html_filepath_,
            epub_filepath_,
        )
        copy_epub_to_docker_output_dir(epub_filepath_)

    if document_request.generate_docx and file_utils.asset_file_needs_update(
        docx_filepath_
    ):

        convert_html_to_docx(
            html_filepath_,
            docx_filepath_,
        )
        copy_docx_to_docker_output_dir(docx_filepath_)

    if should_send_email(document_request.email_address):
        if document_request.generate_pdf:
            attachments = [
                model.Attachment(
                    filepath=pdf_filepath_, mime_type=("application", "octet-stream")
                )
            ]
        if document_request.generate_epub:
            attachments.append(
                model.Attachment(
                    filepath=epub_filepath_, mime_type=("application", "octet-stream")
                )
            )
        if document_request.generate_docx:
            attachments.append(
                model.Attachment(
                    filepath=docx_filepath_, mime_type=("application", "octet-stream")
                )
            )

        send_email_with_attachment(
            document_request.email_address,
            attachments,
            document_request_key_,
        )
    return document_request_key_
