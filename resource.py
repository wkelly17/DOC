from typing import Any, Dict, List, Optional, Tuple, Union
import abc
import bs4  # type: ignore
from glob import glob
import markdown  # type: ignore
import os
import pathlib
import re
import subprocess
import tempfile
from usfm_tools.transform import UsfmTransform  # type: ignore
import yaml

try:
    from url_utils import download_file  # type: ignore
    from file_utils import load_json_object, load_yaml_object, read_file, write_file, unzip  # type: ignore
    from resource_lookup import ResourceJsonLookup
    from bible_books import BOOK_NUMBERS, BOOK_NAMES  # type: ignore
    from config import get_logging_config_file_path, get_markdown_doc_file_names
except:
    from .url_utils import download_file  # type: ignore
    from .file_utils import load_json_object, load_yaml_object, read_file, write_file, unzip  # type: ignore
    from .resource_lookup import ResourceJsonLookup
    from .bible_books import BOOK_NUMBERS, BOOK_NAMES  # type: ignore
    from .config import get_logging_config_file_path, get_markdown_doc_file_names

import logging
import logging.config

with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

# FIXME This note could help for design doc. Needs updating. Resource
# (abstract super class), TWResource, TQResource, TAResource,
# OBSResource, USFMResource API on Resource superclass:
# find_location->List returns the url values via ResourceJsonLookup,
# get_files -> None handles downloading/cloning/unzipping,
# initialize_properties handles setting initial values for instance
# variables, get_content -> str. get_content would get USFM (chunks)
# if it is a USFMResource file, Markdown if it is a TNResource,
# TWResource, TQResource, TAResource, etc.. See USFMSharp's
# SelectMarker method for one way how to build the Resource subclasses
# based on lang_code, resource_type, resource_code, etc.. Then we want
# something like a DocumentAssembler that handles asking each Resource
# in turn for its content via get_content.


