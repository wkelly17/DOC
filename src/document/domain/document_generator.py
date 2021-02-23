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

from __future__ import annotations  # https://www.python.org/dev/peps/pep-0563/

import datetime
import itertools
import os
import re
import subprocess
from typing import TYPE_CHECKING, Callable, List

import icontract

from document import config
from document.domain import model
from document.domain.resource import (
    resource_factory,
    USFMResource,
    TNResource,
    # TWResource,
    # TQResource,
    # TAResource,
)
from document.utils import file_utils

# https://www.python.org/dev/peps/pep-0563/
# https://www.stefaanlippens.net/circular-imports-type-hints-python.html
# Python 3.7 now allows type checks to not be evaluated at function or
# class definition time which in turn solves the issue of circular
# imports which using type hinting/checking can create. Circular imports
# are not always a by-product of bad design but sometimes a by-product,
# in those cases where bad design is not the issue, of Python's
# primitive module system (which is quite lacking). So, this PEP
# allows us to practice better engineering practices: inversion of
# control for factored and maintainable software with type hints
# without resorting to putting everything in one module or using
# function-embedded imports, yuk. Note that you must use the import
# ___future__ annotations to make this work as of now, Dec 9, 2020.
# IF you care, here is how Python got here:
# https://github.com/python/typing/issues/105
if TYPE_CHECKING:
    from document.domain.resource import Resource


logger = config.get_logger(__name__)


