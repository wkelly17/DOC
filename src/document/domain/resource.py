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
import subprocess
from glob import glob
from logdecorator import log_on_start, log_on_end
from typing import Any, cast, Dict, FrozenSet, List, Optional, Tuple

import bs4
import icontract
import markdown
from usfm_tools.transform import UsfmTransform

from document import config

from document.markdown_extensions import (
    wikilink_preprocessor,
    remove_section_preprocessor,
    translation_word_link_preprocessor,
)
from document.domain import bible_books, model, resource_lookup
from document.utils import (
    file_utils,
    html_parsing_utils,
    link_utils,
    markdown_utils,
    url_utils,
)

logger = config.get_logger(__name__)


class Resource:
    """
    Reification of the incoming document resource request
    fortified with additional state as instance variables.
    """

    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        resource_request: model.ResourceRequest,
    ) -> None:
        self._working_dir: str = working_dir
        self._output_dir: str = output_dir
        self._resource_request: model.ResourceRequest = resource_request

        self._lang_code: str = resource_request.lang_code
        self._resource_type: str = resource_request.resource_type
        self._resource_code: str = resource_request.resource_code

        self._resource_dir: str = os.path.join(
            self._working_dir, "{}_{}".format(self._lang_code, self._resource_type)
        )

        self._resource_filename = "{}_{}_{}".format(
            self._lang_code, self._resource_type, self._resource_code
        )

        # Book attributes
        self._book_id: str = self._resource_code
        # FIXME Could get KeyError with request for non-existent book,
        # i.e., we could get bad data from BIEL.
        # NOTE Maybe we should be stricter at the API level about the value of
        # resource code.
        self._book_title = bible_books.BOOK_NAMES[self._resource_code]
        self._book_number = bible_books.BOOK_NUMBERS[self._book_id]

        # Location/lookup related
        self._lang_name: str
        self._resource_type_name: str
        self._resource_url: Optional[str] = None
        self._resource_source: str
        self._resource_jsonpath: Optional[str] = None

        self._manifest: Manifest

        # Content related instance vars
        self._content_files: List[str] = []
        self._content: str
        self._verses_html: List[str] = []

        # Link related
        self._resource_data: dict = {}
        # FIXME Slated for future removal
        self._my_rcs: List = []
        # FIXME Slated for future removal
        self._rc_references: dict = {}

    def __str__(self) -> str:
        """Return a printable string identifying this instance."""
        return "Resource(lang_code: {}, resource_type: {}, resource_code: {})".format(
            self._lang_code, self._resource_type, self._resource_code
        )

    @abc.abstractmethod
    def find_location(self) -> None:
        """
        Find the remote location where a the resource's file assets
        may be found.

        Subclasses override this method.
        """
        raise NotImplementedError

    def get_files(self) -> None:
        """
        Using the resource's remote location, download the resource's file
        assets to disk.
        """
        ResourceProvisioner(self)()

    @abc.abstractmethod
    def _initialize_from_assets(self) -> None:
        """
        Find and load resource asset files that were downloaded to disk.

        Subclasses override.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_content(self) -> None:
        """
        Initialize resource with content found in resource's asset files.

        Subclasses override.
        """
        raise NotImplementedError

    def is_found(self) -> bool:
        """Return true if resource's URL location was found."""
        return self._resource_url is not None

    @property
    def lang_code(self) -> str:
        """Provide public interface for other modules."""
        return self._lang_code

    @property
    def lang_name(self) -> str:
        """Provide public interface for other modules."""
        return self._lang_name

    @property
    def resource_type(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_type

    @property
    def resource_type_name(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_type_name

    @property
    def resource_code(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_code

    @property
    def verses_html(self) -> List[str]:
        """Provide public interface for other modules."""
        return self._verses_html

    @property
    def content(self) -> str:
        """Provide public interface for other modules."""
        return self._content

    @property
    def resource_url(self) -> Optional[str]:
        """Provide public interface for other modules."""
        return self._resource_url

    # This method exists to make a mypy cast possible.
    @resource_url.setter
    def resource_url(self, value: str) -> None:
        """Provide public interface for other modules."""
        self._resource_url = value

    @property
    def resource_dir(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_dir

    @resource_dir.setter
    def resource_dir(self, value: str) -> None:
        """Provide public interface for other modules."""
        self._resource_dir = value

    @property
    def resource_source(self) -> str:
        """Provide public interface for other modules."""
        return self._resource_source


class USFMResource(Resource):
    """
    This class specializes the behavior and state of Resource for
    the case of a USFM resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._chapters_content: Dict = {}

    # We may want to not enforce the post-condition that the
    # resource URL be found since we have a requirement that not found
    # resources are to be handled gracefully. I.e., if we fail to find
    # a ResourceRequest instance we should continue to try to find a
    # DocumentRequest instances's other ResourceRequests instances.
    # @icontract.ensure(
    #     lambda self: self._resource_url is not None and self._lang_name is not None
    # )
    @log_on_end(
        logging.DEBUG,
        "self._resource_url = {self._resource_url} for {self}",
        logger=logger,
    )
    def find_location(self) -> None:
        """See docstring in superclass."""
        # FIXME For better flexibility, the lookup class could be
        # looked up in a table, i.e., dict, that has the key as self
        # classname and the value as the lookup subclass.
        lookup_svc = resource_lookup.USFMResourceJsonLookup()
        resource_lookup_dto: model.ResourceLookupDto = lookup_svc.lookup(self)
        self._lang_name = resource_lookup_dto.lang_name
        self._resource_type_name = resource_lookup_dto.resource_type_name
        self._resource_url = resource_lookup_dto.url
        self._resource_source = resource_lookup_dto.source
        self._resource_jsonpath = resource_lookup_dto.jsonpath

    @log_on_end(
        logging.DEBUG,
        "self._content_files for {self._resource_code}: {self._content_files}",
        logger=logger,
    )
    def _initialize_from_assets(self) -> None:
        """See docstring in superclass."""
        self._manifest = Manifest(self)

        usfm_content_files = glob("{}**/*.usfm".format(self._resource_dir))
        # USFM files sometimes have txt suffix
        txt_content_files = glob("{}**/*.txt".format(self._resource_dir))
        # Sometimes the txt USFM files live at another location
        if not txt_content_files:
            txt_content_files = glob("{}**/**/*.txt".format(self._resource_dir))

        # logger.debug("usfm_content_files: {}".format(list(usfm_content_files)))

        # NOTE We don't need a manifest file to find resource assets
        # on disk as fuzzy search does that for us. We just filter
        # down the list found with fuzzy search to only include those
        # that match the resource code, i.e., book, being requested.
        # This frees us from the brittleness of expecting asset files
        # to be named a certain way for all languages since we are
        # able to just check that the asset file has the resource code
        # as a substring.
        #
        # If desired, in the case where a manifest must be consulted
        # to determine if the file is considered usable, i.e.,
        # 'complete' or 'finished', that can also be done by comparing
        # the filtered file(s) against the manifest's 'finished' list
        # to see if it can be used.
        if usfm_content_files:
            # Only use the content files that match the resource_code
            # in the resource request.
            self._content_files = list(
                filter(
                    lambda usfm_content_file: self._resource_code.lower()
                    in str(usfm_content_file).lower(),
                    usfm_content_files,
                )
            )
        elif txt_content_files:
            # Only use the content files that match the resource_code
            # in the resource request.
            self._content_files = list(
                filter(
                    lambda txt_content_file: self._resource_code.lower()
                    in str(txt_content_file).lower(),
                    txt_content_files,
                )
            )

    @icontract.require(lambda self: self._content_files is not None)
    @icontract.ensure(lambda self: self._resource_filename is not None)
    def get_content(self) -> None:
        """See docstring in superclass."""

        self._initialize_from_assets()

        logger.debug("self._content_files: {}".format(self._content_files))

        if self._content_files is not None:
            # Convert the USFM to HTML and store in file.
            # TODO USFM-Tools books.py can raise MalformedUsfmError
            # when the following code is called. If that happens we
            # want to skip this resource request but continue with
            # others in the same document request. Catch said exception.
            try:
                UsfmTransform.buildSingleHtmlFromFile(
                    pathlib.Path(self._content_files[0]),
                    self._output_dir,
                    self._resource_filename,
                )
            except:
                logger.debug(
                    "Exception while reading USFM file, skipping this resource and continuing with remaining resource requests, if any."
                )
                return None

            # Read the HTML file into _content.
            html_file = "{}.html".format(
                os.path.join(self._output_dir, self._resource_filename)
            )
            assert os.path.exists(html_file)
            self._content = file_utils.read_file(html_file)

            self._initialize_verses_html()

    @property
    def chapters_content(self) -> Dict:
        """Provide public interface for other modules."""
        return self._chapters_content

    @icontract.require(lambda self: self._content)
    @icontract.ensure(lambda self: self._chapters_content)
    def _initialize_verses_html(self) -> None:
        """
        Break apart the USFM HTML content into HTML chapter and verse
        chunks, augment HTML output with additional HTML elements and
        store in an instance variable.
        """
        parser = bs4.BeautifulSoup(self._content, "html.parser")

        chapter_breaks = parser.find_all("h2", attrs={"class": "c-num"})
        localized_chapter_heading = chapter_breaks[0].get_text().split()[0]
        for chapter_break in chapter_breaks:
            chapter_num = int(chapter_break.get_text().split()[1])
            chapter_content = html_parsing_utils.tag_elements_between(
                parser.find(
                    "h2", text="{} {}".format(localized_chapter_heading, chapter_num),
                ),
                # ).next_sibling,
                parser.find(
                    "h2",
                    text="{} {}".format(localized_chapter_heading, chapter_num + 1),
                ),
            )
            chapter_content = [str(tag) for tag in list(chapter_content)]
            chapter_content_parser = bs4.BeautifulSoup(
                "".join(chapter_content), "html.parser",
            )
            chapter_verse_tags: bs4.elements.ResultSet = chapter_content_parser.find_all(
                "span", attrs={"class": "v-num"}
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
            # NOTE Do we really want to enclose each verse in a paragraph element?
            # I've done it mainly for later display purposes, but I don't think it
            # is necessary because in 'by verse' interleaving strategy each verse is
            # sandwiched between HTML header elements anyway. But I do like that it
            # makes the HTML have more closed tags, though the parser has other open
            # tags, so perhaps it isn't worth it. It is easy enough to experiment
            # with removing the enclosing paragraph element and see the result.
            chapter_verse_list = [
                "<p>{} {}</p>".format(verse, verse.next_sibling)
                for verse in chapter_verse_tags
            ]
            # Dictionary to hold verse number, verse value pairs.
            chapter_verses: Dict[str, str] = {}
            for verse_element in chapter_verse_list:
                (
                    verse_num,
                    verse_content_str,
                ) = self._get_verse_num_and_verse_content_str(
                    chapter_num, chapter_content_parser, verse_element
                )
                chapter_verses[verse_num] = verse_content_str
            self._chapters_content[chapter_num] = model.USFMChapter(
                chapter_content=chapter_content,
                chapter_verses=chapter_verses,
                chapter_footnotes=chapter_footnotes,
            )

    def _get_verse_num_and_verse_content_str(
        self,
        chapter_num: int,
        chapter_content_parser: bs4.BeautifulSoup,
        verse_element: str,
    ) -> Tuple[model.VerseRef, model.HtmlContent]:
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

            # NOTE Would have to pass in chapter_num to use this.
            logger.debug(
                "chapter_num: {}, verse_num is a verse range: {}".format(
                    chapter_num, verse_num
                )
            )
        else:
            upper_bound_value = int(verse_num) + 1
            # Get rid of leading zeroes.
            verse_num = str(int(verse_num))

        # Create the lower and upper search bounds for the
        # BeautifulSoup HTML parser.
        lower_id = "{}-ch-{}-v-{}".format(
            str(self._book_number).zfill(3),
            str(chapter_num).zfill(3),
            verse_num.zfill(3),
        )
        upper_id = "{}-ch-{}-v-{}".format(
            str(self._book_number).zfill(3),
            str(chapter_num).zfill(3),
            str(upper_bound_value).zfill(3),
        )
        # Using the upper and lower parse a verse worth of HTML
        # content.
        verse_content_tags = html_parsing_utils.tag_elements_between(
            chapter_content_parser.find(
                "span", attrs={"class": "v-num", "id": lower_id},
            ),
            # ).next_sibling,
            chapter_content_parser.find(
                "span", attrs={"class": "v-num", "id": upper_id},
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
        pattern = r'id="(.+?)-ch-(.+?)-v-(.+?)"'
        verse_content_str = re.sub(
            pattern, r"id='{}-\1-ch-\2-v-\3'".format(self.lang_code), verse_content_str,
        )
        return model.VerseRef(verse_num), model.HtmlContent(verse_content_str)


class TResource(Resource):
    """Provide methods common to all subclasses of TResource."""

    @log_on_end(
        logging.DEBUG,
        "self._resource_url: {self._resource_url} for {self}",
        logger=logger,
    )
    def find_location(self) -> None:
        """Find the URL where the resource's assets are located."""
        lookup_svc = resource_lookup.TResourceJsonLookup()
        resource_lookup_dto: model.ResourceLookupDto = lookup_svc.lookup(self)
        self._lang_name = resource_lookup_dto.lang_name
        self._resource_type_name = resource_lookup_dto.resource_type_name
        self._resource_url = resource_lookup_dto.url
        self._resource_source = resource_lookup_dto.source
        self._resource_jsonpath = resource_lookup_dto.jsonpath

    @icontract.require(lambda self: self._content)
    def _convert_md2html(self) -> None:
        """Convert a resource's Markdown to HTML."""
        self._content = markdown.markdown(self._content)

    @log_on_start(logging.INFO, "Converting MD to HTML...", logger=logger)
    def _transform_content(self) -> None:
        """
        If self._content is not empty, go ahead and transform rc
        resource links and transform content from Markdown to HTML.
        """
        if self._content:
            self._content = link_utils.replace_rc_links(
                self._my_rcs, self._resource_data, self._content
            )
            self._content = link_utils.transform_rc_links(self._content)
            self._convert_md2html()


class TNResource(TResource):
    """
    This class handles specializing Resource for the case when the
    resource is a Translation Notes resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._book_payload: model.TNBookPayload

    @log_on_start(
        logging.INFO, "Processing Translation Notes Markdown...", logger=logger
    )
    def get_content(self) -> None:
        """
        Get Markdown content from this resource's file assets. Then do
        some manipulation of said Markdown content according to the
        needs of the document output. Then convert the Markdown content
        into HTML content.
        """
        self._initialize_from_assets()

        # self._initialize_verses_html()

    @property
    def book_payload(self) -> model.TNBookPayload:
        """Provide public interface for other modules."""
        return self._book_payload

    @log_on_start(
        logging.DEBUG, "self._resource_dir: {self._resource_dir}", logger=logger
    )
    def _initialize_from_assets(self) -> None:
        """See docstring in superclass."""
        self._manifest = Manifest(self)

    @log_on_start(
        logging.INFO,
        "About to convert TN Markdown to HTML with Markdown extension",
        logger=logger,
    )
    def initialize_verses_html(self, tw_resource_dir: Optional[str]) -> None:
        """
        Find book intro, chapter intros, and then the translation
        notes for the verses themselves.
        """
        # WIP. Create the Markdown instance once and have it use our markdown
        # extensions. The first extension changes (See [[rc:foo]]) style links
        # into [](rc:foo) style links. This is an experiment to supplant legacy
        # code that makes Markdown transformations on raw Markdown content.
        md = markdown.Markdown(
            extensions=[
                wikilink_preprocessor.WikiLinkExtension(),
                remove_section_preprocessor.RemoveSectionExtension(),
                translation_word_link_preprocessor.TranslationWordLinkExtension(
                    lang_code={self.lang_code: "Language code for resource"},
                    tw_resource_dir={
                        tw_resource_dir: "Base directory for paths to translation word markdown files"
                    },
                ),
            ]
        )
        # FIXME We can likely now remove the first '**'
        chapter_dirs = sorted(
            glob("{}/**/*{}/*[0-9]*".format(self._resource_dir, self._resource_code))
        )
        # Some languages are organized differently on disk (e.g., depending
        # on if their assets were acquired as a git repo or a zip).
        # We handle this here.
        if not chapter_dirs:
            chapter_dirs = sorted(
                glob("{}/*{}/*[0-9]*".format(self._resource_dir, self._resource_code))
            )
        chapter_verses: Dict[int, model.TNChapterPayload] = {}
        for chapter_dir in chapter_dirs:
            chapter_num = int(os.path.split(chapter_dir)[-1])
            # FIXME For some languages, TN assets are stored in .txt files
            # rather of .md files. Handle this.
            intro_paths = glob("{}/*intro.md".format(chapter_dir))
            intro_path = intro_paths[0] if intro_paths else None
            intro_html = ""
            if intro_path:
                with open(intro_path, "r", encoding="utf-8") as fin:
                    intro_html = fin.read()
                    intro_html = md.convert(intro_html)
            # FIXME For some languages, TN assets are stored in .txt files
            # rather of .md files. Handle this.
            verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
            verses_html: Dict[int, str] = {}
            for filepath in verse_paths:
                verse_num = int(pathlib.Path(filepath).stem)
                verse_content = ""
                with open(filepath, "r", encoding="utf-8") as fin2:
                    verse_content = fin2.read()
                    verse_content = md.convert(verse_content)
                verses_html[verse_num] = verse_content
            chapter_payload = model.TNChapterPayload(
                intro_html=intro_html, verses_html=verses_html
            )
            chapter_verses[chapter_num] = chapter_payload
        # Get the book intro if it exists
        # FIXME For some languages, TN assets are stored in .txt files
        # rather of .md files. Handle this.
        book_intro_path = glob(
            "{}/*{}/front/intro.md".format(self._resource_dir, self._resource_code)
        )
        book_intro_html = ""
        if book_intro_path:
            with open(book_intro_path[0], "r", encoding="utf-8") as fin3:
                book_intro_html = md.convert(fin3.read())
        self._book_payload = model.TNBookPayload(
            intro_html=model.HtmlContent(book_intro_html), chapters=chapter_verses
        )

    def get_verses_for_chapter(
        self, chapter_num: model.ChapterNum
    ) -> Optional[Dict[model.VerseRef, model.HtmlContent]]:
        """
        Return the HTML for verses that are in the chapter with
        chapter_num.
        """
        verses_html = None
        if chapter_num in self.book_payload.chapters:
            verses_html = self.book_payload.chapters[chapter_num].verses_html
        return verses_html

    def format_tn_verse(
        self, chapter_num: model.ChapterNum, verse_num: model.VerseRef,
    ) -> List[model.HtmlContent]:
        """
        Build and return the content for the translation note for chapter
        chapter_num and verse verse_num.
        """
        chapter_verses = self.get_verses_for_chapter(chapter_num)
        tn_verse = None
        if chapter_verses and verse_num in chapter_verses:
            tn_verse = chapter_verses[verse_num]
        if tn_verse is None:
            return [model.HtmlContent("")]

        html: List[model.HtmlContent] = []
        # Add header
        html.append(
            model.HtmlContent(
                config.get_html_format_string("translation_note").format(
                    chapter_num, verse_num
                )
            )
        )
        # Change H1 HTML elements to H4 HTML elements in each translation note
        # so that overall indentation works out.
        html.append(model.HtmlContent(re.sub(r"h1", r"h4", tn_verse)))
        return html


class TQResource(TResource):
    """
    This class specializes Resource for the case of a Translation
    Questions resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._book_payload: model.TQBookPayload

    @log_on_start(
        logging.INFO, "Processing Translation Questions Markdown...", logger=logger
    )
    def get_content(self) -> None:
        """
        Get Markdown content from this resource's file assets. Then do
        some manipulation of said Markdown content according to the
        needs of the document output. Then convert the Markdown content
        into HTML content.
        """

        self._initialize_from_assets()
        # self._initialize_verses_html()

    @property
    def book_payload(self) -> model.TQBookPayload:
        """Provide public interface for other modules."""
        return self._book_payload

    @log_on_start(
        logging.DEBUG, "self._resource_dir: {self._resource_dir}", logger=logger
    )
    def _initialize_from_assets(self) -> None:
        """See docstring in superclass."""
        self._manifest = Manifest(self)

    @log_on_start(
        logging.INFO,
        "About to convert TQ Markdown to HTML with Markdown extension",
        logger=logger,
    )
    def initialize_verses_html(self, tw_resource_dir: Optional[str]) -> None:
        """
        Find translation questions for the verses.
        """
        # Create the Markdown instance once and have it use our markdown
        # extensions.
        md = markdown.Markdown(
            extensions=[
                wikilink_preprocessor.WikiLinkExtension(),
                remove_section_preprocessor.RemoveSectionExtension(),
                translation_word_link_preprocessor.TranslationWordLinkExtension(
                    lang_code={self.lang_code: "Language code for resource"},
                    tw_resource_dir={
                        tw_resource_dir: "Paths to translation words markdown files"
                    },
                ),
            ]
        )
        # FIXME We can likely now remove the first '**'
        chapter_dirs = sorted(
            glob("{}/**/*{}/*[0-9]*".format(self._resource_dir, self._resource_code))
        )
        # Some languages are organized differently on disk (e.g., depending
        # on if their assets were acquired as a git repo or a zip).
        # We handle this here.
        if not chapter_dirs:
            # FIXME We can likely now remove the first '**'
            chapter_dirs = sorted(
                glob("{}/*{}/*[0-9]*".format(self._resource_dir, self._resource_code))
            )
        chapter_verses: Dict[int, model.TQChapterPayload] = {}
        for chapter_dir in chapter_dirs:
            chapter_num = int(os.path.split(chapter_dir)[-1])
            # FIXME For some languages, TQ assets are stored in .txt files
            # rather of .md files. Handle this.
            verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
            verses_html: Dict[int, str] = {}
            for filepath in verse_paths:
                verse_num = int(pathlib.Path(filepath).stem)
                verse_content = ""
                with open(filepath, "r", encoding="utf-8") as fin2:
                    verse_content = fin2.read()
                    # NOTE I don't think translation questions have a
                    # 'Links:' section.
                    # verse_content = markdown_utils.remove_md_section(
                    #     verse_content, "Links:"
                    # )
                    verse_content = md.convert(verse_content)
                verses_html[verse_num] = verse_content
            chapter_payload = model.TQChapterPayload(verses_html=verses_html)
            chapter_verses[chapter_num] = chapter_payload
        self._book_payload = model.TQBookPayload(chapters=chapter_verses)

    def get_verses_for_chapter(
        self, chapter_num: model.ChapterNum
    ) -> Optional[Dict[model.VerseRef, model.HtmlContent]]:
        """
        Return the HTML for verses in chapter_num.
        """
        verses_html = None
        if chapter_num in self.book_payload.chapters:
            verses_html = self.book_payload.chapters[chapter_num].verses_html
        return verses_html

    def format_tq_verse(
        self, chapter_num: model.ChapterNum, verse_num: model.VerseRef,
    ) -> List[model.HtmlContent]:
        """
        Build and return the content for the translation question for chapter
        chapter_num and verse verse_num.
        """
        chapter_verses = self.get_verses_for_chapter(chapter_num)
        tq_verse = None
        if chapter_verses and verse_num in chapter_verses:
            tq_verse = chapter_verses[verse_num]
        if tq_verse is None:
            return [model.HtmlContent("")]

        html: List[model.HtmlContent] = []
        html.append(
            model.HtmlContent(
                config.get_html_format_string("translation_question").format(
                    chapter_num, verse_num
                )
            )
        )
        # Change H1 HTML elements to H4 HTML elements in each translation question
        # so that overall indentation works out.
        html.append(model.HtmlContent(re.sub(r"h1", r"h4", tq_verse)))
        return html


class TWResource(TResource):
    """
    This class specializes Resource for the case of a Translation
    Words resource.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._language_payload: model.TWLanguagePayload

    @log_on_start(
        logging.INFO, "Processing Translation Words Markdown...", logger=logger
    )
    def get_content(self) -> None:
        """
        Get Markdown content from this resource's file assets. Then do
        some manipulation of said Markdown content according to the
        needs of the document output. Then convert the Markdown content
        into HTML content.
        """

        self._initialize_from_assets()
        # self._initialize_verses_html()

    @property
    def language_payload(self) -> model.TWLanguagePayload:
        """Provide public interface for other modules."""
        return self._language_payload

    @log_on_start(
        logging.DEBUG, "self._resource_dir: {self._resource_dir}", logger=logger
    )
    def _initialize_from_assets(self) -> None:
        """See docstring in superclass."""
        self._manifest = Manifest(self)

    @staticmethod
    def get_translation_word_filepaths(resource_dir: str) -> FrozenSet[str]:
        """
        Get the file paths to the translation word files for the
        TWResource instance.
        """
        filepaths = glob("{}/bible/kt/*.md".format(resource_dir))
        filepaths.extend(glob("{}/bible/names/*.md".format(resource_dir)))
        filepaths.extend(glob("{}/bible/other/*.md".format(resource_dir)))
        # Parameter to Markdown extension must be hashable. FrozenSet
        # is hashable.
        return frozenset(filepaths)

    @log_on_start(
        logging.INFO,
        "About to convert TW Markdown to HTML with Markdown extension",
        logger=logger,
    )
    def initialize_verses_html(self, tw_resource_dir: str) -> None:
        """
        Find translation words for the verses.
        """
        # Create the Markdown instance once and have it use our markdown
        # extensions.
        md = markdown.Markdown(
            extensions=[
                wikilink_preprocessor.WikiLinkExtension(),
                remove_section_preprocessor.RemoveSectionExtension(),
                translation_word_link_preprocessor.TranslationWordLinkExtension(
                    lang_code={self.lang_code: "Language code for resource."},
                    tw_resource_dir={
                        tw_resource_dir: "Base directory for Translation word markdown file paths ."
                    },
                ),
            ]
        )
        filepaths = TWResource.get_translation_word_filepaths(tw_resource_dir)
        translation_words_dict: Dict[model.BaseFilename, model.TWNameContentPair] = {}
        for translation_word_file in filepaths:
            with open(translation_word_file, "r") as fin:
                translation_word_content = fin.read()
                # Remember that localized word is sometimes capitalized and sometimes
                # not. So later when we search for the localized word
                # in translation_word_dict.keys
                # compared to the verse we'll need to account for that.
                # For each translation word we encounter in a verse
                # we'll collect a link into a collection which we'll
                # display in a translation words section after the
                # translation questions section for that verse. Later
                # after all verses we'll display all the translation
                # words and each will be prepended with its anchor
                # link. That way the links in verses will point to the
                # word.
                #
                # Translation words are bidirectional. By that I
                # mean that when you are at a verse there follows,
                # after translation questions, links to the
                # translation words that occur in that verse. But then
                # when you navigate to the word by clicking the link,
                # at the end of the translation word note there is a
                # section called 'Uses:' that also has links to the
                # verses wherein the word occurs. So, we need to
                # build up a data structure that for every word
                # collects which verses it occurs in.
                localized_word = translation_word_content.split("\n")[0].split("# ")[1]
                html_word_content = md.convert(translation_word_content)
                # Make adjustments to the HTML here.
                html_word_content = re.sub(r"h2", r"h4", html_word_content)
                html_word_content = re.sub(r"h1", r"h3", html_word_content)
                # We need to store both the word in English, i.e., the filename
                # sans extension; the localized word; and the associated HTML content.
                # Thus we'll use the localized word as key so that we can do lookups
                # against verse content, but for the value, instead of html_word_content
                # only, we'll store a data structure that takes html_word_content and
                # also the English word as fields. The reason is that for non-English
                # languages the word filenames are still in English and we need to have
                # them to make the inter-document linking work (for
                # the filenames), e.g., for 'See also' section references.
                translation_word_base_filename = model.BaseFilename(
                    pathlib.Path(translation_word_file).stem
                )
                translation_words_dict[
                    translation_word_base_filename
                ] = model.TWNameContentPair(
                    localized_word=localized_word, content=html_word_content
                )

        self._language_payload = model.TWLanguagePayload(
            translation_words_dict=translation_words_dict
        )

    def get_translation_word_links(
        self,
        chapter_num: model.ChapterNum,
        verse_num: model.VerseRef,
        verse: model.HtmlContent,
    ) -> List[model.HtmlContent]:
        """
        Add the translation links section which provides links from words
        used in the current verse to their definition, i.e., to their
        translation word content.
        """
        html: List[model.HtmlContent] = []
        # Check if any of the kt_dict, names_dict, or other_dict keys appear in
        # the current scripture verse. If so make a link to point to the word
        # content which occurs later in the document.
        uses: List[model.TWUse] = []
        key: model.BaseFilename
        value: model.TWNameContentPair
        for key, value in self._language_payload.translation_words_dict.items():
            # This checks that the word occurs as an exact sub-string in
            # the verse.
            if re.search(r"\b{}\b".format(value.localized_word), verse):
                use = model.TWUse(
                    lang_code=self.lang_code,
                    book_id=self.resource_code,
                    # FIXME Use localized book name.
                    book_name=bible_books.BOOK_NAMES[self.resource_code],
                    chapter_num=chapter_num,
                    verse_num=verse_num,
                    base_filename=key,
                    localized_word=value.localized_word,
                )
                uses.append(use)
                # Store reference for use in 'Uses:' section that
                # comes later.
                if key in self.language_payload.uses:
                    self.language_payload.uses[key].append(use)
                else:
                    self.language_payload.uses[key] = [use]

        if uses:
            # Add header
            html.append(
                model.HtmlContent(
                    # config.get_html_format_string("translation_words").format(
                    config.get_html_format_string("resource_type_name_with_ref").format(
                        self.resource_type_name, chapter_num, verse_num
                    )
                )
            )
            # Start list formatting
            html.append(config.get_html_format_string("unordered_list_begin"))
            # Append word links.
            uses_list_items = [
                config.get_html_format_string("translation_word_list_item").format(
                    self.lang_code, use.base_filename, use.localized_word,
                )
                for use in uses
            ]
            html.append(model.HtmlContent("\n".join(uses_list_items)))
            # End list formatting
            html.append(config.get_html_format_string("unordered_list_end"))
        return html

    def get_translation_words_section(
        self, include_uses_section: bool = True,
    ) -> List[model.HtmlContent]:
        """
        Build and return the translation words definition section, i.e.,
        the list of all translation words for this language, book
        combination. Include a 'Uses:' section that points from the
        translation word back to the verses which include the translation
        word if include_uses_section is True.
        """
        html: List[model.HtmlContent] = []
        html.append(
            model.HtmlContent(
                config.get_html_format_string("resource_type_name").format(
                    self.resource_type_name
                )
            )
        )

        for (
            base_filename,
            tw_name_content_pair,
        ) in self._language_payload.translation_words_dict.items():
            # NOTE If we un-comment the commented out if conditional logic
            # on the next commented line and remove the same conditional logic which
            # occurs later in this same function, we will only include words in the
            # translation section which occur in current lang_code, book. The
            # problem, I found, with this is that translation note 'See also'
            # sections often refer to translation words that are not part of the
            # lang_code, book combination content and thus those links are dead
            # unless we include them even if they don't have any 'Uses' section.

            # Make linking work.
            tw_name_content_pair.content = model.HtmlContent(
                tw_name_content_pair.content.replace(
                    # FIXME Don't use magic strings, move format
                    # string to config.get_html_format_string
                    "<h3>{}".format(tw_name_content_pair.localized_word),
                    '<h3 id="{}-{}">{}'.format(
                        self.lang_code,
                        base_filename,
                        tw_name_content_pair.localized_word,
                    ),
                )
            )
            uses_section = model.HtmlContent("")

            # See comment above.
            if include_uses_section and base_filename in self.language_payload.uses:
                uses_section = self._get_uses_section(
                    self.language_payload.uses[base_filename]
                )
                tw_name_content_pair.content = model.HtmlContent(
                    tw_name_content_pair.content + uses_section
                )
            html.append(tw_name_content_pair.content)
        return html

    def _get_uses_section(self, uses: List[model.TWUse]) -> model.HtmlContent:
        """
        Construct and return the 'Uses:' section which comes at the end of
        a translation word definition and wherein each item points to
        verses (as targeted by lang_code, book_id, chapter_num, and
        verse_num) wherein the word occurs.
        """
        html: List[model.HtmlContent] = []
        html.append(
            config.get_html_format_string("translation_word_verse_section_header")
        )
        html.append(config.get_html_format_string("unordered_list_begin"))
        for use in uses:
            html_content_str = model.HtmlContent(
                config.get_html_format_string("translation_word_verse_ref_item").format(
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
        html.append(config.get_html_format_string("unordered_list_end"))
        return model.HtmlContent("\n".join(html))


class TAResource(TResource):
    """
    This class specializes Resource for the case of a Translation
    Answers resource.
    """

    @log_on_start(
        logging.INFO, "Processing Translation Academy Markdown...", logger=logger
    )
    def get_content(self) -> None:
        """See docstring in superclass."""
        self._get_ta_markdown()
        self._transform_content()

    def _get_ta_markdown(self) -> None:
        # TODO localization
        ta_md = '<a id="ta-{}"/>\n# Translation Topics\n\n'.format(self._book_id)
        sorted_rcs = sorted(
            # resource["my_rcs"],
            # key=lambda k: resource["resource_data"][k]["title"].lower()
            self._my_rcs,
            key=lambda k: self._resource_data[k]["title"].lower(),
        )
        for rc in sorted_rcs:
            if "/ta/" not in rc:
                continue
            # if resource["resource_data"][rc]["text"]:
            if self._resource_data[rc]["text"]:
                # md = resource["resource_data"][rc]["text"]
                md = self._resource_data[rc]["text"]
            else:
                md = ""
            # id_tag = '<a id="{}"/>'.format(resource["resource_data"][rc]["id"])
            id_tag = '<a id="{}"/>'.format(self._resource_data[rc]["id"])
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{}\n".format(id_tag), md, 1)
            md = markdown_utils.increase_headers(md)
            md += link_utils.get_uses(self._rc_references, rc)
            md += "\n\n"
            ta_md += md
        logger.debug("ta_md is {0}".format(ta_md))
        self._content = ta_md
        # return ta_md


def resource_factory(
    working_dir: str,
    output_dir: str,
    resource_request: model.ResourceRequest,
    # XXX Resources shouldn't care about assembly strategies.
    # assembly_strategy_kind: model.AssemblyStrategyEnum,
) -> Resource:
    """
    Factory method to create the appropriate Resource subclass for
    a given ResourceRequest instance.
    """
    # resource_type is key, Resource subclass is value
    resources = {
        "usfm": USFMResource,
        "ulb": USFMResource,
        "ulb-wa": USFMResource,
        "udb": USFMResource,
        "udb-wa": USFMResource,
        "nav": USFMResource,
        "reg": USFMResource,
        "cuv": USFMResource,
        "udb": USFMResource,
        "tn": TNResource,
        "tn-wa": TNResource,
        "tq": TQResource,
        "tq-wa": TQResource,
        "tw": TWResource,
        "tw-wa": TWResource,
        "ta": TAResource,
        "ta-wa": TAResource,
    }
    return resources[resource_request.resource_type](
        working_dir, output_dir, resource_request
    )  # type: ignore


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
        logger.debug("os.getcwd(): {}".format(os.getcwd()))
        if not os.path.exists(self._resource.resource_dir):
            logger.debug(
                "About to create directory {}".format(self._resource.resource_dir)
            )
            try:
                os.mkdir(self._resource.resource_dir)
            except FileExistsError:
                logger.exception(
                    "Directory {} already existed".format(self._resource.resource_dir)
                )
            else:
                logger.debug("Created directory {}".format(self._resource.resource_dir))

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

        self._resource.resource_url = cast(
            str, self._resource.resource_url
        )  # We know, due to how we got here, that
        # self._resource.resource_url attribute is not None. mypy
        # isn't convinced otherwise without the cast.

        # FIXME To ensure consistent directory naming for later discovery, let's
        # consider not using the url.rpartition(os.path.sep)[2]. Instead let's
        # use a directory built from the parameters of the (updated) resource:
        # os.path.join(resource.resource_dir, resource.resource_type)
        # FIXME We'll have to see if this is the best approach for consistency
        # across different resources' assets in different languages. So far it
        # adheres to the most consistent pattern I've seen in translations.json,
        # but my analysis of translations.json has not been exhaustive. That
        # being said, it has worked fine for several languages and books so far
        # though.
        resource_filepath = os.path.join(
            self._resource.resource_dir,
            self._resource.resource_url.rpartition(os.path.sep)[2],
        )
        logger.debug(
            "Using file location, resource_filepath: {}".format(resource_filepath)
        )

        if self._is_git():
            self._clone_git_repo(resource_filepath)
        else:
            self._download_asset(resource_filepath)

        if self._is_zip():
            self._unzip_asset(resource_filepath)

    def _clone_git_repo(self, resource_filepath: str) -> None:
        """
        Clone the git reop.
        """
        command = "git clone --depth=1 '{}' '{}'".format(
            self._resource.resource_url, resource_filepath
        )
        logger.debug("os.getcwd(): {}".format(os.getcwd()))
        logger.debug("git command: {}".format(command))
        try:
            subprocess.call(command, shell=True)
        except subprocess.SubprocessError:
            logger.debug("os.getcwd(): {}".format(os.getcwd()))
            logger.debug("git command: {}".format(command))
            logger.debug("git clone failed!")
        else:
            logger.debug("git clone succeeded.")
            # Git repos get stored on directory deeper
            self._resource.resource_dir = resource_filepath

    @log_on_start(
        logging.DEBUG,
        "Downloading {self._resource.resource_url} into {resource_filepath}",
        logger=logger,
    )
    @log_on_end(logging.INFO, "Downloading finished.", logger=logger)
    def _download_asset(self, resource_filepath: str) -> None:
        """Download the asset."""
        if file_utils.asset_file_needs_update(resource_filepath):
            # FIXME Might want to retry after some acceptable interval if there is a
            # failure here due to network issues. It has happened very
            # occasionally during testing that there has been a hiccup
            # with the network at this point but succeeded on retry of
            # the same test.
            url_utils.download_file(self._resource.resource_url, resource_filepath)

    @log_on_start(
        logging.DEBUG,
        "Unzipping {resource_filepath} into {self._resource.resource_dir}",
        logger=logger,
    )
    @log_on_end(logging.INFO, "Unzipping finished.", logger=logger)
    @log_on_end(
        logging.DEBUG,
        "self._resource.resource_dir updated: {self._resource.resource_dir}.",
        logger=logger,
    )
    def _unzip_asset(self, resource_filepath: str) -> None:
        """Unzip the asset."""
        file_utils.unzip(resource_filepath, self._resource.resource_dir)
        # Update resource_dir.
        # FIXME We can likely update the glob patterns for resource asset files.
        # Update: Turns out the globs still work with the '**' in them, but
        # perhaps it would be faster to eliminate '**'. Also perhaps it would be
        # faster to use os.scandir there as well, if we can.
        subdirs = [
            f.path for f in os.scandir(self._resource.resource_dir) if f.is_dir()
        ]

        self._resource.resource_dir = subdirs[0]

    @icontract.require(lambda self: self._resource.resource_source)
    def _is_git(self) -> bool:
        """Return true if _resource_source is equal to 'git'."""
        return self._resource.resource_source == model.AssetSourceEnum.GIT

    @icontract.require(lambda self: self._resource.resource_source)
    def _is_zip(self) -> bool:
        """Return true if _resource_source is equal to 'zip'."""
        return self._resource.resource_source == model.AssetSourceEnum.ZIP


class Manifest:
    """
    This class handles finding, loading, and converting manifest
    files for a resource instance.
    """

    def __init__(self, resource: Resource) -> None:
        self._resource = resource
        self._manifest_content: Dict
        # self._manifest_file_path: Optional[pathlib.PurePath] = None
        self._manifest_file_path: Optional[str] = None
        self._version: Optional[str] = None
        self._issued: Optional[str] = None

    @icontract.require(lambda self: self._resource.resource_dir)
    def __call__(self) -> None:
        """All subclasses need to at least find their manifest file,
        if it exists. Subclasses specialize this method to
        additionally initialize other disk layout related properties.
        """
        manifest_file_list = glob("{}**/manifest.*".format(self._resource))
        if manifest_file_list:
            self._manifest_file_path = manifest_file_list[0]
        else:
            self._manifest_file_path = None
        logger.debug("self._manifest_file_path: {}".format(self._manifest_file_path))
        # Find directory where the manifest file is located
        if self._manifest_file_path is not None:
            self._manifest_content = self._load_manifest()
            logger.debug(
                "manifest dir: {}".format(pathlib.Path(self._manifest_file_path).parent)
            )

        if self.manifest_type:
            logger.debug("self.manifest_type: {}".format(self.manifest_type))
            if self._is_yaml():
                version, issued = self._get_manifest_version_and_issued()
                self._version = version
                self._issued = issued
                logger.debug(
                    "_version: {}, _issued: {}".format(self._version, self._issued)
                )
        if self._manifest_content:
            logger.debug("self._manifest_content: {}".format(self._manifest_content))

    @property
    def manifest_type(self) -> Optional[str]:
        """Return the manifest type: yaml, json, or txt."""
        if self._manifest_file_path is not None:
            return pathlib.Path(self._manifest_file_path).suffix
        return None

    @icontract.require(lambda self: self._manifest_file_path is not None)
    def _load_manifest(self) -> dict:
        """Load the manifest file."""
        manifest: dict = {}
        if self._is_yaml():
            manifest = file_utils.load_yaml_object(self._manifest_file_path)
        elif self._is_txt():
            manifest = file_utils.load_yaml_object(self._manifest_file_path)
        elif self._is_json():
            manifest = file_utils.load_json_object(self._manifest_file_path)
        return manifest

    @icontract.require(lambda self: self._manifest_content)
    def _get_manifest_version_and_issued(self) -> Tuple[str, str]:
        """Return the manifest's version and issued values."""
        version = ""
        issued = ""
        # NOTE manifest.txt files do not have 'dublin_core' or
        # 'version' keys.
        version = self._get_manifest_version()
        issued = self._manifest_content["dublin_core"]["issued"]
        return (version, issued)

    def _get_manifest_version(self) -> str:
        version = ""
        try:
            version = self._manifest_content[0]["dublin_core"]["version"]
        except ValueError:
            version = self._manifest_content["dublin_core"]["version"]
        return version

    @icontract.require(lambda self: self.manifest_type)
    def _is_yaml(self) -> bool:
        """Return true if the resource's manifest file has suffix yaml."""
        return self.manifest_type == model.ManifestFormatTypeEnum.YAML

    @icontract.require(lambda self: self.manifest_type)
    def _is_txt(self) -> bool:
        """Return true if the resource's manifest file has suffix json."""
        return self.manifest_type == model.ManifestFormatTypeEnum.TXT

    @icontract.require(lambda self: self.manifest_type)
    def _is_json(self) -> bool:
        """Return true if the resource's manifest file has suffix json."""
        return self.manifest_type == model.ManifestFormatTypeEnum.JSON

    # FIXME Not currently used. The idea for how this would be used is
    # to verify that the book project that we have already found via
    # globbing is indeed considered complete by the translators as
    # codified in the manifest.
    @icontract.require(
        lambda self: self._manifest_content and "projects" in self._manifest_content
    )
    @icontract.ensure(lambda result: result)
    def _get_book_project_from_yaml(self) -> Optional[dict]:
        """
        Return the project that was requested if it matches that found
        in the manifest file for the resource otherwise return an
        empty dict.
        """
        # logger.info("about to get projects")
        # NOTE The old code would return the list of book projects
        # that either contained: 1) all books if no books were
        # specified by the user, or, 2) only those books that
        # matched the books requested from the command line.
        for project in self._manifest_content["projects"]:
            if project["identifier"] in self._resource.resource_code:
                return project
        return None

    # FIXME Not currently used. Might never be used again.
    @icontract.require(
        lambda self: self._manifest_content and "projects" in self._manifest_content
    )
    @icontract.ensure(lambda result: result)
    def _get_book_projects_from_yaml(self) -> List[Dict[Any, Any]]:
        """
        Return the sorted list of projects that are found in the
        manifest file for the resource.
        """
        projects: List[Dict[Any, Any]] = []
        # if (
        #     self._manifest_content and "projects" in self._manifest_content
        # ):
        # logger.info("about to get projects")
        # NOTE The old code would return the list of book projects
        # that either contained: 1) all books if no books were
        # specified by the user, or, 2) only those books that
        # matched the books requested from the command line.
        for project in self._manifest_content["projects"]:
            if project["identifier"] in self._resource.resource_code:
                if not project["sort"]:
                    project["sort"] = bible_books.BOOK_NUMBERS[project["identifier"]]
                projects.append(project)
        return sorted(projects, key=lambda k: k["sort"])

    # FIXME Not currently used. Might never be used again.
    @icontract.require(
        lambda self: self._manifest_content
        and "finished_chunks" in self._manifest_content
    )
    @icontract.ensure(lambda result: result)
    def _get_book_projects_from_json(self) -> List:
        """
        Return the sorted list of projects that are found in the
        manifest file for the resource.
        """
        projects: List[Dict[Any, Any]] = []
        for project in self._manifest_content["finished_chunks"]:
            # TODO In resource_lookup, self._resource_code is used
            # determine jsonpath for lookup. Some resources don't
            # have anything more specific than the lang_code to
            # get resources from. Well, at least one language is
            # like that. In that case it contains a zip that has
            # all the resources contained therein.
            # if self._resource_code is not None:
            projects.append(project)
        return projects
