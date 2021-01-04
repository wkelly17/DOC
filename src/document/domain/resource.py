from __future__ import annotations  # https://www.python.org/dev/peps/pep-0563/

import abc
import logging
import logging.config
import os
import pathlib
import re
import subprocess
from glob import glob
from typing import Any, Dict, Generator, List, Optional, Tuple

import bs4
import icontract
import jinja2
import markdown
import pydantic
import yaml
from usfm_tools.transform import UsfmTransform

from document import config
from document.domain import bible_books, model, resource_lookup
from document.utils import file_utils, link_utils, markdown_utils, url_utils

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


class AbstractResource(abc.ABC):
    """
    Superclass/interface for resource. Provides a simple API for
    locating, getting and initializing a resource's assets.
    """

    @abc.abstractmethod
    def find_location(self) -> None:
        """
        Find the remote location where a the resource's file assets
        may be found.

        Subclasses override this method.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_files(self) -> None:
        """
        Using the resource's remote location, download the resource's file
        assets to disk.

        Subclasses override this method.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def initialize_assets(self) -> None:
        """
        Find and load resource files that were downloaded to disk.

        Subclasses override.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_content(self) -> None:
        """
        Initialize resource with content found in resource's files.

        Subclasses override.
        """
        raise NotImplementedError


class Resource(AbstractResource):
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

        # FIXME Next three instance vars could be properties instead
        self._lang_code: str = resource_request.lang_code
        self._resource_type: str = resource_request.resource_type
        self._resource_code: str = resource_request.resource_code

        self._resource_dir: str = os.path.join(
            self._working_dir, "{}_{}".format(self._lang_code, self._resource_type)
        )

        self._resource_filename: str = "{}_{}_{}".format(
            self._lang_code, self._resource_type, self._resource_code
        )
        self._book_id: str = self._resource_code
        # FIXME Could get KeyError
        self._book_title = bible_books.BOOK_NAMES[self._resource_code]
        self._book_number = bible_books.BOOK_NUMBERS[self._book_id]

        self._resource_url: Optional[str] = None
        self._resource_source: str
        self._resource_jsonpath: Optional[str] = None

        self._manifest: Manifest
        # Content related instance vars
        self._content_files: List[str]
        self._content: str
        # Link related
        self._bad_links: dict = {}
        self._resource_data: dict = {}
        self._my_rcs: List = []
        self._rc_references: dict = {}

        # Verse level content containers
        self._verses_html: List[str]
        # self._verses_html_generator: Generator

    # def _get_verses_html_generator(self) -> Generator:
    #     for i in range(len(self._verses_html) - 1):
    #         yield self._verses_html[i]

    def __str__(self) -> str:
        return "Resource(lang_code: {}, resource_type: {}, resource_code: {})".format(
            self._lang_code, self._resource_type, self._resource_code
        )

    def __repr__(self) -> str:
        return "Resource(lang_code: {}, resource_type: {}, resource_code: {})".format(
            self._lang_code, self._resource_type, self._resource_code
        )

    @property
    def resource_dir_path(self) -> pathlib.Path:
        return pathlib.Path(self._resource_dir)

    def is_found(self) -> bool:
        "Return true if resource's URL location was found."
        return self._resource_url is not None

    def find_location(self) -> None:
        """
        Find the remote location where a the resource's file assets
        may be found.

        Subclasses override this method.
        """
        pass

    def get_files(self) -> None:
        """
        Using the resource's remote location, download the resource's file
        assets to disk.
        """
        _ = ResourceProvisioner(self)()

    # FIXME This should have a better name, e.g., initialize_assets or
    # load_assets or ?
    def initialize_assets(self) -> None:
        """
        Find and load resource files that were downloaded to disk.

        Subclasses override.
        """
        pass

    def get_content(self) -> None:
        """
        Initialize resource with content found in resource's files.

        Subclasses override.
        """
        pass

    ## FIXME Utiity type methods that could possibly be put in a mixin
    ## class and then inherited by each resource subclass, e.g., by
    ## USFMResource, TNResource, etc.:

    # @icontract.require(lambda self: self._resource_source is not None)
    # def _is_usfm(self) -> bool:
    #     """ Return true if _resource_source is equal to 'usfm'. """
    #     return self._resource_source == config.USFM

    # FIXME I am using the bs4 bits of this elsewhere now to decompose
    # the HTNL back into verses (but don't have it worked out totally
    # yet).
    # def _get_chunk_html(self, resource_str: str, chapter: str, verse: str) -> str:
    #     # FIXME Do we want a temp dir here? This is where the USFM
    #     # file chunk requested, by chapter and verse, will be written
    #     # and subsequently read from.
    #     # Build a path where we'll write the USFM chunk into a file
    #     path = tempfile.mkdtemp(
    #         dir=self._working_dir,
    #         prefix="usfm-{}-{}-{}-{}-{}_".format(
    #             self._lang_code,
    #             resource_str,
    #             self._book_id,
    #             chapter,
    #             verse
    #             # self._lang_code, resource, self.book_id, chapter, verse
    #         ),
    #     )
    #     logger.debug(
    #         "path, i.e., location of USFM chunk file to write: {}".format(path)
    #     )
    #     filename_base = "{}-{}-{}-{}".format(
    #         resource_str, self._book_id, chapter, verse
    #     )
    #     # filename_base = "{0}-{1}-{2}-{3}".format(resource, self.book_id, chapter, verse)
    #     # Get the chunk for chapter and verse
    #     try:
    #         chunk = self._usfm_chunks[resource_str][chapter][verse]["usfm"]
    #         # chunk = self.usfm_chunks[resource_str][chapter][verse]["usfm"]
    #     except KeyError:
    #         chunk = ""
    #     # Get the USFM header portion
    #     usfm = self._usfm_chunks[resource_str]["header"]
    #     # If a chapter markder is not present in the chunk, then add one
    #     if "\\c" not in chunk:
    #         usfm += "\n\n\\c {0}\n".format(chapter)
    #     # Add the chapter chunk to the header
    #     usfm += chunk
    #     # FIXME Use instance vars instead?
    #     # FIXME Do we want to use filename_base?
    #     # Write the chapter USFM chunk to file
    #     write_file(os.path.join(path, filename_base + ".usfm"), usfm)
    #     # FIXME Is this what we'll use to build the USFM resource
    #     # content?
    #     # Convert the USFM to HTML
    #     UsfmTransform.buildSingleHtml(path, path, filename_base)
    #     # Read the HTML
    #     html = read_file(os.path.join(path, filename_base + ".html"))
    #     # Get rid of the temp directory
    #     shutil.rmtree(path, ignore_errors=True)
    #     # Get a parser on the HTML
    #     soup = bs4.BeautifulSoup(html, "html.parser")
    #     # Find the h1 element
    #     header = soup.find("h1")
    #     if header:  # h1 element exists
    #         # Delete the h1 element
    #         header.decompose()
    #     # Find the h2 element
    #     chapter_element: Union[
    #         bs4.element.Tag, bs4.element.NavigableString
    #     ] = soup.find("h2")
    #     if chapter_element:  # h2 element exists
    #         # Delete the h2 element
    #         chapter_element.decompose()
    #     # Get the HTML body
    #     html = "".join(["%s" % x for x in soup.body.contents])
    #     return html


class USFMResource(Resource):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._usfm_chunks: dict = {}
        # self._usfm_verses_generator: Generator
        self._verses_html: List[str]
        # self._verses_html_generator: Generator

    @icontract.ensure(lambda self: self._resource_url is not None)
    def find_location(self) -> None:
        """ Find the URL where the resource's assets are located. """
        # FIXME For better flexibility, the lookup class could be
        # looked up in a table, i.e., dict, that has the key as self
        # classname and the value as the lookup subclass.
        lookup_svc = resource_lookup.USFMResourceJsonLookup()
        resource_lookup_dto: model.ResourceLookupDto = lookup_svc.lookup(self)
        self._resource_url = resource_lookup_dto.url
        self._resource_source = resource_lookup_dto.source
        self._resource_jsonpath = resource_lookup_dto.jsonpath
        logger.debug("self._resource_url: {} for {}".format(self._resource_url, self))

    def initialize_assets(self) -> None:
        """
        Explore the resource's downloaded files to initialize file
        structure related properties.
        """
        self._manifest = Manifest(self)

        usfm_content_files = glob("{}**/*.usfm".format(self._resource_dir))
        # USFM files sometimes have txt suffix
        txt_content_files = glob("{}**/*.txt".format(self._resource_dir))

        # logger.debug("usfm_content_files: {}".format(list(usfm_content_files)))

        # NOTE We don't need a manifest file to find resource assets
        # on disk as fuzzy search does that for us. We just filter
        # down the list found with fuzzy search to only include those
        # that match the resource code, i.e., book, being requested.
        # This frees us from the brittleness of expecting asset files
        # to be named a certain way for all languages since we are
        # able to just check that the asset file has the resource code
        # as a substring.
        # If desired, in the case where a manifest must be consulted
        # to determine if the file is considered usable, i.e.,
        # 'complete' or 'finished', that can also be done by compared
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

        logger.debug(
            "self._content_files for {}: {}".format(
                self._resource_code, self._content_files,
            )
        )

    @icontract.require(lambda self: self._content_files is not None)
    @icontract.ensure(lambda self: self._resource_filename is not None)
    def get_content(self) -> None:
        self._get_usfm_chunks()

        # FIXME Experiment with content derived from
        # _get_usfm_verses_generator, use breakpoint to do so. Also,
        # instead of using a generator you could just get the verses
        # directly since there is no real advantage to using a
        # generator as you are creating the generator from a list that
        # is already in memory nested in the _usfm_chunks dictionary.
        # The idea would be to see if we can just get the verse
        # content sans USFM elements and then maybe stuff it into
        # markdown jinja1 templates or something.
        # raise "Work on this homey!!!"

        # logger.debug("self._content_files: {}".format(self._content_files))

        if self._content_files is not None:
            # FIXME Could try different parser here.
            # Create the USFM to HTML and store in file.
            UsfmTransform.buildSingleHtmlFromFiles(
                [pathlib.Path(file) for file in self._content_files],
                self._output_dir,
                self._resource_filename,
            )
            # Read the HTML file into _content.
            html_file = "{}.html".format(
                os.path.join(self._output_dir, self._resource_filename)
            )
            self._content = file_utils.read_file(html_file)

            logger.debug(
                "html content in self._content in {}: {}".format(
                    html_file, self._content
                )
            )

            self._initialize_verses_html()
            logger.debug("self._verses_html from bs4: {}".format(self._verses_html))

            logger.debug("self._bad_links: {}".format(self._bad_links))

    @icontract.require(lambda self: self._content is not None)
    def _initialize_verses_html(self) -> None:
        """
        Break apart the HTML content into HTML verse chunks, augment
        HTML output with additional HTML elements and store in
        _verses_html.
        """
        parser = bs4.BeautifulSoup(self._content, "html.parser")
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "verse"}
        )
        # Add enclosing paragraph to each verse since they will be
        # interleaved against translation notes, etc..
        self._verses_html = ["<p>" + str(verse) + "</p>" for verse in verses_html]

    # FIXME Handle git based usfm with resources.json file and .txt usfm
    # file suffixes.
    @icontract.require(lambda self: self._content_files is not None)
    @icontract.require(lambda self: self._resource_filename is not None)
    @icontract.require(lambda self: self._resource_dir is not None)
    @icontract.ensure(lambda self: self._usfm_chunks is not None)
    def _get_usfm_chunks(self) -> None:
        """
        Read the USFM file contents requested for resource code and
        break it into verse chunks.
        """
        book_chunks: dict = {}
        logger.debug("self._resource_filename: {}".format(self._resource_filename))

        usfm_file = self._content_files[0]
        # FIXME Should be in try block
        usfm_file_content = file_utils.read_file(usfm_file, "utf-8",)

        # FIXME Not sure I like this LBYL style here. Exceptions
        # should actually be the exceptional case here, so this costs
        # performance by checking.
        if usfm_file_content is not None:
            chunks = re.compile(r"\\s5\s*\n*").split(usfm_file_content)
        else:
            return

        # Break chunks into verses
        chunks_per_verse = []
        for chunk in chunks:
            pending_chunk = None
            for line in chunk.splitlines(True):
                # If this is a new verse and there's a pending chunk,
                # finish it and start a new one.
                # logger.debug("pending_chunk: {}".format(pending_chunk))
                if re.search(r"\\v", line) and pending_chunk:
                    chunks_per_verse.append(pending_chunk)
                    pending_chunk = None
                if pending_chunk:
                    pending_chunk = pending_chunk + line
                else:
                    pending_chunk = line

            # If there's a pending chunk, finish it.
            if pending_chunk:
                chunks_per_verse.append(pending_chunk)
        chunks = chunks_per_verse

        header = chunks[0]
        book_chunks["header"] = header
        for chunk in chunks[1:]:
            if not chunk.strip():
                continue
            chapter_search = re.search(
                r"\\c[\u00A0\s](\d+)", chunk
            )  # \u00A0 no break space
            if chapter_search:
                chapter = chapter_search.group(1)
            verses = re.findall(r"\\v[\u00A0\s](\d+)", chunk)
            if not verses:
                continue
            first_verse = verses[0]
            last_verse = verses[-1]
            if chapter not in book_chunks:
                book_chunks[chapter] = {"chunks": []}
            # FIXME first_verse, last_verse, and verses equal the same
            # number, e.g., all 1 or all 2, etc.. They don't seem to encode
            # meaningfully differentiated data that would be useful.
            # first_verse and last_verse are used in
            # TNResource so as to imply that they are expected to
            # represent a range wider than one verse, but as far as
            # execution of the algorithm here, I haven't seen a case where
            # they are ever found to be different.
            # I may remove them later if no ranges ever actually
            # occur - something that remains to be learned. chunk is
            # the verse content itself and of course is
            # necessary.
            data = {
                "usfm": chunk,
                "first_verse": first_verse,
                "last_verse": last_verse,
                "verses": verses,
            }
            book_chunks[chapter][first_verse] = data
            book_chunks[chapter]["chunks"].append(data)
        self._usfm_chunks = book_chunks

    # NOTE Exploratory
    @icontract.require(lambda self: self._usfm_chunks is not None)
    @icontract.require(lambda self: self._usfm_chunks["1"]["chunks"] is not None)
    def _get_usfm_verses_generator(self) -> Generator:
        """
        Return a generator over the raw USFM verses. Might be useful
        for interleaved assembly of the document at the verse level.
        """
        for i in range(len(self._usfm_chunks["1"]["chunks"]) - 1):
            yield self._usfm_chunks["1"]["chunks"][i]

    # def _get_verses_html_generator(self) -> Generator:
    #     """
    #     Return a generator over the USFM converted to HTML verse
    #     spans. Might be useful for interleaved assembly of the
    #     document at the verse level.
    #     """
    #     for i in range(len(self._verses_html) - 1):
    #         yield str(self._verses_html[i])


