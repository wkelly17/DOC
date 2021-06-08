#
#  Copyright (c) 2017 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wycliffeassociates.org>

"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""


import base64
import datetime
import icontract
import logging  # For logdecorator
import os
import pathlib
import pdfkit
import subprocess
import urllib

from logdecorator import log_on_start, log_on_end
from typing import Callable, Dict, List, Optional, Tuple, Union


from document import config
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

logger = config.get_logger(__name__)


class DocumentGenerator:
    """
    This class is the entry point to the backend from Fastapi api.
    Handles turning an incoming document request into a finished
    document.
    """

    # XXX Not sure I'll bother with this precondition since it will be
    # optimized out in production anyway and that is where I'd want to
    # catch spurious resource codes submitted by BIEL.
    # @icontract.require(
    #     lambda document_request: [
    #         (resource_request.resource_code in bible_books.BOOK_NAMES.keys)
    #         for resource_request in document_request.resource_requests
    #     ]
    # )
    @log_on_start(logging.DEBUG, "document_request: {document_request}", logger=logger)
    @log_on_start(logging.DEBUG, "working_dir: {working_dir}", logger=logger)
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

        if not self._output_dir:
            self._output_dir = self._working_dir

        self._resources: List[Resource] = self._initialize_resources(document_request)

        # Uniquely identifies a document request. A resource request
        # is identified by lang_code, resource_type, and
        # resource_code. This can serve as a cache lookup key also so
        # that document requests having the same
        # self._document_request_key can skip processing and simply
        # return the end result document if it still exists and has a
        # modified time of within some arbitrary time window, say, 24
        # hours.
        self._document_request_key = self._initialize_document_request_key(
            document_request
        )
        self._output_filename = os.path.join(
            self._output_dir, "{}.pdf".format(self._document_request_key)
        )

    def run(self) -> None:
        """
        This is the main entry point for this class and the
        backend system.
        """
        # icon no longer exists where it used to. I've saved the
        # icon to ./working/temp for now until we find a different
        # location for the icon if we wish to
        # retrieve it via URL.
        # self._get_unfoldingword_icon()

        # Immediately return pre-built PDF if the document previously been
        # generated and is fresh enough. In that case, front run all requests to
        # the cloud including the more low level resource asset caching
        # mechanism for almost immediate return of PDF.
        if self._document_needs_update():
            self._fetch_resources()
            self._initialize_resource_content()
            self._generate_pdf()
        if config.should_send_email():
            self._send_email_with_pdf_attachment()

    @log_on_start(
        logging.INFO, "Calling _send_email_with_pdf_attachment", logger=logger
    )
    @icontract.require(lambda self: os.path.exists(self._output_filename))
    # FIXME This should probably be made async so that large PDFs
    # don't cause the server to block for a long time.
    def _send_email_with_pdf_attachment(self) -> None:
        """
        If PDF exists, and environment configuration allows sending of
        email, then send an email to the document request
        recipient's email with the PDF attached.
        """

        # Using SendGrid's Python Library
        # https://github.com/sendgrid/sendgrid-python
        # import os
        import sendgrid
        from sendgrid.helpers import mail

        # Get the email HTML body
        html_content = config.get_instantiated_template(
            "email",
            model.EmailPayload(
                document_request_key=self.document_request_key,
            ),
        )
        logger.debug("instantiated email template: {}".format(html_content))

        # Get PDF file contents
        with open(self._output_filename, "rb") as fin:
            data = fin.read()

        # Encode contents of PDF file as Base 64
        encoded = base64.b64encode(data).decode()

        # Build attachment
        attachment = mail.Attachment()
        attachment.file_content = encoded
        attachment.file_type = "application/pdf"
        attachment.file_name = pathlib.Path(self._output_filename).name
        attachment.disposition = "attachment"
        attachment.content_id = "BIEL PDF file"

        sg = sendgrid.SendGridAPIClient(api_key=config.get_sendgrid_api_key())

        # Build the parts of the email message
        from_email = mail.From(config.get_from_email_address())
        to_email = mail.To(self._document_request.email_address)
        subject = mail.Subject("The BIEL PDF you requested is attached")
        content = mail.HtmlContent(html_content)

        # Create the mail message and attach the attachment object
        mail = mail.Mail(from_email, to_email, subject, content)
        mail.add_attachment(attachment)

        # Send the email
        try:
            response = sg.client.mail.send.post(request_body=mail.get())
            logger.debug("response.status_code: {}".format(response.status_code))
            # This can really put out alot since it includes the
            # encoded PDF and if the PDF is a long one, then this will
            # be too much info.
            # logger.debug("response.body: {}".format(response.body))
            logger.debug("response.headers: {}".format(response.headers))
        except mail.SendGridException as sg_exception:
            logger.debug("Problem sending email: {}".format(sg_exception))
        except urllib.error.HTTPError as exception:
            logger.debug("Problem sending email: {}".format(exception))

    # Front run all requests to the cloud, including the
    # more low level resource asset caching mechanism for almost immediate
    # return of PDF.
    @icontract.require(lambda self: self._working_dir and self._document_request_key)
    def _document_needs_update(self) -> bool:
        """
        Perform caching of PDF document according to the
        caching policy expressed in
        file_utils.asset_file_needs_update.
        """
        pdf_file_path = os.path.join(
            self._working_dir, "{}.pdf".format(self._document_request_key)
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
            "About to write HTML to {}".format(
                self.get_finished_html_document_filepath()
            )
        )
        file_utils.write_file(
            self.get_finished_html_document_filepath(),
            self._content,
        )

    def _enclose_html_content(self) -> None:
        """
        Write the enclosing HTML and body elements around the HTML
        body content for the document.
        """
        html = config.get_document_html_header()
        html += self._content
        html += config.get_document_html_footer()
        self._content = html

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
            ", ".join(
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
            ", ".join(
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
            ", ".join(
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
        logger.debug("unloaded resources: {}".format(unloaded))
        html_file_path = "{}.html".format(
            os.path.join(self._working_dir, self._document_request_key)
        )
        assert os.path.exists(html_file_path)
        output_pdf_file_path = "{}.pdf".format(
            os.path.join(self._working_dir, self._document_request_key)
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
        with open(config.get_logo_image_path(), "rb") as fin:
            base64_encoded_logo_image = base64.b64encode(fin.read())
        # FIXME Either or both of the next two expressions could blow
        # up if we fail to read in and encode the image file
        # successfully.
        images: Dict[str, Union[str, bytes]] = {
            "logo": base64_encoded_logo_image,
        }
        # Use Jinja2 to instantiate the cover page.
        cover = config.get_instantiated_template(
            "cover",
            model.CoverPayload(
                title=title,
                unfound=unfound,
                unloaded=unloaded,
                revision_date=revision_date,
                images=images,
            ),
        )
        logger.debug("cover: {}".format(cover))
        cover_filepath = os.path.join(config.get_working_dir(), "cover.html")
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
            logger.debug("Copy PDF command: {}".format(copy_command))
            subprocess.call(copy_command, shell=True)

    @property
    def document_request_key(self) -> str:
        """Provide public access method for other modules."""
        return self._document_request_key

    @property
    def found_resources(self) -> List[Resource]:
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
                resource.get_files()
            else:
                logger.info("{} was not found".format(resource))
                # Keep a list of unfound resources so that we can use
                # it for reporting or retrying.
                self._unfound_resources.append(resource)

    @icontract.require(lambda self: self._found_resources)
    def _initialize_resource_content(self) -> None:
        """
        Initialize the resources from their found assets and
        generate their content for later typesetting.
        """
        for resource in self._found_resources:
            # usfm_tools parser can throw a MalformedUsfmError parse error if the
            # USFM for the resource is malformed (from the perspective of the
            # parser). If that happens keep track of the unloaded resource for
            # reporting on the cover page of the generated PDF and log the issue,
            # but continue handling other resources in the document request.
            try:
                resource.get_content()
            except exceptions.MalformedUsfmError:
                self._unloaded_resources.append(resource)
                logger.debug(
                    "Exception while reading USFM file for {}, skipping this resource and continuing with remaining resource requests, if any.".format(
                        resource
                    )
                )

    @icontract.require(lambda document_request: document_request is not None)
    def _initialize_resources(
        self, document_request: model.DocumentRequest
    ) -> List[Resource]:
        """
        Given a DocumentRequest, return a list of a Resource
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
                "-".join(
                    [
                        resource.lang_code,
                        resource.resource_type,
                        resource.resource_code,
                    ]
                )
                + "_"
            )
        return "{}_{}".format(
            document_request_key[:-1], document_request.assembly_strategy_kind
        )

    @icontract.require(lambda self: self._working_dir and self._document_request_key)
    def get_finished_html_document_filepath(self) -> str:
        """
        Return the location on disk where the HTML finished document may be
        found.
        """
        finished_document_path = "{}.html".format(
            os.path.join(self._working_dir, self._document_request_key)
        )
        return finished_document_path

    @icontract.require(lambda self: self._working_dir and self._document_request_key)
    def get_finished_document_filepath(self) -> str:
        """
        Return the location on disk where the finished PDF document may be
        found.
        """
        finished_document_path = "{}.pdf".format(
            os.path.join(self._working_dir, self._document_request_key)
        )
        return finished_document_path

    @icontract.require(lambda self: self._document_request_key)
    def get_finished_document_request_key(self) -> str:
        """
        Return the finished PDF document request key.
        """
        finished_document_path = "{}.pdf".format(
            os.path.join(self._working_dir, self._document_request_key)
        )
        return self.document_request_key

    def _generate_pdf(self) -> None:
        """
        If the PDF doesn't yet exist, go ahead and generate it
        using the content for each resource.
        """
        if not os.path.isfile(self._output_filename):
            self._assemble_content()
            logger.info("Generating PDF...")
            self._convert_html_to_pdf()

    def _get_unfoldingword_icon(self) -> None:
        """Get Unfolding Word's icon for display in generated PDF."""
        if not os.path.isfile(config.get_logo_image_path()):
            command = "curl -o {}/icon-tn.png {}".format(
                self._working_dir,
                config.get_icon_url(),
            )
            subprocess.call(command, shell=True)
