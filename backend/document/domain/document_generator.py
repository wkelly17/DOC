"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""

import shutil
import smtplib
import subprocess
import time
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename, exists, join
from typing import Any, Iterable, Mapping, Optional, Sequence

import jinja2
import pdfkit  # type: ignore
from celery import current_task
from document.config import settings
from document.domain import (
    bible_books,
    parsing,
    resource_lookup,
    worker,
)
from document.domain.assembly_strategies import assembly_strategies
from document.domain.model import (
    AssemblyLayoutEnum,
    AssemblyStrategyEnum,
    Attachment,
    BookContent,
    ChunkSizeEnum,
    DocumentRequest,
    HtmlContent,
    ResourceRequest,
    TWBook,
    TWUse,
    USFMBook,
)
from document.utils import file_utils
from pydantic import Json
from toolz import unique  # type: ignore

logger = settings.logger(__name__)


def document_request_key(
    resource_requests: Sequence[ResourceRequest],
    assembly_strategy_kind: AssemblyStrategyEnum,
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
    max_filename_len: int = 240,
    underscore: str = "_",
    hyphen: str = "-",
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
    resource_request_keys = underscore.join(
        [
            hyphen.join(
                [
                    resource_request.lang_code,
                    resource_request.resource_type,
                    resource_request.resource_code,
                ]
            )
            for resource_request in resource_requests
        ]
    )
    document_request_key = "{}_{}_{}_{}".format(
        resource_request_keys,
        assembly_strategy_kind.value,
        assembly_layout_kind.value,
        chunk_size.value,
    )
    if len(document_request_key) >= max_filename_len:
        # Likely the generated filename was too long for the OS where this is
        # running. In that case, use the current time as a document_request_key
        # value as doing so results in an acceptably short length.
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


def instantiated_template(template_lookup_key: str, document_request_key: str) -> str:
    """
    Instantiate Jinja2 template with dto BaseModel instance. Return
    instantiated template as string.
    """
    with open(template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    env = jinja2.Environment(autoescape=True).from_string(template)
    return env.render(data=document_request_key)


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
    assembly_layout_kind: Optional[AssemblyLayoutEnum],
) -> str:
    """
    Choose the appropriate HTML header given the
    assembly_layout_kind. The HTML header, naturally, contains the CSS
    definitions and they in turn can be used to affect visual
    compactness.
    """
    if assembly_layout_kind and assembly_layout_kind in [
        AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
    ]:
        return template("header_compact_enclosing")
    else:
        return template("header_enclosing")


def uses_section(
    uses: Sequence[TWUse],
    translation_word_verse_section_header_str: str = settings.TRANSLATION_WORD_VERSE_SECTION_HEADER_STR,
    unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
    translation_word_verse_ref_item_fmt_str: str = settings.TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR,
    unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
    book_numbers: Mapping[str, str] = bible_books.BOOK_NUMBERS,
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
    num_zeros: int = 3,
) -> HtmlContent:
    """
    Construct and return the 'Uses:' section which comes at the end of
    a translation word definition and wherein each item points to
    verses (as targeted by lang_code, book_id, chapter_num, and
    verse_num) wherein the word occurs.
    """
    html: list[HtmlContent] = []
    html.append(translation_word_verse_section_header_str)
    html.append(unordered_list_begin_str)
    for use in uses:
        html_content_str = HtmlContent(
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
    return HtmlContent("\n".join(html))


def translation_words_section(
    book_content_unit: TWBook,
    include_uses_section: bool = True,
    resource_type_name_fmt_str: str = settings.RESOURCE_TYPE_NAME_FMT_STR,
    opening_h3_fmt_str: str = settings.OPENING_H3_FMT_STR,
    opening_h3_with_id_fmt_str: str = settings.OPENING_H3_WITH_ID_FMT_STR,
) -> Iterable[HtmlContent]:
    """
    Build and return the translation words definition section, i.e.,
    the list of all translation words for this language, book
    combination. Include a 'Uses:' section that points from the
    translation word back to the verses which include the translation
    word if include_uses_section is True.
    """
    if book_content_unit.name_content_pairs:
        yield HtmlContent(
            resource_type_name_fmt_str.format(book_content_unit.resource_type_name)
        )

    for name_content_pair in book_content_unit.name_content_pairs:
        # NOTE Another approach to including translation words would be to
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
        name_content_pair.content = HtmlContent(
            name_content_pair.content.replace(
                opening_h3_fmt_str.format(name_content_pair.localized_word),
                opening_h3_with_id_fmt_str.format(
                    book_content_unit.lang_code,
                    name_content_pair.localized_word,
                    name_content_pair.localized_word,
                ),
            )
        )
        uses_section_ = HtmlContent("")

        # See comment above.
        if (
            include_uses_section
            and name_content_pair.localized_word in book_content_unit.uses
        ):
            uses_section_ = uses_section(
                book_content_unit.uses[name_content_pair.localized_word]
            )
            name_content_pair.content = HtmlContent(
                name_content_pair.content + uses_section_
            )
        yield name_content_pair.content


def assemble_content(
    document_request_key: str,
    document_request: DocumentRequest,
    book_content_units: Iterable[BookContent],
) -> str:
    """
    Assemble and return the content from all requested resources according to the
    assembly_strategy requested.
    """
    # Get the assembly strategy function appropriate given the users
    # choice of document_request.assembly_strategy_kind
    assembly_strategy = assembly_strategies.assembly_strategy_factory(
        document_request.assembly_strategy_kind
    )
    t0 = time.time()
    # Now, actually do the assembly given the additional
    # information of the document_request.assembly_layout_kind.
    content = "".join(
        assembly_strategy(
            book_content_units,
            document_request.assembly_layout_kind,
            document_request.chunk_size,
        )
    )
    t1 = time.time()
    logger.debug("Time for interleaving document: %s", t1 - t0)

    t0 = time.time()
    tw_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, TWBook)
    ]
    # We need to see if the document request included any usfm because
    # if it did we'll generate not only the TW word defs but also the
    # links to them from the notes area that exists adjacent to the
    # scripture versees themselves.
    usfm_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, USFMBook)
    ]
    # Add the translation words definition section for each language requested.
    for tw_book_content_unit in unique(
        tw_book_content_units, key=lambda unit: unit.lang_code
    ):
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

    t1 = time.time()
    logger.debug("Time for add TW content to document: %s", t1 - t0)

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
    attachments: list[Attachment],
    document_request_key: str,
    content_disposition: str = "attachment",
    from_email_address: str = settings.FROM_EMAIL_ADDRESS,
    smtp_password: str = settings.SMTP_PASSWORD,
    email_send_subject: str = settings.EMAIL_SEND_SUBJECT,
    smtp_host: str = settings.SMTP_HOST,
    smtp_port: int = settings.SMTP_PORT,
    comma_space: str = ", ",
) -> None:
    """
    If environment configuration allows sending of
    email, then send an email to the document request
    recipient's email with the document attached.
    """
    lexception = logger.exception

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

        # Add the attachments to the message
        for attachment in attachments:
            try:
                with open(attachment.filepath, "rb") as fp:
                    msg = MIMEBase(attachment.mime_type[0], attachment.mime_type[1])
                    msg.set_payload(fp.read())
                encode_base64(msg)
                msg.add_header(
                    "Content-Disposition",
                    content_disposition,
                    filename=basename(attachment.filepath),
                )
                outer.attach(msg)
            except Exception:
                lexception("Unable to open one of the attachments. Caught exception: ")

        # Get the email body
        message_body = instantiated_template("email", document_request_key)
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