class TResource(Resource):
    """ Provide methods common to all subclasses of TResource. """

    def find_location(self) -> None:
        """ Find the URL where the resource's assets are located. """
        # FIXME For better flexibility, the lookup class could be
        # looked up in a table, i.e., dict, that has the key as self
        # classname and the value as the lookup subclass.
        lookup_svc = resource_lookup.TResourceJsonLookup()
        resource_lookup_dto: model.ResourceLookupDto = lookup_svc.lookup(self)
        self._resource_url = resource_lookup_dto.url
        self._resource_source = resource_lookup_dto.source
        self._resource_jsonpath = resource_lookup_dto.jsonpath
        logger.debug("self._resource_url: {} for {}".format(self._resource_url, self))

    def initialize_assets(self) -> None:
        """ Programmatically discover the manifest and content files. """
        self._manifest = Manifest(self)

        logger.debug("self._resource_dir: {}".format(self._resource_dir))
        # Get the content files
        markdown_files = glob(
            "{}/*{}/**/*.md".format(self._resource_dir, self._resource_code)
        )
        # logger.debug("markdown_files: {}".format(markdown_files))
        markdown_content_files = list(
            filter(
                lambda x: str(pathlib.Path(x).stem).lower()
                not in config.get_markdown_doc_file_names(),
                markdown_files,
            )
        )
        txt_files = glob(
            "{}/*{}/**/*.txt".format(self._resource_dir, self._resource_code)
        )
        # logger.debug("txt_files: {}".format(txt_files))
        txt_content_files = list(
            filter(
                lambda txt_file: str(pathlib.Path(txt_file).stem).lower()
                not in config.get_markdown_doc_file_names(),
                txt_files,
            )
        )

        if markdown_content_files:
            self._content_files = list(
                filter(
                    lambda markdown_file: self._resource_code.lower()
                    in markdown_file.lower(),
                    markdown_files,
                )
            )
        if txt_content_files:
            self._content_files = list(
                filter(
                    lambda txt_file: self._resource_code.lower() in txt_file.lower(),
                    txt_files,
                )
            )

        self._initialize_verses_html()

        # logger.debug(
        #     "markdown_content_files: {}, txt_content_files: {}".format(
        #         markdown_content_files, txt_content_files,
        #     )
        # )
        logger.debug(
            "self._content_files for {}: {}".format(
                self._resource_code, self._content_files,
            )
        )

    def _initialize_verses_html(self) -> None:

        # FIXME This whole method could be rewritten. We want to find
        # book intro, chapter intros, and then the verses themselves.
        # We can do all that with globbing as below rather than the
        # laborious way it is done elsewhere in this codebase.
        verse_files = sorted(
            glob(
                "{}/*{}/*[0-9][0-9]/*[0-9][0-9].md".format(
                    self._resource_dir, self._resource_code
                )
            )
        )

        self._verses_html = []
        for filepath in verse_files:
            verse_content = ""
            with open(filepath, "r") as fin:
                verse_content = fin.read()
            self._verses_html.append(markdown.markdown(verse_content))
        # self._verses_html_generator = self._get_verses_html_generator()
        logger.debug("self._verses_html: {}".format(self._verses_html))

    @icontract.require(lambda self: self._content is not None)
    def _convert_md2html(self) -> None:
        """ Convert a resource's Markdown to HTML. """
        # assert self._content is not None, "self._content cannot be None here."
        # FIXME Perhaps we can manipulate resource links, rc://, by
        # writing our own parser extension.
        self._content = markdown.markdown(self._content)


