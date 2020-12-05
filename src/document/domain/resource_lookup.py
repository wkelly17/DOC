from typing import Dict, List, Optional, Set, Tuple, Union
import abc
import icontract
import os
from datetime import datetime, timedelta
import pathlib
import pprint
import tempfile

import json  # Just for test debug output

from jsonpath_rw import jsonpath
from jsonpath_rw_ext import parse
import jsonpath_rw_ext as jp
import urllib.request, urllib.parse, urllib.error

# Handle running in container or as standalone script
# try:
from document.utils import file_utils
from document.utils import url_utils
from document import config

# from document.domain.resource import (
#     Resource,
#     USFMResource,
#     TNResource,
#     TWResource,
#     TQResource,
#     TAResource,
# )

# except:
#     from .document.utils.file_utils import load_json_object  # type: ignore
#     from .document.utils.url_utils import download_file  # type: ignore
#     from .document.config import (  # type: ignore
#         get_translations_json_location,
#         get_individual_usfm_url_jsonpath,
#         get_resource_url_level_1_jsonpath,
#         get_resource_url_level_2_jsonpath,
#         get_resource_download_format_jsonpath,
#         get_logging_config_file_path,
#         get_working_dir,
#         get_english_repos_dict,
#     )
#     from .document.domain.resource import (
#         Resource,
#         USFMResource,
#         TNResource,
#         TWResource,
#         TQResource,
#         TAResource,
#     )

# from .resource_utils import resource_has_markdown_files

import yaml
import logging
import logging.config

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)


logger = logging.getLogger(__name__)

AResource = Union[USFMResource, TAResource, TNResource, TQResource, TWResource]


class ResourceLookup(abc.ABC):
    """ Abstract base class that formalizes resource lookup. Currently
    we do lookup via JSON and translations.json, but later we may use
    a GraphQL API. The interface (hopefully) doesn't have to change (much)
    and thus call sites in client code can remain largely unchanged. """

    @abc.abstractmethod
    def lookup(self, resource: AResource) -> Optional[str]:
        raise NotImplementedError