# HTML to PDF converters:
# princexml ($$$$) or same through docraptor ($$),
# wkhtmltopdf via pdfkit (can't handle column-count directive),
# weasyprint (does a nice job, but is slow),
# pagedjs-cli (does a really nice job, but is really slow - uses puppeteer underneath),
# electron-pdf (similar speed to wkhtmltopdf) which uses chrome underneath the hood,
# gotenburg which uses chrome under the hood and provides a nice api in Docker (untested),
# raw chrome headless (works well and is about the same speed as weasyprint),
# ebook-convert (currently blows up because docker runs chrome as root)
def convert_html_to_pdf(
    html_filepath: str,
    pdf_filepath: str,
    email_address: Optional[str],
    document_request_key: str,
    wkhtmltopdf_options: dict[str, Optional[str]] = settings.WKHTMLTOPDF_OPTIONS,
) -> None:
    """
    Generate PDF from HTML, copy it to output directory, possibly send to email_address as attachment.
    """
    assert exists(html_filepath)
    logger.info("Generating PDF %s...", pdf_filepath)

    t0 = time.time()
    pdfkit.from_file(
        html_filepath,
        pdf_filepath,
        options=wkhtmltopdf_options,
    )
    t1 = time.time()
    logger.debug("Time for converting HTML to PDF: %s", t1 - t0)
    copy_file_to_docker_output_dir(pdf_filepath)
    if should_send_email(email_address):
        attachments = [
            Attachment(filepath=pdf_filepath, mime_type=("application", "pdf"))
        ]
        current_task.update_state(state="Sending email")
        send_email_with_attachment(
            email_address,
            attachments,
            document_request_key,
        )