class DocumentGenerator:
    """
    This class is the entry point to the backend from Fastapi api.
    Handles turning an incoming document request into a finished
    document.
    """

    def __init__(
        self,
        document_request: model.DocumentRequest,
        working_dir: str,
        output_dir: str,
    ) -> None:
        # Get the concrete Strategy pattern Callable based on the
        # assembly_strategy kind passed in from BIEL's UI
        self.assembly_strategy: Callable[
            [DocumentGenerator], str
        ] = _assembly_strategy_factory(document_request.assembly_strategy_kind)
        self.working_dir = working_dir
        self.output_dir = output_dir
        # The Markdown and later HTML for the document which is
        # composed of the Markdown and later HTML for each resource.
        self.content = ""
        # Store resource requests that were requested, but do not
        # exist.
        self.unfound_resources: List[Resource] = []
        self.found_resources: List[Resource] = []

        # Show the dictionary that was passed in.
        logger.debug("document_request: {}".format(document_request))

        if not self.output_dir:
            self.output_dir = self.working_dir

        # logger.debug("Working dir is {}".format(self.working_dir))

        # TODO To be production worthy, we need to make this resilient
        # to errors when creating Resource instances.
        self._resources: List[Resource] = self._initialize_resources(document_request)

        # Uniquely identifies a document request. A resource request
        # is identified by lang_code, resource_type, and
        # resource_code. This can serve as a cache lookup key also so
        # that document requests having the same
        # self._document_request_key can skip processing and simply
        # return the end result document if it still exists.
        self._document_request_key = self._initialize_document_request_key(
            document_request
        )

        logger.debug(
            "self._document_request_key: {}".format(self._document_request_key)
        )

    def run(self) -> None:
        """
        This is the main entry point for this class and the
        backend system.
        """
        # FIXME icon no longer exists where it used to. I've saved the
        # icon to ./working/temp for now until we find a different
        # location for the icon that is to be used.
        # self._get_unfoldingword_icon()

        self._fetch_resources()
        self._initialize_resource_content()
        self._generate_pdf()

    def _assemble_content(self) -> None:
        """
        Concatenate/interleave the content from all requested resources
        according to the assembly_strategy requested and write out to a single
        HTML file excluding a wrapping HTML and BODY element.
        Precondition: each resource has already generated HTML of its
        body content (sans enclosing HTML and body elements) and
        stored it in its _content instance variable.
        """
        self.content = self.assembly_strategy(self)
        self._enclose_html_content()
        logger.debug(
            "About to write HTML to {}".format(self.get_finished_document_filepath())
        )
        file_utils.write_file(
            self.get_finished_document_filepath(), self.content,
        )

    def _enclose_html_content(self) -> None:
        """
        Write the enclosing HTML and body elements around the HTML
        body content for the document.
        """
        html = config.get_document_html_header()
        html += self.content
        html += config.get_document_html_footer()
        self.content = html

    def _convert_html2pdf(self) -> None:
        """Generate PDF from HTML contained in self.content."""
        now = datetime.datetime.now()
        revision_date = "{}-{}-{}".format(now.year, now.month, now.day)
        logger.debug("PDF to be written to: {}".format(self.output_dir))
        # FIXME This should probably be something else, but this will
        # do for now.
        title = "Resources: "
        title += ",".join({resource.resource_code for resource in self._resources})
        # FIXME When run locally xelatex chokes because the LaTeX
        # template does not set the \setmainlanguage{} and
        # \setotherlanguages{} to any value. If I manually edit the
        # final latex file to have these set and then run xelatex
        # manually on the file it produces the PDF sucessfully. This
        # issue does not arise when the code is run in the Docker
        # container for some unknown reason.
        command = config.get_pandoc_command().format(
            # First hack at a title. Used to be just self.book_title which
            # doesn't make sense anymore.
            title,
            # FIXME This should probably be today's date since not all
            # resources have a manifest file from which issued may be
            # initialized. And since we are dealing with multiple resources
            # per document, which issued date would we use? It doesn't really
            # make sense to use it anymore so I am substituting revision_date
            # instead for now.
            # resource._issued if resource._issued else "",
            revision_date,
            # FIXME Not all resources have a manifest file from which version
            # may be initialized. Further, a document request can include
            # multiple resources each of which can have a manifest file,
            # depending on what is requested, and thus a _version, which one
            # would we use? It doesn't make sense to use this anymore. For now
            # I am just going to use some meaningless literal instead of the
            # next commented out line.
            # resource._version if resource._version else ""
            "TBD",
            # Outside vs. inside Docker container
            self.output_dir,
            self.working_dir,
            # FIXME A document generation request is composed of theoretically
            # an infinite number of arbitrarily ordered resources. In this new
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
        # Next command replaces cp /working/tn-temp/*.pdf /output in
        # old system
        copy_command = "cp {}/{}.pdf {}".format(
            self.output_dir, self._document_request_key, "/output"
        )
        # logger.debug(
        #     "os.listdir(self.working_dir): {}".format(os.listdir(self.working_dir))
        # )
        # logger.debug(
        #     "os.listdir(self.output_dir): {}".format(os.listdir(self.output_dir))
        # )
        subprocess.call(command, shell=True)
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
        lambda self: len(self.found_resources), name="len_found_resources"
    )
    @icontract.snapshot(
        lambda self: len(self.unfound_resources), name="len_unfound_resources"
    )
    @icontract.ensure(
        lambda self, OLD: len(self.found_resources) > OLD.len_found_resources
        or len(self.unfound_resources) > OLD.len_unfound_resources
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
                self.found_resources.append(resource)
                resource.get_files()
            else:
                logger.info("{} was not found".format(resource))
                # Keep a list of unfound resources so that we can use
                # it for reporting.
                self.unfound_resources.append(resource)

    @icontract.require(lambda self: self.found_resources)
    def _initialize_resource_content(self) -> None:
        """
        Initialize the resources from their found assets and
        generate their content for later typesetting.
        """
        for resource in self.found_resources:
            resource.initialize_from_assets()
            # NOTE You could pass a USFM resource if it exists to get_content
            # for TResource subclasses. This would presuppose that we initialize
            # USFM resources first in this loop or break out into multiple
            # loops: one for USFM, one for TResource subclasses. Perhaps you
            # would also sort the resources by lang_code so that they are interleaved
            # such that their expected language relationship is retained.
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
                resource_factory(
                    self.working_dir,
                    self.output_dir,
                    resource_request,
                    document_request.assembly_strategy_kind,
                )
            )
        return resources

    def _initialize_document_request_key(
        self, document_request: model.DocumentRequest
    ) -> str:
        """Return the document_request_key."""
        document_request_key = ""
        for resource in document_request.resource_requests:
            # NOTE Alternatively, could create a (md5?) hash of th
            # concatenation of lang_code, resource_type,
            # resource_code.
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

    @icontract.require(lambda self: self.working_dir and self._document_request_key)
    def get_finished_document_filepath(self) -> str:
        """
        Return the location on disk where the finished document may be
        found.
        """
        finished_document_path = "{}.html".format(
            os.path.join(self.working_dir, self._document_request_key)
        )
        return finished_document_path

    def _generate_pdf(self) -> None:
        """
        If the PDF doesn't yet exist, go ahead and generate it
        using the content for each resource.
        """
        output_filename: str = os.path.join(
            self.output_dir, "{}.pdf".format(self._document_request_key)
        )
        if not os.path.isfile(output_filename):
            self._assemble_content()
            logger.info("Generating PDF...")
            self._convert_html2pdf()
            # TODO Return json message containing any resources that
            # we failed to find so that the front end can let the user
            # know.
            logger.debug(
                "Unfound resource requests: {}".format(
                    "; ".join(str(resource) for resource in self.unfound_resources)
                ),
            )

    def _get_unfoldingword_icon(self) -> None:
        """Get Unfolding Word's icon for display in generated PDF."""
        if not os.path.isfile(os.path.join(self.working_dir, "icon-tn.png")):
            command = "curl -o {}/icon-tn.png {}".format(
                self.working_dir, config.get_icon_url(),
            )
            subprocess.call(command, shell=True)


