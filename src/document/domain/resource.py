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
        self._resource_url: Optional[str] = None
        self._resource_source: str
        self._resource_jsonpath: Optional[str] = None

        self._manifest: Manifest

        # Content related instance vars
        self._content_files: List[str] = []
        self._content: str
        self._verses_html: List[str] = []

        # Link related
        # FIXME _bad_links will be removed
        self._bad_links: dict = {}
        self._resource_data: dict = {}
        self._my_rcs: List = []
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
        # FIXME Next (commented) line slated for removal
        # self._usfm_chunks: Dict = {}
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

    # FIXME this log message is slated for removal.
    # @log_on_end(
    #     logging.DEBUG, "self._bad_links: {self._bad_links}", logger=logger,
    # )
    @icontract.require(lambda self: self._content_files is not None)
    @icontract.ensure(lambda self: self._resource_filename is not None)
    def get_content(self) -> None:
        """See docstring in superclass."""
        # FIXME Slated for removal.
        # self._get_usfm_chunks()

        self._initialize_from_assets()

        logger.debug("self._content_files: {}".format(self._content_files))

        if self._content_files is not None:
            # Convert the USFM to HTML and store in file.
            # TODO USFM-Tools books.py can raise MalformedUsfmError
            # when the following code is called. If that happens we
            # want to skip this resource request but continue with
            # others in the same document request. The TODO is that I
            # need to work out where I want to catch said exception.
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

            # logger.debug(
            #     "html content in self._content in {}: {}".format(
            #         html_file, self._content
            #     )
            # )

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
            chapter_verses_parser = bs4.BeautifulSoup(
                "".join(chapter_content), "html.parser",
            )
            chapter_verse_tags: bs4.elements.ResultSet = chapter_verses_parser.find_all(
                "span", attrs={"class": "v-num"}
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
            chapter_verses: Dict[int, str] = {}
            for verse_element in chapter_verse_list:
                # Get the verse num from the verse HTML tag's id value.
                # split is more performant than re.
                # See https://stackoverflow.com/questions/7501609/python-re-split-vs-split
                verse_num = int(str(verse_element).split("-v-")[1].split('"')[0])
                lower_id = "{}-ch-{}-v-{}".format(
                    str(self._book_number).zfill(3),
                    str(chapter_num).zfill(3),
                    str(verse_num).zfill(3),
                )
                upper_id = "{}-ch-{}-v-{}".format(
                    str(self._book_number).zfill(3),
                    str(chapter_num).zfill(3),
                    str(verse_num + 1).zfill(3),
                )
                verse_content_tags = html_parsing_utils.tag_elements_between(
                    chapter_verses_parser.find(
                        "span", attrs={"class": "v-num", "id": lower_id},
                    ),
                    # ).next_sibling,
                    chapter_verses_parser.find(
                        "span", attrs={"class": "v-num", "id": upper_id},
                    ),
                )
                verse_content = [str(tag) for tag in list(verse_content_tags)]
                # Hacky way to remove some redundant parsing results due to recursion in
                # BeautifulSoup. Should use bs4 more expertly to avoid this if it is
                # possible. But this does work and produces the desired result in the
                # end.
                del verse_content[1:4]
                verse_content_str = "".join(verse_content)
                # HACK "Fix" BeautifulSoup parsing issue wherein sometimes a verse
                # contains its content but also includes a subsequent verse or verses or
                # a recapitulation of all previous verses. This does fix the problem
                # though and gives the desired result:
                verse_content_str = (
                    '<span class="v-num"'
                    + verse_content_str.split('<span class="v-num"')[1]
                )
                # At this point we alter verse_content_str span's ID by prepending the
                # lang_code to ensure unique verse references within language scope in a
                # multi-language document.
                pattern = r'id="(.+?)-ch-(.+?)-v-(.+?)"'
                verse_content_str = re.sub(
                    pattern,
                    r"id='{}-\1-ch-\2-v-\3'".format(self.lang_code),
                    verse_content_str,
                )
                chapter_verses[verse_num] = verse_content_str
            self._chapters_content[chapter_num] = model.USFMChapter(
                chapter_content=chapter_content, chapter_verses=chapter_verses,
            )

    # FIXME Remove
    # @icontract.require(
    #     lambda self: self._content_files
    #     and self._resource_filename
    #     and self._resource_dir
    # )
    # @icontract.ensure(lambda self: self._usfm_chunks)
    # def _get_usfm_chunks(self) -> None:
    #     """
    #     Read the USFM file contents requested for resource code and
    #     break it into verse chunks.
    #     """
    #     book_chunks: dict = {}
    #     logger.debug("self._resource_filename: {}".format(self._resource_filename))

    #     usfm_file = self._content_files[0]
    #     usfm_file_content = file_utils.read_file(usfm_file, "utf-8")

    #     # FIXME Not sure I like this LBYL style here. Exceptions
    #     # should actually be the exceptional case here, so this costs
    #     # performance by checking.
    #     if usfm_file_content is not None:
    #         chunks = re.compile(r"\\s5\s*\n*").split(usfm_file_content)
    #     else:
    #         return

    #     # Break chunks into verses
    #     chunks_per_verse = []
    #     for chunk in chunks:
    #         pending_chunk = None
    #         for line in chunk.splitlines(True):
    #             # If this is a new verse and there's a pending chunk,
    #             # finish it and start a new one.
    #             if re.search(r"\\v", line) and pending_chunk:
    #                 chunks_per_verse.append(pending_chunk)
    #                 pending_chunk = None
    #             if pending_chunk:
    #                 pending_chunk += line
    #             else:
    #                 pending_chunk = line

    #         # If there's a pending chunk, finish it.
    #         if pending_chunk:
    #             chunks_per_verse.append(pending_chunk)
    #     chunks = chunks_per_verse

    #     header = chunks[0]
    #     book_chunks["header"] = header
    #     for chunk in chunks[1:]:
    #         chapter: Optional[str] = None
    #         if not chunk.strip():
    #             continue
    #         chapter_search = re.search(
    #             r"\\c[\u00A0\s](\d+)", chunk
    #         )  # \u00A0 no break space
    #         if chapter_search:
    #             chapter = chapter_search.group(1)
    #         verses = re.findall(r"\\v[\u00A0\s](\d+)", chunk)
    #         if not verses:
    #             continue
    #         first_verse = verses[0]
    #         last_verse = verses[-1]
    #         if chapter not in book_chunks:
    #             book_chunks[chapter] = {"chapters": []}
    #         # FIXME first_verse, last_verse, and verses equal the same
    #         # number, e.g., all 1 or all 2, etc.. They don't seem to encode
    #         # meaningfully differentiated data that would be useful.
    #         # first_verse and last_verse are used in
    #         # TNResource so as to imply that they are expected to
    #         # represent a range wider than one verse, but as far as
    #         # execution of the algorithm here, I haven't seen a case where
    #         # they are ever found to be different.
    #         # I may remove them later if no ranges ever actually
    #         # occur - something that remains to be learned. chunk is
    #         # the verse content itself and of course is
    #         # necessary.
    #         data = {
    #             "usfm": chunk,
    #             "first_verse": first_verse,
    #             "last_verse": last_verse,
    #             "verses": verses,
    #         }
    #         book_chunks[chapter][first_verse] = data
    #         book_chunks[chapter]["chapters"].append(data)
    #     self._usfm_chunks = book_chunks


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
        self._resource_url = resource_lookup_dto.url
        self._resource_source = resource_lookup_dto.source
        self._resource_jsonpath = resource_lookup_dto.jsonpath

    @icontract.require(lambda self: self._content)
    def _convert_md2html(self) -> None:
        """Convert a resource's Markdown to HTML."""
        self._content = markdown.markdown(self._content)

    @log_on_start(logging.INFO, "Converting MD to HTML...", logger=logger)
    # FIXME This log message is slated for removal.
    # @log_on_end(logging.DEBUG, "self._bad_links: {self._bad_links}", logger=logger)
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
        # FIXME All the work is done in _initialize_verses_html.
        # So these legacy methods are turned off for now. There are
        # likely bits of logic from these two functions that will find
        # their way back into the system later though (in a different
        # and improved form), e.g., linking.
        # self._get_tn_markdown()
        # self._transform_content()
        self._initialize_from_assets()

        self._initialize_verses_html()

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

    def _initialize_verses_html(self) -> None:
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
                # FIXME Decide how to handle translation word under
                # different contexts, e.g.: no TW requested.
                translation_word_link_preprocessor.TranslationWordLinkExtension(
                    lang_code={self.lang_code: "Language code for resource."}
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
                    # NOTE I am not sure the 'Links' section make
                    # sense in the new interleaving design, so let's
                    # remove it for now.
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
                    # FIXME We could just comment out the next line, i.e.,
                    # not convert Markdown to HTML yet. We could do
                    # the conversion in the assembly strategies
                    # instead and do it all at once for all Markdown
                    # content?
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
    ) -> Dict[model.VerseNum, model.HtmlContent]:
        """
        Return the HTML for verses that are in the chapter with
        chapter_num.
        """
        return self.book_payload.chapters[chapter_num].verses_html

    def format_tn_verse(
        self, chapter_num: model.ChapterNum, verse_num: model.VerseNum,
    ) -> List[model.HtmlContent]:
        """
        Build and return the content for the translation note for chapter
        chapter_num and verse verse_num.
        """
        tn_verse = self.get_verses_for_chapter(chapter_num)[verse_num]
        if not tn_verse:
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

    # FIXME Obselete. Slated for removal.
    # @icontract.require(lambda self: self._resource_code)
    # def _get_tn_markdown(self) -> None:
    #     tn_md = ""
    #     book_dir: str = self._get_book_dir()
    #     logger.debug("book_dir: {}".format(book_dir))

    #     if not os.path.isdir(book_dir):
    #         return

    #     # TODO Might need localization
    #     # tn_md = '# Translation Notes\n<a id="tn-{}"/>\n\n'.format(self._book_id)
    #     # NOTE This is now in the book intro template
    #     # tn_md = '# Translation Notes\n<a id="tn-{}"/>\n\n'.format(self._resource_code)

    #     book_intro_template = self._initialize_tn_book_intro()

    #     tn_md += book_intro_template

    #     for chapter in sorted(os.listdir(book_dir)):
    #         chapter_dir = os.path.join(book_dir, chapter)
    #         logger.debug("chapter_dir: {}".format(chapter_dir))
    #         chapter = chapter.lstrip("0")
    #         if os.path.isdir(chapter_dir) and re.match(r"^\d+$", chapter):
    #             chapter_intro_md = self._initialize_tn_chapter_intro(
    #                 chapter_dir, chapter
    #             )
    #             # TODO Could chunk files ever be something other than
    #             # verses? For instance, could they be a range of
    #             # verses instead?
    #             # Get all the Markdown files that start with a digit
    #             # and end with suffix md.
    #             chunk_files = sorted(glob(os.path.join(chapter_dir, "[0-9]*.md")))
    #             logger.debug("chapter chunk_files: {}".format(chunk_files))
    #             for _, chunk_file in enumerate(chunk_files):
    #                 (
    #                     first_verse,
    #                     last_verse,
    #                     title,
    #                     md,
    #                 ) = link_utils.initialize_tn_chapter_files(
    #                     self._book_id,
    #                     self._book_title,
    #                     self._lang_code,
    #                     chunk_file,
    #                     chapter,
    #                 )

    #                 # anchors = ""
    #                 pre_md = ""
    #                 # FIXME I don't think it should be fetching USFM
    #                 # stuff here in this method under the new design.
    #                 # _initialize_tn_chapter_verse_links now takes a
    #                 # first argument of a USFMResource instance which
    #                 # will provide the _usfm_chunks.
    #                 # if bool(self._usfm_chunks):
    #                 #     # Create links to each chapter
    #                 #     anchors += link_utils.initialize_tn_chapter_verse_anchor_links(
    #                 #         # Need to pass usfm_chunks from a USFMResource instance here.
    #                 #         chapter, first_verse
    #                 #     )
    #                 #     pre_md = "\n## {}\n{}\n\n".format(title, anchors)
    #                 #     # TODO localization
    #                 #     pre_md += "### Unlocked Literal Bible\n\n[[ulb://{}/{}/{}/{}/{}]]\n\n".format(
    #                 #         self._lang_code,
    #                 #         self._book_id,
    #                 #         self._pad(chapter),
    #                 #         self._pad(first_verse),
    #                 #         self._pad(last_verse),
    #                 #     )
    #                 # TODO localization
    #                 pre_md += "### Translation Notes\n"
    #                 md = "{}\n{}\n\n".format(pre_md, md)

    #                 # FIXME Handle case where the user doesn't request tw resource.
    #                 # We don't want conditionals protecting execution
    #                 # of tw related code, but that is what we are
    #                 # doing for now until the code is refactored
    #                 # toward a better design. Just making this work
    #                 # with legacy for the moment.
    #                 # TODO This needs to be moved to a different logic
    #                 # path.

    #                 # FIXME This should be moved to TWResource. Note
    #                 # that it may be necessary to compare what
    #                 # _initialize_tn_translation_words does compared
    #                 # to what _get_tw_markdown does to see if they are
    #                 # redundant.
    #                 # tw_md = self._initialize_tn_translation_words(chapter, first_verse)
    #                 # md = "{}\n{}\n\n".format(md, tw_md)

    #                 # FIXME This belongs in USFMResource or in a new
    #                 # UDBResource.
    #                 # NOTE For now, I could guard this with a
    #                 # conditional that checks if UDB exists.
    #                 # NOTE The idea of this function assumes that UDB
    #                 # exists every time.
    #                 # NOTE For now commenting this out to see how far
    #                 # we get without it.

    #                 # md += self._initialize_tn_udb(
    #                 #     chapter, title, first_verse, last_verse
    #                 # )

    #                 tn_md += md

    #                 links = self._initialize_tn_links(
    #                     self._lang_code,
    #                     self._book_id,
    #                     bool(book_intro_template),
    #                     bool(chapter_intro_md),
    #                     chapter,
    #                 )
    #                 tn_md += links + "\n\n"
    #         else:
    #             logger.debug(
    #                 "chapter_dir: {}, chapter: {}".format(chapter_dir, chapter)
    #             )

    #     self._content = tn_md

    # @icontract.require(
    #     lambda lang_code, book_id, book_has_intro, chapter_has_intro, chapter: lang_code
    #     and book_id
    #     and chapter
    # )
    # def _initialize_tn_links(
    #     self,
    #     lang_code: str,
    #     book_id: str,
    #     book_has_intro: bool,
    #     chapter_has_intro: bool,
    #     chapter: str,
    # ) -> str:
    #     """
    #     Add a Markdown level 3 header populated with links to
    #     the book's intro and chapter intro as well as links to
    #     translation questions for the same book.
    #     """
    #     links = "### Links:\n\n"
    #     if book_has_intro:
    #         links += "* [[rc://{}/tn/help/{}/front/intro]]\n".format(lang_code, book_id)
    #     if chapter_has_intro:
    #         links += "* [[rc://{}/tn/help/{}/{}/intro]]\n".format(
    #             lang_code, book_id, link_utils.pad(book_id, chapter),
    #         )
    #     links += "* [[rc://{}/tq/help/{}/{}]]\n".format(
    #         lang_code, book_id, link_utils.pad(book_id, chapter),
    #     )
    #     return links

    # FIXME This is slated for removal.
    # FIXME I think this code can probably be greatly simplified,
    # moved to _get_tn_markdown and then removed.
    # FIXME Should we change to function w no non-local side-effects
    # and move to markdown_utils.py?
    # @icontract.require(
    #     lambda self: self._resource_dir and self._lang_code and self._resource_type
    # )
    # def _get_book_dir(self) -> str:
    #     """
    #     Given the lang_code, resource_type, and resource_dir,
    #     generate the book directory.
    #     """
    #     filepath: str = os.path.join(
    #         self._resource_dir, "{}_{}".format(self._lang_code, self._resource_type)
    #     )
    #     # logger.debug("self._lang_code: {}".format(self._lang_code))
    #     # logger.debug("self._resource_type: {}".format(self._resource_type))
    #     # logger.debug("self._resource_dir: {}".format(self._resource_dir))
    #     # logger.debug("filepath: {}".format(filepath))
    #     if os.path.isdir(filepath):
    #         book_dir = filepath
    #     else:  # git repo case
    #         book_dir = os.path.join(self._resource_dir, self._resource_code)
    #     return book_dir

    # def _initialize_tn_book_intro(self) -> str:
    #     book_intro_template: str = ""
    #     book_intro_files: List[str] = []
    #     book_intro_files = list(
    #         filter(
    #             lambda content_file: os.path.join("front", "intro")
    #             in content_file.lower(),
    #             self._content_files,
    #         )
    #     )

    #     tn_book_intro_content_md = ""
    #     if book_intro_files and os.path.isfile(book_intro_files[0]):
    #         logger.debug("book_intro_files[0]: {}".format(book_intro_files[0]))
    #         tn_book_intro_content_md = file_utils.read_file(book_intro_files[0])
    #         title: str = markdown_utils.get_first_header(tn_book_intro_content_md)
    #         book_intro_id_tag = '<a id="tn-{}-front-intro"/>'.format(self._book_id)
    #         book_intro_anchor_id = "tn-{}-front-intro".format(self._book_id)
    #         book_intro_rc_link = "rc://{}/tn/help/{}/front/intro".format(
    #             self._lang_code, self._book_id
    #         )
    #         data = model.BookIntroTemplateDto(
    #             book_id=self._book_id,
    #             content=tn_book_intro_content_md,
    #             id_tag=book_intro_id_tag,
    #             anchor_id=book_intro_anchor_id,
    #         )

    #         book_intro_template = config.get_instantiated_template("book_intro", data)

    #         self._resource_data[book_intro_rc_link] = {
    #             "rc": book_intro_rc_link,
    #             "id": book_intro_anchor_id,
    #             "link": "#{}".format(book_intro_anchor_id),
    #             "title": title,
    #         }
    #         self._my_rcs.append(book_intro_rc_link)
    #         link_utils.get_resource_data_from_rc_links(
    #             self._lang_code,
    #             self._my_rcs,
    #             self._rc_references,
    #             self._resource_data,
    #             self._bad_links,
    #             self._working_dir,
    #             tn_book_intro_content_md,
    #             book_intro_rc_link,
    #         )

    #     return book_intro_template
    #     # Old code that new code above replaces:
    #     # intro_file = os.path.join(book_dir, "front", "intro.md")
    #     # book_has_intro = os.path.isfile(intro_file)
    #     # md = ""
    #     # if book_has_intro:
    #     #     md = file_utils.read_file(intro_file)
    #     #     title = markdown_utils.get_first_header(md)
    #     #     md = link_utils.fix_tn_links(self._lang_code, self._book_id, md, "intro")
    #     #     md = markdown_utils.increase_headers(md)
    #     #     # bring headers of 5 or more #'s down 1
    #     #     md = markdown_utils.decrease_headers(md, 5)
    #     #     id_tag = '<a id="tn-{}-front-intro"/>'.format(self._book_id)
    #     #     md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{}\n".format(id_tag), md, 1)
    #     #     # Create placeholder link
    #     #     rc = "rc://{}/tn/help/{}/front/intro".format(self._lang_code, self._book_id)
    #     #     anchor_id = "tn-{}-front-intro".format(self._book_id)
    #     #     self._resource_data[rc] = {
    #     #         "rc": rc,
    #     #         "id": anchor_id,
    #     #         "link": "#{}".format(anchor_id),
    #     #         "title": title,
    #     #     }
    #     #     self._my_rcs.append(rc)
    #     #     link_utils.get_resource_data_from_rc_links(
    #     #         self._lang_code,
    #     #         self._my_rcs,
    #     #         self._rc_references,
    #     #         self._resource_data,
    #     #         self._bad_links,
    #     #         self._working_dir,
    #     #         md,
    #     #         rc,
    #     #     )
    #     #     md += "\n\n"

    # def _initialize_tn_chapter_intro(self, chapter_dir: str, chapter: str) -> str:
    #     tn_chapter_intro_md = ""
    #     intro_file = os.path.join(chapter_dir, "intro.md")
    #     if os.path.isfile(intro_file):
    #         try:
    #             tn_chapter_intro_md = file_utils.read_file(intro_file)
    #         except ValueError as exc:
    #             logger.debug("Error opening file:", exc)
    #             return ""
    #         else:
    #             title = markdown_utils.get_first_header(tn_chapter_intro_md)
    #             tn_chapter_intro_md = link_utils.fix_tn_links(
    #                 self._lang_code, self._book_id, tn_chapter_intro_md, chapter
    #             )
    #             tn_chapter_intro_md = markdown_utils.increase_headers(
    #                 tn_chapter_intro_md
    #             )
    #             tn_chapter_intro_md = markdown_utils.decrease_headers(
    #                 tn_chapter_intro_md, 5, 2
    #             )  # bring headers of 5 or more #'s down 2
    #             id_tag = '<a id="tn-{}-{}-intro"/>'.format(
    #                 self._book_id, link_utils.pad(self._book_id, chapter)
    #             )
    #             tn_chapter_intro_md = re.compile(r"# ([^\n]+)\n").sub(
    #                 r"# \1\n{}\n".format(id_tag), tn_chapter_intro_md, 1
    #             )
    #             # Create placeholder link
    #             rc = "rc://{}/tn/help/{}/{}/intro".format(
    #                 self._lang_code,
    #                 self._book_id,
    #                 link_utils.pad(self._book_id, chapter),
    #             )
    #             anchor_id = "tn-{}-{}-intro".format(
    #                 self._book_id, link_utils.pad(self._book_id, chapter)
    #             )
    #             self._resource_data[rc] = {
    #                 "rc": rc,
    #                 "id": anchor_id,
    #                 "link": "#{}".format(anchor_id),
    #                 "title": title,
    #             }
    #             self._my_rcs.append(rc)
    #             link_utils.get_resource_data_from_rc_links(
    #                 self._lang_code,
    #                 self._my_rcs,
    #                 self._rc_references,
    #                 self._resource_data,
    #                 self._bad_links,
    #                 self._working_dir,
    #                 tn_chapter_intro_md,
    #                 rc,
    #             )
    #             tn_chapter_intro_md += "\n\n"
    #     return tn_chapter_intro_md

    # FIXME Should we change to function w no non-local side-effects
    # and move to markdown_utils.py?
    # def _initialize_tn_translation_words(self, chapter: str, first_verse: str) -> str:
    #     # Add Translation Words for passage
    #     tw_md = ""
    #     # FIXME This should probably become _tw_refs_by_verse on TWResource
    #     if self.tw_refs_by_verse:
    #         tw_refs = get_tw_refs(
    #             self.tw_refs_by_verse,
    #             self._book_title,
    #             chapter,
    #             first_verse
    #             # self.tw_refs_by_verse, self.book_title, chapter, first_verse
    #         )
    #         if tw_refs:
    #             # TODO localization
    #             tw_md += "### Translation Words\n\n"
    #             for tw_ref in tw_refs:
    #                 file_ref_md = "* [{}](rc://en/tw/dict/bible/{}/{})\n".format(
    #                     tw_ref["Term"], tw_ref["Dir"], tw_ref["Ref"]
    #                 )
    #                 tw_md += file_ref_md
    #     return tw_md

    # FIXME Should we change to function w no non-local side-effects
    # and move to markdown_utils.py?
    # def _initialize_tn_udb(
    #     self, chapter: str, title: str, first_verse: str, last_verse: str
    # ) -> str:
    #     # TODO Handle when there is no USFM requested.
    #     # If we're inside a UDB bridge, roll back to the beginning of it
    #     udb_first_verse = first_verse
    #     udb_first_verse_ok = False
    #     while not udb_first_verse_ok:
    #         try:
    #             _ = self._usfm_chunks["udb"][chapter][udb_first_verse]["usfm"]
    #             udb_first_verse_ok = True
    #         except KeyError:
    #             udb_first_verse_int = int(udb_first_verse) - 1
    #             if udb_first_verse_int <= 0:
    #                 break
    #             udb_first_verse = str(udb_first_verse_int)

    #     # TODO localization
    #     md = "### Unlocked Dynamic Bible\n\n[[udb://{}/{}/{}/{}/{}]]\n\n".format(
    #         self._lang_code,
    #         self._book_id,
    #         link_utils.pad(self._book_id, chapter),
    #         link_utils.pad(self._book_id, udb_first_verse),
    #         link_utils.pad(self._book_id, last_verse),
    #     )
    #     rc = "rc://{}/tn/help/{}/{}/{}".format(
    #         self._lang_code,
    #         self._book_id,
    #         link_utils.pad(self._book_id, chapter),
    #         link_utils.pad(self._book_id, first_verse),
    #     )
    #     anchor_id = "tn-{}-{}-{}".format(
    #         self._book_id,
    #         link_utils.pad(self._book_id, chapter),
    #         link_utils.pad(self._book_id, first_verse),
    #     )
    #     self._resource_data[rc] = {
    #         # self.resource_data[rc] = {
    #         "rc": rc,
    #         "id": anchor_id,
    #         "link": "#{}".format(anchor_id),
    #         "title": title,
    #     }
    #     self._my_rcs.append(rc)
    #     link_utils.get_resource_data_from_rc_links(
    #         self._lang_code,
    #         self._my_rcs,
    #         self._rc_references,
    #         self._resource_data,
    #         self._bad_links,
    #         self._working_dir,
    #         md,
    #         rc,
    #     )
    #     md += "\n\n"
    #     return md


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
        # FIXME All the work is done in _initialize_verses_html.
        # So these legacy methods are turned off for now. There are
        # likely bits of logic from these two functions that will find
        # their way back into the system later though (in a different
        # and improved form), e.g., linking.
        # self._get_tn_markdown()
        # self._transform_content()

        self._initialize_from_assets()
        self._initialize_verses_html()

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

    def _initialize_verses_html(self) -> None:
        """
        Find translation questions for the verses.
        """
        # Create the Markdown instance once and have it use our markdown
        # extensions.
        md = markdown.Markdown(
            extensions=[
                wikilink_preprocessor.WikiLinkExtension(),
                remove_section_preprocessor.RemoveSectionExtension(),
                # FIXME Decide how to handle translation word under
                # different contexts, e.g.: no TW requested.
                translation_word_link_preprocessor.TranslationWordLinkExtension(
                    lang_code={self.lang_code: "Language code for resource."}
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
            # intro_paths = glob("{}/*intro.md".format(chapter_dir))
            # intro_path = intro_paths[0] if intro_paths else None
            # intro_html = ""
            # if intro_path:
            #     with open(intro_path, "r", encoding="utf-8") as fin:
            #         intro_html = fin.read()
            #         # NOTE I am not sure the 'Links' section make
            #         # sense in the new interleaving design, so let's
            #         # remove it for now.
            #         intro_html = markdown_utils.remove_md_section(intro_html, "Links:")
            #         intro_html = md.convert(intro_html)
            # FIXME For some languages, TQ assets are stored in .txt files
            # rather of .md files. Handle this.
            verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
            verses_html: Dict[int, str] = {}
            for filepath in verse_paths:
                verse_num = int(pathlib.Path(filepath).stem)
                verse_content = ""
                with open(filepath, "r", encoding="utf-8") as fin2:
                    verse_content = fin2.read()
                    # NOTE I am not sure the 'Links' section make
                    # sense in the new interleaving design, so let's
                    # remove it for now.
                    # NOTE I don't think translation questions have a
                    # 'Links:' section.
                    # verse_content = markdown_utils.remove_md_section(
                    #     verse_content, "Links:"
                    # )
                    # FIXME We could just comment out the next line, i.e.,
                    # not convert Markdown to HTML yet. We could do
                    # the conversion in the assembly strategies
                    # instead and do it all at once for all Markdown
                    # content?
                    verse_content = md.convert(verse_content)
                verses_html[verse_num] = verse_content
            chapter_payload = model.TQChapterPayload(verses_html=verses_html)
            chapter_verses[chapter_num] = chapter_payload
        self._book_payload = model.TQBookPayload(chapters=chapter_verses)

    def get_verses_for_chapter(
        self, chapter_num: model.ChapterNum
    ) -> Dict[model.VerseNum, model.HtmlContent]:
        """
        Return the HTML for verses in chapter_num.
        """
        return self.book_payload.chapters[chapter_num].verses_html

    def format_tq_verse(
        self, chapter_num: model.ChapterNum, verse_num: model.VerseNum,
    ) -> List[model.HtmlContent]:
        """
        Build and return the content for the translation question for chapter
        chapter_num and verse verse_num.
        """
        tq_verse = self.get_verses_for_chapter(chapter_num)[verse_num]
        if not tq_verse:
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

    # def _get_tq_markdown(self) -> None:
    #     """Build tq markdown"""
    #     tq_md = '# Translation Questions\n<a id="tq-{}"/>\n\n'.format(self._book_id)
    #     title = "{} Translation Questions".format(self._book_title)
    #     tq_rc_link = "rc://{}/tq/help/{}".format(self._lang_code, self._book_id)
    #     anchor_id = "tq-{}".format(self._book_id)
    #     self._resource_data[tq_rc_link] = {
    #         "rc": tq_rc_link,
    #         "id": anchor_id,
    #         "link": "#{}".format(anchor_id),
    #         "title": title,
    #     }
    #     self._my_rcs.append(tq_rc_link)
    #     tq_book_dir = os.path.join(self._resource_dir, self._book_id)
    #     for chapter in sorted(os.listdir(tq_book_dir)):
    #         chapter_dir = os.path.join(tq_book_dir, chapter)
    #         chapter = chapter.lstrip("0")
    #         if os.path.isdir(chapter_dir) and re.match(r"^\d+$", chapter):
    #             id_tag = '<a id="tq-{}-{}"/>'.format(
    #                 self._book_id, link_utils.pad(self._book_id, chapter)
    #             )
    #             tq_md += "## {} {}\n{}\n\n".format(self._book_title, chapter, id_tag)
    #             # TODO localization
    #             title = "{} {} Translation Questions".format(self._book_title, chapter)
    #             tq_rc_link = "rc://{}/tq/help/{}/{}".format(
    #                 self._lang_code,
    #                 self._book_id,
    #                 link_utils.pad(self._book_id, chapter),
    #             )
    #             anchor_id = "tq-{}-{}".format(
    #                 self._book_id, link_utils.pad(self._book_id, chapter)
    #             )
    #             self._resource_data[tq_rc_link] = {
    #                 "rc": tq_rc_link,
    #                 "id": anchor_id,
    #                 "link": "#{0}".format(anchor_id),
    #                 "title": title,
    #             }
    #             self._my_rcs.append(tq_rc_link)
    #             for chunk in sorted(os.listdir(chapter_dir)):
    #                 chunk_file = os.path.join(chapter_dir, chunk)
    #                 first_verse = os.path.splitext(chunk)[0].lstrip("0")
    #                 if os.path.isfile(chunk_file) and re.match(r"^\d+$", first_verse):
    #                     tq_chapter_md = file_utils.read_file(chunk_file)
    #                     tq_chapter_md = markdown_utils.increase_headers(
    #                         tq_chapter_md, 2
    #                     )
    #                     tq_chapter_md = re.compile("^([^#\n].+)$", flags=re.M).sub(
    #                         r'\1 [<a href="#tn-{}-{}-{}">{}:{}</a>]'.format(
    #                             self._book_id,
    #                             link_utils.pad(self._book_id, chapter),
    #                             link_utils.pad(self._book_id, first_verse),
    #                             chapter,
    #                             first_verse,
    #                         ),
    #                         tq_chapter_md,
    #                     )
    #                     # TODO localization
    #                     title = "{} {}:{} Translation Questions".format(
    #                         self._book_title, chapter, first_verse
    #                     )
    #                     tq_rc_link = "rc://{}/tq/help/{}/{}/{}".format(
    #                         self._lang_code,
    #                         self._book_id,
    #                         link_utils.pad(self._book_id, chapter),
    #                         link_utils.pad(self._book_id, first_verse),
    #                     )
    #                     anchor_id = "tq-{}-{}-{}".format(
    #                         self._book_id,
    #                         link_utils.pad(self._book_id, chapter),
    #                         link_utils.pad(self._book_id, first_verse),
    #                     )
    #                     self._resource_data[tq_rc_link] = {
    #                         "rc": tq_rc_link,
    #                         "id": anchor_id,
    #                         "link": "#{}".format(anchor_id),
    #                         "title": title,
    #                     }
    #                     self._my_rcs.append(tq_rc_link)
    #                     link_utils.get_resource_data_from_rc_links(
    #                         self._lang_code,
    #                         self._my_rcs,
    #                         self._rc_references,
    #                         self._resource_data,
    #                         self._bad_links,
    #                         self._working_dir,
    #                         tq_chapter_md,
    #                         tq_rc_link,
    #                     )
    #                     tq_chapter_md += "\n\n"
    #                     tq_md += tq_chapter_md
    #     logger.debug("tq_md is {0}".format(tq_md))
    #     self._content = tq_md
    #     # return tq_md


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
        # FIXME All the work is done in _initialize_verses_html.
        # So these legacy methods are turned off for now. There are
        # likely bits of logic from these two functions that will find
        # their way back into the system later though (in a different
        # and improved form), e.g., linking.
        # self._get_tw_markdown()
        # self._transform_content()

        self._initialize_from_assets()
        self._initialize_verses_html()

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

    # FIXME This logic may need to happen inside the
    # TranslationWordLinkExtension rather than here.
    def _get_translation_word_filepaths(self) -> FrozenSet[str]:
        """
        Get the file paths to the translation word files for the
        TWResource instance.
        """
        filepaths = glob("{}/bible/kt/*.md".format(self.resource_dir))
        filepaths.extend(glob("{}/bible/names/*.md".format(self.resource_dir)))
        filepaths.extend(glob("{}/bible/other/*.md".format(self.resource_dir)))
        # Parameter to Markdown extension must be hashable. FrozenSet
        # is hashable.
        return frozenset(filepaths)

    # FIXME Refactor to make DRY
    def _initialize_verses_html(self) -> None:
        """
        Find translation words for the verses.
        """
        # Create the Markdown instance once and have it use our markdown
        # extensions.
        # FIXME In the case of translation words we may want to wait
        # until assembly to do conversion from Markdown to HTML rather
        # than doing it here.
        filepaths = self._get_translation_word_filepaths()
        # FIXME I could avoid this instantiation and instead store the
        # verse content in Markdown form until assembly strategy time.
        md = markdown.Markdown(
            extensions=[
                wikilink_preprocessor.WikiLinkExtension(),
                remove_section_preprocessor.RemoveSectionExtension(),
                # FIXME Decide how to handle translation word under
                # different contexts, e.g.: no TW requested.
                translation_word_link_preprocessor.TranslationWordLinkExtension(
                    lang_code={self.lang_code: "Language code for resource."},
                    filepaths={
                        filepaths: "Translation word markdown file paths for resource."
                    },
                ),
            ]
        )

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
                # TODO We have to find out how all display words are
                # displayed by looking at the legacy PDF. Do they
                # display translation_word words followed by names and then other?
                # The localized word is the very first word in the
                # first line right after the Markdown 1st level
                # header, i.e., right after '#'.
                # NOTE Translation words are bidirectional. By that I
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
                # FIXME I could avoid converting to HTML now and do it
                # later in assembly strategy.
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
                # them to make the inter-document linking work (for the filenames) for
                # 'See also' section references.
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
        # translation_words_dict: Dict[model.BaseFilename, model.TWNameContentPair],
        chapter_num: model.ChapterNum,
        verse_num: model.VerseNum,
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
                # FIXME Perhaps we can later simplify to use one data structure instead
                # of both uses and tw_resource.language_payload.uses.
                if key in self.language_payload.uses:
                    self.language_payload.uses[key].append(use)
                else:
                    self.language_payload.uses[key] = [use]

        if uses:
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("translation_words").format(
                        chapter_num, verse_num
                    )
                )
            )
            html.append(config.get_html_format_string("unordered_list_begin"))
            # Append word links.
            uses_list_items = [
                config.get_html_format_string("translation_word_list_item").format(
                    self.lang_code, use.base_filename, use.localized_word,
                )
                for use in uses
            ]
            html.append(model.HtmlContent("\n".join(uses_list_items)))
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
        html.append(config.get_html_format_string("translation_words_section"))

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

            # if base_filename in tw_resource.language_payload.uses:

            # Make linking work.
            tw_name_content_pair.content = model.HtmlContent(
                tw_name_content_pair.content.replace(
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

    # FIXME Remove
    # @log_on_start(
    #     logging.INFO, "Processing Translation Words Markdown...", logger=logger
    # )
    # def get_content(self) -> None:
    #     """See docstring in superclass."""
    #     self._get_tw_markdown()
    #     self._transform_content()

    # def _get_tw_markdown(self) -> None:
    #     # From entrypoint.sh in Interleaved_Resource_Generator, i.e.,
    #     # container.
    #     # Combine OT and NT tW files into single refs file, skipping header row of NT
    #     # cp         /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_OT_PDF.txt    /working/tn-temp/tw_refs.csv
    #     # tail -n +2 /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_NT_PDF.txt >> /working/tn-temp/tw_refs.csv

    #     # TODO localization
    #     tw_md = '<a id="tw-{}"/>\n# Translation Words\n\n'.format(self._book_id)
    #     # tw_md = '<a id="tw-{0}"/>\n# Translation Words\n\n'.format(self.book_id)
    #     sorted_rcs = sorted(
    #         self._my_rcs, key=lambda k: self._resource_data[k]["title"].lower()
    #     )
    #     for rc in sorted_rcs:
    #         if "/tw/" not in rc:
    #             continue
    #         if self._resource_data[rc]["text"]:
    #             md = self._resource_data[rc]["text"]
    #         else:
    #             md = ""
    #         id_tag = '<a id="{}"/>'.format(self._resource_data[rc]["id"])
    #         md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{}\n".format(id_tag), md, 1)
    #         md = markdown_utils.increase_headers(md)
    #         uses = link_utils.get_uses(self._rc_references, rc)
    #         if uses == "":
    #             continue
    #         md += uses
    #         md += "\n\n"
    #         tw_md += md
    #     # TODO localization
    #     tw_md = markdown_utils.remove_md_section(tw_md, "Bible References")
    #     # TODO localization
    #     tw_md = markdown_utils.remove_md_section(
    #         tw_md, "Examples from the Bible stories"
    #     )

    #     logger.debug("tw_md is {}".format(tw_md))
    #     self._content = tw_md
    #     # return tw_md


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
    # FIXME Why should resources care about assembly strategies?
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
        # conxider not using the url.rpartition(os.path.sep)[2]. Instead let's
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
            # with the network at this point.
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
        # FIXME Update resource_dir. If we make this change, it will likely mean we
        # can update the glob patterns for resource asset files.
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
