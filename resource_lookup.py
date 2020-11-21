from typing import Dict, List, Optional, Set, Tuple
import abc
import os
from datetime import datetime, timedelta
import pprint
import tempfile

import json  # Just for test debug output

from jsonpath_rw import jsonpath  # type: ignore
from jsonpath_rw_ext import parse  # type: ignore
import jsonpath_rw_ext as jp  # for calling extended methods
import urllib.request, urllib.parse, urllib.error

# Handle running in container or as standalone script
try:
    from file_utils import load_json_object
    from url_utils import download_file
    from config import (
        get_translations_json_location,
        get_individual_usfm_url_jsonpath,
        get_resource_url_level_1_jsonpath,
        get_resource_url_level_2_jsonpath,
        get_resource_download_format_jsonpath,
        get_logging_config_file_path,
        get_working_dir,
        get_english_repos_dict,
    )
    from resource_utils import resource_has_markdown_files
except:
    from .file_utils import load_json_object
    from .url_utils import download_file
    from .config import (
        get_translations_json_location,
        get_individual_usfm_url_jsonpath,
        get_resource_url_level_1_jsonpath,
        get_resource_url_level_2_jsonpath,
        get_resource_download_format_jsonpath,
        get_logging_config_file_path,
        get_working_dir,
        get_english_repos_dict,
    )
    from .resource_utils import resource_has_markdown_files

import yaml
import logging
import logging.config

with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


logger = logging.getLogger(__name__)


class ResourceLookup(abc.ABC):
    """ Abstract base class that formalizes resource lookup. Currently
    we do lookup via JSON and translations.json, but later we may use
    a GraphQL API. The interface (hopefully) doesn't have to change (much)
    and thus call sites in client code can remain largely unchanged. """

    @abc.abstractmethod
    def lookup(self, resource: Dict) -> List[Optional[str]]:
        raise NotImplementedError


