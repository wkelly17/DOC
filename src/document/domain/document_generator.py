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
import logging  # For logdecorator
import os
import pdfkit
import subprocess
from logdecorator import log_on_start, log_on_end
from typing import Callable, Dict, List, Optional, Tuple, Union

import icontract

from document import config
from document.domain import assembly_strategies, bible_books, model, resource_lookup
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
        self._assembly_sub_strategy: Callable[
            [
                Optional[USFMResource],
                Optional[TNResource],
                Optional[TQResource],
                Optional[TWResource],
                Optional[TAResource],
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

    def run(self) -> None:
        """
        This is the main entry point for this class and the
        backend system.
        """
        # FIXME icon no longer exists where it used to. I've saved the
        # icon to ./working/temp for now until we find a different
        # location for the icon that is to be used if we wish to
        # retrieve it via URL. Otherwise we'll just always get it from
        # file. Update: for now I am retrieving the legacy icon from
        # archive.org. I've commented it out again though because
        # archive.org is sloooow. Besides I don't think we want
        # something as important as a logo for our PDF cover page to
        # be missing due to network issues.
        # self._get_unfoldingword_icon()

        # Immediately return pre-built PDF if the document has already been
        # requested and is fresh enough. In that case, front run all requests to
        # the cloud including the more low level resource asset caching
        # mechanism for almost immediate return of PDF.
        # if self._document_needs_update():
        self._fetch_resources()
        self._initialize_resource_content()
        self._generate_pdf(pdf_generation_method=config.get_pdf_generation_method())
        # else:
        #     # FIXME Need to handle case where previous document was
        #     generated, but it contained fewer than requested
        #     resources because one of the resources requested had an
        #     invalid resource type for the language requested, e.g.,
        #     lang_code: zh, resource_type: ulb. ulb should have been
        #     cuv for zh.
        #     self._serve_pdf_document()

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

    # FIXME implement
    @log_on_end(
        logging.INFO, "Called _serve_pdf_document (not yet implemented)", logger=logger
    )
    def _serve_pdf_document(self) -> None:
        """
        Placeholder for serving PDF document to the user. NOTE Likely we'll
        hand off the responsibility to a fronting web server like
        nginx because experience says that OS level send-file support
        is more stable than doing it through something like Python.
        """
        pass

    def _assemble_content(self) -> None:
        """
        Concatenate/interleave the content from all requested resources
        according to the assembly_strategy requested and write out to a single
        HTML file excluding a wrapping HTML and BODY element.
        Precondition: each resource has already generated HTML of its
        body content (sans enclosing HTML and body elements) and
        stored it in its _content instance variable.
        """
        self._assembly_strategy = assembly_strategies._assembly_strategy_factory(
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
            self.get_finished_html_document_filepath(), self._content,
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
    def _convert_html2pdf(self) -> None:
        """Generate PDF from HTML contained in self.content."""
        now = datetime.datetime.now()
        revision_date = "{}-{}-{}".format(now.year, now.month, now.day)
        # FIXME This should probably be something else, but this will
        # do for now.
        title = "Resources: {}".format(
            ", ".join(
                sorted(
                    {
                        "{}: {}".format(
                            resource.lang_name,
                            bible_books.BOOK_NAMES[resource.resource_code],
                        )
                        for resource in self._resources
                    }
                )
            )
        )
        # FIXME When run locally xelatex chokes because the LaTeX template does
        # not set the \setmainlanguage{} and \setotherlanguages{} commands of
        # the polyglossia package to any value. I can comment out that LaTeX
        # code and then it runs. Or if I manually edit the final latex file to
        # have these set to English, say, even if more than English is used, and
        # then run xelatex manually on the file it produces the PDF
        # successfully. This issue does not arise when the code is run in the
        # Docker container for some unknown reason.
        command = config.get_pandoc_command().format(
            # First hack at a title. Used to be just self.book_title which
            # doesn't make sense anymore.
            title,
            # FIXME Not all resources have a manifest file from which
            # issued may be initialized. Further, a document request
            # can include multiple languages and multiple resources
            # each of which can have a manifest file. So which issued
            # date would we use? It doesn't really make sense to use
            # it anymore so I am substituting revision_date instead
            # for now.
            # resource._issued if resource._issued else "",
            revision_date,
            # FIXME Not all resources have a manifest file from which
            # version may be initialized. Further, a document request
            # can include multiple languages and multiple resources
            # each of which can have a manifest file, depending on
            # what is requested, and thus a _version; which one would
            # we use? It doesn't make sense to use this anymore. For
            # now I am just going to use some meaningless literal
            # instead of the next commented out line.
            # resource._version if resource._version else ""
            "TBD",
            self._output_dir,
            self._working_dir,
            # FIXME A document generation request is composed of theoretically
            # an infinite number of arbitrarily ordered resources. In this
            # context using the file location for one resource doesn't make
            # sense as in the next commented out line of code. Instead we use
            # the filename unique to the document generation request itself.
            # resource._filename_base,
            self._document_request_key,
            # NOTE Having revision_date likely obviates _issued above.
            revision_date,
            config.get_tex_format_location(),
            config.get_tex_template_location(),
        )
        logger.debug("pandoc command: {}".format(command))
        copy_command = "cp {}/{}.pdf {}".format(
            self._output_dir, self._document_request_key, "/output"
        )
        subprocess.call(command, shell=True)
        logger.debug("IN_CONTAINER: {}".format(os.environ.get("IN_CONTAINER")))
        if os.environ.get("IN_CONTAINER"):
            logger.info("About to cp PDF to /output")
            logger.debug("Copy PDF command: {}".format(copy_command))
            subprocess.call(copy_command, shell=True)

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
                        for resource in self._resources
                    }
                )
            )
        )
        html_file_path = "{}.html".format(
            os.path.join(self._working_dir, self._document_request_key)
        )
        assert os.path.exists(html_file_path)
        output_pdf_file_path = "{}.pdf".format(
            os.path.join(self._working_dir, self._document_request_key)
        )
        options = {
            "page-size": "Letter",
            # 'margin-top': '0.75in',
            # 'margin-right': '0.75in',
            # 'margin-bottom': '0.75in',
            # 'margin-left': '0.75in',
            "encoding": "UTF-8",
            "load-error-handling": "ignore",
            "outline": "",  # Produce an outline
            "outline-depth": "3",  # Only go depth of 3 on the outline
            "enable-internal-links": "",  # enable internal links
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
            model.CoverPayload(title=title, revision_date=revision_date, images=images),
        )
        logger.debug("cover: {}".format(cover))
        with open(os.path.join(config.get_working_dir(), "cover.html"), "w") as fout:
            fout.write(cover)
        cover_filepath = os.path.join(config.get_working_dir(), "cover.html")
        pdfkit.from_file(
            html_file_path, output_pdf_file_path, options=options, cover=cover_filepath
        )
        assert os.path.exists(output_pdf_file_path)
        copy_command = "cp {}/{}.pdf {}".format(
            self._output_dir, self._document_request_key, "/output"
        )
        logger.debug("IN_CONTAINER: {}".format(os.environ.get("IN_CONTAINER")))
        if os.environ.get("IN_CONTAINER"):
            logger.info("About to cp PDF to /output")
            logger.debug("Copy PDF command: {}".format(copy_command))
            subprocess.call(copy_command, shell=True)

    @property
    def document_request_key(self) -> str:
        """Provide public access method for other modules."""
        return self._document_request_key

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
                # it for reporting.
                self._unfound_resources.append(resource)

    @icontract.require(lambda self: self._found_resources)
    def _initialize_resource_content(self) -> None:
        """
        Initialize the resources from their found assets and
        generate their content for later typesetting.
        """
        for resource in self._found_resources:
            resource.get_content()

    @icontract.require(lambda document_request: document_request is not None)
    def _initialize_resources(
        self, document_request: model.DocumentRequest
    ) -> List[Resource]:
        """
        Given a DocumentRequest instance, return a list of Resource
        objects.
        """
        resources: List[Resource] = []
        for resource_request in document_request.resource_requests:
            resources.append(
                resource_factory(self._working_dir, self._output_dir, resource_request,)
            )
        return resources

    # FIXME We probably want to make an (md5) hash of the document request key
    # prior to returning it as otherwise they can get very long if many
    # languages and books are requested. It would be nice to be able to
    # reverse engineer the hash though since the hash input is designed to
    # be a form of documentation of the document request.
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

    def _generate_pdf(
        self, pdf_generation_method: str = model.PdfGenerationMethodEnum.LATEX
    ) -> None:
        """
        If the PDF doesn't yet exist, go ahead and generate it
        using the content for each resource.
        """
        output_filename: str = os.path.join(
            self._output_dir, "{}.pdf".format(self._document_request_key)
        )
        if not os.path.isfile(output_filename):
            self._assemble_content()
            logger.info("Generating PDF...")
            if pdf_generation_method == model.PdfGenerationMethodEnum.LATEX:
                self._convert_html2pdf()
            else:
                self._convert_html_to_pdf()
            # TODO Return json message containing any resources that
            # we failed to find so that the front end can let the user
            # know.

    def _get_unfoldingword_icon(self) -> None:
        """Get Unfolding Word's icon for display in generated PDF."""
        if not os.path.isfile(config.get_logo_image_path()):
            command = "curl -o {}/icon-tn.png {}".format(
                self._working_dir, config.get_icon_url(),
            )
            subprocess.call(command, shell=True)