class Resource(abc.ABC):
    """ Reification of the incoming document resource request
    fortified with additional state as instance variables. """

    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        lookup_svc: ResourceJsonLookup,
        resource: Dict,
    ) -> None:
        self._working_dir = working_dir
        self._output_dir = output_dir
        self._resource = resource
        self._lang_code = resource["lang_code"]
        self._resource_type = resource["resource_type"]
        self._resource_code = (
            resource["resource_code"] if resource["resource_code"] else None
        )
        self._resource_url: Optional[str] = None
        self._resource_dir: str = os.path.join(
            self._working_dir, "{}_{}".format(self._lang_code, self._resource_type)
        )
        self._p: pathlib.Path = pathlib.Path(self._resource_dir)
        self._resource_filename: Optional[str] = None
        self._resource_file_format: Optional[str] = None
        self._resource_filepath: Optional[str] = None
        self._bad_links: Dict = {}
        self._book_id: Optional[str] = None
        self._book_title: Optional[str] = None
        self._book_number: Optional[str] = None
        self._filename_base: Optional[str] = None
        self._manifest: Optional[Dict] = None
        self._manifest_file_path: Optional[pathlib.PurePath] = None
        self._manifest_file_dir: Optional[str] = None
        self._content_files: Optional[List[str]] = None
        self._manifest_type: Optional[str] = None
        self._version: Optional[str] = None
        self._issued: Optional[str] = None
        # NOTE We actually want to pass in the lookup_svc, not create
        # another one here - we don't want to load up the heap with
        # unnecessary ResourceJsonLookup objects. This assumes that
        # flask will handle each request in its own process. I.e., we
        # need to consider contention over Resources using the same
        # ResourceJsonLookup instance.
        self._lookup_svc: ResourceJsonLookup = lookup_svc
        self._content: str
        self._resource_data: Dict = {}
        self._my_rcs: List = []
        self._rc_references: Dict = {}
        self._resource_jsonpath: Optional[str] = None

    def __str__(self) -> Dict:
        # return vars(self)
        return "Resource(lang_code: {}, resource_type: {}, resource_code: {})".format(
            self._lang_code, self._resource_type, self._resource_code
        )

    # def __str__(self) -> None:
    #     return (
    #         self.__class__.__name__
    #         + "("
    #         + "working_dir="
    #         + self._working_dir
    #         + ", lang_code="
    #         + self._lang_code
    #         + ", resource_type="
    #         + self._resource_type
    #         + ", resource_code="
    #         + self._resource_code
    #         + ", resource_url="
    #         + self._resource_url
    #         + ", resource_dir="
    #         + self._resource_dir
    #         + ", resource_filename="
    #         + self._resource_filename
    #         + ", resource_file_format="
    #         + self._resource_file_format
    #         + ", resource_filepath="
    #         + self._resource_filepath
    #         + ", bad_links="
    #         + self._bad_links
    #         + ")"
    #     )

    # public
    def find_location(self) -> None:
        """ Find the URL where the resource's assets are located. """
        self._resource_url = self._lookup_svc.lookup(self)
        logger.debug("self._resource_url: {}".format(self._resource_url))

    # public
    def is_found(self) -> bool:
        "Return true if resource's URL location was found."
        return self._resource_url is not None

    # public
    def get_files(self) -> None:
        """ Using the resource's location"""
        self._prepare_resource_directory()
        # NOTE The initialization of resource file format is done in
        # resource_lookup module now in lookup method.
        self._initialize_resource_dir_for_git_repos()
        self._acquire_resource()

    # protected
    def _prepare_resource_directory(self) -> None:
        """ If it doesn't exist yet, create the directory for the
        resource where it will be downloaded to. """

        logger.debug("os.getcwd(): {}".format(os.getcwd()))
        if not os.path.exists(self._resource_dir):
            logger.debug("About to create directory {}".format(self._resource_dir))
            try:
                os.mkdir(self._resource_dir)
                logger.debug("Created directory {}".format(self._resource_dir))
            except:
                logger.exception(
                    "Failed to create directory {}".format(self._resource_dir)
                )

    def _initialize_resource_dir_for_git_repos(self) -> None:
        """ Git repos have a difference _resource_dir location and so
        must be handled differently. """
        if self._is_git():
            filename: str = self._resource_url.rpartition(os.path.sep)[2]
            # Git repo has an extra layer of depth directory
            self._resource_dir = os.path.join(self._resource_dir, filename)

    # protected
    def _acquire_resource(self) -> None:
        """ Download or git clone resource and unzip resulting file if it
        is a zip file. """

        logger.debug("self._resource_url: {}".format(self._resource_url))

        # FIXME To ensure consistent directory naming for later
        # discovery, let's not use the url.rpartition(os.path.sep)[2].
        # Instead let's use a directory built from the parameters of
        # the (updated) resource:
        # os.path.join(resource["resource_dir"], resource["resource_type"])
        logger.debug(
            "os.path.join(self._resource_dir, self._resource_type): {}".format(
                os.path.join(self._resource_dir, self._resource_type)
            )
        )
        self._resource_filepath = os.path.join(
            self._resource_dir, self._resource_url.rpartition(os.path.sep)[2]
        )
        logger.debug(
            "Using file location, _resource_filepath: {}".format(
                self._resource_filepath
            )
        )

        if self._is_git():  # Is a git repo, so clone it.
            try:
                command: str = "git clone --depth=1 '{}' '{}'".format(
                    # FIXME self._resource_filepath used to be filepath
                    self._resource_url,
                    self._resource_filepath,
                )
                logger.debug("os.getcwd(): {}".format(os.getcwd()))
                logger.debug("git command: {}".format(command))
                subprocess.call(command, shell=True)
                logger.debug("git clone succeeded.")
                # Git repos get stored on directory deeper
                self._resource_dir = self._resource_filepath
            except:
                logger.debug("os.getcwd(): {}".format(os.getcwd()))
                logger.debug("git command: {}".format(command))
                logger.debug("git clone failed!")
        else:  # Is not a git repo, so just download it.
            try:
                logger.debug(
                    "Downloading {} into {}".format(
                        self._resource_url, self._resource_filepath
                    )
                )
                download_file(self._resource_url, self._resource_filepath)
            finally:
                logger.debug("downloading finished.")

        if self._is_zip():  # Downloaded file was a zip, so unzip it.
            try:
                logger.debug(
                    "Unzipping {} into {}".format(
                        self._resource_filepath, self._resource_dir
                    )
                )
                unzip(self._resource_filepath, self._resource_dir)
            finally:
                logger.debug("unzipping finished.")

    # protected
    def _is_git(self) -> bool:
        """ Return true if _resource_file_format is equal to 'git'. """
        return self._resource_file_format == "git"

    # protected
    def _is_zip(self) -> bool:
        """ Return true if _resource_file_format is equal to 'zip'. """
        return self._resource_file_format == "zip"

    # protected
    def _is_usfm(self) -> bool:
        """ Return true if _resource_file_format is equal to 'usfm'. """
        return self._resource_file_format == "usfm"

    # protected
    def _is_yaml(self) -> bool:
        """ Return true if the resource's manifest file has suffix
        yaml. """
        return self._manifest_type == "yaml"

    # protected
    def _is_json(self) -> bool:
        """ Return true if the resource's manifest file has suffix
        json. """
        return self._manifest_type == "json"

    # NOTE Not sure about this one. Some instance variables are
    # settable in the constructor and some only after their associated
    # files are acquired.
    # NOTE This may not end up as part of the Resource API. So far I
    # haven't used it for anything.
    @abc.abstractmethod
    def initialize_properties(self) -> None:
        raise NotImplementedError

    # protected
    def _discover_manifest(self) -> None:
        """ All subclasses need to at least find their manifest file,
        if it exists. Subclasses specialize this method to
        additionally initialize other disk layout related properties.
        """
        logger.debug("self._p: {}".format(self._p))
        manifest_file_list = list(self._p.glob("**/manifest.*"))
        self._manifest_file_path = (
            None if len(manifest_file_list) == 0 else list(manifest_file_list)[0]
        )
        logger.debug("self._manifest_file_path: {}".format(self._manifest_file_path))
        # Find directory where the manifest file is located
        if (
            self._manifest_file_path is not None
            and len(self._manifest_file_path.parents) > 0
        ):
            self._manifest_file_dir = self._manifest_file_path.parents[0]

        logger.debug("self._manifest_file_dir: {}".format(self._manifest_file_dir))

        if self._manifest_file_path is not None:
            if self._manifest_file_path.suffix == ".yaml":
                self._manifest = load_yaml_object(self._manifest_file_path)
                self._manifest_type = "yaml"
            elif self._manifest_file_path.suffix == ".txt":
                self._manifest = load_yaml_object(self._manifest_file_path)
                self._manifest_type = "txt"
            elif self._manifest_file_path.suffix == ".json":
                self._manifest = load_json_object(self._manifest_file_path)
                self._manifest_type = "json"
        else:
            logger.debug(
                "manifest file does not exist for resource {}.".format(
                    self._resource_type
                )
            )

        if self._manifest_type:
            logger.debug("self._manifest_type: {}".format(self._manifest_type))
        if self._manifest:
            logger.debug("self._manifest: {}".format(self._manifest))

        # NOTE manifest.txt files do not have 'dublin_core' or
        # 'version' keys.
        # TODO Handle manifest.json which has different fields.
        if self._manifest_type and self._is_yaml():
            if (
                # FIXME This next line doesn't type check with mypy
                0 in self._manifest
                and self._manifest[0]["dublin_core"]["version"] is not None
            ):
                self._version = self._manifest[0]["dublin_core"]["version"]
            elif (
                0 not in self._manifest
                and self._manifest["dublin_core"]["version"] is not None
            ):
                self._version = self._manifest["dublin_core"]["version"]
            self._issued = self._manifest["dublin_core"]["issued"]
            logger.debug(
                "_version: {}, _issued: {}".format(self._version, self._issued)
            )

    @abc.abstractmethod
    def get_content(self) -> None:
        raise NotImplementedError

    # protected
    def _pad(self, num: str) -> str:
        if self._book_id == "psa":
            # return str(num).zfill(3)
            return num.zfill(3)
        # return str(num).zfill(2)
        return num.zfill(2)

    def _get_uses(self, rc) -> str:
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
    def _get_resource_data_from_rc_links(self, text, source_rc) -> None:
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
                        t = read_file(file_path)
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

    # protected
    def _fix_tw_links(self, text: str, dictionary) -> str:
        rep = {
            r"\]\(\.\./([^/)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/{}/\1)".format(
                self._lang_code,
                dictionary
                # self.lang_code, dictionary
            ),
            r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/\1)".format(
                self._lang_code
            ),
        }
        for pattern, repl in rep.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text

    # protected
    def _increase_headers(self, text: str, increase_depth: int = 1) -> str:
        if text:
            text = re.sub(
                r"^(#+) +(.+?) *#*$",
                r"\1{0} \2".format("#" * increase_depth),
                text,
                flags=re.MULTILINE,
            )
        return text

    # protected
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
    #             # self.lang_code, resource, self.book_id, chapter, verse
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
    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        lookup_svc: ResourceJsonLookup,
        resource: Dict,
    ) -> None:
        # I am not sure if this is the right design to call the
        # super's constructor. I may end up not having an __init__ in
        # the abstract superclass and instead just implementing it in
        # each subclass since they might need to be very different
        # from one another. Basically, this is a WIP.
        super().__init__(working_dir, output_dir, lookup_svc, resource)
        # TODO Add anything else that should be initialized in a
        # resource. It may be the case that not all initialization can
        # happen at once since some initialization can only happen
        # after the resources files have been acquired.
        self._usfm_chunks: Dict = {}

    # FIXME This is probably too tricky for others to read and it
    # doesn't type check with mypy. If I rewrite this then I'll have
    # to add __repr__ and __str__ methods to other subclasses too.
    # def __repr__(self) -> Dict:
    #     return (
    #         super(USFMResource, self)
    #         .__repr__()
    #         .update({"usfm_chunks": self._usfm_chunks})
    #     )

    # def __str__(self) -> str:
    #     s = "USFMResource" + "("
    #     for k, v in self.__repr__().items():
    #         s += k + "=" + v
    #     s += ")"
    #     return s

    # NOTE Maybe we'll do inversion of control by passing in a
    # ResourceJsonLookup instance and call its lookup method passing
    # the params needed from self.
    def find_location(self) -> None:
        super().find_location()

    # public
    def get_files(self) -> None:
        super().get_files()

    # public
    def initialize_properties(self) -> None:
        self._discover_layout()

        # FIXME This likely can be better envisioned and implemented.
        if self._is_usfm():
            self._initialize_book_properties_when_no_manifest()
        elif self._is_git() and self._is_yaml():
            self._initialize_book_properties_from_manifest_yaml()
        elif self._is_git() and self._is_json():
            self._initialize_book_properties_from_manifest_json()

        # TODO Handle manifest.yaml, manifest.txt, and manifest.json
        # formats - they each have different structure and keys.
        # elif not self._is_git() and self._is_txt():

        # FIXME This may still be needed for non manifest.yaml cases,
        # but for manifest.yaml case it is initialized elsewhere.
        # NOTE Without this, things blow up on line 973.
        # self._initialize_filename_base()

    def _discover_layout(self):
        """ Explore the resource's downloaded files to initialize file
        structure related properties. """

        super()._discover_manifest()

        usfm_content_files = list(self._p.glob("**/*.usfm"))
        # markdown_files = list(q.glob("**/*.md"))
        # USFM files sometimes have txt suffix
        txt_content_files = list(self._p.glob("**/*.txt"))
        # Find the manifest file, if any

        # logger.debug("usfm_content_files: {}".format(usfm_content_files))

        if len(usfm_content_files) > 0:  # This resource does have USFM files
            # Only use the content files that match the resource_code
            # in the resource request.
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(),
                    usfm_content_files,
                )
            )
        elif len(txt_content_files) > 0:
            # Only use the content files that match the resource_code
            # in the resource request.
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(),
                    txt_content_files,
                )
            )

        logger.debug(
            "self._content_files for {}: {}".format(
                self._resource_code, self._content_files,
            )
        )

    # protected
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _initialize_book_properties_when_no_manifest(self) -> None:
        # NOTE USFM book files have form 01-GEN or GEN. So we lowercase
        # then split on hyphen and get second component to get
        # the book id.
        assert (
            self._is_usfm()
        ), "Calling _initialize_book_properties_when_no_manifest requires a USFM file-based resource"
        logger.debug("self._resource_filename: {}".format(self._resource_filename))
        if "-" in self._resource_filename:
            book_id = self._resource_filename.split("-")[1]
        else:
            book_id = self._resource_filename
        self._book_id = book_id.lower()
        logger.debug("book_id for usfm file: {}".format(self._book_id))
        self._book_title = BOOK_NAMES[self._resource_code]
        self._book_number = BOOK_NUMBERS[self._book_id]
        logger.debug("book_number for usfm file: {}".format(self._book_number))

    # protected
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _initialize_book_properties_from_manifest_yaml(self) -> None:
        # NOTE USFM book files have form 01-GEN or GEN. So we lowercase
        # then split on hyphen and get second component to get
        # the book id.
        assert (
            self._is_git()
        ), "Calling _initialize_book_properties_from_manifest_yaml requires a git repo"
        assert (
            self._is_yaml()
        ), "Calling _initialize_book_properties_from_manifest_yaml requires a manifest.yaml"
        projects: List[Dict[Any, Any]] = self._get_book_projects_from_yaml()
        logger.debug("book projects: {}".format(projects))
        for p in projects:
            project: Dict[Any, Any] = p
            self._book_id = p["identifier"]
            self._book_title = p["title"].replace(" translationNotes", "")
            self._book_number = BOOK_NUMBERS[self._book_id]
            # TODO This likely needs to change because of how we
            # build resource_dir
            self._filename_base = "{}_tn_{}-{}_v{}".format(
                self._lang_code,
                self._book_number.zfill(2),
                self._book_id.upper(),
                self._version,
            )
            # FIXME Is it necessary to reset _rc_references since
            # it is a per resource instance variable now?
            self._rc_references = {}
            # resource.update({"my_rcs": []})
            # FIXME Is it necessary to reset _my_rcs since
            # it is a per resource instance variable now?
            self._my_rcs = []
            logger.debug(
                "Creating {} for {} ({}-{})...".format(
                    self._resource_type,
                    self._book_title,
                    self._book_number,
                    self._book_id.upper(),
                )
            )

    # protected
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _initialize_book_properties_from_manifest_json(self) -> None:
        # NOTE USFM book files have form 01-GEN or GEN. So we lowercase
        # then split on hyphen and get second component to get
        # the book id.
        assert (
            self._is_git()
        ), "Calling _initialize_book_properties_from_manifest_json requires a git repo"
        assert (
            self._is_json()
        ), "Calling _initialize_book_properties_from_manifest_json requires manifest.json"
        logger.info("is json")
        # FIXME
        projects: List = self._get_book_projects_from_json()
        logger.debug("book projects: {}".format(projects))
        logger.debug("type of projects: {}".format(type(projects)))
        for p in projects:
            project: Dict[Any, Any] = p  # FIXME This is not used
            self._book_id = self._resource_code
            # self._book_id = p["identifier"]
            self._book_title = BOOK_NAMES[self._resource_code]
            # self._book_title = p["title"].replace(" translationNotes", "")
            self._book_number = BOOK_NUMBERS[self._book_id]
            # TODO This likely needs to change because of how we
            # build resource_dir
            self._filename_base = "{}_tn_{}-{}_v{}".format(
                self._lang_code,
                self._book_number.zfill(2),
                self._book_id.upper(),
                self._version,
            )
            # FIXME Is it necessary to reset _rc_references since
            # it is a per resource instance variable now?
            self._rc_references = {}
            # resource.update({"my_rcs": []})
            # FIXME Is it necessary to reset _my_rcs since
            # it is a per resource instance variable now?
            self._my_rcs = []
            logger.debug(
                "Creating {} for {} ({}-{})...".format(
                    self._resource_type,
                    self._book_title,
                    self._book_number,
                    self._book_id.upper(),
                )
            )

    # protected
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _get_book_projects_from_yaml(self) -> List[Dict[Any, Any]]:
        """ Return the sorted list of projects that are found in the
        manifest file for the resource. """

        projects: List[Dict[Any, Any]] = []
        if (
            self._manifest and "projects" in self._manifest
        ):  # This is the manifest.yaml case.
            logger.info("about to get projects")
            for p in self._manifest["projects"]:
                # for p in self.manifest["projects"]:
                # NOTE You can have a manifest.yaml file and not have a
                # resource_code specified, e.g., lang_code='as',
                # resource_type='tn', resource_code=''
                # FIXME Is this correct?
                if (
                    self._resource_code is not None
                    and p["identifier"] in self._resource_code
                ):
                    # if not self.books or p["identifier"] in self.books:
                    if not p["sort"]:
                        p["sort"] = BOOK_NUMBERS[p["identifier"]]
                    projects.append(p)
            return sorted(projects, key=lambda k: k["sort"])
        else:
            logger.info("empty projects check is true...")
            return projects

    # protected
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

    # protected
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _initialize_filename_base(self) -> None:
        assert (
            self._book_id
        ), "self._book_id didn't get initialized in _initialize_book_properties"
        assert (
            self._book_title
        ), "self._book_title didn't get initialized in _initialize_book_properties"
        assert (
            self._book_number
        ), "self._book_number didn't get initialized in _initialize_book_properties"

        self._filename_base = "{}_{}_{}-{}".format(
            self._lang_code,
            self._resource_type,
            self._book_number.zfill(2),
            self._book_id.upper(),
        )
        # FIXME Should we be using self._filename_base or
        # self._resource_dir combined with self._resource_filename?
        logger.debug("filename_base: {}".format(self._filename_base))

    # public
    def get_content(self) -> None:
        self._get_usfm_chunks()
        # logger.debug("self._resource_filename: {}".format(self._resource_filename))

        filename = "{}_{}_{}".format(
            self._lang_code, self._resource_type, self._resource_filename,
        )
        logger.debug(
            "About to suck up files from {} and output the result to {}".format(
                self._resource_dir, self._output_dir
            )
        )
        # Create the USFM to HTML and store in file.
        UsfmTransform.buildSingleHtmlFromFiles(
            # self._resource_dir,
            self._content_files,
            self._output_dir,
            filename,
        )
        # Read the HTML file into _content.
        self._content = read_file("{}/{}.html".format(self._output_dir, filename))
        # self._content = read_file("{}/{}.md".format(self._output_dir, filename))
        logger.debug("self._bad_links: {}".format(self._bad_links))

    # protected
    # FIXME Handle git based usfm with resources.json file and .txt usfm
    # file suffixes.
    # FIXME This is game for rewrite or removal considering new
    # approach in _discover_layout using pathlib.
    def _get_usfm_chunks(self) -> None:
        book_chunks: dict = {}

        # logger.debug(
        #     "is_yaml: {}, is_json: {}".format(self._is_yaml(), self._is_json())
        # )

        # FIXME Not sure I ever needed this conditional
        if self._is_yaml():  # Layout of resource having manifest.yaml
            logger.debug(
                "About to read: {}".format(
                    "{}/{}.usfm".format(self._resource_dir, self._resource_filename)
                )
            )
            # FIXME Consider: self._content_files gives the correct path instead
            # of this. Whether or not it is wise to use
            # self._content_files instead of the next line is yet to
            # be analyzed.
            usfm = read_file(
                self._content_files[0],
                # os.path.join(
                #     "{}/{}.usfm".format(self._resource_dir, self._resource_filename)
                # ),
                "utf-8",
            )
        elif self._is_json():  # Layout of resource having manifest.json
            # FIXME Properties are not initialized properly for this
            # case prior to reaching this point.
            logger.debug(
                "About to read: {}".format(
                    "{}/{}.usfm".format(self._resource_dir, self._resource_filename)
                )
            )
            usfm = read_file(
                os.path.join(
                    "{}/{}.usfm".format(self._resource_dir, self._resource_filename)
                ),
                "utf-8",
            )
        else:  # No manifest file
            logger.debug(
                "About to read: {}".format(
                    "{}/{}.usfm".format(self._resource_dir, self._resource_filename)
                )
            )
            usfm = read_file(
                os.path.join(
                    "{}/{}.usfm".format(self._resource_dir, self._resource_filename)
                ),
                "utf-8",
            )

        chunks = re.compile(r"\\s5\s*\n*").split(usfm)

        # Break chunks into verses
        chunks_per_verse = []
        for chunk in chunks:
            pending_chunk = None
            for line in chunk.splitlines(True):
                # If this is a new verse and there's a pending chunk,
                # finish it and start a new one.
                if re.search(r"\\v", line) and pending_chunk:
                    chunks_per_verse.append(pending_chunk)
                    pending_chunk = None
                pending_chunk = pending_chunk + line if pending_chunk else line
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
        # logger.debug("self._usfm_chunks: {}".format(book_chunks))