class ResourceJsonLookup(ResourceLookup):
    """ A class that let's you download the translations.json file and
    retrieve values from it using jsonpath. """

    def __init__(
        self,
        working_dir: str = config.get_working_dir(),
        json_file_url: str = config.get_translations_json_location(),
    ) -> None:

        self._working_dir = working_dir
        self._json_file_url = json_file_url

        if not self._working_dir:
            logger.info("Creating working dir")
            self._working_dir = tempfile.mkdtemp(prefix="json_")

        logger.info("Working dir is {}".format(self._working_dir))

        self._json_file = pathlib.Path(
            os.path.join(
                self._working_dir, self._json_file_url.rpartition(os.path.sep)[2]
            )
        )

        logger.info("JSON file is {}".format(self._json_file))

        self._json_data: Dict = {}
        # NOTE Test running it here instead of in _lookup
        self._get_data()

    # protected access level
    @icontract.require(lambda self: self._json_file_url is not None)
    @icontract.require(lambda self: self._json_file is not None)
    @icontract.ensure(lambda self: self._json_data is not None)
    def _get_data(self) -> None:
        """ Download json data and parse it into equivalent python objects. """
        logger.info("About to check if we need new translations.json")
        if self._data_needs_update():
            # Download json file
            try:
                logger.info("Downloading {}...".format(self._json_file_url))
                url_utils.download_file(
                    self._json_file_url, str(self._json_file.resolve())
                )
            finally:
                logger.info("finished downloading json file.")

        if self._json_data is None:
            # Load json file
            try:
                logger.info("Loading json file {}...".format(self._json_file))
                self._json_data = file_utils.load_json_object(
                    self._json_file
                )  # json_data should possibly live on its own object
            finally:
                logger.info("Finished loading json file.")

    # protected
    @icontract.require(lambda self: self._json_file is not None)
    def _data_needs_update(self) -> bool:
        """ Given the json file path, return true if it has
        not been updated within 24 hours. """
        logger.info("About to check if translations.json needs update.")
        # Does the translations file exist?
        if not os.path.isfile(self._json_file):
            return True
        file_mod_time: datetime = datetime.fromtimestamp(
            os.stat(self._json_file).st_mtime
        )  # This is a datetime.datetime object!
        now: datetime = datetime.today()
        max_delay: timedelta = timedelta(minutes=60 * 24)
        # Has it been more than 24 hours since last modification time?
        return now - file_mod_time > max_delay

    # NOTE Some target languages only provide a resource at
    # $[*].contents[?name='reg'].links[?format='Download']. In that
    # case, grab the repo url from repo_url part of query string. Then
    # perhaps you'd want to use gitea to get the repo or git clone
    # directly with depth 1.
    # TODO Research: Do 'Read on Web' format resources have an associated git
    # repo if they don't have a sibling 'Download' format URL? I
    # looked at "erk-x-erakor" for intance and there one can see there
    # is no symmetry between the 'Read on Web' and 'Download' format
    # URLs that can be extrapolated to other language resources;
    # perhaps it can to a subset, but the relationship between the
    # 'Read on Web' and 'Download' format URLs seems to vary by
    # language and resource type.
    # NOTE ulb can be a zip or a git repo.
    @icontract.require(lambda self: self._json_data is not None)
    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.require(lambda resource: resource._resource_code is not None)
    @icontract.ensure(lambda result: result is not None)
    def lookup(self, resource: AResource) -> Optional[str]:
        """ Given a resource, comprised of language code, e.g., 'wum',
        a resource type, e.g., 'tn', and an optional resource code,
        e.g., 'gen', return URL for resource. """

        url: Optional[str] = None

        # Ironically, for English, translations.json file only
        # contains URLs to PDF assets. Therefore, we have this guard
        # to handle English resource requests separately and outside
        # of translations.json.
        # FIXME These conditionals are a code smell saying that the
        # code paths belong to the resource classes themselves.
        if resource._lang_code == "en":
            url = self._try_english_git_repo_location(resource)
        else:
            # FIXME Check the conditional logic flow to make sure we
            # aren't overwriting previously found URLs or doing
            # unnecessary work. The conditionals seems like a code smell
            # telling me that the code paths belong to different objects.
            # For instance, perhaps lookup and _lookup belong in Resource
            # subclasses as protected methods.
            if (
                resource._resource_type == "usfm"
            ):  # format='usfm' points to single USFM files.
                url = self._try_individual_usfm_location(resource)

            if url is None and resource._resource_type in [
                "reg",
                "ulb",
                "udb",
            ]:  # USFM files
                url = self._try_git_repo_location(resource)

            # FIXME This c/should probably live in a
            # TResourceJsonLookup that handles lookups for tn, tq, tw,
            # ta.
            if url is None or resource.has_markdown():
                url = self._try_markdown_files_level1_location(resource)
                if url is None:  # For the language in question, the resource is
                    # apparently at its alternative location which we try next.
                    url = self._try_markdown_files_level2_location(resource)

            if url is None and resource.has_markdown():
                url = self._try_markdown_files_level1_sans_resource_code_location(
                    resource
                )

            if url is None and resource.has_markdown():
                url = self._try_markdown_files_level2_sans_resource_code_location(
                    resource
                )

        return url

    @icontract.require(lambda resource: resource._lang_code == "en")
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda resource: resource._resource_file_format == "git")
    @icontract.ensure(lambda resource: resource._resource_url is not None)
    def _try_english_git_repo_location(self, resource: AResource) -> Optional[str]:
        """ If successful, return a string containing the URL of repo,
        otherwise return None. """
        url: Optional[str] = None
        url = config.get_english_repos_dict()[resource.resource_type]
        resource._resource_file_format = "git"
        # resource._resource_jsonpath is None for English git
        # repos because they can't be found in translations.json.
        resource._resource_jsonpath = None
        resource._resource_url = url
        return url

    # FIXME This probably should live in a USFMResourceJsonLookup # class.
    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.require(lambda resource: resource._resource_code is not None)
    @icontract.ensure(lambda resource: resource._resource_file_format == "git")
    @icontract.ensure(lambda resource: resource._resource_jsonpath is not None)
    def _try_git_repo_location(self, resource: AResource) -> Optional[str]:
        """ If successful, return a string containing the URL of USFM
        repo, otherwise return None. """
        jsonpath_str = get_resource_download_format_jsonpath().format(
            resource._lang_code, resource._resource_type, resource._resource_code,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            # Get the portion of the query string that gives
            # the repo URL
            url = self._parse_repo_url_from_json_url(urls[0])
        resource._resource_file_format = "git"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        logger.debug(
            "resource._resource_url: {} for {}".format(resource._resource_url, resource)
        )
        return url

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.require(lambda resource: resource._resource_code is not None)
    @icontract.ensure(lambda resource: resource._resource_file_format == "usfm")
    @icontract.ensure(lambda resource: resource._resource_jsonpath is not None)
    def _try_individual_usfm_location(self, resource: AResource) -> Optional[str]:
        """ If successful, return a string containing the URL of USFM
        file, otherwise None. """
        # Many languages have a git repo found by
        # format='Download' that is parallel to the
        # individual, per book, USFM files.
        #
        # There is at least one language, code='ar', that has only
        # single USFM files. In that particular language all the
        # individual USFM files per book can also be found in a zip
        # file,
        # $[?code='ar'].contents[?code='nav'].links[format='zip'],
        # which also contains the manifest.yaml file.
        # That language is the only one with a
        # contents[?code='nav'].
        #
        # Another, yet different, example is the case of
        # $[?code="avd"] which has format="usfm" without
        # having a zip containing USFM files at the same level.
        jsonpath_str = get_individual_usfm_url_jsonpath().format(
            resource._lang_code, resource._resource_type, resource._resource_code,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        resource._resource_file_format = "usfm"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda resource: resource._resource_file_format == "zip")
    @icontract.ensure(lambda resource: resource._resource_jsonpath is not None)
    def _try_markdown_files_level1_location(self, resource: AResource) -> Optional[str]:
        """ If successful, return a string containing the URL of
        Markdown zip file, otherwise return None. """
        jsonpath_str = get_resource_url_level_1_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda resource: resource._resource_file_format == "zip")
    @icontract.ensure(lambda resource: resource._resource_jsonpath is not None)
    def _try_markdown_files_level2_location(self, resource: AResource) -> Optional[str]:
        """ If successful, return a string containing the URL of
        Markdown zip file, otherwise return None. """
        jsonpath_str = get_resource_url_level_2_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda resource: resource._resource_file_format == "zip")
    @icontract.ensure(lambda resource: resource._resource_jsonpath is not None)
    def _try_markdown_files_level1_sans_resource_code_location(
        self, resource: AResource
    ) -> Optional[str]:
        """ If successful, return a string containing the URL of the
        Markdown zip file, otherwise return None. """
        # Some languages, e.g., code='as', have all of their
        # translation notes, 'tn', for all chapters in all books in
        # one zip file which is found at the book level, but not at
        # the chapter level of the translations.json file.
        jsonpath_str = get_resource_url_level_1_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda resource: resource._resource_file_format == "zip")
    @icontract.ensure(lambda resource: resource._resource_jsonpath is not None)
    def _try_markdown_files_level2_sans_resource_code_location(
        self, resource: AResource
    ) -> Optional[str]:
        """ For the language in question, the resource is apparently
        at its alternative location which we try next. If successful,
        return a string containing the URL of the Markdown zip file,
        otherwise return None."""
        jsonpath_str = get_resource_url_level_2_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    # protected
    @icontract.require(lambda self: self._json_data is not None)
    @icontract.require(lambda jsonpath: jsonpath is not None)
    @icontract.ensure(lambda result: result is not None)
    def _lookup(self, jsonpath: str,) -> List[str]:
        """ Return jsonpath value or empty list if node doesn't exist. """
        # self._get_data()
        logger.info("jsonpath: {}".format(jsonpath))
        value: List[str] = jp.match(
            jsonpath, self._json_data,
        )
        value_set: Set = set(value)
        return list(value_set)

    # protected
    # FIXME Add contracts
    def _parse_repo_url_from_json_url(
        self,
        url: Optional[str],
        repo_url_dict_key: str = "../download-scripture?repo_url",
    ) -> Optional[str]:
        """ Given a URL of the form
        ../download-scripture?repo_url=https%3A%2F%2Fgit.door43.org%2Fburje_duro%2Fam_gen_text_udb&book_name=Genesis,
        return the repo_url query parameter value. """
        # TODO Try ./download-scripture?repo_url if the default
        # doesn't work since some languages use the latter query key.
        if url is None:
            return None
        result: dict = urllib.parse.parse_qs(url)
        result_lst: List = result[repo_url_dict_key]
        if result_lst is not None and len(result_lst) > 0:
            return result_lst[0]
        else:
            return None

    @icontract.require(lambda self: self._json_data is not None)
    @icontract.ensure(lambda result: result is not None)
    def lang_codes(self) -> List[str]:
        """ Convenience method that can be called from UI to get the
        set of all language codes available through API. Presumably
        this could be called to populate a dropdown menu. """
        # return list(sorted(set(self._lookup("$[*].code"))))
        # self._get_data()
        codes: List[str] = []
        for lang in self._json_data:
            codes.append(lang["code"])
        # return self._lookup("$[*].code")
        return codes

    @icontract.require(lambda self: self._json_data is not None)
    @icontract.ensure(lambda result: result is not None)
    @icontract.ensure(lambda result: len(result) > 0)
    def lang_codes_and_names(self) -> List[Tuple[str, str]]:
        """ Convenience method that can be called from UI to get the
        set of all language code, name tuples available through API.
        Presumably this could be called to populate a dropdown menu.
        """
        # self._get_data()
        codes_and_names: List[Tuple[str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self._json_data:
            codes_and_names.append((d["code"], d["name"]))
        return codes_and_names

    @icontract.ensure(lambda result: result is not None)
    @icontract.ensure(lambda result: len(result) > 0)
    def resource_types(self) -> List[str]:
        """ Convenience method that can be called, e.g., from the UI,
        to get the set of all resource types. """
        return self._lookup("$[*].contents[*].code")

    @icontract.ensure(lambda result: result is not None)
    @icontract.ensure(lambda result: len(result) > 0)
    def resource_codes(self) -> List[str]:
        """ Convenience method that can be called, e.g., from the UI,
        to get the set of all resource codes. """
        return self._lookup("$[*].contents[*].subcontents[*].code")