class TNResource(TResource):
    def _get_template(self, template_lookup_key: str, dto: pydantic.BaseModel) -> str:
        """
        Instantiate template with dto BaseModel instance. Return
        instantiated template as string.
        """
        # FIXME Maybe use jinja2.PackageLoader here instead: https://github.com/tfbf/usfm/blob/master/usfm/html.py
        with open(
            config.get_markdown_template_path(template_lookup_key), "r"
        ) as filepath:
            md_template = filepath.read()
        # FIXME Handle exceptions
        md_environment = jinja2.Environment().from_string(md_template)
        return md_environment.render(data=dto)

    def get_content(self) -> None:
        logger.info("Processing Translation Notes Markdown...")
        self._get_tn_markdown()
        # FIXME
        self._content = link_utils.replace_rc_links(
            self._my_rcs, self._resource_data, self._content
        )
        self._content = link_utils.fix_links(self._content)
        logger.info("Converting MD to HTML...")
        self._convert_md2html()

    # FIXME Should we change to function w no non-local side-effects
    # and move to markdown_utils.py?
    @icontract.require(lambda self: self._resource_code is not None)
    def _get_tn_markdown(self) -> None:
        tn_md = ""
        book_dir: str = self._get_book_dir()
        logger.debug("book_dir: {}".format(book_dir))

        if not os.path.isdir(book_dir):
            return

        # FIXME We should be using templates and then inserting values
        # not building markdown imperatively.
        # TODO Might need localization
        # tn_md = '# Translation Notes\n<a id="tn-{}"/>\n\n'.format(self._book_id)
        # NOTE This is now in the book intro template
        # tn_md = '# Translation Notes\n<a id="tn-{}"/>\n\n'.format(self._resource_code)

        book_has_intro, book_intro_template_dto = self._initialize_tn_book_intro()

        book_intro_template: str = self._get_template(
            "book_intro", book_intro_template_dto
        )

        # tn_md += tn_md_intro
        tn_md += book_intro_template

        for chapter in sorted(os.listdir(book_dir)):
            chapter_dir = os.path.join(book_dir, chapter)
            logger.debug("chapter_dir: {}".format(chapter_dir))
            # FIXME lang_code ml, for instance, doesn't lead with a digit, but
            # with ml_tn_*, e.g., ml_tn_57-TIT.tsv
            chapter = chapter.lstrip("0")
            # logger.debug("chapter: {}".format(chapter))
            if os.path.isdir(chapter_dir) and re.match(r"^\d+$", chapter):
                # logger.debug("chapter_dir, {}, exists".format(chapter_dir))
                chapter_has_intro, tn_md_temp = self._initialize_tn_chapter_intro(
                    chapter_dir, chapter
                )
                # Get all the Markdown files that start with a digit
                # and end with suffix md.
                chunk_files = sorted(glob(os.path.join(chapter_dir, "[0-9]*.md")))
                logger.debug("chunk_files: {}".format(chunk_files))
                for _, chunk_file in enumerate(chunk_files):
                    (
                        first_verse,
                        last_verse,
                        title,
                        md,
                    ) = link_utils.initialize_tn_chapter_files(
                        self._book_id,
                        self._book_title,
                        self._lang_code,
                        chunk_file,
                        chapter,
                    )

                    anchors = ""
                    pre_md = ""
                    # FIXME I don't think it should be fetching USFM
                    # stuff here in this method under the new design.
                    # _initialize_tn_chapter_verse_links now takes a
                    # first argument of a USFMResource instance which
                    # will provide the _usfm_chunks.
                    # if bool(self._usfm_chunks):
                    #     # Create links to each chapter
                    #     anchors += link_utils.initialize_tn_chapter_verse_links(
                    #         chapter, first_verse
                    #     )
                    #     pre_md = "\n## {}\n{}\n\n".format(title, anchors)
                    #     # TODO localization
                    #     pre_md += "### Unlocked Literal Bible\n\n[[ulb://{}/{}/{}/{}/{}]]\n\n".format(
                    #         self._lang_code,
                    #         self._book_id,
                    #         self._pad(chapter),
                    #         self._pad(first_verse),
                    #         self._pad(last_verse),
                    #     )
                    # TODO localization
                    pre_md += "### Translation Notes\n"
                    md = "{}\n{}\n\n".format(pre_md, md)

                    # FIXME Handle case where the user doesn't request tw resource.
                    # We don't want conditionals protecting execution
                    # of tw related code, but that is what we are
                    # doing for now until the code is refactored
                    # toward a better design. Just making this work
                    # with legacy for the moment.
                    # TODO This needs to be moved to a different logic
                    # path.

                    # FIXME This should be moved to TWResource. Note
                    # that it may be necessary to compare what
                    # _initialize_tn_translation_words does compared
                    # to what _get_tw_markdown does to see if they are
                    # redundant.
                    # tw_md = self._initialize_tn_translation_words(chapter, first_verse)
                    # md = "{}\n{}\n\n".format(md, tw_md)

                    # FIXME This belongs in USFMResource or in a new
                    # UDBResource.
                    # NOTE For now, I could guard this with a
                    # conditional that checks if UDB exists.
                    # NOTE The idea of this function assumes that UDB
                    # exists every time.
                    # NOTE For now commenting this out to see how far
                    # we get without it.

                    # md += self._initialize_tn_udb(
                    #     chapter, title, first_verse, last_verse
                    # )

                    tn_md += md

                    links = link_utils.initialize_tn_links(
                        self._lang_code,
                        self._book_id,
                        book_has_intro,
                        chapter_has_intro,
                        chapter,
                    )
                    tn_md += links + "\n\n"
            else:
                logger.debug(
                    "chapter_dir: {}, chapter: {}".format(chapter_dir, chapter)
                )

        self._content = tn_md

    # FIXME I think this code can probably be greatly simplified,
    # moved to _get_tn_markdown and then removed.
    # FIXME Should we change to function w no non-local side-effects
    # and move to markdown_utils.py?
    @icontract.require(lambda self: self._resource_dir is not None)
    @icontract.require(lambda self: self._lang_code is not None)
    @icontract.require(lambda self: self._resource_type is not None)
    def _get_book_dir(self) -> str:
        """ Given the lang_code, resource_type, and resource_dir,
        generate the book directory. """
        filepath: str = os.path.join(
            self._resource_dir, "{}_{}".format(self._lang_code, self._resource_type)
        )
        # logger.debug("self._lang_code: {}".format(self._lang_code))
        # logger.debug("self._resource_type: {}".format(self._resource_type))
        # logger.debug("self._resource_dir: {}".format(self._resource_dir))
        # logger.debug("filepath: {}".format(filepath))
        if os.path.isdir(filepath):
            book_dir = filepath
        else:  # git repo case
            book_dir = os.path.join(self._resource_dir, self._resource_code)
        return book_dir

    def _initialize_tn_book_intro(self) -> Tuple[bool, model.BookIntroTemplateDto]:
        book_intro_files: List = list(
            filter(
                lambda x: os.path.join("front", "intro") in x.lower(),
                self._content_files,
            )
        )
        logger.debug("book_intro_files[0]: {}".format(book_intro_files[0]))
        book_has_intro = os.path.isfile(book_intro_files[0])
        # FIXME Need exception handler, or, just use: with
        # open(book_intro_files[0], "r") as f:
        book_intro_content: str = file_utils.read_file(book_intro_files[0])
        title: str = markdown_utils.get_first_header(book_intro_content)
        book_intro_id_tag: str = '<a id="tn-{}-front-intro"/>'.format(self._book_id)
        book_intro_anchor_id: str = "tn-{}-front-intro".format(self._book_id)
        book_intro_rc: str = "rc://{}/tn/help/{}/front/intro".format(
            self._lang_code, self._book_id
        )
        data = model.BookIntroTemplateDto(
            book_id=self._book_id,
            content=book_intro_content,
            id_tag=book_intro_id_tag,
            anchor_id=book_intro_anchor_id,
        )

        # FIXME Begin side-effecting
        self._resource_data[book_intro_rc] = {
            "rc": book_intro_rc,
            "id": book_intro_anchor_id,
            "link": "#{}".format(book_intro_anchor_id),
            "title": title,
        }
        self._my_rcs.append(book_intro_rc)
        link_utils.get_resource_data_from_rc_links(
            self._lang_code,
            self._my_rcs,
            self._rc_references,
            self._resource_data,
            self._bad_links,
            self._working_dir,
            book_intro_content,
            book_intro_rc,
        )

        # Old code that new code above replaces:
        # intro_file = os.path.join(book_dir, "front", "intro.md")
        # book_has_intro = os.path.isfile(intro_file)
        # md = ""
        # if book_has_intro:
        #     md = file_utils.read_file(intro_file)
        #     title = markdown_utils.get_first_header(md)
        #     md = link_utils.fix_tn_links(self._lang_code, self._book_id, md, "intro")
        #     md = markdown_utils.increase_headers(md)
        #     # bring headers of 5 or more #'s down 1
        #     md = markdown_utils.decrease_headers(md, 5)
        #     id_tag = '<a id="tn-{}-front-intro"/>'.format(self._book_id)
        #     md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{}\n".format(id_tag), md, 1)
        #     # Create placeholder link
        #     rc = "rc://{}/tn/help/{}/front/intro".format(self._lang_code, self._book_id)
        #     anchor_id = "tn-{}-front-intro".format(self._book_id)
        #     self._resource_data[rc] = {
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
        return (book_has_intro, data)

    def _initialize_tn_chapter_intro(
        self, chapter_dir: str, chapter: str
    ) -> Tuple[bool, str]:
        intro_file = os.path.join(chapter_dir, "intro.md")
        chapter_has_intro = os.path.isfile(intro_file)
        if chapter_has_intro:
            # logger.info("chapter has intro")
            # FIXME Handle exceptions
            md = file_utils.read_file(intro_file)
            title = markdown_utils.get_first_header(md)
            md = link_utils.fix_tn_links(self._lang_code, self._book_id, md, chapter)
            md = markdown_utils.increase_headers(md)
            md = markdown_utils.decrease_headers(
                md, 5, 2
            )  # bring headers of 5 or more #'s down 2
            id_tag = '<a id="tn-{}-{}-intro"/>'.format(
                self._book_id, link_utils.pad(self._book_id, chapter)
            )
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{}\n".format(id_tag), md, 1)
            # Create placeholder link
            rc = "rc://{}/tn/help/{}/{}/intro".format(
                self._lang_code, self._book_id, link_utils.pad(self._book_id, chapter),
            )
            anchor_id = "tn-{}-{}-intro".format(
                self._book_id, link_utils.pad(self._book_id, chapter)
            )
            self._resource_data[rc] = {
                "rc": rc,
                "id": anchor_id,
                "link": "#{}".format(anchor_id),
                "title": title,
            }
            self._my_rcs.append(rc)
            link_utils.get_resource_data_from_rc_links(
                self._lang_code,
                self._my_rcs,
                self._rc_references,
                self._resource_data,
                self._bad_links,
                self._working_dir,
                md,
                rc,
            )
            md += "\n\n"
            return (chapter_has_intro, md)
        else:
            logger.info("chapter has no intro")
            return (chapter_has_intro, "")

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


