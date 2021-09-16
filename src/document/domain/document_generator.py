"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""


#  Copyright (c) 2017 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wycliffeassociates.org>


import base64
import datetime

import icontract
import logging  # For logdecorator
import os
import pdfkit
import smtplib
import subprocess

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logdecorator import log_on_start, log_on_end
from typing import Callable, Dict, List, Optional, Union


from document.config import settings
from document.domain import assembly_strategies, bible_books, model
from document.domain.resource import (
    resource_factory,
    Resource,
    USFMResource,
    TNResource,
    TWResource,
    TQResource,
    TAResource,
)
from document.utils import file_utils

from usfm_tools.support import exceptions

logger = settings.get_logger(__name__)

COMMASPACE = ", "
HYPHEN = "-"
UNDERSCORE = "_"


class DocumentGenerator:
    """
    This class is the entry point to the backend from Fastapi api.
    Handles turning an incoming document request into a finished
    document.
    """

    @icontract.require(
        lambda working_dir, output_dir, document_request: working_dir
        and output_dir
        and document_request
        and document_request.resource_requests
        and [
            resource_request
            for resource_request in document_request.resource_requests
            if resource_request.lang_code
            and resource_request.resource_type
            in settings.resource_type_lookup_map().keys()
            and resource_request.resource_code in bible_books.BOOK_NAMES.keys()
        ]
    )
    @log_on_start(logging.DEBUG, "document_request: {document_request}", logger=logger)
    @log_on_start(logging.DEBUG, "working_dir: {working_dir}", logger=logger)
    @log_on_start(logging.DEBUG, "output_dir: {output_dir}", logger=logger)
    @log_on_end(
        logging.DEBUG,
        "self._document_request_key: {self._document_request_key}",
        logger=logger,
    )
    def __init__(
        self,
        document_request: model.DocumentRequest,
        working_dir: str,
        output_dir: str,
    ) -> None:
        self._document_request: model.DocumentRequest = document_request
        self._assembly_strategy: Callable[[DocumentGenerator], str]
        self.assembly_sub_strategy: Callable[
            [
                Optional[USFMResource],
                Optional[TNResource],
                Optional[TQResource],
                Optional[TWResource],
                Optional[TAResource],
                Optional[USFMResource],
                model.AssemblySubstrategyEnum,
            ],
            model.HtmlContent,
        ]
        self.assembly_sub_strategy_for_book_then_lang: Callable[
            [
                List[USFMResource],
                List[TNResource],
                List[TQResource],
                List[TWResource],
                List[TAResource],
                model.AssemblySubstrategyEnum,
            ],
            model.HtmlContent,
        ]
        self._working_dir = working_dir
        self._output_dir = output_dir
        # In the end, prior to PDF generation, this is where the
        # generated HTML is stored.
        self._content = ""
        # Store resource requests that were requested, but do not
        # exist.
        self._unfound_resources: List[Resource] = []
        self._found_resources: List[Resource] = []
        self._unloaded_resources: List[Resource] = []

        # Uniquely identifies a document request. A resource request
        # is identified by lang_code, resource_type, and
        # resource_code. This can serve as a cache lookup key also so
        # that document requests having the same
        # self._document_request_key can skip processing and simply
        # return the end result document if it still exists and has a
        # modified time of within some arbitrary time window, say, 24
        # hours. Needs to be called before _initialize_resources
        # because the return value is used there.
        self._document_request_key = self._initialize_document_request_key(
            document_request
        )
        self._resources: List[Resource] = self._initialize_resources(document_request)

        self._output_filename = os.path.join(
            self._output_dir, "{}.pdf".format(self._document_request_key)
        )

    def run(self) -> None:
        """
        This is the main entry point for this class and the
        backend system.
        """
        # Immediately return pre-built PDF if the document previously been
        # generated and is fresh enough. In that case, front run all requests to
        # the cloud including the more low level resource asset caching
        # mechanism for comparatively immediate return of PDF.
        if self._document_needs_update():
            self._fetch_resources()
            self._initialize_resource_content()
            self._generate_pdf()
        if self._should_send_email():
            self._send_email_with_pdf_attachment()

    def _should_send_email(self) -> bool:
        """
        Return True if configuration is set to send email and the user
        has supplied an email address.
        """
        return settings.SEND_EMAIL and self._document_request.email_address is not None

    @log_on_start(
        logging.INFO, "Calling _send_email_with_pdf_attachment", logger=logger
    )
    @icontract.require(lambda self: os.path.exists(self._output_filename))
    def _send_email_with_pdf_attachment(self) -> None:
        """
        If PDF exists, and environment configuration allows sending of
        email, then send an email to the document request
        recipient's email with the PDF attached.
        """
        if self._document_request.email_address:  # make mypy happy though redundant
            sender = settings.FROM_EMAIL_ADDRESS
            email_password = settings.SMTP_PASSWORD
            recipients = [self._document_request.email_address]

            logger.debug("Email sender %s, recipients: %s", sender, recipients)

            # Create the enclosing (outer) message
            outer = MIMEMultipart()
            outer["Subject"] = settings.EMAIL_SEND_SUBJECT
            outer["To"] = COMMASPACE.join(recipients)
            outer["From"] = sender
            # outer.preamble = "You will not see this in a MIME-aware mail reader.\n"

            # List of attachments
            attachments = [self._output_filename]

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
            message_body = settings.instantiated_template(
                "email",
                model.EmailPayload(
                    document_request_key=self.document_request_key,
                ),
            )
            logger.debug("instantiated email template: %s", message_body)

            outer.attach(MIMEText(message_body, "plain"))

            composed = outer.as_string()

            # Send the email
            try:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    smtp.login(sender, email_password)
                    smtp.sendmail(sender, recipients, composed)
                    smtp.close()
                logger.info("Email sent!")
            except Exception:
                logger.exception("Unable to send the email. Caught exception: ")

    @icontract.require(lambda self: self._working_dir and self._document_request_key)
    def _document_needs_update(self) -> bool:
        """
        Perform caching of PDF document according to the
        caching policy expressed in
        file_utils.asset_file_needs_update.

        Front run all requests to the cloud, including the more low
        level resource asset caching mechanism for almost immediate
        return of PDF.
        """
        pdf_file_path = os.path.join(
            self._output_dir, "{}.pdf".format(self._document_request_key)
        )
        return file_utils.asset_file_needs_update(pdf_file_path)

    def _assemble_content(self) -> None:
        """
        Concatenate/interleave the content from all requested resources
        according to the assembly_strategy requested and write out to a single
        HTML file excluding a wrapping HTML and BODY element.
        Precondition: each resource has already generated HTML of its
        body content (sans enclosing HTML and body elements) and
        stored it in its _content instance variable.
        """
        self._assembly_strategy = assembly_strategies.assembly_strategy_factory(
            self._document_request.assembly_strategy_kind
        )
        # Pass self as param because the Callable stored in
        # self._assembly_strategy is a function and not a method.
        self._content = self._assembly_strategy(self)
        self._enclose_html_content()
        logger.debug(
            "About to write HTML to %s", self.finished_html_document_filepath()
        )
        file_utils.write_file(
            self.finished_html_document_filepath(),
            self._content,
        )

    def _enclose_html_content(self) -> None:
        """
        Write the enclosing HTML and body elements around the HTML
        body content for the document.
        """
        html = []
        html.append(settings.document_html_header())
        html.append(self._content)
        html.append(settings.document_html_footer())
        self._content = "".join(html)

    @log_on_start(
        logging.DEBUG, "PDF to be written to: {self._output_dir}", logger=logger
    )
    def _convert_html_to_pdf(self) -> None:
        """Generate PDF from HTML contained in self.content."""
        now = datetime.datetime.now()
        revision_date = "Generated on: {}-{}-{}".format(now.year, now.month, now.day)
        # FIXME This should probably be something else, but this will
        # do for now.
        title = "{}".format(
            COMMASPACE.join(
                sorted(
                    {
                        "{}: {}".format(
                            resource.lang_name,
                            bible_books.BOOK_NAMES[resource.resource_code],
                        )
                        for resource in self._found_resources
                    }
                )
            )
        )
        unfound = "{}".format(
            COMMASPACE.join(
                sorted(
                    {
                        "{}-{}-{}".format(
                            resource.lang_code,
                            resource.resource_type,
                            resource.resource_code,
                        )
                        for resource in self._unfound_resources
                    }
                )
            )
        )
        unloaded = "{}".format(
            COMMASPACE.join(
                sorted(
                    {
                        "{}-{}-{}".format(
                            resource.lang_code,
                            resource.resource_type,
                            resource.resource_code,
                        )
                        for resource in self._unloaded_resources
                    }
                )
            )
        )
        logger.debug("Resources that could not be loaded: {}".format(unloaded))
        html_file_path = "{}.html".format(
            os.path.join(self._output_dir, self._document_request_key)
        )
        assert os.path.exists(html_file_path)
        output_pdf_file_path = "{}.pdf".format(
            os.path.join(self._output_dir, self._document_request_key)
        )
        # For options see https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
        options = {
            "page-size": "Letter",
            # 'margin-top': '0.75in',
            # 'margin-right': '0.75in',
            # 'margin-bottom': '0.75in',
            # 'margin-left': '0.75in',
            "encoding": "UTF-8",
            "load-error-handling": "ignore",
            "outline": None,  # Produce an outline
            "outline-depth": "3",  # Only go depth of 3 on the outline
            "enable-internal-links": None,  # enable internal links
            "header-left": "[section]",
            "header-right": "[subsection]",
            "header-line": None,  # Produce a line under the header
            "footer-center": "[page]",
            "footer-line": None,  # Produce a line above the footer
        }
        with open(settings.LOGO_IMAGE_PATH, "rb") as fin:
            base64_encoded_logo_image = base64.b64encode(fin.read())
            images: Dict[str, Union[str, bytes]] = {
                "logo": base64_encoded_logo_image,
            }
        # Use Jinja2 to instantiate the cover page.
        cover = settings.instantiated_template(
            "cover",
            model.CoverPayload(
                title=title,
                unfound=unfound,
                unloaded=unloaded,
                revision_date=revision_date,
                images=images,
            ),
        )
        # logger.debug("cover: %s", cover)
        cover_filepath = os.path.join(settings.working_dir(), "cover.html")
        with open(cover_filepath, "w") as fout:
            fout.write(cover)
        pdfkit.from_file(
            html_file_path, output_pdf_file_path, options=options, cover=cover_filepath
        )
        assert os.path.exists(output_pdf_file_path)
        copy_command = "cp {}/{}.pdf {}".format(
            self._output_dir, self._document_request_key, "/output"
        )
        logger.debug("IN_CONTAINER: {}".format(os.environ.get("IN_CONTAINER")))
        if os.environ.get("IN_CONTAINER"):
            logger.info("About to cp PDF to Docker bind mount on host")
            logger.debug("Copy PDF command: %s", copy_command)
            subprocess.call(copy_command, shell=True)

    @property
    def document_request_key(self) -> str:
        """Provide public access method for other modules."""
        return self._document_request_key

    @property
    def found_resources(self) -> List[Resource]:
        """Provide public access method for other modules."""
        return self._found_resources

    @icontract.require(lambda self: self._resources)
    @icontract.snapshot(
        lambda self: len(self._found_resources), name="len_found_resources"
    )
    @icontract.snapshot(
        lambda self: len(self._unfound_resources), name="len_unfound_resources"
    )
    @icontract.ensure(
        lambda self, OLD: len(self._found_resources) > OLD.len_found_resources
        or len(self._unfound_resources) > OLD.len_unfound_resources
    )
    def _fetch_resources(self) -> None:
        """
        Get the resources' files from the network. Those that are
        found successfully add to self.found_resources. Those that are
        not found add to self.unfound_resources.
        """
        for resource in self._resources:
            resource.find_location()
            if resource.is_found():
                # Keep a list of resources that were found, we'll use
                # it soon.
                self._found_resources.append(resource)
                resource.provision_asset_files()
            else:
                logger.info("{} was not found".format(resource))
                # Keep a list of unfound resources so that we can use
                # it for reporting or retrying.
                self._unfound_resources.append(resource)

    # NOTE It is possible to have not found any resources due to a
    # malformed document request, e.g., asking for a resource that
    # doesn't exist. Thus we can't assert that self._found_resources
    # has at least one resource.
    # @icontract.require(lambda self: self._found_resources)
    def _initialize_resource_content(self) -> None:
        """
        Initialize the resources from their found assets and
        generate their content for later typesetting.
        """
        for resource in self._found_resources:
            # usfm_tools parser can throw a MalformedUsfmError parse error if the
            # USFM for the resource is malformed (from the perspective of the
            # parser). If that happens keep track of said usfm resource for
            # reporting on the cover page of the generated PDF and log the issue,
            # but continue handling other resources in the document request.
            try:
                resource.update_resource_with_asset_content()
            except exceptions.MalformedUsfmError:
                self._unloaded_resources.append(resource)
                logger.debug(
                    "Exception while reading USFM file for %s, skipping this resource and continuing with remaining resource requests, if any.",
                    resource,
                )
                logger.exception("Caught exception:")

    def _initialize_resources(
        self, document_request: model.DocumentRequest
    ) -> List[Resource]:
        """
        Given a DocumentRequest, return a list of Resource
        instances, one for each ResourceRequest in the
        DocumentRequest.
        """
        resources: List[Resource] = []
        for resource_request in document_request.resource_requests:
            resources.append(
                resource_factory(
                    self._working_dir,
                    self._output_dir,
                    resource_request,
                    document_request.resource_requests,
                )
            )
        return resources

    def _initialize_document_request_key(
        self, document_request: model.DocumentRequest
    ) -> str:
        """Return the document_request_key."""
        document_request_key = ""
        for resource in document_request.resource_requests:
            document_request_key += (
                HYPHEN.join(
                    [
                        resource.lang_code,
                        resource.resource_type,
                        resource.resource_code,
                    ]
                )
                + UNDERSCORE
            )
        return "{}_{}".format(
            document_request_key[:-1], document_request.assembly_strategy_kind
        )

    @icontract.require(lambda self: self._working_dir and self._document_request_key)
    def finished_html_document_filepath(self) -> str:
        """
        Return the location on disk where the HTML finished document may be
        found.
        """
        return "{}.html".format(
            os.path.join(self._output_dir, self._document_request_key)
        )

    @icontract.require(lambda self: self._working_dir and self._document_request_key)
    def finished_document_filepath(self) -> str:
        """
        Return the location on disk where the finished PDF document may be
        found.
        """
        return "{}.pdf".format(
            os.path.join(self._output_dir, self._document_request_key)
        )

    def _generate_pdf(self) -> None:
        """
        If the PDF doesn't yet exist, go ahead and generate it
        using the content for each resource.
        """
        if not os.path.isfile(self._output_filename):
            self._assemble_content()
            logger.info("Generating PDF...")
            self._convert_html_to_pdf()
