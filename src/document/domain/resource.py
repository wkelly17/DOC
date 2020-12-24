from __future__ import annotations  # https://www.python.org/dev/peps/pep-0563/
from typing import Any, Dict, List, Optional, Tuple

import abc
import bs4
from glob import glob
import icontract
import markdown
import os
import pathlib
import re
import subprocess
import tempfile
from usfm_tools.transform import UsfmTransform
import yaml

from document.utils import url_utils
from document.utils import file_utils
from document.domain import bible_books
from document import config
from document.domain import resource_lookup
from document.domain import model

import logging
import logging.config

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


class AbstractResource(abc.ABC):
    @abc.abstractmethod
    def find_location(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def initialize_properties(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_files(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_content(self) -> None:
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

        # FIXME Is this what you want consistently?
        self._resource_filename: str = "{}_{}_{}".format(
            self._lang_code, self._resource_type, self._resource_code
        )
        # self._resource_filename: Optional[str] = None
        self._book_id: str = self._resource_code
        # FIXME Could get KeyError
        self._book_title = bible_books.BOOK_NAMES[self._resource_code]
        self._book_number = bible_books.BOOK_NUMBERS[self._book_id]

        self._resource_url: Optional[str] = None
        # self._filename_base: Optional[str] = None
        # NOTE Next line wouldn't work unless you had access to
        # self._version which isn't available here. Why would we need
        # version anyway?
        # self._filename_base = "{}_tn_{}-{}_v{}".format(
        #     self._lang_code,
        #     self._book_number.zfill(2),
        #     self._book_id.upper(),
        #     self._version,
        # )
        self._resource_source: str
        self._resource_jsonpath: Optional[str] = None

        # Manifest related instance vars
        # FIXME It might be better to just have a manifest class, set
        # it to None here and then instantiate it when we get to
        # manifests. Then we'd have one manifest specific inst vars
        # instead of five.
        self._manifest: Optional[Dict] = None
        self._manifest_file_path: Optional[pathlib.PurePath] = None
        self._version: Optional[str] = None
        self._issued: Optional[str] = None
        # Content related instance vars
        self._content_files: Optional[List[str]] = None
        self._content: Optional[str] = None
        self._bad_links: dict = {}
        self._resource_data: dict = {}
        self._my_rcs: List = []
        self._rc_references: dict = {}

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

    @property
    def manifest_type(self) -> Optional[str]:
        if self._manifest_file_path is not None:
            return self._manifest_file_path.suffix
        return None

    def is_found(self) -> bool:
        "Return true if resource's URL location was found."
        return self._resource_url is not None

    def initialize_properties(self) -> None:
        "Subclasses provide."
        pass

    def find_location(self) -> None:
        "Subclasses provide."
        pass

    def get_content(self) -> None:
        "Subclasses provide."
        pass

    def get_files(self) -> None:
        """ Using the resource's location, obtain provision the save
        location and then get the resources associated files. """
        provisioner = ResourceProvisioner(self)
        provisioner.provision()

    @icontract.require(lambda self: self._resource_source is not None)
    def _is_usfm(self) -> bool:
        """ Return true if _resource_source is equal to 'usfm'. """
        return self._resource_source == config.USFM

    @icontract.require(lambda self: self.manifest_type is not None)
    def _is_yaml(self) -> bool:
        """ Return true if the resource's manifest file has suffix
        yaml. """
        return self.manifest_type == config.YAML

    @icontract.require(lambda self: self.manifest_type is not None)
    def _is_txt(self) -> bool:
        """ Return true if the resource's manifest file has suffix
        json. """
        return self.manifest_type == config.TXT

    @icontract.require(lambda self: self.manifest_type is not None)
    def _is_json(self) -> bool:
        """ Return true if the resource's manifest file has suffix
        json. """
        return self.manifest_type == config.JSON

    # FIXME A bit of a cluster with lots of side effecting
    # FIXME Perhaps many of these inst vars don't need persistence as
    # an inst var and their values could instead be calculated as
    # needed lazily.
    @icontract.require(lambda self: self.resource_dir_path is not None)
    def _discover_manifest(self) -> None:
        """ All subclasses need to at least find their manifest file,
        if it exists. Subclasses specialize this method to
        additionally initialize other disk layout related properties.
        """
        logger.debug("self.resource_dir_path: {}".format(self.resource_dir_path))
        manifest_file_list = list(self.resource_dir_path.glob("**/manifest.*"))
        # FIXME We may be saving inst vars unnecessarily below. If we
        # must save state maybe we'll have a Manifest dataclass that
        # stores the values as fields and can be composed into the
        # Resource. Maybe we'd only store the and its path manifest
        # itself in inst vars and then get the others values as
        # properties.
        self._manifest_file_path = (
            None if len(manifest_file_list) == 0 else list(manifest_file_list)[0]
        )
        logger.debug("self._manifest_file_path: {}".format(self._manifest_file_path))
        # Find directory where the manifest file is located
        if self._manifest_file_path is not None:
            self._manifest = self._load_manifest()
            logger.debug("manifest dir: {}".format(self._manifest_file_path.parent))

        # # FIXME Rather than all this checking we could just convert to
        # # one manifest type, say, json or whatever is considered the
        # # latest manifest type by WA.
        # # if self._manifest_file_path is not None:
        # if self._is_yaml():
        #     self._manifest = file_utils.load_yaml_object(self._manifest_file_path)
        #     self._manifest_type = config.YAML
        # elif self._manifest_file_path.suffix == config.TXT_SUFFIX:
        #     self._manifest = file_utils.load_yaml_object(self._manifest_file_path)
        #     self._manifest_type = config.TXT
        # elif self._manifest_file_path.suffix == config.JSON_SUFFIX:
        #     self._manifest = file_utils.load_json_object(self._manifest_file_path)
        #     self._manifest_type = config.JSON
        # # else:
        # #     logger.debug(
        # #         "manifest file does not exist for resource {}.".format(
        # #             self._resource_type
        # #         )
        # #     )

        if self.manifest_type:
            logger.debug("self.manifest_type: {}".format(self.manifest_type))
            if self._is_yaml():
                self._version, self._issued = self._get_manifest_version_and_issued()
                logger.debug(
                    "_version: {}, _issued: {}".format(self._version, self._issued)
                )
        if self._manifest:
            logger.debug("self._manifest: {}".format(self._manifest))

    @icontract.require(lambda self: self._manifest_file_path is not None)
    def _load_manifest(self) -> dict:
        """ Load the manifest file. """
        manifest: dict = {}
        if self._is_yaml():
            manifest = file_utils.load_yaml_object(self._manifest_file_path)
            # NOTE self.manifest_type is a property now
            # self._manifest_type = config.YAML
        elif self._is_txt():
            manifest = file_utils.load_yaml_object(self._manifest_file_path)
            # NOTE self.manifest_type is a property now
            # self._manifest_type = config.TXT
        elif self._is_json():
            manifest = file_utils.load_json_object(self._manifest_file_path)
            # NOTE self.manifest_type is a property now
            # self._manifest_type = config.JSON
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
            # FIXME This next line doesn't type check with mypy
            self._manifest
            and 0 in self._manifest
            and self._manifest[0]["dublin_core"]["version"] is not None
        ):
            version = self._manifest[0]["dublin_core"]["version"]
        elif (
            self._manifest
            and 0 not in self._manifest
            and self._manifest["dublin_core"]["version"] is not None
        ):
            version = self._manifest["dublin_core"]["version"]
        if self._manifest is not None:
            issued = self._manifest["dublin_core"]["issued"]
        return (version, issued)

    @icontract.require(lambda num: num is not None)
    @icontract.require(lambda num: isinstance(num, str))
    def _pad(self, num: str) -> str:
        if self._book_id == "psa":
            # return str(num).zfill(3)
            return num.zfill(3)
        # return str(num).zfill(2)
        return num.zfill(2)

    def _get_uses(self, rc: str) -> str:
        md = ""
        if self._rc_references[rc]:
            references = []
            for reference in self._rc_references[rc]:
                if "/tn/" in reference:
                    references.append("* [[{}]]".format(reference))
            if references:
                # TODO localization
                md += "### Uses:\n\n"
                md += "\n".join(references)
                md += "\n"
        return md

    # FIXME This legacy code is a mess of mixed up concerns. This
    # method is called from tn and tq concerned code so when we move
    # it it will probably have to live in a module that can be mixed
    # into both TNResource and TQResource or the method itself will be
    # teased apart so that conditionals are reduced and code paths
    # pertaining to the instance are the only ones preserved in the
    # instance's version of this method.
    @icontract.require(lambda text: text is not None)
    @icontract.require(lambda source_rc: source_rc is not None)
    def _get_resource_data_from_rc_links(self, text: str, source_rc: str) -> None:
        for rc in re.findall(
            r"rc://[A-Z0-9/_-]+", text, flags=re.IGNORECASE | re.MULTILINE
        ):
            parts = rc[5:].split("/")
            resource_tmp = parts[1]
            path = "/".join(parts[3:])

            if rc not in self._my_rcs:
                self._my_rcs.append(rc)
            if rc not in self._rc_references:
                self._rc_references[rc] = []
            self._rc_references[rc].append(source_rc)

            if rc not in self._resource_data:
                title = ""
                t = ""
                anchor_id = "{}-{}".format(resource_tmp, path.replace("/", "-"))
                link = "#{}".format(anchor_id)
                try:
                    file_path = os.path.join(
                        self._working_dir,
                        "{}_{}".format(self._lang_code, resource_tmp),
                        "{}.md".format(path),
                    )
                    if not os.path.isfile(file_path):
                        file_path = os.path.join(
                            self._working_dir,
                            "{}_{}".format(self._lang_code, resource_tmp),
                            "{}/01.md".format(path),
                        )
                    if not os.path.isfile(file_path):
                        # TODO localization?
                        if path.startswith("bible/other/"):
                            # TODO localization?
                            path2 = re.sub(r"^bible/other/", r"bible/kt/", path)
                        else:
                            # TODO localization?
                            path2 = re.sub(r"^bible/kt/", r"bible/other/", path)
                        anchor_id = "{}-{}".format(
                            resource_tmp, path2.replace("/", "-")
                        )
                        link = "#{}".format(anchor_id)
                        file_path = os.path.join(
                            self._working_dir,
                            "{}_{}".format(self._lang_code, resource_tmp),
                            "{}.md".format(path2),
                        )
                    if os.path.isfile(file_path):
                        t = file_utils.read_file(file_path)
                        title = get_first_header(t)
                        t = self._fix_tw_links(t, path.split("/")[1])
                    else:
                        # TODO bad_links doesn't exist yet, but should
                        # be on resources dict.
                        if rc not in self._bad_links:
                            self._bad_links[rc] = []
                        self._bad_links[rc].append(source_rc)
                except:
                    # TODO
                    if rc not in self._bad_links:
                        self._bad_links[rc] = []
                    self._bad_links[rc].append(source_rc)
                self._resource_data[rc] = {
                    "rc": rc,
                    "link": link,
                    "id": anchor_id,
                    "title": title,
                    "text": t,
                }
                if t:
                    self._get_resource_data_from_rc_links(t, rc)

    # legacy
    def _fix_tw_links(self, text: str, dictionary: str) -> str:
        rep = {
            r"\]\(\.\./([^/)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/{}/\1)".format(
                self._lang_code, dictionary
            ),
            r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/\1)".format(
                self._lang_code
            ),
        }
        for pattern, repl in rep.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text

    def _increase_headers(self, text: str, increase_depth: int = 1) -> str:
        if text:
            text = re.sub(
                r"^(#+) +(.+?) *#*$",
                r"\1{0} \2".format("#" * increase_depth),
                text,
                flags=re.MULTILINE,
            )
        return text

    @icontract.require(lambda text: text is not None)
    def _decrease_headers(
        self, text: str, minimum_header: int = 1, decrease: int = 1
    ) -> str:
        if text:
            text = re.sub(
                r"^({0}#*){1} +(.+?) *#*$".format(
                    "#" * (minimum_header - decrease), "#" * decrease
                ),
                r"\1 \2",
                text,
                flags=re.MULTILINE,
            )
        return text

    # def _replace_bible_links(self, text: str) -> str:
    #     bible_links = re.findall(
    #         r"(?:udb|ulb)://[A-Z0-9/]+", text, flags=re.IGNORECASE | re.MULTILINE
    #     )
    #     bible_links = list(set(bible_links))
    #     logger.debug("bible_links: {}".format(bible_links))
    #     rep = {}
    #     for link in sorted(bible_links):
    #         parts = link.split("/")
    #         logger.debug("parts: {}".format(parts))
    #         resource_str = parts[0][0:3]
    #         logger.debug("resource_str: {}".format(resource_str))
    #         chapter = parts[4].lstrip("0")
    #         logger.debug("chapter: {}".format(chapter))
    #         first_verse = parts[5].lstrip("0")
    #         logger.debug("first_verse: {}".format(first_verse))
    #         rep[link] = "<div>{0}</div>".format(
    #             # FIXME It looks like this presupposes that, as per
    #             # the old logic path, we build links to USFM files and
    #             # then later, i.e., here, actually produce the HTML
    #             # from the USFM. Such presuppositions are
    #             # inappropriate now.
    #             self._get_chunk_html(resource_str, chapter, first_verse)
    #         )
    #     rep = dict(
    #         (re.escape("[[{0}]]".format(link)), html) for link, html in rep.items()
    #     )
    #     pattern = re.compile("|".join(list(rep.keys())))
    #     text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    #     return text

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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._usfm_chunks: dict = {}

    def __repr__(self) -> str:
        return "{}, superclass: {}".format(type(self).__name__, super().__repr__())

    @icontract.ensure(
        lambda self: self._resource_url is not None
    )  # FIXME This is only useful during development to find resources which have exceptional jsonpaths. But the logic needs to allow for not finding a resource, so I am just using this temporarily to root out resources with exceptional jsonpaths.
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

    def initialize_properties(self) -> None:
        self._discover_layout()

        # FIXME This likely can be better envisioned and implemented.
        # if self._is_usfm():
        #     self._initialize_book_properties_when_no_manifest()
        # if self._is_git() and self._is_yaml():
        #     self._initialize_book_properties_from_manifest_yaml()
        # if self._is_git() and self._is_json():
        #     self._initialize_book_properties_from_manifest_json()

        # TODO Handle manifest.yaml, manifest.txt, and manifest.json
        # formats - they each have different structure and keys.
        # elif not self._is_git() and self._is_txt():

        # FIXME This may still be needed for non manifest.yaml cases,
        # but for manifest.yaml case it is initialized elsewhere.
        # NOTE Without this, things blow up on line 973.
        # self._initialize_filename_base()

    def _discover_layout(self) -> None:
        """ Explore the resource's downloaded files to initialize file
        structure related properties. """

        super()._discover_manifest()

        usfm_content_files = self.resource_dir_path.glob("**/*.usfm")
        # USFM files sometimes have txt suffix
        txt_content_files = self.resource_dir_path.glob("**/*.txt")

        # logger.debug("usfm_content_files: {}".format(usfm_content_files))

        if len(list(usfm_content_files)) > 0:  # This resource does have USFM files
            # Only use the content files that match the resource_code
            # in the resource request.
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(),
                    [str(file) for file in usfm_content_files],
                )
            )
        elif len(list(txt_content_files)) > 0:
            # Only use the content files that match the resource_code
            # in the resource request.
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(),
                    [str(file) for file in txt_content_files],
                )
            )

        logger.debug(
            "self._content_files for {}: {}".format(
                self._resource_code, self._content_files,
            )
        )

    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
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
    # approach in _discover_layout using pathlib.
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
    # approach in _discover_layout using pathlib.
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

    # FIXME This is no longer used
    def _get_book_project_from_yaml(self) -> dict:
        """ Return the project that was requested if it matches that
        found in the manifest file for the resource otherwise return
        an empty dict. """

        if (
            self._manifest and "projects" in self._manifest
        ):  # This is the manifest.yaml case.
            # logger.info("about to get projects")
            # NOTE The old code would return the list of book projects
            # that either contained: 1) all books if no books were
            # specified by the user, or, 2) only those books that
            # matched the books requested from the command line.
            for p in self._manifest["projects"]:
                if p["identifier"] in self._resource_code:
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

    # FIXME This is no longer called. We might only want some version
    # of this to check if the book's source file is considered
    # complete. This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _get_book_projects_from_yaml(self) -> List[Dict[Any, Any]]:
        """ Return the sorted list of projects that are found in the
        manifest file for the resource. """

        projects: List[Dict[Any, Any]] = []
        if (
            self._manifest and "projects" in self._manifest
        ):  # This is the manifest.yaml case.
            # logger.info("about to get projects")
            # NOTE The old code would return the list of book projects
            # that either contained: 1) all books if no books were
            # specified by the user, or, 2) only those books that
            # matched the books requested from the command line.
            for p in self._manifest["projects"]:
                if (
                    self._resource_code is not None  # _resource_code is never none
                    and p["identifier"] in self._resource_code
                ):
                    if not p["sort"]:
                        p["sort"] = bible_books.BOOK_NUMBERS[p["identifier"]]
                    projects.append(p)
            return sorted(projects, key=lambda k: k["sort"])
        else:
            logger.info("empty projects check is true...")
            return projects

    # FIXME This is no longer called. We might only want some version
    # of this to check if the book's source file is considered
    # complete. This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _get_book_project_from_json(self) -> dict:
        """ Return the project that was requested if it is found in the
        manifest.json file for the resource, otherwise return an empty
        dict. """

        # projects: List[Dict[Any, Any]] = []
        if (
            self._manifest and "finished_chunks" in self._manifest
        ):  # This is the manifest.json case
            logger.info("about to get finished_chunks from manifest.json")

            # NTOE From _get_book_projects_from_yaml:
            # for p in self._manifest["projects"]:
            #     if (
            #         self._resource_code is not None
            #         and p["identifier"] in self._resource_code
            #     ):
            #         if not p["sort"]:
            #             p["sort"] = bible_books.BOOK_NUMBERS[p["identifier"]]
            #         projects.append(p)
            # return sorted(projects, key=lambda k: k["sort"])

            for p in self._manifest["finished_chunks"]:
                if p["identifier"] in self._resource_code:
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
    def _get_book_projects_from_json(self) -> List:
        """ Return the sorted list of projects that are found in the
        manifest file for the resource. """

        projects: List[Dict[Any, Any]] = []
        if (
            self._manifest and "finished_chunks" in self._manifest
        ):  # This is the manifest.json case
            logger.info("about to get finished_chunks from manifest.json")

            # NTOE From _get_book_projects_from_yaml:
            # for p in self._manifest["projects"]:
            #     if (
            #         self._resource_code is not None
            #         and p["identifier"] in self._resource_code
            #     ):
            #         if not p["sort"]:
            #             p["sort"] = bible_books.BOOK_NUMBERS[p["identifier"]]
            #         projects.append(p)
            # return sorted(projects, key=lambda k: k["sort"])

            for p in self._manifest["finished_chunks"]:
                # TODO In resource_lookup, self._resource_code is used
                # determine jsonpath for lookup. Some resources don't
                # have anything more specific than the lang_code to
                # get resources from. Well, at least one language is
                # like that. In that case it contains a zip that has
                # all the resources contained therein.
                # if self._resource_code is not None:
                projects.append(p)
            return projects
        else:
            logger.info("empty projects check is true...")
            return projects

    # FIXME This is done in __init__ and is no longer needed here
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    # @icontract.require(lambda self: self._book_id is not None)
    # @icontract.require(lambda self: self._book_title is not None)
    # @icontract.require(lambda self: self._book_number is not None)
    # @icontract.ensure(lambda self: self._filename_base is not None)
    # def _initialize_filename_base(self) -> None:
    #     self._filename_base = "{}_{}_{}-{}".format(
    #         self._lang_code,
    #         self._resource_type,
    #         self._book_number.zfill(2),
    #         self._book_id.upper(),
    #     )
    #     # FIXME Should we be using self._filename_base or
    #     # self._resource_dir combined with self._resource_filename?
    #     logger.debug("filename_base: {}".format(self._filename_base))

    @icontract.ensure(lambda self: self._resource_filename is not None)
    @icontract.ensure(lambda self: self._lang_code is not None)
    @icontract.ensure(lambda self: self._resource_type is not None)
    @icontract.ensure(lambda self: self._book_number is not None)
    @icontract.ensure(lambda self: self._book_id is not None)
    @icontract.ensure(lambda self: self._content is not None)
    def get_content(self) -> None:
        self._get_usfm_chunks()

        # Create the USFM to HTML and store in file.
        UsfmTransform.buildSingleHtmlFromFiles(
            # self._resource_dir,
            self._content_files,
            self._output_dir,
            self._resource_filename,
        )
        # Read the HTML file into _content.
        html_file = "{}.html".format(
            os.path.join(self._output_dir, self._resource_filename)
        )
        self._content = file_utils.read_file(html_file)
        logger.debug("self._bad_links: {}".format(self._bad_links))

    # FIXME Handle git based usfm with resources.json file and .txt usfm
    # file suffixes.
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    @icontract.require(lambda self: self._resource_filename is not None)
    @icontract.require(lambda self: self._resource_dir is not None)
    @icontract.ensure(lambda self: self._usfm_chunks is not None)
    def _get_usfm_chunks(self) -> None:
        book_chunks: dict = {}
        logger.debug("self._resource_filename: {}".format(self._resource_filename))

        usfm_file_content: Optional[str] = self._get_usfm_file_content()

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
                logger.debug("pending_chunk: {}".format(pending_chunk))
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
            c_search = re.search(r"\\c[\u00A0\s](\d+)", chunk)  # \u00A0 no break space
            if c_search:
                chapter = c_search.group(1)
            verses = re.findall(r"\\v[\u00A0\s](\d+)", chunk)
            if not verses:
                continue
            first_verse = verses[0]
            last_verse = verses[-1]
            if chapter not in book_chunks:
                book_chunks[chapter] = {"chunks": []}
            data = {
                "usfm": chunk,
                "first_verse": first_verse,
                "last_verse": last_verse,
                "verses": verses,
            }
            book_chunks[chapter][first_verse] = data
            book_chunks[chapter]["chunks"].append(data)
        self._usfm_chunks = book_chunks
        logger.debug(
            "chapter worth of verses in self._usfm_chunks[chapter][last_verse]: {}".format(
                book_chunks[chapter][last_verse]
            )
        )

    def _get_usfm_file_content(self) -> Optional[str]:
        """
        Get the USFM file content for the resource if it is
        available, otherwise return None.
        """
        usfm: Optional[str] = None
        usfm_file: str = os.path.join(
            self._resource_dir,
            "{}-{}.usfm".format(self._book_number, self._book_id.upper()),
        )
        # FIXME Maybe it is unpythonic to check this. Perhaps instead
        # we should just attempt to read the file and if USFM is None
        # then we know it failed and we can try the alternate file
        # name.
        if os.path.exists(usfm_file):
            logger.debug("About to read: {}".format(usfm_file))
            # FIXME Need to handle exceptions (unless they are already
            # handled by read_file).
            usfm = file_utils.read_file(usfm_file, "utf-8",)
        else:  # Individual USFM files can have this alternate naming scheme.
            usfm_file = os.path.join(
                self._resource_dir, "{}.usfm".format(self._book_id.upper()),
            )
            if os.path.exists(usfm_file):
                logger.debug("About to read: {}".format(usfm_file))
                usfm = file_utils.read_file(usfm_file, "utf-8",)
        return usfm