class TWResource(TResource):
    def get_content(self) -> None:
        logger.info("Processing Translation Words Markdown...")
        self._get_tw_markdown()
        # FIXME
        self._content = link_utils.replace_rc_links(
            self._my_rcs, self._resource_data, self._content
        )
        self._content = link_utils.fix_links(self._content)
        logger.info("Converting MD to HTML...")
        self._convert_md2html()
        logger.debug("self._bad_links: {}".format(self._bad_links))

    # FIXME Should this be a function with no side effects and put in
    # markdown_utils module?
    # def _get_tw_markdown(self) -> str:
    def _get_tw_markdown(self) -> None:

        # From entrypoint.sh in Interleaved_Resource_Generator, i.e.,
        # container.
        # Combine OT and NT tW files into single refs file, skipping header row of NT
        # cp         /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_OT_PDF.txt    /working/tn-temp/tw_refs.csv
        # tail -n +2 /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_NT_PDF.txt >> /working/tn-temp/tw_refs.csv

        # TODO localization
        tw_md = '<a id="tw-{}"/>\n# Translation Words\n\n'.format(self._book_id)
        # tw_md = '<a id="tw-{0}"/>\n# Translation Words\n\n'.format(self.book_id)
        sorted_rcs = sorted(
            self._my_rcs,
            key=lambda k: self._resource_data[k]["title"].lower()
            # self.my_rcs, key=lambda k: self.resource_data[k]["title"].lower()
        )
        for rc in sorted_rcs:
            if "/tw/" not in rc:
                continue
            if self._resource_data[rc]["text"]:
                md = self._resource_data[rc]["text"]
            else:
                md = ""
            id_tag = '<a id="{}"/>'.format(self._resource_data[rc]["id"])
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{}\n".format(id_tag), md, 1)
            md = markdown_utils.increase_headers(md)
            uses = link_utils.get_uses(self._rc_references, rc)
            if uses == "":
                continue
            md += uses
            md += "\n\n"
            tw_md += md
        # TODO localization
        tw_md = markdown_utils.remove_md_section(tw_md, "Bible References")
        # TODO localization
        tw_md = markdown_utils.remove_md_section(
            tw_md, "Examples from the Bible stories"
        )

        logger.debug("tw_md is {}".format(tw_md))
        self._content = tw_md
        # return tw_md