# Assembly strategies utilize the Strategy pattern:
# https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py


def _assemble_content_by_verse(docgen: DocumentGenerator) -> str:
    """
    Assemble and return the collection of resources' content according
    to the 'by verse' strategy with a particular (arbitrary to this
    strategy) ordering of resources. E.g., For Genesis, TN book intro
    if available, For Genesis 1, TN chapter intro if available,
    followed by USFM for Genesis 1:1 followed by Translation Notes for
    Genesis 1:1, followed by Translation words for Genesis 1:1,
    followed by Translation questions for Genesis 1:1, followed by
    Translation answers for Genesis 1:1, etc..

    Example: The user selects, say, two languages: Swahili and
    English. They request USFM (specifically ULB) and TN for both: The
    arbitrary interleaving algorithm for this strategy is:

    1. For English (just because, say, in this strategy we arbitrarily
sort languages alphabetically):
       * For each book:
       ** TN book intro if any
       ** For each chapter:
 ]o      *** TN chapter intro if any
       *** Chapter heading from USFM
       **** For each verse:
       ***** USFM verse
       ***** TN for USFM verse
       ***** (if it had been requested) TW for USFM verse
       ***** (if it had been requested) TQ for USFM verse
       ***** (if it had been requested) TA for USFM verse
       ***** etc.
    1. For Swahili:
       * For each book:
       ** TN book intro if any
       ** For each chapter:
       *** TN chapter intro if any
       *** Chapter heading from USFM
       **** For each verse:
       ***** USFM verse
       ***** TN for USFM verse
       ***** (if it had been requested) TW for USFM verse
       ***** (if it had been requested) TQ for USFM verse
       ***** (if it had been requested) TA for USFM verse
       ***** etc.

    """
    # NOTE: For now we are ignoring links that may be presented. I
    # hope to handle their transformations with a Markdown extension
    # plugin rather than the legacy way of doing regexp search and
    # replace on markdown content that has been concatenated. So we'll
    # transform them at the time the markdown is converted to HTML.

    # NOTE Each strategy can interleave resource material the way it
    # wants. A user could choose a strategy they want at the front
    # end. Presumably, we could offer the user such strategies from a
    # dropdown that would be intelligent enough to only present
    # choices that make sense for the number of languages and
    # resources they have selected, e.g., we wouldn't bother them with
    # the choice of interleaving strategy if for instance all they
    # wanted was TN for Swahili and nothing else.

    # Utility function to clean things up.
    def adjust_book_intro_headings(book_intro: str) -> str:
        """
        Change levels on headings.
        """
        # Move the H2 out of the way, we'll deal with it last.
        book_intro = re.sub(r"h2", r"h6", book_intro)
        book_intro = re.sub(r"h1", r"h2", book_intro)
        book_intro = re.sub(r"h3", r"h4", book_intro)
        # Now make those H6s that we used temporarily into H3s.
        return re.sub(r"h6", r"h3", book_intro)

    def adjust_chapter_intro_headings(chapter_intro: str) -> str:
        """
        Change levels on headings.
        """
        # Move the H2 out of the way, we'll deal with it last.
        chapter_intro = re.sub(r"h4", r"h6", chapter_intro)
        chapter_intro = re.sub(r"h3", r"h4", chapter_intro)
        chapter_intro = re.sub(r"h1", r"h3", chapter_intro)
        chapter_intro = re.sub(r"h2", r"h4", chapter_intro)
        # Now make those unwanted H6s that we used temporarily into H3s.
        return re.sub(r"h6", r"h5", chapter_intro)

    logger.info(
        "Assembling document by interleaving at the verse level using 'verse2' strategy."
    )
    resources_sorted_by_language = sorted(
        docgen.found_resources, key=lambda resource: resource.lang_code
    )
    html = []
    for language, group_by_lang in itertools.groupby(
        resources_sorted_by_language, lambda resource: resource.lang_code
    ):
        html.append("<h1>Language: {}</h1>".format(language))

        # For groupby's sake, we need to first sort
        # group_by_lang before doing a groupby operation on it so that
        # resources will be clumped together by resource code, i.e.,
        # by language, otherwise a new group will be created every time a new
        # resource_code is sequentially encountered.
        resources_sorted_by_book = sorted(
            group_by_lang, key=lambda resource: resource.resource_code
        )
        for book, group_by_book in itertools.groupby(
            resources_sorted_by_book, lambda resource: resource.resource_code
        ):
            html.append("<h2>Book: {}</h2>".format(book))

            # Save grouper generator since it will get exhausted
            # when used and exhausted generators cannot be reused.
            resources = list(group_by_book)
            tn_resources = [
                resource for resource in resources if isinstance(resource, TNResource)
            ]
            # Add in the book intro.
            tn_resource = tn_resources[0] if tn_resources else None
            book_intro = tn_resource.book_payload.intro_html if tn_resource else ""
            book_intro = adjust_book_intro_headings(book_intro)
            html.append(book_intro)

            usfm_resources = [
                resource for resource in resources if isinstance(resource, USFMResource)
            ]
            usfm_resource = usfm_resources[0] if usfm_resources else None

            # FIXME A user could request only TN and not USFM so
            # you'll need to handle that case. In such a case, the
            # else expression will just be to grab the TN and join it
            # into a string and append it to the html local var.
            if usfm_resource:
                # PEP526 disallows declaration of types in for loops, but allows this.
                chapter_num: int
                chapter: model.USFMChapter
                # Dict keys need to be sorted as their order is not guaranteed.
                for chapter_num, chapter in sorted(
                    usfm_resource.chapters_content.items()
                ):
                    # Add in the USFM chapter heading.
                    chapter_heading = chapter.chapter_content[0]
                    # chapter_heading = re.sub(r"h2", r"h3", chapter_heading)
                    html.append(chapter_heading)

                    # Add in the translation notes chapter intro.
                    chapter_intro = (
                        tn_resource.book_payload.chapters[chapter_num].intro_html
                        if tn_resource
                        else ""
                    )
                    chapter_intro = adjust_chapter_intro_headings(chapter_intro)
                    html.append(chapter_intro)

                    # NOTE This commented out section is for use when
                    # we implement a by chapter interleaving strategy.
                    # Skip some useless elements and get the USFM
                    # verse HTML content.
                    # Chapter all at once including formatting HTML
                    # elements. This would be useful for a 'by
                    # chapter' interleaving strategy.
                    # usfm_verses = chapter.chapter_content[3:]

                    # Get TN chapter verses
                    tn_verses = (
                        tn_resource.book_payload.chapters[chapter_num].verses_html
                        if tn_resource
                        else {}
                    )
                    # PEP526 disallows declaration of types in for
                    # loops, but allows this.
                    verse_num: int
                    verse: str
                    # Now let's interleave USFM verse with its
                    # translation note if available.
                    for verse_num, verse in sorted(chapter.chapter_verses.items()):
                        html.append("<h3>Verse</h3>")
                        html.append(verse)
                        if verse_num in tn_verses:
                            html.append("<h3>Translation note</h3>")
                            # Change H1 HTML elements to H4 HTML
                            # elements in each translation note.
                            tn_verse = tn_verses[verse_num]
                            html.append(re.sub(r"h1", r"h4", tn_verse))

    return "\n".join(html)


def _assembly_strategy_factory(
    assembly_strategy_kind: model.AssemblyStrategyEnum,
) -> Callable[[DocumentGenerator], str]:
    """
    Strategy pattern. Given an assembly_strategy_kind, returns the
    appropriate strategy function.
    """
    strategies = {
        model.AssemblyStrategyEnum.verse: _assemble_content_by_verse,
    }
    return strategies[assembly_strategy_kind]