class TResource(Resource):

    # FIXME Should this be copied to each TResource subclass instead?
    @icontract.ensure(
        lambda self: self._resource_url is not None
    )  # FIXME This is only useful during development to find resources which have exceptional jsonpaths. But the logic needs to allow for not finding a resource, so I am just using this temporarily to root out resources with exceptional jsonpaths.
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

    # FIXME Should this be copied to each TResource subclass instead?
    @icontract.require(lambda self: self._content is not None)
    def _convert_md2html(self) -> None:
        """ Convert a resource's Markdown to HTML. """
        assert self._content is not None, "self._content cannot be None here."
        self._content = markdown.markdown(self._content)

    # FIXME Bit of a legacy cluster.
    @icontract.require(lambda self: self._content is not None)
    @icontract.require(lambda self: self._my_rcs is not None)
    def _replace_rc_links(self) -> None:
        """ Given a resource's markdown text, replace links of the
        form [[rc://en/tw/help/bible/kt/word]] with links of the form
        [God's Word](#tw-kt-word). """
        # logger.debug("self._content: {}".format(self._content))
        logger.debug("self._my_rcs: {}".format(self._my_rcs))
        rep = dict(
            (
                re.escape("[[{0}]]".format(rc)),
                "[{0}]({1})".format(
                    self._resource_data[rc]["title"].strip(),
                    self._resource_data[rc]["link"],
                ),
            )
            for rc in self._my_rcs
        )
        logger.debug("rep: {}".format(rep))
        pattern: re.Pattern = re.compile("|".join(list(rep.keys())))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], self._content)

        # Change ].(rc://...) rc links, e.g. [Click here](rc://en/tw/help/bible/kt/word) => [Click here](#tw-kt-word)
        rep = dict(
            (re.escape("]({0})".format(rc)), "]({0})".format(info["link"]))
            for rc, info in self._resource_data.items()
        )
        pattern = re.compile("|".join(list(rep.keys())))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

        # Change rc://... rc links, e.g. rc://en/tw/help/bible/kt/word => [God's](#tw-kt-word)
        rep = dict(
            (re.escape(rc), "[{0}]({1})".format(info["title"], info["link"]))
            for rc, info in self._resource_data.items()
        )
        pattern = re.compile("|".join(list(rep.keys())))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

        self._content = text

    # FIXME Legacy cluster. This used to be a function and
    # maybe still should be, but for now I've made it an instance
    # method.
    def _fix_links(self) -> None:
        rep = {}

        def replace_tn_with_door43_link(match):
            book = match.group(1)
            chapter = match.group(2)
            verse = match.group(3)
            if book in bible_books.BOOK_NUMBERS:
                book_num = bible_books.BOOK_NUMBERS[book]
            else:
                return None
            if int(book_num) > 40:
                anchor_book_num = str(int(book_num) - 1)
            else:
                anchor_book_num = book_num
            url = "https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/{}-{}.html#{}-ch-{}-v-{}".format(
                book_num.zfill(2),
                book.upper(),
                anchor_book_num.zfill(3),
                chapter.zfill(3),
                verse.zfill(3),
            )
            return url

        def replace_obs_with_door43_link(match):
            url = "https://live.door43.org/u/Door43/en_obs/b9c4f076ff/{}.html".format(
                match.group(1)
            )
            return url

        # convert OBS links: rc://en/tn/help/obs/15/07 => https://live.door43.org/u/Door43/en_obs/b9c4f076ff/15.html
        rep[r"rc://[^/]+/tn/help/obs/(\d+)/(\d+)"] = replace_obs_with_door43_link

        # convert tN links (NT books use USFM numbering in HTML file name, but standard book numbering in the anchor):
        # rc://en/tn/help/rev/15/07 => https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/67-REV.html#066-ch-015-v-007
        rep[
            r"rc://[^/]+/tn/help/(?!obs)([^/]+)/(\d+)/(\d+)"
        ] = replace_tn_with_door43_link

        # convert RC links, e.g. rc://en/tn/help/1sa/16/02 => https://git.door43.org/Door43/en_tn/1sa/16/02.md
        rep[
            r"rc://([^/]+)/(?!tn)([^/]+)/([^/]+)/([^\s\)\]\n$]+)"
        ] = r"https://git.door43.org/Door43/\1_\2/src/master/\4.md"

        # convert URLs to links if not already
        rep[
            r'([^"\(])((http|https|ftp)://[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
        ] = r"\1[\2](\2)"

        # URLS wth just www at the start, no http
        rep[
            r'([^A-Za-z0-9"\(\/])(www\.[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
        ] = r"\1[\2](http://\2.md)"

        for pattern, repl in rep.items():
            self._content = re.sub(pattern, repl, self._content, flags=re.IGNORECASE)

    def initialize_properties(self) -> None:
        self._discover_layout()

    def _discover_layout(self) -> None:
        """ Programmatically discover the manifest and content files. """
        # Execute logic common to all resources
        super()._discover_manifest()

        # Get the content files
        markdown_files = self.resource_dir_path.glob("**/*.md")
        markdown_content_files = filter(
            lambda x: str(x.stem).lower() not in config.get_markdown_doc_file_names(),
            markdown_files,
        )
        txt_files = self.resource_dir_path.glob("**/*.txt")
        txt_content_files = filter(
            lambda x: str(x.stem).lower() not in config.get_markdown_doc_file_names(),
            txt_files,
        )

        if len(list(markdown_content_files)) > 0:
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(),
                    [str(file) for file in markdown_files],
                )
            )
        if len(list(txt_content_files)) > 0:
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(),
                    [str(file) for file in txt_files],
                )
            )

        logger.debug(
            "self._content_files for {}: {}".format(
                self._resource_code, self._content_files,
            )
        )