# Only exists for a common interface for _convert_md2html
class TResource(Resource):
    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        lookup_svc: ResourceJsonLookup,
        resource: Dict,
    ) -> None:
        super().__init__(working_dir, output_dir, lookup_svc, resource)

    def _convert_md2html(self) -> None:
        """ Convert a resource's Markdown to HTML. """
        self._content = markdown.markdown(self._content)

    # protected
    # FIXME Bit of a legacy cluster. This used to be a function and
    # maybe still should be, but for now I've made it an instance
    # method.
    def _replace_rc_links(self) -> None:
        """ Given a resource's markdown text, replace links of the form [[rc://en/tw/help/bible/kt/word]] with links of the form [God's Word](#tw-kt-word). """
        logger.debug("self._content: {}".format(self._content))
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
        pattern = re.compile("|".join(list(rep.keys())))
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

    # protected
    # FIXME Bit of a legacy cluster. This used to be a function and
    # maybe still should be, but for now I've made it an instance
    # method.
    def _fix_links(self) -> None:
        rep = {}

        def replace_tn_with_door43_link(match):
            book = match.group(1)
            chapter = match.group(2)
            verse = match.group(3)
            if book in BOOK_NUMBERS:
                book_num = BOOK_NUMBERS[book]
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

    def _discover_layout(self):
        # Execute logic common to all resources
        super()._discover_manifest()

        # Get the content files
        markdown_files = list(self._p.glob("**/*.md"))
        markdown_content_files = filter(
            lambda x: str(x.stem).lower() not in get_markdown_doc_file_names(),
            markdown_files,
        )
        txt_files = list(self._p.glob("**/*.txt"))
        txt_content_files = filter(
            lambda x: str(x.stem).lower() not in get_markdown_doc_file_names(),
            txt_files,
        )

        if len(list(markdown_content_files)) > 0:
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(),
                    markdown_files,
                )
            )
        if len(list(txt_content_files)) > 0:
            self._content_files = list(
                filter(
                    lambda x: self._resource_code.lower() in str(x).lower(), txt_files,
                )
            )

        logger.debug(
            "self._content_files for {}: {}".format(
                self._resource_code, self._content_files,
            )
        )