# HTML to ePub converters:
# pandoc (this doesn't respect two column),
# html-to-epub which is written in go (this doesn't respect two column),
# ebook-convert (this respects two column).
def convert_html_to_epub(
    html_filepath: str,
    epub_filepath: str,
    email_address: Optional[str],
    document_request_key: str,
    pandoc_options: str = settings.PANDOC_OPTIONS,
) -> None:
    """Generate ePub from HTML, possibly send to email_address as attachment."""
    assert exists(html_filepath)
    ebook_convert_command = (
        "/calibre-bin/calibre/ebook-convert {} {} --no-default-epub-cover".format(
            html_filepath, epub_filepath
        )
    )
    logger.debug("Generate ePub command: %s", ebook_convert_command)
    t0 = time.time()
    subprocess.call(ebook_convert_command, shell=True)
    t1 = time.time()
    logger.debug("Time for converting HTML to ePub: %s", t1 - t0)
    copy_file_to_docker_output_dir(epub_filepath)
    if should_send_email(email_address):
        attachments = [
            Attachment(filepath=epub_filepath, mime_type=("application", "epub+zip"))
        ]

        current_task.update_state(state="Sending email")
        send_email_with_attachment(
            email_address,
            attachments,
            document_request_key,
        )


# HTML to DOCX conversion:
# pandoc cannot handle two column layouts (manually created or with
# column-count),
# ebook-convert handles two column, but the page breaking is buggy,
# python-docx can build Docx from scratch but would require change in
# pipeline as it doesn't do HTML to DOCX conversion. Ironically, if python-docx
# gave the greatest control over document creation we could get PDFs
# from the Docx possibly. If we went this direction it would mean
# modifying the USFM parser to have a Docx renderer.
# pdf2docx can (with some bugginess/imperfections) create a Docx from
# a PDF including two column layout, but it takes a really long time
# and for documents that include, say, TW resource, it could take hours.
def convert_html_to_docx(
    html_filepath: str,
    docx_filepath: str,
    email_address: Optional[str],
    document_request_key: str,
    pandoc_options: str = settings.PANDOC_OPTIONS,
) -> None:
    """Generate Docx from HTML, possibly send to email_address as attachment."""
    assert exists(html_filepath)
    pandoc_command = "pandoc {} {} -o {}".format(
        pandoc_options,
        html_filepath,
        docx_filepath,
    )
    logger.debug("Generate Docx command: %s", pandoc_command)
    t0 = time.time()
    subprocess.call(pandoc_command, shell=True)
    t1 = time.time()
    logger.debug("Time for converting HTML to Docx: %s", t1 - t0)
    copy_file_to_docker_output_dir(docx_filepath)
    if should_send_email(email_address):
        attachments = [
            Attachment(
                filepath=docx_filepath,
                mime_type=(
                    "application",
                    "vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            )
        ]
        current_task.update_state(state="Sending email")
        send_email_with_attachment(
            email_address,
            attachments,
            document_request_key,
        )


def html_filepath(
    document_request_key: str, output_dir: str = settings.DOCUMENT_OUTPUT_DIR
) -> str:
    """Given document_request_key, return the HTML output file path."""
    return join(output_dir, "{}.html".format(document_request_key))


def pdf_filepath(
    document_request_key: str, output_dir: str = settings.DOCUMENT_OUTPUT_DIR
) -> str:
    """Given document_request_key, return the PDF output file path."""
    return join(output_dir, "{}.pdf".format(document_request_key))


def epub_filepath(
    document_request_key: str, output_dir: str = settings.DOCUMENT_OUTPUT_DIR
) -> str:
    """Given document_request_key, return the ePub output file path."""
    return join(output_dir, "{}.epub".format(document_request_key))


def docx_filepath(
    document_request_key: str, output_dir: str = settings.DOCUMENT_OUTPUT_DIR
) -> str:
    """Given document_request_key, return the docx output file path."""
    return join(output_dir, "{}.docx".format(document_request_key))


def cover_filepath(
    document_request_key: str, output_dir: str = settings.DOCUMENT_OUTPUT_DIR
) -> str:
    """Given document_request_key, return the HTML cover output file path."""
    return join(output_dir, "{}_cover.html".format(document_request_key))


def select_assembly_layout_kind(
    document_request: DocumentRequest,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    language_book_order: AssemblyStrategyEnum = AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
    book_language_order: AssemblyStrategyEnum = AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
    one_column_compact: AssemblyLayoutEnum = AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
    sl_sr: AssemblyLayoutEnum = AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
    sl_sr_compact: AssemblyLayoutEnum = AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
    one_column: AssemblyLayoutEnum = AssemblyLayoutEnum.ONE_COLUMN,
) -> AssemblyLayoutEnum:
    """
    Make an intelligent choice of what layout to use given the
    DocumentRequest instance the user has requested. Note that prior to
    this, we've already validated the DocumentRequest instance in the
    DocumentRequest's validator. If we hadn't then we wouldn't be able
    to make the assumptions this function makes.
    """

    # The assembly_layout_kind does not get set by the UI, so if it is set
    # that means that the request is coming from a client other than the UI
    # which may set its value. In either case case validation of the
    # DocumentRequest instance will have already occurred by this point thus
    # ensuring that the document request's values are valid in which case we
    # can simply return it the assembly_layout_kind that was set.
    if document_request.assembly_layout_kind:
        return document_request.assembly_layout_kind

    # assembly_layout_kind was not yet chosen, but validation tells us
    # that other values of the document request instance are valid, so now
    # we can intelligently choose the right assembly_layout_kind for the
    # user based on the other values of the document request instance.
    if (
        document_request.layout_for_print
        and document_request.assembly_strategy_kind == language_book_order
    ):
        return one_column_compact
    elif (
        not document_request.layout_for_print
        and document_request.assembly_strategy_kind == language_book_order
    ):
        return one_column
    elif (
        not document_request.layout_for_print
        and document_request.assembly_strategy_kind == book_language_order
    ):
        return sl_sr

    return one_column


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
    copy_file_to_docker_output_dir(output_filename)


def copy_file_to_docker_output_dir(
    filepath: str,
    document_output_dir: str = settings.DOCUMENT_SERVE_DIR,
) -> None:
    """
    Copy file to docker_container_document_output_dir.
    """
    assert exists(filepath)
    logger.debug("About to cp file to %s", document_output_dir)
    shutil.copy(filepath, document_output_dir)


@worker.app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def main(document_request_json: Json[Any]) -> Json[Any]:
    """
    This is the main entry point for this module.
    """
    document_request = DocumentRequest.parse_raw(document_request_json)
    logger.debug(
        "document_request: %s",
        document_request,
    )
    document_request.assembly_layout_kind = select_assembly_layout_kind(
        document_request
    )
    # Generate the document request key that identifies this and
    # identical document requests.
    document_request_key_ = document_request_key(
        document_request.resource_requests,
        document_request.assembly_strategy_kind,
        document_request.assembly_layout_kind,
        document_request.chunk_size,
    )
    html_filepath_ = html_filepath(document_request_key_)
    pdf_filepath_ = pdf_filepath(document_request_key_)
    epub_filepath_ = epub_filepath(document_request_key_)
    docx_filepath_ = docx_filepath(document_request_key_)

    if file_utils.asset_file_needs_update(html_filepath_):
        # Update the state of the worker process. This is used by the
        # UI to report status.
        current_task.update_state(state="Locating assets")
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

        # Determine which resource URLs were actually found.
        found_resource_lookup_dtos = [
            resource_lookup_dto
            for resource_lookup_dto in resource_lookup_dtos
            if resource_lookup_dto.url is not None
        ]

        current_task.update_state(state="Provisioning asset files")
        t0 = time.time()
        resource_dirs = [
            resource_lookup.provision_asset_files(dto)
            for dto in found_resource_lookup_dtos
        ]
        t1 = time.time()
        logger.debug(
            "Time to provision asset files (acquire and write to disk): %s", t1 - t0
        )

        current_task.update_state(state="Parsing asset files")
        # Initialize found resources from their provisioned assets.
        t0 = time.time()
        book_content_units = [
            parsing.book_content(
                resource_lookup_dto,
                resource_dir,
                document_request.resource_requests,
                document_request.layout_for_print,
                document_request.chunk_size,
            )
            for resource_lookup_dto, resource_dir in zip(
                found_resource_lookup_dtos, resource_dirs
            )
        ]

        t1 = time.time()
        logger.debug("Time to parse all resource content: %s", t1 - t0)

        current_task.update_state(state="Assembling content")
        content = assemble_content(
            document_request_key_, document_request, book_content_units
        )
        write_html_content_to_file(
            content,
            html_filepath_,
        )
    else:
        logger.debug("Cache hit for %s", html_filepath_)

    # Immediately return pre-built PDF if the document has previously been
    # generated and is fresh enough. In that case, front run all requests to
    # the cloud including the more low level resource asset caching
    # mechanism for comparatively immediate return of PDF.
    if document_request.generate_pdf and file_utils.asset_file_needs_update(
        pdf_filepath_
    ):
        current_task.update_state(state="Converting to PDF format")
        convert_html_to_pdf(
            html_filepath_,
            pdf_filepath_,
            document_request.email_address,
            document_request_key_,
        )
    else:
        logger.debug("Cache hit for %s", pdf_filepath_)

    if document_request.generate_epub and file_utils.asset_file_needs_update(
        epub_filepath_
    ):
        current_task.update_state(state="Converting to ePub format")
        convert_html_to_epub(
            html_filepath_,
            epub_filepath_,
            document_request.email_address,
            document_request_key_,
        )
    else:
        logger.debug("Cache hit for %s", epub_filepath_)

    if document_request.generate_docx and file_utils.asset_file_needs_update(
        docx_filepath_
    ):
        current_task.update_state(state="Converting to Docx format")
        convert_html_to_docx(
            html_filepath_,
            docx_filepath_,
            document_request.email_address,
            document_request_key_,
        )
    else:
        logger.debug("Cache hit for %s", docx_filepath_)

    return document_request_key_
