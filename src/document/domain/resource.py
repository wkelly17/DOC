"""
This module provides classes that reify the concept of a resource.
There are different classes for each resource type.
"""

from __future__ import annotations  # https://www.python.org/dev/peps/pep-0563/

import abc
import logging  # For logdecorator
import os
import pathlib
import re
import shutil
import subprocess
from glob import glob
from typing import Any, Optional, Protocol

import bs4
import icontract
import markdown
from logdecorator import log_on_end, log_on_start
from pydantic import AnyUrl
from usfm_tools.transform import UsfmTransform

from document.config import settings
from document.domain import bible_books, model, resource_lookup
from document.markdown_extensions import (
    link_transformer_preprocessor,
    remove_section_preprocessor,
)
from document.utils import file_utils, html_parsing_utils, tw_utils, url_utils

logger = settings.logger(__name__)

H1, H2, H3, H4 = "h1", "h2", "h3", "h4"


class Resource:
    """
    Built from the incoming document resource request
    fortified with additional state as instance variables.
    """

    def __init__(
        self,
        # This is where resource asset files get downloaded to and
        # where generated PDFs are placed.
        working_dir: str,
        output_dir: str,
        # The resource request that this resource reifies.
        resource_request: model.ResourceRequest,
        # The resource requests from the document request. This is
        # not used by Resource instances directly, but is passed
        # to the LinkTransformerExtension.
        resource_requests: list[model.ResourceRequest],
    ) -> None:
        self._working_dir = working_dir
        self._output_dir = output_dir
        # DESIGN-ISSUE Avail the resource of the ResourceRequest instances in
        # the DocumentRequest so that it can in turn hand thenm to the
        # LinkTransformerExtension which in turn will use it to determine if
        # link references in markdown content point at a resource that was
        # actually requested, i.e., part of the DocumentRequest or not, and can
        # thus be linked. Design-wise, this is an unfortunate linking together
        # of DocumentRequest, Resource, and LinkTransformerExtension that I
        # tried to avoid in design until this point.
        self._resource_requests = resource_requests
        self._resource_request = resource_request

        # Directory may not exist yet. If not, this is dealt with later in an
        # appropriate place later on.
        self._resource_dir = os.path.join(
            self._working_dir, "{}_{}".format(self.lang_code, self.resource_type)
        )

        self._resource_filename = "{}_{}_{}".format(
            self.lang_code, self.resource_type, self.resource_code
        )

        # Book attributes
        self._book_title: str = bible_books.BOOK_NAMES[self.resource_code]
        self._book_number: str = bible_books.BOOK_NUMBERS[self.resource_code]

        # Location/lookup related
        self._resource_lookup_dto: model.ResourceLookupDto

        # Content related instance vars
        self._content_files: list[str] = []
        self._content: str
        self._verses_html: list[str] = []

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "Resource(lang_code: {}, resource_type: {}, resource_code: {})".format(
            self.lang_code, self.resource_type, self.resource_code
        )

    def __repr__(self) -> str:
        """Return a printable string representation identifying this instance."""
        return "Resource(lang_code: {}, resource_type: {}, resource_code: {})".format(
            self.lang_code, self.resource_type, self.resource_code
        )

    @abc.abstractmethod
    def find_location(self) -> bool:
        """
        Initialize self._resource_lookup_dto and return True if
        self._resource_lookup_dto.url was initialized to not None,
        False otherwise.

        Subclasses override this method.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def provision_asset_files(self) -> None:
        """
        Using the resource's remote location, download the resource's file
        assets to disk.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_resource_with_asset_content(self) -> None:
        """
        Initialize resource with content found in resource's asset files.

        Subclasses override.
        """
        raise NotImplementedError

    @property
    def lang_code(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_request.lang_code

    @property
    def resource_type(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_request.resource_type

    @property
    def resource_type_name(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_lookup_dto.resource_type_name

    @property
    def resource_code(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_request.resource_code

    @property
    def content(self) -> str:
        """Provide public interface for other modules."""
        return self._content

    @property
    def lang_name(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_lookup_dto.lang_name

    @property
    def resource_url(self) -> Optional[AnyUrl]:
        """Provide public interface for other modules."""
        return self._resource_lookup_dto.url

    # This method exists to make a mypy cast possible.
    @resource_url.setter
    def resource_url(self, value: AnyUrl) -> None:
        """Provide public interface for other modules."""
        self._resource_lookup_dto.url = value

    @property
    def resource_source(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_lookup_dto.source

    @property
    def resource_requests(self) -> list[model.ResourceRequest]:
        """Provide public interface for other modules."""
        return self._resource_requests

    @property
    def resource_dir(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_dir

    @resource_dir.setter
    def resource_dir(self, value: str) -> None:
        """Provide public interface for other modules."""
        self._resource_dir = value


class USFMResource(Resource):
    """
    This class specializes the behavior and state of Resource for
    the case of a USFM resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._chapter_content: dict[model.ChapterNum, model.USFMChapter] = {}
        self._html_initializer = USFMHtmlInitializer(self)
        self._finder: resource_lookup.USFMResourceJsonLookup = (
            resource_lookup.USFMResourceJsonLookup()
        )

    # Not-found resources are to be handled gracefully. I.e., if we fail to
    # find a location for a ResourceRequest instance we should continue to
    # try to find a DocumentRequest instances's other ResourceRequests
    # instances. That is why we do not have a post-condition that would
    # request a resource URL be found for every resource.
    @log_on_end(
        logging.DEBUG,
        "self._resource_lookup_dto.url = {self._resource_lookup_dto.url} for {self}",
        logger=logger,
    )
    def find_location(self) -> bool:
        """See docstring in superclass."""
        resource_lookup_dto: model.ResourceLookupDto = self._finder.lookup(
            self.lang_code, self.resource_type, self.resource_code
        )
        self._resource_lookup_dto = resource_lookup_dto
        return self._resource_lookup_dto.url is not None

    def _update_resource_dir(self) -> None:
        """Update resource_dir."""
        subdirs = [f.path for f in os.scandir(self.resource_dir) if f.is_dir()]

        if subdirs:
            self._resource_dir = subdirs[0]
            logger.debug(
                "self._resource.resource_dir updated: %s",
                self.resource_dir,
            )

    def provision_asset_files(self) -> None:
        """
        Using the resource's remote location, download the resource's file
        assets to disk.
        """
        ResourceProvisioner(self)()

    @log_on_start(logging.DEBUG, "self._resource_dir: {self._resource_dir}")
    @icontract.ensure(lambda self: self._resource_filename is not None)
    def update_resource_with_asset_content(self) -> None:
        """See docstring in superclass."""

        usfm_content_files: list[str] = []
        txt_content_files: list[str] = []

        # We don't need a manifest file to find resource assets
        # on disk. We just use globbing and then filter
        # down the list found to only include those
        # files that match the resource code, i.e., book, being requested.
        # This frees us from some of the brittleness of using manifests
        # to find files. Some resources do not provide a manifest
        # anyway.
        usfm_content_files = glob("{}**/*.usfm".format(self._resource_dir))
        if not usfm_content_files:
            # USFM files sometimes have txt suffix instead of usfm
            txt_content_files = glob("{}**/*.txt".format(self._resource_dir))
            # Sometimes the txt USFM files live at another location
            if not txt_content_files:
                txt_content_files = glob("{}**/**/*.txt".format(self._resource_dir))

        # If desired, in the case where a manifest must be consulted
        # to determine if the file is considered usable, i.e.,
        # 'complete' or 'finished', that can also be done by comparing
        # the filtered file(s) against the manifest's 'finished' list
        # to see if it can be used. Such logic could live
        # approximately here if desired.
        if usfm_content_files:
            # Only use the content files that match the resource_code
            # in the resource request.
            self._content_files = list(
                filter(
                    lambda usfm_content_file: self._resource_request.resource_code.lower()
                    in str(usfm_content_file).lower(),
                    usfm_content_files,
                )
            )
        elif txt_content_files:
            # Only use the content files that match the resource_code.
            self._content_files = list(
                filter(
                    lambda txt_content_file: self._resource_request.resource_code.lower()
                    in str(txt_content_file).lower(),
                    txt_content_files,
                )
            )

        logger.debug("self._content_files: %s", self._content_files)

        if self._content_files:
            # FIXME Some languages, like ndh-x-chindali, provide their USFM files in
            # a git repo rather than as standalone USFM files. A USFM git repo can
            # have each USFM chapter in a separate directory and each verse in a
            # separate file in that directory. However, the parser expects one USFM
            # file per book, therefore we need to concatenate the book's USFM files
            # into one USFM file.
            # FIXME A problem, currently with this WIP, is that USFM
            # files having the git repo arrangement described above do
            # not seem to have, at least in ndh-x-chindali's case, the
            # \id USFM element that the parser expects thus leading to
            # a MalformedUsfmError. This is unfortunate as the USFM
            # may otherwise be totally fine. Likely, in a coming
            # update we'll make modifications to the parser or provide
            # workarounds that will allow such USFM resources to be
            # utilized.
            # FIXME An unfinished prototype approach for handling the
            # git ndh-x-chindali repo type case:
            # if len(self._content_files) > 1:
            #     # Read the content of each file into a list.
            #     markdown_content = []
            #     for markdown_file in sorted(self._content_files):
            #         with open(markdown_file, "r") as fin:
            #             markdown_content.append(fin.read())
            #             markdown_content.append(" ")
            #     # Write the concatenated markdown content to a
            #     # non-clobberable filename.
            #     filename = os.path.join(
            #         self.resource_dir,
            #         "{}_{}_{}_{}.md".format(
            #             self.lang_code,
            #             self.resource_type,
            #             self.resource_code,
            #             time.time(),
            #         ),
            #     )
            #     with open(filename, "w") as fout:
            #         fout.write("".join(markdown_content))
            #     # Make the temp file our only content file.
            #     self._content_files = [filename]
            # logger.debug("self._content_files[0]: %s", self._content_files[0])

            # Convert the USFM to HTML and store in file. USFM-Tools books.py can
            # raise MalformedUsfmError when the following code is called. The
            # document_generator module will catch that error but continue with
            # other resource requests in the same document request.
            UsfmTransform.buildSingleHtmlFromFile(
                pathlib.Path(self._content_files[0]),
                self._output_dir,
                self._resource_filename,
            )
            # Read the HTML file into _content.
            html_file = "{}.html".format(
                os.path.join(self._output_dir, self._resource_filename)
            )
            assert os.path.exists(html_file)
            self._content = file_utils.read_file(html_file)

            self._html_initializer._initialize_verses_html()

    @property
    def chapter_content(self) -> dict[model.ChapterNum, model.USFMChapter]:
        """Provide public interface for other modules."""
        return self._chapter_content


class TResource(Resource):
    """Provide methods common to all subclasses of TResource."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._finder: resource_lookup.TResourceJsonLookup = (
            resource_lookup.TResourceJsonLookup()
        )

    def find_location(self) -> bool:
        """See docstring in superclass."""
        resource_lookup_dto: model.ResourceLookupDto = self._finder.lookup(
            self.lang_code, self.resource_type, self.resource_code
        )
        self._resource_lookup_dto = resource_lookup_dto
        return self._resource_lookup_dto.url is not None

    def provision_asset_files(self) -> None:
        """
        Using the resource's remote location, download the resource's file
        assets to disk.
        """
        ResourceProvisioner(self)()

    @icontract.require(
        lambda lang_code, resource_requests: lang_code and resource_requests
    )
    @icontract.ensure(lambda result: result)
    def _markdown_instance(
        self,
        lang_code: str,
        resource_type: str,
        resource_requests: list[model.ResourceRequest],
        tw_resource_dir: Optional[str] = None,
    ) -> markdown.Markdown:
        """
        Initialize and return a markdown.Markdown instance that can be
        used to convert Markdown content to HTML content. This mainly
        exists to implement the Law of Demeter and to clean up the
        code of TResource subclasses by DRYing things up.
        """
        if not tw_resource_dir:
            tw_resource_dir = tw_utils.tw_resource_dir(lang_code)
        translation_words_dict = tw_utils.translation_words_dict(tw_resource_dir)
        return markdown.Markdown(
            extensions=[
                remove_section_preprocessor.RemoveSectionExtension(),
                link_transformer_preprocessor.LinkTransformerExtension(
                    lang_code=[self.lang_code, "Language code for resource"],
                    resource_requests=[
                        self.resource_requests,
                        "The list of resource requests contained in the document request.",
                    ],
                    translation_words_dict=[
                        translation_words_dict,
                        "Dictionary mapping translation word asset file name sans suffix to translation word asset file path.",
                    ],
                ),
            ]
        )


class TNResource(TResource):
    """
    This class handles specializing Resource for the case when the
    resource is a Translation Notes resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._book_payload: model.TNBookPayload
        self._html_initializer = TNHtmlInitializer(self)

    def update_resource_with_asset_content(self) -> None:
        """
        Get Markdown content from this resource's file assets. Then do
        some manipulation of said Markdown content according to the
        needs of the document output. Then convert the Markdown content
        into HTML content.
        """
        self._html_initializer._initialize_verses_html()

    @property
    def book_payload(self) -> model.TNBookPayload:
        """Provide public interface for other modules."""
        return self._book_payload

    def verses_for_chapter(
        self, chapter_num: model.ChapterNum
    ) -> Optional[dict[model.VerseRef, model.HtmlContent]]:
        """
        Return the HTML for verses that are in the chapter with
        chapter_num.
        """
        verses_html = None
        if chapter_num in self.book_payload.chapters:
            verses_html = self.book_payload.chapters[chapter_num].verses_html
        return verses_html

    def format_tn_verse(
        self,
        chapter_num: model.ChapterNum,
        verse_num: model.VerseRef,
        verse: model.HtmlContent,
    ) -> list[model.HtmlContent]:
        """
        This is a slightly different form of TNResource.tn_verse that is used
        when no USFM has been requested.
        """
        html: list[model.HtmlContent] = []
        html.append(
            model.HtmlContent(
                settings.TN_RESOURCE_TYPE_NAME_WITH_ID_AND_REF_FMT_STR.format(
                    self.lang_code,
                    bible_books.BOOK_NUMBERS[self.resource_code].zfill(3),
                    str(chapter_num).zfill(3),
                    verse_num.zfill(3),
                    self.resource_type_name,
                    chapter_num,
                    verse_num,
                )
            )
        )
        # Change H1 HTML elements to H4 HTML elements in each translation note.
        html.append(model.HtmlContent(re.sub(H1, H4, verse)))
        return html


class TQResource(TResource):
    """
    This class specializes Resource for the case of a Translation
    Questions resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._book_payload: model.TQBookPayload
        self._html_initializer = TQHtmlInitializer(self)

    def update_resource_with_asset_content(self) -> None:
        """
        Get Markdown content from this resource's file assets. Then do
        some manipulation of said Markdown content according to the
        needs of the document output. Then convert the Markdown content
        into HTML content.
        """
        self._html_initializer._initialize_verses_html()

    @property
    def book_payload(self) -> model.TQBookPayload:
        """Provide public interface for other modules."""
        return self._book_payload

    def verses_for_chapter(
        self, chapter_num: model.ChapterNum
    ) -> Optional[dict[model.VerseRef, model.HtmlContent]]:
        """Return the HTML for verses in chapter_num."""
        verses_html = None
        if chapter_num in self.book_payload.chapters:
            verses_html = self.book_payload.chapters[chapter_num].verses_html
        return verses_html

    def format_tq_verse(
        self,
        chapter_num: model.ChapterNum,
        verse_num: model.VerseRef,
    ) -> list[model.HtmlContent]:
        """
        Build and return the content for the translation question for chapter
        chapter_num and verse verse_num.
        """
        chapter_verses = self.verses_for_chapter(chapter_num)
        tq_verse = None
        if chapter_verses and verse_num in chapter_verses:
            tq_verse = chapter_verses[verse_num]
        if tq_verse is None:
            return [model.HtmlContent("")]

        html: list[model.HtmlContent] = []
        html.append(
            model.HtmlContent(
                settings.TRANSLATION_QUESTION_FMT_STR.format(chapter_num, verse_num)
            )
        )
        # Change H1 HTML elements to H4 HTML elements in each translation question
        # so that overall indentation works out.
        html.append(model.HtmlContent(re.sub(H1, H4, tq_verse)))
        return html


class TWResource(TResource):
    """
    This class specializes Resource for the case of a Translation
    Words resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._language_payload: model.TWLanguagePayload
        self._html_initializer = TWHtmlInitializer(self)

    def update_resource_with_asset_content(self) -> None:
        """
        Get Markdown content from this resource's file assets. Then do
        some manipulation of said Markdown content according to the
        needs of the document output. Then convert the Markdown content
        into HTML content.
        """
        self._html_initializer._initialize_verses_html()

    @property
    def language_payload(self) -> model.TWLanguagePayload:
        """Provide public interface for other modules."""
        return self._language_payload

    def translation_word_links(
        self,
        chapter_num: model.ChapterNum,
        verse_num: model.VerseRef,
        verse: model.HtmlContent,
    ) -> list[model.HtmlContent]:
        """
        Add the translation word links section which provides links from words
        used in the current verse to their definition.
        """
        html: list[model.HtmlContent] = []
        uses: list[model.TWUse] = []
        name_content_pair: model.TWNameContentPair
        for name_content_pair in self._language_payload.name_content_pairs:
            # This checks that the word occurs as an exact sub-string in
            # the verse.
            if re.search(
                r"\b{}\b".format(re.escape(name_content_pair.localized_word)), verse
            ):
                use = model.TWUse(
                    lang_code=self.lang_code,
                    book_id=self.resource_code,
                    book_name=bible_books.BOOK_NAMES[self.resource_code],
                    chapter_num=chapter_num,
                    verse_num=verse_num,
                    localized_word=name_content_pair.localized_word,
                )
                uses.append(use)
                # Store reference for use in 'Uses:' section that
                # comes later.
                if name_content_pair.localized_word in self.language_payload.uses:
                    self.language_payload.uses[name_content_pair.localized_word].append(
                        use
                    )
                else:
                    self.language_payload.uses[name_content_pair.localized_word] = [use]

        if uses:
            # Add header
            html.append(
                model.HtmlContent(
                    settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR.format(
                        self.resource_type_name, chapter_num, verse_num
                    )
                )
            )
            # Start list formatting
            html.append(settings.UNORDERED_LIST_BEGIN_STR)
            # Append word links.
            uses_list_items = [
                settings.TRANSLATION_WORD_LIST_ITEM_FMT_STR.format(
                    self.lang_code,
                    use.localized_word,
                    use.localized_word,
                )
                for use in list(tw_utils.uniq(uses))  # Get the unique uses
            ]
            html.append(model.HtmlContent("\n".join(uses_list_items)))
            # End list formatting
            html.append(settings.UNORDERED_LIST_END_STR)
        return html

    def translation_words_section(
        self,
        include_uses_section: bool = True,
    ) -> list[model.HtmlContent]:
        """
        Build and return the translation words definition section, i.e.,
        the list of all translation words for this language, book
        combination. Include a 'Uses:' section that points from the
        translation word back to the verses which include the translation
        word if include_uses_section is True.
        """
        html: list[model.HtmlContent] = []
        html.append(
            model.HtmlContent(
                settings.RESOURCE_TYPE_NAME_FMT_STR.format(self.resource_type_name)
            )
        )

        for name_content_pair in self._language_payload.name_content_pairs:
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
                    settings.OPENING_H3_FMT_STR.format(
                        name_content_pair.localized_word
                    ),
                    settings.OPENING_H3_WITH_ID_FMT_STR.format(
                        self.lang_code,
                        name_content_pair.localized_word,
                        name_content_pair.localized_word,
                    ),
                )
            )
            uses_section = model.HtmlContent("")

            # See comment above.
            if (
                include_uses_section
                and name_content_pair.localized_word in self.language_payload.uses
            ):
                uses_section = self._uses_section(
                    self.language_payload.uses[name_content_pair.localized_word]
                )
                name_content_pair.content = model.HtmlContent(
                    name_content_pair.content + uses_section
                )
            html.append(name_content_pair.content)
        return html

    def _uses_section(self, uses: list[model.TWUse]) -> model.HtmlContent:
        """
        Construct and return the 'Uses:' section which comes at the end of
        a translation word definition and wherein each item points to
        verses (as targeted by lang_code, book_id, chapter_num, and
        verse_num) wherein the word occurs.
        """
        html: list[model.HtmlContent] = []
        html.append(settings.TRANSLATION_WORD_VERSE_SECTION_HEADER_STR)
        html.append(settings.UNORDERED_LIST_BEGIN_STR)
        for use in uses:
            html_content_str = model.HtmlContent(
                settings.TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR.format(
                    use.lang_code,
                    bible_books.BOOK_NUMBERS[use.book_id].zfill(3),
                    str(use.chapter_num).zfill(3),
                    str(use.verse_num).zfill(3),
                    bible_books.BOOK_NAMES[use.book_id],
                    use.chapter_num,
                    use.verse_num,
                )
            )
            html.append(html_content_str)
        html.append(settings.UNORDERED_LIST_END_STR)
        return model.HtmlContent("\n".join(html))


# FIXME The implementation was just a quick template based off of
# TQResource, but needs to change a LOT. It is wildly incorrect and
# just a placeholder, logic is not even close to correct/done. We
# still have to decide how to handle TA resources.
class TAResource(TResource):
    """
    This class specializes Resource for the case of a Translation
    Answers resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._book_payload: model.TABookPayload
        self._html_initializer = TAHtmlInitializer(self)

    def update_resource_with_asset_content(self) -> None:
        """
        Get Markdown content from this resource's file assets. Then do
        some manipulation of said Markdown content according to the
        needs of the document output. Then convert the Markdown content
        into HTML content.
        """
        self._html_initializer._initialize_verses_html()

    @property
    def book_payload(self) -> model.TABookPayload:
        """Provide public interface for other modules."""
        return self._book_payload

    def verses_for_chapter(
        self, chapter_num: model.ChapterNum
    ) -> Optional[dict[model.VerseRef, model.HtmlContent]]:
        """Return the HTML for verses in chapter_num."""
        verses_html = None
        if chapter_num in self.book_payload.chapters:
            verses_html = self.book_payload.chapters[chapter_num].verses_html
        return verses_html


@icontract.require(
    lambda working_dir, output_dir, resource_request, resource_requests: working_dir
    and output_dir
    and resource_request
    and resource_request.lang_code
    and resource_request.resource_type
    and resource_request.resource_code
)
@icontract.ensure(lambda result: result)
def resource_factory(
    working_dir: str,
    output_dir: str,
    resource_request: model.ResourceRequest,
    resource_requests: list[model.ResourceRequest],
) -> Resource:
    """
    Factory method to create the appropriate Resource subclass for
    a given ResourceRequest instance.
    """
    return settings.resource_type_lookup_map()[resource_request.resource_type](
        working_dir,
        output_dir,
        resource_request,
        resource_requests,
    )


class ResourceProvisioner:
    """
    This class handles creating the necessary directory for a resource
    adn then acquiring the resource instance's file assets into the
    directory using the cloud location for the asset provided by the
    appropriate ResourceLookup subclass.
    """

    def __init__(self, resource: Resource):
        self._resource = resource

    def __call__(self) -> None:
        """
        Prepare the resource directory and then download the
        resource's file assets into that directory.
        """
        self._prepare_resource_directory()
        self._acquire_resource()

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "ResourceProvisioner(resource: {})".format(self._resource)

    @icontract.ensure(lambda self: self._resource.resource_dir)
    def _prepare_resource_directory(self) -> None:
        """
        If it doesn't exist yet, create the directory for the
        resource where it will be downloaded to.
        """
        if not os.path.exists(self._resource.resource_dir):
            logger.debug("About to create directory %s", self._resource.resource_dir)
            try:
                os.mkdir(self._resource.resource_dir)
            except FileExistsError:
                logger.exception(
                    "Directory {} already existed".format(self._resource.resource_dir)
                )
            else:
                logger.debug("Created directory %s", self._resource.resource_dir)

    @icontract.require(
        lambda self: self._resource.resource_type
        and self._resource.resource_dir
        and self._resource.resource_url
    )
    @log_on_start(
        logging.DEBUG,
        "self._resource.resource_url: {self._resource.resource_url} for {self}",
        logger=logger,
    )
    def _acquire_resource(self) -> None:
        """
        Download or git clone resource and unzip resulting file if it
        is a zip file.
        """

        if (
            self._resource.resource_url
        ):  # We know that resource_url is not None because of how we got here, but mypy isn't convinced. Let's convince mypy.
            resource_filepath = os.path.join(
                self._resource.resource_dir,
                self._resource.resource_url.rpartition(os.path.sep)[2],
            )

            logger.debug("resource_filepath: %s", resource_filepath)
            # Check if resource assets need updating otherwise use
            # what we already have on disk.
            if file_utils.asset_file_needs_update(resource_filepath):
                if _is_git(self._resource.resource_source):
                    self._clone_git_repo(resource_filepath)
                else:
                    self._download_asset(resource_filepath)

                if _is_zip(self._resource.resource_source):
                    self._unzip_asset(resource_filepath)
            if _is_git(self._resource.resource_source) or _is_zip(
                self._resource.resource_source
            ):
                # When a git repo is cloned or when a zip file is
                # unzipped, a subdirectory of resource_dir is created
                # as a result. Update resource_dir to point to that
                # subdirectory.
                self._update_resource_dir()

    def _update_resource_dir(self) -> None:
        """
        Update resource_dir to point to the first subdirectory of
        resource_dir found.

        Why? When a git repo is cloned or when a zip file is unzipped,
        a subdirectory of resource_dir is created as a result. Update
        resource_dir to point to that subdirectory.
        """
        subdirs = [
            f.path for f in os.scandir(self._resource.resource_dir) if f.is_dir()
        ]
        if subdirs:
            self._resource.resource_dir = subdirs[0]
            logger.debug(
                "resource_dir updated: %s",
                self._resource.resource_dir,
            )

    def _clone_git_repo(self, resource_filepath: str) -> None:
        """
        Clone the git repo. If the repo was previously cloned but
        the ASSET_CACHING_PERIOD has expired then delete the repo and
        clone it again to get updates.
        """
        if os.path.exists(resource_filepath):
            logger.debug(
                "About to delete pre-existing git repo %s in order to recreate it.",
                resource_filepath,
            )
            try:
                shutil.rmtree(resource_filepath)
            except OSError:
                logger.debug(
                    "Directory %s was not removed due to an error.",
                    resource_filepath,
                )
                logger.exception("Caught exception: ")
        command = "git clone --depth=1 '{}' '{}'".format(
            self._resource.resource_url, resource_filepath
        )
        logger.debug("Attempting to clone into %s ...", resource_filepath)
        try:
            subprocess.call(command, shell=True)
        except subprocess.SubprocessError:
            logger.debug("git command: %s", command)
            logger.debug("git clone failed!")
        else:
            logger.debug("git command: %s", command)
            logger.debug("git clone succeeded.")

    def _download_asset(self, resource_filepath: str) -> None:
        """Download the asset."""
        logger.debug(
            "Downloading %s into %s", self._resource.resource_url, resource_filepath
        )
        # FIXME Might want to retry after some acceptable interval if there is a
        # failure here due to network issues. It has happened very occasionally
        # during testing that there has been a hiccup with the network at this
        # point but succeeded on retry of the same test.
        url_utils.download_file(self._resource.resource_url, resource_filepath)
        logger.info("Downloading finished.")

    @icontract.require(
        lambda resource_filepath: resource_filepath
        and os.path.exists(resource_filepath)
    )
    def _unzip_asset(self, resource_filepath: str) -> None:
        """Unzip the asset."""
        logger.debug(
            "Unzipping %s into %s", resource_filepath, self._resource.resource_dir
        )
        file_utils.unzip(resource_filepath, self._resource.resource_dir)
        logger.info("Unzipping finished.")


@icontract.require(lambda resource_source: resource_source)
def _is_zip(resource_source: str) -> bool:
    """Return true if resource_source is equal to 'zip'."""
    return resource_source == model.AssetSourceEnum.ZIP


@icontract.require(lambda resource_source: resource_source)
def _is_git(resource_source: str) -> bool:
    """Return true if resource_source is equal to 'git'."""
    return resource_source == model.AssetSourceEnum.GIT


class HtmlInitializer(Protocol):
    """
    Define a protocol class for classes that will act as HTML
    initializers of a resource's content.
    """

    @abc.abstractmethod
    def _initialize_verses_html(self) -> None:
        ...


class USFMHtmlInitializer:
    """
    This class's purpose is to break apart the USFMResource's HTML
    content into HTML chapter and verse chunks, augment HTML output with
    additional HTML elements and store in an instance variable.
    """

    def __init__(self, resource: USFMResource):
        self._resource = resource

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "USFMHtmlInitializer(resource: {})".format(self._resource)

    @icontract.require(lambda self: self._resource._content)
    @icontract.ensure(lambda self: self._resource._chapter_content)
    def _initialize_verses_html(self) -> None:
        """
        Break apart the USFM HTML content into HTML chapter and verse
        chunks, augment HTML output with additional HTML elements and
        store in an instance variable.
        """
        parser = bs4.BeautifulSoup(self._resource._content, "html.parser")

        chapter_breaks = parser.find_all(H2, attrs={"class": "c-num"})
        localized_chapter_heading = chapter_breaks[0].get_text().split()[0]
        for chapter_break in chapter_breaks:
            chapter_num = model.ChapterNum(int(chapter_break.get_text().split()[1]))
            chapter_content = html_parsing_utils.tag_elements_between(
                parser.find(
                    H2,
                    text="{} {}".format(localized_chapter_heading, chapter_num),
                ),
                # ).next_sibling,
                parser.find(
                    H2,
                    text="{} {}".format(localized_chapter_heading, chapter_num + 1),
                ),
            )
            chapter_content = [str(tag) for tag in list(chapter_content)]
            chapter_content_parser = bs4.BeautifulSoup(
                "".join(chapter_content),
                "html.parser",
            )
            chapter_verse_tags: bs4.elements.ResultSet = (
                chapter_content_parser.find_all("span", attrs={"class": "v-num"})
            )
            chapter_footnote_tag: bs4.elements.ResultSet = chapter_content_parser.find(
                "div", attrs={"class": "footnotes"}
            )
            chapter_footnotes = (
                model.HtmlContent(str(chapter_footnote_tag))
                if chapter_footnote_tag
                else model.HtmlContent("")
            )
            # Get each verse opening span tag and then the actual verse text for
            # this chapter and enclose them each in a p element.
            chapter_verse_list = [
                "<p>{} {}</p>".format(verse, verse.next_sibling)
                for verse in chapter_verse_tags
            ]
            # Dictionary to hold verse number, verse value pairs.
            chapter_verses: dict[str, str] = {}
            for verse_element in chapter_verse_list:
                (verse_num, verse_content_str,) = self._verse_num_and_verse_content_str(
                    chapter_num, chapter_content_parser, verse_element
                )
                chapter_verses[verse_num] = verse_content_str
            self._resource._chapter_content[chapter_num] = model.USFMChapter(
                chapter_content=chapter_content,
                chapter_verses=chapter_verses,
                chapter_footnotes=chapter_footnotes,
            )

    def _verse_num_and_verse_content_str(
        self,
        chapter_num: int,
        chapter_content_parser: bs4.BeautifulSoup,
        verse_element: str,
    ) -> tuple[model.VerseRef, model.HtmlContent]:
        """
        Handle some messy initialization and return the
        chapter_num and verse_content_str.
        """
        # Rather than a single verse num, the item in
        # verse_num may be a verse range, e.g., 1-2.
        # See test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order
        # for test that triggers this situation.
        # Get the verse num from the verse HTML tag's id value.
        # split is more performant than re.
        # See https://stackoverflow.com/questions/7501609/python-re-split-vs-split
        verse_num = str(verse_element).split("-v-")[1].split('"')[0]
        # Check for hyphen in the range
        verse_num_components = verse_num.split("-")
        if len(verse_num_components) > 1:
            upper_bound_value = int(verse_num_components[1]) + 1
            # Get rid of leading zeroes on first verse number
            # in range.
            verse_num_int = int(verse_num_components[0])
            # Get rid of leading zeroes on second verse number
            # in range.
            verse_num2_int = int(verse_num_components[1])
            # Recreate the verse range, now without leading
            # zeroes.
            verse_num = "{}-{}".format(str(verse_num_int), str(verse_num2_int))
            # logger.debug(
            #     "chapter_num: %s, verse_num is a verse range: %s",
            #     chapter_num,
            #     verse_num,
            # )
        else:
            upper_bound_value = int(verse_num) + 1
            # Get rid of leading zeroes.
            verse_num = str(int(verse_num))

        # Create the lower and upper search bounds for the
        # BeautifulSoup HTML parser.
        lower_id = "{}-ch-{}-v-{}".format(
            str(self._resource._book_number).zfill(3),
            str(chapter_num).zfill(3),
            verse_num.zfill(3),
        )
        upper_id = "{}-ch-{}-v-{}".format(
            str(self._resource._book_number).zfill(3),
            str(chapter_num).zfill(3),
            str(upper_bound_value).zfill(3),
        )
        # Using the upper and lower parse a verse worth of HTML
        # content.
        verse_content_tags = html_parsing_utils.tag_elements_between(
            chapter_content_parser.find(
                "span",
                attrs={"class": "v-num", "id": lower_id},
            ),
            # ).next_sibling,
            chapter_content_parser.find(
                "span",
                attrs={"class": "v-num", "id": upper_id},
            ),
        )
        verse_content = [str(tag) for tag in list(verse_content_tags)]
        # Hacky way to remove some redundant parsing results due to recursion in
        # BeautifulSoup. Perhaps there is bs4 mway to avoid this. But
        # this does work and produces the desired result in the end.
        del verse_content[1:4]
        verse_content_str = "".join(verse_content)
        # HACK "Fix" BeautifulSoup parsing issue wherein sometimes a verse
        # contains its content but also includes a subsequent verse or verses or
        # a recapitulation of all previous verses. This does fix the problem
        # though and gives the desired result:
        verse_content_str = (
            '<span class="v-num"' + verse_content_str.split('<span class="v-num"')[1]
        )
        # At this point we alter verse_content_str span's ID by prepending the
        # lang_code to ensure unique verse references within language scope in a
        # multi-language document.
        pattern = settings.VERSE_ANCHOR_ID_FMT_STR
        verse_content_str = re.sub(
            pattern,
            settings.VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR.format(
                self._resource.lang_code
            ),
            verse_content_str,
        )
        return model.VerseRef(verse_num), model.HtmlContent(verse_content_str)


class TNHtmlInitializer:
    """
    This class's purpose is to break apart the TNResource's HTML
    content into HTML chapter and verse chunks, augment HTML output with
    additional HTML elements and store in an instance variable.
    """

    def __init__(self, resource: TNResource):
        self._resource = resource

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "TNHtmlInitializer(resource: {})".format(self._resource)

    @log_on_start(
        logging.INFO,
        "About to convert TN Markdown to HTML with Markdown extension",
        logger=logger,
    )
    def _initialize_verses_html(self) -> None:
        """
        Find book intro, chapter intros, and then the translation
        notes for the verses themselves.
        """
        # Initialize the Python-Markdown extensions that get invoked
        # when md.convert is called.
        md: markdown.Markdown = self._resource._markdown_instance(
            self._resource.lang_code,
            self._resource.resource_type,
            self._resource.resource_requests,
        )
        # FIXME We can likely now remove the first '**' if we want. It
        # works as is though, it is just a minor optimization, but I'd
        # need to fully it test it before making the change.
        chapter_dirs = sorted(
            glob(
                "{}/**/*{}/*[0-9]*".format(
                    self._resource.resource_dir,
                    self._resource.resource_code,
                )
            )
        )
        # Some languages are organized differently on disk (e.g., depending
        # on if their assets were acquired as a git repo or a zip).
        # We handle this here.
        if not chapter_dirs:
            chapter_dirs = sorted(
                glob(
                    "{}/*{}/*[0-9]*".format(
                        self._resource.resource_dir,
                        self._resource.resource_code,
                    )
                )
            )
        chapter_verses: dict[int, model.TNChapterPayload] = {}
        for chapter_dir in chapter_dirs:
            chapter_num = int(os.path.split(chapter_dir)[-1])
            intro_paths = glob("{}/*intro.md".format(chapter_dir))
            # For some languages, TN assets are stored in .txt files
            # rather of .md files.
            if not intro_paths:
                intro_paths = glob("{}/*intro.txt".format(chapter_dir))
            intro_path = intro_paths[0] if intro_paths else None
            intro_md = ""
            intro_html = ""
            if intro_path:
                intro_md = file_utils.read_file(intro_path)
                intro_html = md.convert(intro_md)
            verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
            # For some languages, TN assets are stored in .txt files
            # rather of .md files.
            if not verse_paths:
                verse_paths = sorted(glob("{}/*[0-9]*.txt".format(chapter_dir)))
            verses_html: dict[int, str] = {}
            for filepath in verse_paths:
                verse_num = int(pathlib.Path(filepath).stem)
                verse_content = ""
                verse_content = file_utils.read_file(filepath)
                verse_content = md.convert(verse_content)
                verses_html[verse_num] = verse_content
            chapter_payload = model.TNChapterPayload(
                intro_html=intro_html, verses_html=verses_html
            )
            chapter_verses[chapter_num] = chapter_payload
        # Get the book intro if it exists
        book_intro_path = glob(
            "{}/*{}/front/intro.md".format(
                self._resource.resource_dir,
                self._resource.resource_code,
            )
        )
        # For some languages, TN assets are stored in .txt files
        # rather of .md files.
        if not book_intro_path:
            book_intro_path = glob(
                "{}/*{}/front/intro.txt".format(
                    self._resource.resource_dir, self._resource.resource_code
                )
            )
        book_intro_html = ""
        if book_intro_path:
            book_intro_html = file_utils.read_file(book_intro_path[0])
            book_intro_html = md.convert(book_intro_html)
        self._resource._book_payload = model.TNBookPayload(
            intro_html=model.HtmlContent(book_intro_html), chapters=chapter_verses
        )


class TQHtmlInitializer:
    """
    This class's purpose is to break apart the TQResource's HTML
    content into HTML chapter and verse chunks, augment HTML output with
    additional HTML elements and store in an instance variable.
    """

    def __init__(self, resource: TQResource):
        self._resource = resource

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "TQHtmlInitializer(resource: {})".format(self._resource)

    @log_on_start(
        logging.INFO,
        "About to convert TQ Markdown to HTML with Markdown extension",
        logger=logger,
    )
    def _initialize_verses_html(self) -> None:
        """Find translation questions for the verses."""
        # Create the Markdown instance once and have it use our markdown
        # extensions.
        md: markdown.Markdown = self._resource._markdown_instance(
            self._resource.lang_code,
            self._resource.resource_type,
            self._resource.resource_requests,
        )
        # FIXME We can likely now remove the first '**' for a tiny
        # speedup, but I'd need to test thorougly first.
        chapter_dirs = sorted(
            glob(
                "{}/**/*{}/*[0-9]*".format(
                    self._resource.resource_dir, self._resource.resource_code
                )
            )
        )
        # Some languages are organized differently on disk (e.g., depending
        # on if their assets were acquired as a git repo or a zip).
        # We handle this here.
        if not chapter_dirs:
            chapter_dirs = sorted(
                glob(
                    "{}/*{}/*[0-9]*".format(
                        self._resource.resource_dir, self._resource.resource_code
                    )
                )
            )
        chapter_verses: dict[int, model.TQChapterPayload] = {}
        for chapter_dir in chapter_dirs:
            chapter_num = int(os.path.split(chapter_dir)[-1])
            verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
            # For some languages, TQ assets may be stored in .txt files
            # rather of .md files.
            # FIXME This is true of TN assets, but I am not yet sure of TQ assets
            # that use the TXT suffix.
            if not verse_paths:
                verse_paths = sorted(glob("{}/*[0-9]*.txt".format(chapter_dir)))
            verses_html: dict[int, str] = {}
            for filepath in verse_paths:
                verse_num = int(pathlib.Path(filepath).stem)
                verse_content = file_utils.read_file(filepath)
                # with open(filepath, "r", encoding="utf-8") as fin2:
                #     verse_content = fin2.read()
                # NOTE I don't think translation questions have a
                # 'Links:' section.
                # verse_content = markdown_utils.remove_md_section(
                #     verse_content, "Links:"
                # )
                verse_content = md.convert(verse_content)
                verses_html[verse_num] = verse_content
            chapter_payload = model.TQChapterPayload(verses_html=verses_html)
            chapter_verses[chapter_num] = chapter_payload
        self._resource._book_payload = model.TQBookPayload(chapters=chapter_verses)


class TWHtmlInitializer:
    """
    This class's purpose is to break apart the TWResource's HTML
    content into HTML chapter and verse chunks, augment HTML output with
    additional HTML elements and store in an instance variable.
    """

    def __init__(self, resource: TWResource):
        self._resource = resource

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "TWHtmlInitializer(resource: {})".format(self._resource)

    @log_on_start(
        logging.INFO,
        "About to convert TW Markdown to HTML with Markdown extension",
        logger=logger,
    )
    def _initialize_verses_html(self) -> None:
        """Find translation words for the verses."""
        # Create the Markdown instance once and have it use our markdown
        # extensions.
        md: markdown.Markdown = self._resource._markdown_instance(
            self._resource.lang_code,
            self._resource.resource_type,
            self._resource.resource_requests,
            self._resource.resource_dir,
        )
        # FIXME tw_utils.get_translation_word_filepaths is already called in
        # self._get_markdown_instance implicitly. Could we rearrange the API so
        # that this doesn't have to be called again here as a special
        # case for TWResource? It isn't a big deal, but let's revisit
        # this as a low priority item.

        # tw_resource_dir = tw_utils.tw_resource_dir(self._resource.lang_code)
        translation_word_filepaths = tw_utils.translation_word_filepaths(
            # tw_resource_dir if tw_resource_dir else self._resource.resource_dir
            self._resource.resource_dir
        )
        name_content_pairs: list[model.TWNameContentPair] = []
        for translation_word_filepath in translation_word_filepaths:
            translation_word_content = file_utils.read_file(translation_word_filepath)
            # Translation words are bidirectional. By that I mean that when you are
            # at a verse there follows, after translation questions, links to the
            # translation words that occur in that verse. But then when you navigate
            # to the word by clicking such a link, at the end of the resulting
            # translation word note there is a section called 'Uses:' that also has
            # links back to the verses wherein the word occurs.
            localized_translation_word = tw_utils.localized_translation_word(
                translation_word_content
            )
            html_word_content = md.convert(translation_word_content)
            # Make adjustments to the HTML here.
            html_word_content = re.sub(H2, H4, html_word_content)
            html_word_content = re.sub(H1, H3, html_word_content)
            name_content_pairs.append(
                model.TWNameContentPair(
                    localized_word=localized_translation_word, content=html_word_content
                )
            )

        self._resource._language_payload = model.TWLanguagePayload(
            # Sort the name content pairs by localized translation word
            name_content_pairs=sorted(
                name_content_pairs,
                key=lambda name_content_pair: name_content_pair.localized_word,
            )
        )


class TAHtmlInitializer:
    """
    This class's purpose is to break apart the TAResource's HTML
    content into HTML chapter and verse chunks, augment HTML output with
    additional HTML elements and store in an instance variable.
    """

    def __init__(self, resource: TAResource):
        self._resource = resource

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "TAHtmlInitializer(resource: {})".format(self._resource)

    @log_on_start(
        logging.INFO,
        "About to convert TA Markdown to HTML with Markdown extension",
        logger=logger,
    )
    def _initialize_verses_html(self) -> None:
        """Find translation academy for the verses."""
        # Create the Markdown instance once and have it use our markdown
        # extensions.
        md: markdown.Markdown = self._resource._markdown_instance(
            self._resource.lang_code,
            self._resource.resource_type,
            self._resource.resource_requests,
        )
        chapter_dirs = sorted(
            glob(
                "{}/**/*{}/*[0-9]*".format(
                    self._resource.resource_dir, self._resource.resource_code
                )
            )
        )
        # Some languages are organized differently on disk (e.g., depending
        # on if their assets were acquired as a git repo or a zip).
        # We handle this here.
        if not chapter_dirs:
            chapter_dirs = sorted(
                glob(
                    "{}/*{}/*[0-9]*".format(
                        self._resource.resource_dir, self._resource.resource_code
                    )
                )
            )
        chapter_verses: dict[int, model.TAChapterPayload] = {}
        for chapter_dir in chapter_dirs:
            chapter_num = int(os.path.split(chapter_dir)[-1])
            # FIXME For some languages, TQ assets are stored in .txt files
            # rather of .md files. Handle this.
            verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
            verses_html: dict[int, str] = {}
            for filepath in verse_paths:
                verse_num = int(pathlib.Path(filepath).stem)
                verse_content = file_utils.read_file(filepath)
                # with open(filepath, "r", encoding="utf-8") as fin2:
                #     verse_content = fin2.read()
                # NOTE I don't think translation questions have a
                # 'Links:' section.
                # verse_content = markdown_utils.remove_md_section(
                #     verse_content, "Links:"
                # )
                verse_content = md.convert(verse_content)
                verses_html[verse_num] = verse_content
            chapter_payload = model.TAChapterPayload(verses_html=verses_html)
            chapter_verses[chapter_num] = chapter_payload
        self._resource._book_payload = model.TABookPayload(chapters=chapter_verses)