class TQResource(TResource):
    def get_content(self) -> None:
        logger.info("Processing Translation Questions Markdown...")
        self._get_tq_markdown()
        # FIXME
        # self._replace_rc_links()
        # self._fix_links()
        logger.info("Converting MD to HTML...")
        self._convert_md2html()

    def _get_tq_markdown(self) -> None:
        """Build tq markdown"""
        # TODO localization
        tq_md = '# Translation Questions\n<a id="tq-{}"/>\n\n'.format(self._book_id)
        # TODO localization
        title = "{} Translation Questions".format(self._book_title)
        rc = "rc://{}/tq/help/{}".format(self._lang_code, self._book_id)
        anchor_id = "tq-{}".format(self._book_id)
        self._resource_data[rc] = {
            "rc": rc,
            "id": anchor_id,
            "link": "#{}".format(anchor_id),
            "title": title,
        }
        self._my_rcs.append(rc)
        tq_book_dir = os.path.join(self._resource_dir, self._book_id)
        for chapter in sorted(os.listdir(tq_book_dir)):
            chapter_dir = os.path.join(tq_book_dir, chapter)
            chapter = chapter.lstrip("0")
            if os.path.isdir(chapter_dir) and re.match(r"^\d+$", chapter):
                id_tag = '<a id="tq-{}-{}"/>'.format(
                    self._book_id, link_utils.pad(self._book_id, chapter)
                )
                tq_md += "## {} {}\n{}\n\n".format(self._book_title, chapter, id_tag)
                # TODO localization
                title = "{} {} Translation Questions".format(self._book_title, chapter)
                rc = "rc://{}/tq/help/{}/{}".format(
                    self._lang_code,
                    self._book_id,
                    link_utils.pad(self._book_id, chapter),
                )
                anchor_id = "tq-{}-{}".format(
                    self._book_id, link_utils.pad(self._book_id, chapter)
                )
                self._resource_data[rc] = {
                    "rc": rc,
                    "id": anchor_id,
                    "link": "#{0}".format(anchor_id),
                    "title": title,
                }
                self._my_rcs.append(rc)
                for chunk in sorted(os.listdir(chapter_dir)):
                    chunk_file = os.path.join(chapter_dir, chunk)
                    first_verse = os.path.splitext(chunk)[0].lstrip("0")
                    if os.path.isfile(chunk_file) and re.match(r"^\d+$", first_verse):
                        md = file_utils.read_file(chunk_file)
                        md = markdown_utils.increase_headers(md, 2)
                        md = re.compile("^([^#\n].+)$", flags=re.M).sub(
                            r'\1 [<a href="#tn-{}-{}-{}">{}:{}</a>]'.format(
                                self._book_id,
                                link_utils.pad(self._book_id, chapter),
                                link_utils.pad(self._book_id, first_verse),
                                chapter,
                                first_verse,
                            ),
                            md,
                        )
                        # TODO localization
                        title = "{} {}:{} Translation Questions".format(
                            self._book_title, chapter, first_verse
                        )
                        rc = "rc://{}/tq/help/{}/{}/{}".format(
                            self._lang_code,
                            self._book_id,
                            link_utils.pad(self._book_id, chapter),
                            link_utils.pad(self._book_id, first_verse),
                        )
                        anchor_id = "tq-{}-{}-{}".format(
                            self._book_id,
                            link_utils.pad(self._book_id, chapter),
                            link_utils.pad(self._book_id, first_verse),
                        )
                        self._resource_data[rc] = {
                            "rc": rc,
                            "id": anchor_id,
                            "link": "#{}".format(anchor_id),
                            "title": title,
                        }
                        self._my_rcs.append(rc)
                        link_utils.get_resource_data_from_rc_links(
                            self._lang_code,
                            self._my_rcs,
                            self._rc_references,
                            self._resource_data,
                            self._bad_links,
                            self._working_dir,
                            md,
                            rc,
                        )
                        md += "\n\n"
                        tq_md += md
        logger.debug("tq_md is {0}".format(tq_md))
        self._content = tq_md
        # return tq_md