class TNResource(TResource):
    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        lookup_svc: ResourceJsonLookup,
        resource: Dict,
    ) -> None:
        super().__init__(working_dir, output_dir, lookup_svc, resource)

    def find_location(self) -> None:
        super().find_location()

    def get_files(self) -> None:
        super().get_files()

    def initialize_properties(self) -> None:
        # FIXME Assess the file type being used, e.g., txt, tsv, md
        super().initialize_properties()

    def get_content(self) -> None:
        logger.info("Processing Translation Notes Markdown...")
        self._get_tn_markdown()
        # FIXME
        self._replace_rc_links()
        self._fix_links()
        logger.info("Converting MD to HTML...")
        self._convert_md2html()
        logger.debug("self._bad_links: {}".format(self._bad_links))

    # protected
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
                chunk_files = sorted(glob(os.path.join(chapter_dir, "[0-9]*.md")))
                logger.debug("chunk_files: {}".format(chunk_files))
                for _, chunk_file in enumerate(chunk_files):
                    logger.info("in loop through chunk files")
                    (
                        first_verse,
                        last_verse,
                        title,
                        md,
                    ) = self._initialize_tn_chapter_files(chunk_file, chapter)

                    anchors = ""
                    pre_md = ""
                    # FIXME I don't think it should be fetching USFM
                    # stuff here in this method.
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
                logger.info("Next log call is in else clause")
                logger.debug(
                    "chapter_dir: {}, chapter: {}".format(chapter_dir, chapter)
                )

        # logger.debug("tn_md is {}".format(tn_md))
        self._content = tn_md
        # return tn_md

    def _get_book_dir(self) -> str:
        if os.path.isdir(
            os.path.join(
                self._resource_dir,
                "{}_{}".format(self._lang_code, self._resource_type),
            )
        ):
            # logger.info("here we are")
            logger.debug(
                "Here is the directory we expect: {}".format(
                    os.path.join(
                        self._resource_dir,
                        "{}_{}".format(self._lang_code, self._resource_type),
                    )
                )
            )
            # logger.debug(
            #     "self._resource_dir: {}, self._lang_code: {}, self._resource_type: {}, self._book_id: {}, self._resource_code: {}".format(
            #         self._resource_dir,
            #         self._lang_code,
            #         self._resource_type,
            #         self._book_id,
            #         self._resource_code,
            #     )
            # )
            # FIXME self._book_id can be None here
            book_dir = os.path.join(
                self._resource_dir,
                "{}_{}".format(self._lang_code, self._resource_type),
                # # self._book_id,
                # self._resource_code,
            )
        else:
            # book_dir = os.path.join(self._resource_dir, self._book_id)
            book_dir = os.path.join(self._resource_dir, self._resource_code)
        return book_dir

    def _initialize_tn_book_intro(self, book_dir: str) -> Tuple[bool, str]:
        intro_file = os.path.join(book_dir, "front", "intro.md")
        book_has_intro = os.path.isfile(intro_file)
        md = ""
        if book_has_intro:
            md = read_file(intro_file)
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
            md = read_file(intro_file)
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
        self, chunk_file, chapter
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
        md = self._increase_headers(read_file(chunk_file), 3)
        md = self._decrease_headers(md, 5)  # bring headers of 5 or more #'s down 1
        md = self._fix_tn_links(md, chapter)
        # TODO localization
        md = md.replace("#### Translation Words", "### Translation Words")
        return (first_verse, last_verse, title, md)

    # FIXME This should possibly live in a UDBResource
    def _initialize_tn_chapter_verse_links(self, chapter: str, first_verse: str) -> str:
        anchors = ""
        try:
            for verse in self._usfm_chunks["ulb"][chapter][first_verse]["verses"]:
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
    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        lookup_svc: ResourceJsonLookup,
        resource: Dict,
    ) -> None:
        super().__init__(working_dir, output_dir, lookup_svc, resource)

    def find_location(self) -> None:
        super().find_location()

    def get_files(self) -> None:
        super().get_files()

    def initialize_properties(self) -> None:
        super().initialize_properties()

    def get_content(self) -> None:
        logger.info("Processing Translation Words Markdown...")
        self._get_tw_markdown()
        # FIXME
        # self._replace_rc_links()
        # self._fix_links()
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
    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        lookup_svc: ResourceJsonLookup,
        resource: Dict,
    ) -> None:
        super().__init__(working_dir, output_dir, lookup_svc, resource)

    def find_location(self) -> None:
        super().find_location()

    def get_files(self) -> None:
        super().get_files()

    def initialize_properties(self) -> None:
        super().initialize_properties()

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
                        md = read_file(chunk_file)
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
    def __init__(
        self,
        working_dir: str,
        output_dir: str,
        lookup_svc: ResourceJsonLookup,
        resource: Dict,
    ) -> None:
        super().__init__(working_dir, output_dir, lookup_svc, resource)

    def find_location(self) -> None:
        super().find_location()

    def get_files(self) -> None:
        super().get_files()

    def initialize_properties(self) -> None:
        super().initialize_properties()

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
    def _get_resource_data_from_rc_links(self, text, source_rc) -> None:
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
                        t = read_file(file_path)
                        title_file = os.path.join(
                            os.path.dirname(file_path), "title.md"
                        )
                        question_file = os.path.join(
                            os.path.dirname(file_path), "sub-title.md"
                        )
                        if os.path.isfile(title_file):
                            title = read_file(title_file)
                        else:
                            title = get_first_header(t)
                        if os.path.isfile(question_file):
                            question = read_file(question_file)
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

    # protected
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


# QUESTION Do we need a resource code to create the right Resource
# subclass? At a basic level, all we need is the resource_type to
# determine the subclass of Resource to create. However, it might be
# nice to have special subclasses that use the resource_code to know
# how to retrieve a value differently based on its value. I think,
# however, that this will not be needed.
def ResourceFactory(
    working_dir: str, output_dir: str, lookup_svc: ResourceJsonLookup, resource: Dict
) -> Resource:
    """ Factory method. """
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
    return resources[resource["resource_type"]](
        working_dir, output_dir, lookup_svc, resource
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