class ResourceJsonLookup(ResourceLookup):
    """ A class that let's you download the translations.json file and
    retrieve values from it using jsonpath. """

    def __init__(
        self,
        working_dir: Optional[
            str
        ] = get_working_dir(),  # This is in /tools in the Docker container
        json_file_url: str = get_translations_json_location(),
    ) -> None:

        self.working_dir = working_dir
        self.json_file_url = json_file_url

        if not self.working_dir:
            logger.info("Creating working dir")
            self.working_dir = tempfile.mkdtemp(prefix="json_")

        logger.info("Working dir is {}".format(self.working_dir))

        self.json_file: str = os.path.join(
            self.working_dir, self.json_file_url.rpartition(os.path.sep)[2]
        )

        logger.info("JSON file is {}".format(self.json_file))

        self.json_data: Optional[Dict] = None

    # protected access level
    def _get_data(self) -> None:
        """ Download json data and parse it into equivalent python objects. """
        if self._data_needs_update():
            # Download json file
            try:
                logger.info("Downloading {}...".format(self.json_file_url))
                download_file(self.json_file_url, self.json_file)
            finally:
                logger.info("finished downloading json file.")

        if self.json_data is None:
            # Load json file
            try:
                logger.info("Loading json file {}...".format(self.json_file))
                self.json_data = load_json_object(
                    self.json_file
                )  # json_data should possibly live on its own object
            finally:
                logger.info("finished loading json file.")

    # protected access level
    def _data_needs_update(self) -> bool:
        """ Given the json file path, return true if it has
        not been updated within 24 hours. """
        # Does the translations file exist?
        if not os.path.isfile(self.json_file):
            return True
        file_mod_time: datetime = datetime.fromtimestamp(
            os.stat(self.json_file).st_mtime
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
    def lookup(self, resource) -> Optional[str]:
        """ Given a resource, comprised of language code, e.g., 'wum',
        a resource type, e.g., 'tn', and an optional resource code,
        e.g., 'gen', return URL for resource. """

        # resource._resource_code = (
        #     None if not resource._resource_code else resource._resource_code
        # )

        assert resource._lang_code is not None, "lang_code is required"
        assert resource._resource_type is not None, "resource_type is required"
        assert resource._resource_code is not None, "resource_code is required"

        # urls: List[str] = []
        url: Optional[str] = None

        # Ironically, English is not available in the
        # translations.json file in a useful form as there only URLs
        # to PDF assets can be obtained. Therefore, we have this guard
        # to handle English resource requests separately and outside
        # of translations.json.
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

            if (
                url is not None
                # and len(urls) == 0
                and resource._resource_type in ["reg", "ulb", "udb"]  # USFM files
            ):
                url = self._try_git_repo_location(resource)

            # FIXME This c/should probably live in a
            # TResourceJsonLookup that handles lookups for tn, tq, tw,
            # ta.
            if (url is not None) or resource_has_markdown_files(resource):  # Code smell
                url = self._try_markdown_files_level1_location(resource)
                if url is not None:  # For the language in question, the resource is
                    # apparently at its alternative location which we try next.
                    url = self._try_markdown_files_level2_location(resource)

            if (
                url is not None
                # and len(urls) == 0
                and resource_has_markdown_files(resource)
            ):
                url = self._try_markdown_files_level1_sans_resource_code_location(
                    resource
                )

            if url is not None:  # and len(urls) == 0:
                url = self._try_markdown_files_level2_sans_resource_code_location(
                    resource
                )

            # FIXME This comment may be incorrect now.
            # Store the jsonpath that was used as it will be used to
            # determine how to acquire the resource, e.g., if a jsonpath
            # was used that points to a git repo then the git client will
            # be used otherwise we download from a CDN.
            # resource._resource_jsonpath = jsonpath_str

        return url

    def _try_english_git_repo_location(self, resource) -> Optional[str]:
        """ If successful, return a string containing the URL of repo,
        otherwise return None. """
        url: Optional[str] = None
        url = get_english_repos_dict()[resource._resource_type]
        resource._resource_file_format = "git"
        # NOTE resource._resource_jsonpath is None for English git
        # repos because they can't be found in translations.json.
        resource._resource_jsonpath = None
        resource._resource_url = url
        return url

    # FIXME This probably should live in a USFMResourceJsonLookup # class.
    def _try_git_repo_location(self, resource) -> Optional[str]:
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
        # Code smell to produce a side effect here.
        resource._resource_file_format = "git"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    def _try_individual_usfm_location(self, resource) -> Optional[str]:
        """ If successful, return a string containing the URL of USFM
        file, otherwise None. """
        # FIXME This comment is outdated.
        # NOTE Many languages have a git repo found by
        # format='Download' that is parallel to the
        # individual, per book, USFM files and in that case
        # the git repo should be preferred. But there is at
        # least one language, code='ar', that has only single
        # USFM files. In that particular language all the
        # individual USFM files per book can also be found in
        # a zip file,
        # $[?code='ar'].contents[?code='nav'].links[format='zip'],
        # which also contains the manifest.yaml file.
        # That language is the only one with a
        # contents[?code='nav'].
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
        # Code smell to produce a side effect here.
        resource._resource_file_format = "usfm"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    def _try_markdown_files_level1_location(self, resource) -> Optional[str]:
        """ If successful, return a string containing the URL of
        Markdown zip file, otherwise return None. """
        jsonpath_str = get_resource_url_level_1_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        # Code smell to produce a side effect here.
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    def _try_markdown_files_level2_location(self, resource) -> Optional[str]:
        """ If successful, return a string containing the URL of
        Markdown zip file, otherwise return None. """
        jsonpath_str = get_resource_url_level_2_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        # Code smell to produce a side effect here.
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    def _try_markdown_files_level1_sans_resource_code_location(
        self, resource
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
        # Code smell to produce a side effect here.
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    def _try_markdown_files_level2_sans_resource_code_location(
        self, resource
    ) -> Optional[str]:
        """ For the language in question, the resource is apparently
        at its alternative location which we try next. If successful,
        return a string containing the URL of the Markdown zip file,
        otherwise return None."""
        jsonpath_str = get_resource_url_level_2_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[tr] = self._lookup(jsonpath_str)
        url: Optional[str] = None
        if urls is not None and len(urls) > 0:
            url = urls[0]
        # Code smell to produce a side effect here.
        resource._resource_file_format = "zip"
        resource._resource_jsonpath = jsonpath_str
        resource._resource_url = url
        return url

    # protected access level
    def _lookup(self, jsonpath: str,) -> List[Optional[str]]:
        """ Return jsonpath value or empty list if node doesn't exist. """
        self._get_data()
        logger.info("jsonpath: {}".format(jsonpath))
        value: List[str] = jp.match(
            jsonpath, self.json_data,
        )
        value_set: Set = set(value)
        return list(value_set)

    # protected access level
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

    def lang_codes(self) -> List[Optional[str]]:
        """ Convenience method that can be called from UI to get the
        set of all language codes available through API. Presumably
        this could be called to populate a dropdown menu. """
        # return list(sorted(set(self._lookup("$[*].code"))))
        self._get_data()
        codes: List[str] = []
        for lang in self.json_data:
            codes.append(lang["code"])
        # return self._lookup("$[*].code")
        return codes

    # NOTE We really would only need lang_codes and
    # lang_codes_and_names, especially since there are a different
    # number of codes than names, so they should not be decoupled when
    # names are desired. Thus, commented out for now.
    # def lang_names(self) -> List[Optional[str]]:
    #     # FIXME This method is SLOW. Language codes and names are
    #     # not in a one to one relationship and so we have to
    #     # specifically lookup the name for the code which means we
    #     # have to do a jsonpath lookup for every language code.
    #     # Massive use of the heap plus jsonpath processing time.
    #     """ Convenience method that can be called from UI to get the
    #     set of all language names available through API. Presumably
    #     this could be called to populate a dropdown menu. """
    #     codes: List[Optional[str]] = self.lang_codes()
    #     names: List[str] = []
    #     for code in codes:
    #         name_arr = self._lookup("$[?code='{}'].name".format(code))
    #         if name_arr is not None and len(name_arr):
    #             names.append(name_arr[0])
    #         else:
    #             names.append("Name not provided")
    #     return names

    def lang_codes_and_names(self) -> List[Tuple[str, str]]:
        """ Convenience method that can be called from UI to get the
        set of all language code, name tuples available through API.
        Presumably this could be called to populate a dropdown menu.
        """
        self._get_data()
        codes_and_names: List[Tuple[str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self.json_data:
            codes_and_names.append((d["code"], d["name"]))
        return codes_and_names

    def resource_types(self) -> List[Optional[str]]:
        """ Convenience method that can be called, e.g., from the UI,
        to get the set of all resource types. """
        return self._lookup("$[*].contents[*].code")

    def resource_codes(self) -> List[Optional[str]]:
        """ Convenience method that can be called, e.g., from the UI,
        to get the set of all resource codes. """
        return self._lookup("$[*].contents[*].subcontents[*].code")