class TAResource(TResource):
    def get_content(self) -> None:
        logger.info("Processing Translation Academy Markdown...")
        self._get_ta_markdown()
        # FIXME
        # self._replace_rc_links()
        # self._fix_links()
        logger.info("Converting MD to HTML...")
        self._convert_md2html()

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
    working_dir: str, output_dir: str, resource_request: model.ResourceRequest
) -> Resource:
    """ Factory method. """
    # resource_type is key, Resource subclass is value
    resources = {
        "usfm": USFMResource,
        "ulb": USFMResource,
        "ulb-wa": USFMResource,
        "udb": USFMResource,
        "udb-wa": USFMResource,
        "reg": USFMResource,
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
    )


def get_tw_refs(tw_refs_by_verse: dict, book: str, chapter: str, verse: str) -> List:
    """ Returns a list of refs for the given book, chapter, verse, or
        empty list if no matches. """
    if tw_refs_by_verse and book not in tw_refs_by_verse:
        return []
    if chapter not in tw_refs_by_verse[book]:
        return []
    if verse not in tw_refs_by_verse[book][chapter]:
        return []
    return tw_refs_by_verse[book][chapter][verse]


class ResourceProvisioner:
    """
    This class handles creating the necessary directory for a resource
    adn then acquiring the resource instance's file assets into the
    directory.
    """

    def __init__(self, resource: Resource):
        self._resource = resource

    def __call__(self) -> None:
        self._prepare_resource_directory()
        self._acquire_resource()

    @icontract.ensure(lambda self: self._resource._resource_dir is not None)
    def _prepare_resource_directory(self) -> None:
        """ If it doesn't exist yet, create the directory for the
        resource where it will be downloaded to. """

        logger.debug("os.getcwd(): {}".format(os.getcwd()))
        if not os.path.exists(self._resource._resource_dir):
            logger.debug(
                "About to create directory {}".format(self._resource._resource_dir)
            )
            try:
                os.mkdir(self._resource._resource_dir)
                logger.debug(
                    "Created directory {}".format(self._resource._resource_dir)
                )
            except:
                logger.exception(
                    "Failed to create directory {}".format(self._resource._resource_dir)
                )

    @icontract.require(lambda self: self._resource._resource_type is not None)
    @icontract.require(lambda self: self._resource._resource_dir is not None)
    @icontract.require(lambda self: self._resource._resource_url is not None)
    def _acquire_resource(self) -> None:
        """ Download or git clone resource and unzip resulting file if it
        is a zip file. """

        assert (
            self._resource._resource_url is not None
        ), "self._resource_url must not be None"
        logger.debug(
            "self._resource._resource_url: {} for {}".format(
                self._resource._resource_url, self
            )
        )

        # FIXME To ensure consistent directory naming for later
        # discovery, let's not use the url.rpartition(os.path.sep)[2].
        # Instead let's use a directory built from the parameters of
        # the (updated) resource:
        # os.path.join(resource["resource_dir"], resource["resource_type"])
        # logger.debug(
        #     "os.path.join(self._resource_dir, self._resource_type): {}".format(
        #         os.path.join(self._resource_dir, self._resource_type)
        #     )
        # )
        # FIXME Not sure if this is the right approach for consistency
        resource_filepath = os.path.join(
            self._resource._resource_dir,
            self._resource._resource_url.rpartition(os.path.sep)[2],
        )
        logger.debug(
            "Using file location, resource_filepath: {}".format(resource_filepath)
        )

        if self._is_git():  # Is a git repo, so clone it.
            try:
                command: str = "git clone --depth=1 '{}' '{}'".format(
                    # FIXME resource_filepath used to be filepath
                    self._resource._resource_url,
                    resource_filepath,
                )
                logger.debug("os.getcwd(): {}".format(os.getcwd()))
                logger.debug("git command: {}".format(command))
                subprocess.call(command, shell=True)
                logger.debug("git clone succeeded.")
                # Git repos get stored on directory deeper
                # FIXME Beware this may not be correct any longer
                self._resource._resource_dir = resource_filepath
            except:
                logger.debug("os.getcwd(): {}".format(os.getcwd()))
                logger.debug("git command: {}".format(command))
                logger.debug("git clone failed!")
        else:  # Is not a git repo, so just download it.
            try:
                logger.debug(
                    "Downloading {} into {}".format(
                        self._resource._resource_url, resource_filepath
                    )
                )
                url_utils.download_file(self._resource._resource_url, resource_filepath)
            finally:
                logger.debug("Downloading finished.")

        if self._is_zip():  # Downloaded file was a zip, so unzip it.
            try:
                logger.debug(
                    "Unzipping {} into {}".format(
                        resource_filepath, self._resource._resource_dir
                    )
                )
                file_utils.unzip(resource_filepath, self._resource._resource_dir)
            finally:
                logger.debug("Unzipping finished.")

    @icontract.require(lambda self: self._resource._resource_source is not None)
    def _is_git(self) -> bool:
        """ Return true if _resource_source is equal to 'git'. """
        return self._resource._resource_source == config.GIT

    @icontract.require(lambda self: self._resource._resource_source is not None)
    def _is_zip(self) -> bool:
        """ Return true if _resource_source is equal to 'zip'. """
        return self._resource._resource_source == config.ZIP