class TNResource(TResource):
    def get_content(self) -> None:
        logger.info("Processing Translation Notes Markdown...")
        self._get_tn_markdown()
        # FIXME
        self._replace_rc_links()
        self._fix_links()
        logger.info("Converting MD to HTML...")
        self._convert_md2html()
        logger.debug("self._bad_links: {}".format(self._bad_links))

    @icontract.require(lambda self: self._resource_code is not None)
    def _get_tn_markdown(self) -> None:
        book_dir: str = self._get_book_dir()
        logger.debug("book_dir: {}".format(book_dir))

        if not os.path.isdir(book_dir):
            return

        # TODO Might need localization
        # tn_md = '# Translation Notes\n<a id="tn-{}"/>\n\n'.format(self._book_id)
        tn_md = '# Translation Notes\n<a id="tn-{}"/>\n\n'.format(self._resource_code)

        book_has_intro, tn_md_intro = self._initialize_tn_book_intro(book_dir)
        tn_md += tn_md_intro

        # FIXME Use os.listdir(book_dir) to programmatically discover
        # all files. Then after lower-casing each filename, match the
        # filename in the list that contains the resource_code.
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
                # FIXME Could use pathlib here instead of glob from lib
                chunk_files = sorted(glob(os.path.join(chapter_dir, "[0-9]*.md")))
                logger.debug("chunk_files: {}".format(chunk_files))
                for _, chunk_file in enumerate(chunk_files):
                    # logger.info("in loop through chunk files")
                    (
                        first_verse,
                        last_verse,
                        title,
                        md,
                    ) = self._initialize_tn_chapter_files(chunk_file, chapter)

                    anchors = ""
                    pre_md = ""
                    # FIXME I don't think it should be fetching USFM
                    # stuff here in this method under the new design.
                    # _initialize_tn_chapter_verse_links now takes a
                    # first argument of a USFMResource instance which
                    # will provide the _usfm_chunks.
                    # if bool(self._usfm_chunks):
                    #     # Create links to each chapter
                    #     anchors += self._initialize_tn_chapter_verse_links(
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

                    links = self._initialize_tn_links(
                        book_has_intro, chapter_has_intro, chapter
                    )
                    tn_md += links + "\n\n"
            else:
                logger.debug(
                    "chapter_dir: {}, chapter: {}".format(chapter_dir, chapter)
                )

        self._content = tn_md

    @icontract.require(lambda self: self._resource_dir is not None)
    @icontract.require(lambda self: self._lang_code is not None)
    @icontract.require(lambda self: self._resource_type is not None)
    def _get_book_dir(self) -> str:
        """ Given the lang_code, resource_type, and resource_dir,
        generate the book directory. """
        filepath: str = os.path.join(
            self._resource_dir, "{}_{}".format(self._lang_code, self._resource_type)
        )
        logger.debug("self._lang_code: {}".format(self._lang_code))
        logger.debug("self._resource_type: {}".format(self._resource_type))
        logger.debug("self._resource_dir: {}".format(self._resource_dir))
        logger.debug("filepath: {}".format(filepath))
        if os.path.isdir(filepath):
            book_dir = filepath
        else:  # FIXME What case is this, I don't recall.
            logger.info("in else of _get_book_dir")
            book_dir = os.path.join(self._resource_dir, self._resource_code)
        return book_dir

    def _initialize_tn_book_intro(self, book_dir: str) -> Tuple[bool, str]:
        intro_file = os.path.join(book_dir, "front", "intro.md")
        book_has_intro = os.path.isfile(intro_file)
        md = ""
        if book_has_intro:
            md = file_utils.read_file(intro_file)
            title = get_first_header(md)
            # FIXME
            md = self._fix_tn_links(md, "intro")
            # FIXME
            md = self._increase_headers(md)
            # FIXME
            md = self._decrease_headers(md, 5)  # bring headers of 5 or more #'s down 1
            id_tag = '<a id="tn-{0}-front-intro"/>'.format(self._book_id)
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{0}\n".format(id_tag), md, 1)
            rc = "rc://{0}/tn/help/{1}/front/intro".format(
                self._lang_code, self._book_id
            )
            anchor_id = "tn-{}-front-intro".format(self._book_id)
            # FIXME This proaably will blow up.
            self._resource_data[rc] = {
                "rc": rc,
                "id": anchor_id,
                "link": "#{0}".format(anchor_id),
                "title": title,
            }
            self._my_rcs.append(rc)
            # FIXME
            self._get_resource_data_from_rc_links(md, rc)
            md += "\n\n"
        return (book_has_intro, md)

    def _initialize_tn_chapter_intro(
        self, chapter_dir: str, chapter: str
    ) -> Tuple[bool, str]:
        intro_file = os.path.join(chapter_dir, "intro.md")
        chapter_has_intro = os.path.isfile(intro_file)
        if chapter_has_intro:
            logger.info("chapter has intro")
            md = file_utils.read_file(intro_file)
            title = get_first_header(md)
            md = self._fix_tn_links(md, chapter)
            md = self._increase_headers(md)
            md = self._decrease_headers(
                md, 5, 2
            )  # bring headers of 5 or more #'s down 2
            id_tag = '<a id="tn-{}-{}-intro"/>'.format(
                self._book_id, self._pad(chapter)
            )
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{}\n".format(id_tag), md, 1)
            rc = "rc://{}/tn/help/{}/{}/intro".format(
                self._lang_code, self._book_id, self._pad(chapter),
            )
            anchor_id = "tn-{}-{}-intro".format(self._book_id, self._pad(chapter))
            self._resource_data[rc] = {
                # self.resource_data[rc] = {
                "rc": rc,
                "id": anchor_id,
                "link": "#{}".format(anchor_id),
                "title": title,
            }
            self._my_rcs.append(rc)
            # self.my_rcs.append(rc)
            self._get_resource_data_from_rc_links(md, rc)
            md += "\n\n"
            return (chapter_has_intro, md)
        else:
            logger.info("chapter has no intro")
            return (chapter_has_intro, "")

    def _fix_tn_links(self, text: str, chapter: str) -> str:
        rep = {
            re.escape(
                # TODO localization
                "**[2 Thessalonians intro](../front/intro.md)"
                # TODO localization
            ): "**[2 Thessalonians intro](../front/intro.md)**",
            r"\]\(\.\./\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tn/help/\1)".format(
                self._lang_code
            ),
            r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tn/help/{}/\1)".format(
                self._lang_code, self._book_id
            ),
            r"\]\(\./([^)]+?)(\.md)*\)": r"](rc://{}/tn/help/{}/{}/\1)".format(
                self._lang_code, self._book_id, self._pad(chapter),
            ),
            r"\n__.*\|.*": r"",
        }
        for pattern, repl in rep.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE | re.MULTILINE)
        return text

    def _initialize_tn_chapter_files(
        self, chunk_file: str, chapter: str
    ) -> Tuple[str, Optional[str], str, str]:
        first_verse = os.path.splitext(os.path.basename(chunk_file))[0].lstrip("0")
        logger.debug("first_verse: {}".format(first_verse))
        # FIXME TNResource doesn't have self._usfm_chunks
        # logger.debug("self._usfm_chunks: {}".format(self._usfm_chunks))
        # if bool(self._usfm_chunks):
        #     last_verse = self._usfm_chunks["ulb"][chapter][first_verse]["last_verse"]
        # else:
        #     last_verse = None
        last_verse = None
        if last_verse is not None and first_verse != last_verse:
            title = "{} {}:{}-{}".format(
                self._book_title,
                chapter,
                first_verse,
                last_verse
                # self.book_title, chapter, first_verse, last_verse
            )
        else:
            title = "{} {}:{}".format(
                self._book_title,
                chapter,
                first_verse
                # self.book_title, chapter, first_verse
            )
        md = self._increase_headers(file_utils.read_file(chunk_file), 3)
        md = self._decrease_headers(md, 5)  # bring headers of 5 or more #'s down 1
        md = self._fix_tn_links(md, chapter)
        # TODO localization
        md = md.replace("#### Translation Words", "### Translation Words")
        return (first_verse, last_verse, title, md)

    # FIXME This should possibly have a USFMResource instance passed
    # in as parameter for the sake of self._usfm_chunks
    def _initialize_tn_chapter_verse_links(
        self, usfm_resource: USFMResource, chapter: str, first_verse: str
    ) -> str:
        anchors = ""
        try:
            for verse in usfm_resource._usfm_chunks["ulb"][chapter][first_verse][
                "verses"
            ]:
                anchors += '<a id="tn-{}-{}-{}"/>'.format(
                    self._book_id, self._pad(chapter), self._pad(verse),
                )
        except:
            pass  # TODO
        logger.debug("anchors: {}".format(anchors))
        return anchors

    # FIXME This should probably be moved to TWResource
    def _initialize_tn_translation_words(self, chapter: str, first_verse: str) -> str:
        # Add Translation Words for passage
        tw_md = ""
        # FIXME This should probably become _tw_refs_by_verse on TWResource
        if self.tw_refs_by_verse:
            tw_refs = get_tw_refs(
                self.tw_refs_by_verse,
                self._book_title,
                chapter,
                first_verse
                # self.tw_refs_by_verse, self.book_title, chapter, first_verse
            )
            if tw_refs:
                # TODO localization
                tw_md += "### Translation Words\n\n"
                for tw_ref in tw_refs:
                    file_ref_md = "* [{}](rc://en/tw/dict/bible/{}/{})\n".format(
                        tw_ref["Term"], tw_ref["Dir"], tw_ref["Ref"]
                    )
                    tw_md += file_ref_md
        return tw_md

    # FIXME This doesn't belong on TNResource. It should be in
    # USFMResource. There are two types of USFM: ULB and UDB.
    # Currently we only have USFMResource for both. Should we have
    # ULBResource, UDBResource, and maybe USFMResource also? I need to
    # think about this.
    def _initialize_tn_udb(
        self, chapter: str, title: str, first_verse: str, last_verse: str
    ) -> str:
        # TODO Handle when there is no USFM requested.
        # If we're inside a UDB bridge, roll back to the beginning of it
        udb_first_verse = first_verse
        udb_first_verse_ok = False
        while not udb_first_verse_ok:
            try:
                _ = self._usfm_chunks["udb"][chapter][udb_first_verse]["usfm"]
                udb_first_verse_ok = True
            except KeyError:
                udb_first_verse_int = int(udb_first_verse) - 1
                if udb_first_verse_int <= 0:
                    break
                udb_first_verse = str(udb_first_verse_int)

        # TODO localization
        md = "### Unlocked Dynamic Bible\n\n[[udb://{}/{}/{}/{}/{}]]\n\n".format(
            self._lang_code,
            self._book_id,
            self._pad(chapter),
            self._pad(udb_first_verse),
            self._pad(last_verse),
        )
        rc = "rc://{}/tn/help/{}/{}/{}".format(
            self._lang_code, self._book_id, self._pad(chapter), self._pad(first_verse),
        )
        anchor_id = "tn-{}-{}-{}".format(
            self._book_id, self._pad(chapter), self._pad(first_verse),
        )
        self._resource_data[rc] = {
            # self.resource_data[rc] = {
            "rc": rc,
            "id": anchor_id,
            "link": "#{}".format(anchor_id),
            "title": title,
        }
        self._my_rcs.append(rc)
        self._get_resource_data_from_rc_links(md, rc)
        md += "\n\n"
        return md

    def _initialize_tn_links(
        self, book_has_intro: bool, chapter_has_intro: bool, chapter: str
    ) -> str:
        # TODO localization
        links = "### Links:\n\n"
        if book_has_intro:
            links += "* [[rc://{}/tn/help/{}/front/intro]]\n".format(
                self._lang_code, self._book_id
            )
        if chapter_has_intro:
            links += "* [[rc://{0}/tn/help/{1}/{2}/intro]]\n".format(
                self._lang_code, self._book_id, self._pad(chapter),
            )
        links += "* [[rc://{0}/tq/help/{1}/{2}]]\n".format(
            self._lang_code, self._book_id, self._pad(chapter),
        )
        return links