class Manifest:
    """
    This class handles finding, loading, and converting manifest
    files for a resource instance.
    """

    def __init__(self, resource: Resource) -> None:
        self._resource = resource
        self._manifest_content: Dict
        self._manifest_file_path: Optional[pathlib.PurePath] = None
        self._version: Optional[str] = None
        self._issued: Optional[str] = None

    # FIXME A bit of a cluster with lots of side effecting
    # FIXME Perhaps many of these inst vars don't need persistence as
    # an inst var and their values could instead be calculated as
    # needed lazily.
    @icontract.require(lambda self: self._resource.resource_dir_path is not None)
    def __call__(self) -> None:
        """ All subclasses need to at least find their manifest file,
        if it exists. Subclasses specialize this method to
        additionally initialize other disk layout related properties.
        """
        logger.debug(
            "self._resource.resource_dir_path: {}".format(
                self._resource.resource_dir_path
            )
        )
        # FIXME This could just be a glob and not a pathlib glob
        manifest_file_list = list(
            self._resource.resource_dir_path.glob("**/manifest.*")
        )
        # FIXME We may be saving inst vars unnecessarily below. If we
        # must save state maybe we'll have a Manifest dataclass that
        # stores the values as fields and can be composed into the
        # Resource. Maybe we'd only store the and its path manifest
        # itself in inst vars and then get the others values as
        # properties.
        if manifest_file_list:
            self._manifest_file_path = list(manifest_file_list)[0]
        else:
            self._manifest_file_path = None
        logger.debug("self._manifest_file_path: {}".format(self._manifest_file_path))
        # Find directory where the manifest file is located
        if self._manifest_file_path is not None:
            self._manifest_content = self._load_manifest()
            logger.debug("manifest dir: {}".format(self._manifest_file_path.parent))

        if self.manifest_type:
            logger.debug("self.manifest_type: {}".format(self.manifest_type))
            if self._is_yaml():
                self._version, self._issued = self._get_manifest_version_and_issued()
                logger.debug(
                    "_version: {}, _issued: {}".format(self._version, self._issued)
                )
        if self._manifest_content:
            logger.debug("self._manifest_content: {}".format(self._manifest_content))

    @icontract.require(lambda self: self._manifest_file_path is not None)
    def _load_manifest(self) -> dict:
        """ Load the manifest file. """
        manifest: dict = {}
        if self._is_yaml():
            manifest = file_utils.load_yaml_object(self._manifest_file_path)
        elif self._is_txt():
            manifest = file_utils.load_yaml_object(self._manifest_file_path)
        elif self._is_json():
            manifest = file_utils.load_json_object(self._manifest_file_path)
        return manifest

    @icontract.require(lambda self: self._manifest is not None)
    def _get_manifest_version_and_issued(self) -> Tuple[str, str]:
        """ Return the manifest's version and issued values. """
        version: str = ""
        issued: str = ""
        # NOTE manifest.txt files do not have 'dublin_core' or
        # 'version' keys.
        # TODO Handle manifest.json which has different fields.
        # FIXME Can we flatten this conditional and therefore be more
        # pythonic?
        if (
            self._manifest_content
            # FIXME This next line doesn't type check with mypy
            and 0 in self._manifest_content
            and self._manifest_content[0]["dublin_core"]["version"] is not None
        ):
            version = self._manifest_content[0]["dublin_core"]["version"]
        elif (
            self._manifest_content
            and 0 not in self._manifest_content
            and self._manifest_content["dublin_core"]["version"] is not None
        ):
            version = self._manifest_content["dublin_core"]["version"]
        if self._manifest_content is not None:
            issued = self._manifest_content["dublin_core"]["issued"]
        return (version, issued)

    @icontract.require(lambda self: self.manifest_type is not None)
    def _is_yaml(self) -> bool:
        """ Return true if the resource's manifest file has suffix yaml. """
        return self.manifest_type == config.YAML

    @icontract.require(lambda self: self.manifest_type is not None)
    def _is_txt(self) -> bool:
        """ Return true if the resource's manifest file has suffix json. """
        return self.manifest_type == config.TXT

    @icontract.require(lambda self: self.manifest_type is not None)
    def _is_json(self) -> bool:
        """ Return true if the resource's manifest file has suffix json. """
        return self.manifest_type == config.JSON

    @property
    def manifest_type(self) -> Optional[str]:
        if self._manifest_file_path is not None:
            return self._manifest_file_path.suffix
        return None

    # FIXME This is not currently used
    # FIXME If it is used later it should be a public method, i.e., no
    # leading underscore.
    def _get_book_project_from_yaml(self) -> dict:
        """
        Return the project that was requested if it matches that found
in the manifest file for the resource otherwise return an empty dict.
        """

        if (
            self._manifest_content and "projects" in self._manifest_content
        ):  # This is the manifest.yaml case.
            # logger.info("about to get projects")
            # NOTE The old code would return the list of book projects
            # that either contained: 1) all books if no books were
            # specified by the user, or, 2) only those books that
            # matched the books requested from the command line.
            for p in self._manifest_content["projects"]:
                if p["identifier"] in self._resource._resource_code:
                    return p
                    # if not p["sort"]:
                    #     p["sort"] = bible_books.BOOK_NUMBERS[p["identifier"]]
                    # projects.append(p)
            # return sorted(projects, key=lambda k: k["sort"])
        else:
            logger.info(
                "manifest.yaml did not contain any matching books in its projects node..."
            )
            return {}
        return {}

    # FIXME This is not currently called. We might only want some version
    # of this to check if the book's source file is considered
    # complete. This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    # FIXME If it is used later it should be a public method, i.e., no
    # leading underscore.
    def _get_book_projects_from_yaml(self) -> List[Dict[Any, Any]]:
        """
        Return the sorted list of projects that are found in the
manifest file for the resource.
        """

        projects: List[Dict[Any, Any]] = []
        if (
            self._manifest_content and "projects" in self._manifest_content
        ):  # This is the manifest.yaml case.
            # logger.info("about to get projects")
            # NOTE The old code would return the list of book projects
            # that either contained: 1) all books if no books were
            # specified by the user, or, 2) only those books that
            # matched the books requested from the command line.
            for p in self._manifest_content["projects"]:
                if (
                    self._resource._resource_code
                    is not None  # _resource_code is never none
                    and p["identifier"] in self._resource._resource_code
                ):
                    if not p["sort"]:
                        p["sort"] = bible_books.BOOK_NUMBERS[p["identifier"]]
                    projects.append(p)
            return sorted(projects, key=lambda k: k["sort"])
        else:
            logger.info("empty projects check is true...")
            return projects

    # FIXME This is not currently called. We might only want some version
    # of this to check if the book's source file is considered
    # complete. This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    # FIXME If it is used later it should be a public method, i.e., no
    # leading underscore.
    def _get_book_project_from_json(self) -> dict:
        """
        Return the project that was requested if it is found in the
manifest.json file for the resource, otherwise return an empty dict.
        """

        # projects: List[Dict[Any, Any]] = []
        if (
            self._manifest_content and "finished_chunks" in self._manifest_content
        ):  # This is the manifest.json case
            logger.info("about to get finished_chunks from manifest.json")

            # NOTE From _get_book_projects_from_yaml:
            # for p in self._manifest_content["projects"]:
            #     if (
            #         self._resource._resource_code is not None
            #         and p["identifier"] in self._resource._resource_code
            #     ):
            #         if not p["sort"]:
            #             p["sort"] = bible_books.BOOK_NUMBERS[p["identifier"]]
            #         projects.append(p)
            # return sorted(projects, key=lambda k: k["sort"])

            for p in self._manifest_content["finished_chunks"]:
                if p["identifier"] in self._resource._resource_code:
                    return p
                # projects.append(p)
            # return projects
        else:
            logger.info(
                "no project was found in manifest.json matching the requested book..."
            )
            return {}
        return {}

    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    # FIXME If it is used later it should be a public method, i.e., no
    # leading underscore.
    @icontract.require(lambda self: self._manifest_content["finished_chunks"])
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

    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib usage.
    # @icontract.require(lambda self: self._resource_code is not None)
    # @icontract.require(lambda self: self._resource_filename is not None)
    # @icontract.ensure(
    #     lambda self: self._book_id is not None
    # )  # FIXME This doesn't exist yet
    # @icontract.ensure(
    #     lambda self: self._book_number is not None
    # )  # FIXME This doesn't exist yet
    # @icontract.ensure(
    #     lambda self: self._book_title is not None
    # )  # FIXME This doesn't exist yet
    # def _initialize_book_properties_when_no_manifest(self) -> None:
    # NOTE USFM book files have form 01-GEN or GEN. So we lowercase
    # then split on hyphen and get second component to get
    # the book id.
    # assert (
    #     self._is_usfm()
    # ), "Calling _initialize_book_properties_when_no_manifest requires a USFM file-based resource"
    # FIXME Why derive book_id when we have the same information
    # in resource_code?
    # if "-" in self._resource_filename:
    #     book_id = self._resource_filename.split("-")[1]
    # else:
    #     book_id = self._resource_filename
    # self._book_id = book_id.lower()
    # FIXME Just for development to see if this ever triggers
    # since book_id and resource_code should be equal. See FIXME note
    # above.
    # assert (
    #     self._book_id == self._resource_code
    # ), "Book name should match resource code"
    # logger.debug("book_id for usfm file: {}".format(self._book_id))
    # self._book_title = bible_books.BOOK_NAMES[self._resource_code]
    # self._book_number = bible_books.BOOK_NUMBERS[self._book_id]
    # logger.debug("book_number for usfm file: {}".format(self._book_number))

    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib usage.
    # def _initialize_book_properties_from_manifest_yaml(self) -> None:
    # NOTE USFM book files have form 01-GEN or GEN. So we lowercase
    # then split on hyphen and get second component to get
    # the book id.
    # assert (
    #     self._is_git()
    # ), "Calling _initialize_book_properties_from_manifest_yaml requires a git repo"
    # assert (
    #     self._is_yaml()
    # ), "Calling _initialize_book_properties_from_manifest_yaml requires a manifest.yaml"
    # projects: List[Dict[Any, Any]] = self._get_book_projects_from_yaml()
    # project: dict = self._get_book_project_from_yaml()
    # logger.debug("book projects: {}".format(projects))
    # logger.debug("book project: {}".format(project))
    # Invariant: projects is len == 0 or 1
    # assert (
    #     len(projects) <= 1
    # ), "projects is always less than or equal to 1 in length"
    # for p in projects:
    #     project: Dict[Any, Any] = p
    #     self._book_id = p["identifier"]
    #     self._book_title = p["title"].replace(" translationNotes", "")
    #     self._book_number = bible_books.BOOK_NUMBERS[self._book_id]
    #     # TODO This likely needs to change because of how we
    #     # build resource_dir
    #     self._filename_base = "{}_tn_{}-{}_v{}".format(
    #         self._lang_code,
    #         self._book_number.zfill(2),
    #         self._book_id.upper(),
    #         self._version,
    #     )
    # self._book_id = project[
    #     "identifier"
    # ]  # FIXME Isn't book id always equal to resource_code?
    # Although perhaps localization is obtained by asking the
    # project for the book_id? I think book id is always English
    # though.
    # self._book_title = project["title"].replace(" translationNotes", "") # FIXME This could be initialized in
    # __init__ like so: self._book_title = bible_books.BOOK_NAMES[self._resource_code]
    # self._book_number = bible_books.BOOK_NUMBERS[
    #     self._book_id
    # ]  # FIXME Can't this be determined in __init__?
    # TODO This likely needs to change because of how we
    # build resource_dir
    # FIXME I don't think we even use this inst var
    # self._filename_base = "{}_tn_{}-{}_v{}".format(
    #     self._lang_code,
    #     self._book_number.zfill(2),
    #     self._book_id.upper(),  # FIXME This could blow up if book requested doesn't exist
    #     self._version,
    # )

    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib usage.
    # FIXME This needs contracts
    # def _initialize_book_properties_from_manifest_json(self) -> None:
    #     # NOTE USFM book files have form 01-GEN or GEN. So we lowercase
    #     # then split on hyphen and get second component to get
    #     # the book id.
    #     assert (
    #         self._is_git()
    #     ), "Calling _initialize_book_properties_from_manifest_json requires a git repo"
    #     assert (
    #         self._is_json()
    #     ), "Calling _initialize_book_properties_from_manifest_json requires manifest.json"
    #     logger.info("is json")
    #     # FIXME This should be like from_yaml version; return only one
    #     # project as one book is requested per resource
    #     projects: List = self._get_book_projects_from_json()
    #     logger.debug("book projects: {}".format(projects))
    #     for p in projects:
    #         project: Dict[Any, Any] = p  # FIXME This is not used
    #         self._book_id = self._resource_code
    #         # self._book_id = p["identifier"]
    #         self._book_title = bible_books.BOOK_NAMES[self._resource_code]
    #         # self._book_title = p["title"].replace(" translationNotes", "")
    #         self._book_number = bible_books.BOOK_NUMBERS[self._book_id]
    #         # TODO This likely needs to change because of how we
    #         # build resource_dir
    #         self._filename_base = "{}_tn_{}-{}_v{}".format(
    #             self._lang_code,
    #             self._book_number.zfill(2),
    #             self._book_id.upper(),
    #             self._version,
    #         )