class TWResource(TResource):
    def get_content(self) -> None:
        logger.info("Processing Translation Words Markdown...")
        self._get_tw_markdown()
        # FIXME
        # self._replace_rc_links()
        ## self._fix_links()
        # self._content = fix_links(self._content)
        logger.info("Converting MD to HTML...")
        self._convert_md2html()
        logger.debug("self._bad_links: {}".format(self._bad_links))

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
            md = self._increase_headers(md)
            uses = self._get_uses(rc)
            if uses == "":
                continue
            md += uses
            md += "\n\n"
            tw_md += md
        # TODO localization
        tw_md = remove_md_section(tw_md, "Bible References")
        # TODO localization
        tw_md = remove_md_section(tw_md, "Examples from the Bible stories")

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
        logger.debug("self._bad_links: {}".format(self._bad_links))

    # def _get_tq_markdown(self) -> str:
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
                id_tag = '<a id="tq-{}-{}"/>'.format(self._book_id, self._pad(chapter))
                tq_md += "## {} {}\n{}\n\n".format(self._book_title, chapter, id_tag)
                # TODO localization
                title = "{} {} Translation Questions".format(self._book_title, chapter)
                rc = "rc://{}/tq/help/{}/{}".format(
                    self._lang_code, self._book_id, self._pad(chapter)
                )
                anchor_id = "tq-{}-{}".format(self._book_id, self._pad(chapter))
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
                        md = self._increase_headers(md, 2)
                        md = re.compile("^([^#\n].+)$", flags=re.M).sub(
                            r'\1 [<a href="#tn-{}-{}-{}">{}:{}</a>]'.format(
                                self._book_id,
                                self._pad(chapter),
                                self._pad(first_verse),
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
                            self._pad(chapter),
                            self._pad(first_verse),
                        )
                        anchor_id = "tq-{}-{}-{}".format(
                            self._book_id, self._pad(chapter), self._pad(first_verse)
                        )
                        self._resource_data[rc] = {
                            "rc": rc,
                            "id": anchor_id,
                            "link": "#{}".format(anchor_id),
                            "title": title,
                        }
                        self._my_rcs.append(rc)
                        self._get_resource_data_from_rc_links(md, rc)
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
        logger.debug("self._bad_links: {}".format(self._bad_links))

    # def _get_ta_markdown(self) -> str:
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
            md = self._increase_headers(md)
            md += self._get_uses(rc)
            md += "\n\n"
            ta_md += md
        logger.debug("ta_md is {0}".format(ta_md))
        self._content = ta_md
        # return ta_md

    # FIXME This legacy code is a mess of mixed up concerns. This
    # method is called from tn and tq concerned code so when we move
    # it it will probably have to live in a module that can be mixed
    # into both TNResource and TQResource or the method itself will be
    # teased apart so that conditionals are reduced and code paths
    # pertaining to the instance are the only ones preserved in the
    # instances version of this method.
    def _get_resource_data_from_rc_links(self, text: str, source_rc: str) -> None:
        for rc in re.findall(
            r"rc://[A-Z0-9/_-]+", text, flags=re.IGNORECASE | re.MULTILINE
        ):
            parts = rc[5:].split("/")
            resource_tmp = parts[1]
            path = "/".join(parts[3:])
            logger.debug(
                "parts: {}, resource_tmp: {}, path: {}".format(
                    parts, resource_tmp, path
                )
            )

            if rc not in self._my_rcs:
                self._my_rcs.append(rc)
            if rc not in self._rc_references:
                self._rc_references[rc] = []
            self._rc_references[rc].append(source_rc)

            if rc not in self._resource_data:
                title = ""
                t = ""
                anchor_id = "{}-{}".format(resource_tmp, path.replace("/", "-"))
                link = "#{}".format(anchor_id)
                try:
                    file_path = os.path.join(
                        self._working_dir,
                        "{}_{}".format(self._lang_code, resource_tmp),
                        "{}.md".format(path),
                    )
                    if not os.path.isfile(file_path):
                        file_path = os.path.join(
                            self._working_dir,
                            "{}_{}".format(self._lang_code, resource_tmp),
                            "{}/01.md".format(path),
                        )
                    if os.path.isfile(file_path):
                        t = file_utils.read_file(file_path)
                        title_file = os.path.join(
                            os.path.dirname(file_path), "title.md"
                        )
                        question_file = os.path.join(
                            os.path.dirname(file_path), "sub-title.md"
                        )
                        if os.path.isfile(title_file):
                            title = file_utils.read_file(title_file)
                        else:
                            title = get_first_header(t)
                        if os.path.isfile(question_file):
                            question = file_utils.read_file(question_file)
                            # TODO localization?
                            question = "This page answers the question: *{}*\n\n".format(
                                question
                            )
                        else:
                            question = ""
                        t = "# {}\n\n{}{}".format(title, question, t)
                        t = self._fix_ta_links(t, path.split("/")[0])
                    else:
                        # TODO bad_links doesn't exist yet, but should
                        # be on resources dict.
                        if rc not in self._bad_links:
                            self._bad_links[rc] = []
                        self._bad_links[rc].append(source_rc)
                except:
                    # TODO
                    if rc not in self._bad_links:
                        self._bad_links[rc] = []
                    self._bad_links[rc].append(source_rc)
                self._resource_data[rc] = {
                    "rc": rc,
                    "link": link,
                    "id": anchor_id,
                    "title": title,
                    "text": t,
                }
                if t:
                    self._get_resource_data_from_rc_links(t, rc)

    def _fix_ta_links(self, text: str, manual: str) -> str:
        rep = {
            r"\]\(\.\./([^/)]+)/01\.md\)": r"](rc://{0}/ta/man/{1}/\1)".format(
                self._lang_code, manual
            ),
            r"\]\(\.\./\.\./([^/)]+)/([^/)]+)/01\.md\)": r"](rc://{}/ta/man/\1/\2)".format(
                self._lang_code
            ),
            r"\]\(([^# :/)]+)\)": r"](rc://{}/ta/man/{}/\1)".format(
                self._lang_code, manual
            ),
        }
        for pattern, repl in rep.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text


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


def get_first_header(text: str) -> str:
    lines = text.split("\n")
    if lines:
        for line in lines:
            if re.match(r"^ *#+ ", line):
                return re.sub(r"^ *#+ (.*?) *#*$", r"\1", line)
        return lines[0]
    return "NO TITLE"


def remove_md_section(md: str, section_name: str) -> str:
    """ Given markdown and a section name, removes the section and the text contained in the section. """
    header_regex = re.compile("^#.*$")
    section_regex = re.compile("^#+ " + section_name)
    out_md = ""
    in_section = False
    for line in md.splitlines():
        if in_section:
            if header_regex.match(line):
                # We found a header.  The section is over.
                out_md += line + "\n"
                in_section = False
        else:
            if section_regex.match(line):
                # We found the section header.
                in_section = True
            else:
                out_md += line + "\n"
    return out_md


class ResourceProvisioner:
    """
    This class handles creating the necessary directory for a resource
    adn then acquiring the resource instance's file assets into the
    directory.
    """

    def __init__(self, resource: Resource):
        self._resource = resource

    def provision(self) -> None:
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
