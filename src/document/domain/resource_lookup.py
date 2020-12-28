from __future__ import annotations  # https://www.python.org/dev/peps/pep-0563/
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING, Union
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

from document.utils import file_utils
from document.utils import url_utils
from document import config
from document.domain import model

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
    from document.domain.resource import (
        Resource,
        USFMResource,
        TNResource,
        TWResource,
        TQResource,
        TAResource,
    )

    # Define type alias for brevity
    # AResource = Union[
    #     USFMResource, TResource, TAResource, TNResource, TQResource, TWResource
    # ]


import yaml
import logging
import logging.config

# from logdecorator import log_on_end, log_on_start

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)


logger = logging.getLogger(__name__)


class ResourceJsonLookup:
    """
    A class that let's you retrieve values from it using jsonpath.
    Subclasses of ResourceLookup delegate to this class.
    """

    def __init__(self) -> None:
        """
        Delegate obtaining the translations.json source file to
        SourceDataFetcher class.
        """
        # NOTE This be a Singleton
        self._source_data_fetcher = SourceDataFetcher()

    # # Make composition less arduous.
    # def __getattr__(self, attribute: str) -> Any:
    #     return getattr(self._source_data_fetcher, attribute)

    @property
    def source_data_fetcher(self) -> SourceDataFetcher:
        return self._source_data_fetcher

    @property
    def json_data(self) -> dict:
        return self.source_data_fetcher._json_data

    def _get_data(self) -> None:
        self.source_data_fetcher._get_data()

    @icontract.require(lambda resource: resource._lang_code == "en")
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda result: result.source == config.GIT)
    @icontract.ensure(lambda result: result.url is not None)
    def _get_english_git_repo_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of repo,
        otherwise return None.
        """
        url: str = config.get_english_repos_dict()[resource._resource_type]
        return model.ResourceLookupDto(url=url, source=config.GIT, jsonpath=None)

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.require(lambda resource: resource._resource_code is not None)
    @icontract.ensure(lambda result: result.source == config.GIT)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_git_repo_location(self, resource: Resource) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of USFM
        repo, otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = config.get_resource_download_format_jsonpath().format(
            resource._lang_code, resource._resource_type, resource._resource_code,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls is not None and len(urls) > 0:
            # Get the portion of the query string that gives
            # the repo URL
            url = self._parse_repo_url_from_json_url(urls[0])
        return model.ResourceLookupDto(
            url=url, source=config.GIT, jsonpath=jsonpath_str
        )

    @icontract.require(lambda self: self.source_data_fetcher.json_data is not None)
    @icontract.require(lambda jsonpath: jsonpath is not None)
    @icontract.ensure(lambda result: result is not None)
    # @log_on_start(logging.DEBUG, "jsonpath: {jsonpath}")
    def _lookup(self, jsonpath: str) -> List[str]:
        """ Return jsonpath value or empty list if node doesn't exist. """
        self._get_data()
        value: List[str] = jp.match(
            jsonpath, self.json_data,
        )
        logger.debug("jsonpath: {}".format(jsonpath))
        logger.debug("value[0:4] from translations.json: {}".format(value[0:4]))
        value_set: Set = set(value)
        return list(value_set)

    # FIXME Add contracts
    def _parse_repo_url_from_json_url(
        self, url: Optional[str], repo_url_dict_key: str = config.REPO_URL_DICT_KEY,
    ) -> Optional[str]:
        """
        Given a URL of the form
        ../download-scripture?repo_url=https%3A%2F%2Fgit.door43.org%2Fburje_duro%2Fam_gen_text_udb&book_name=Genesis,
        return the repo_url query parameter value.
        """
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


# SourceDataFetcher is delegated to from ResourceJsonLookup (or its
# subclasses) any one of which act as a Fascade for client code.
class SourceDataFetcher:
    """
    Class responsible for obtaining the source data, e.g.,
    translations.json, from which we do our lookups.
    """

    def __init__(
        self,
        working_dir: str = config.get_working_dir(),
        json_file_url: str = config.get_translations_json_location(),
    ) -> None:

        self._working_dir = working_dir
        self._json_file_url = json_file_url

        logger.info("Working dir is {}".format(self._working_dir))

        self._json_file = pathlib.Path(
            os.path.join(
                self._working_dir, self._json_file_url.rpartition(os.path.sep)[2]
            )
        )

        logger.info("JSON file is {}".format(self._json_file))

        self._json_data: dict = {}

    @property
    def json_data(self) -> dict:
        return self._json_data

    @icontract.require(lambda self: self._json_file_url is not None)
    @icontract.require(lambda self: self._json_file is not None)
    @icontract.ensure(lambda self: self._json_data is not None)
    def _get_data(self) -> None:
        """ Download json data and parse it into equivalent python objects. """
        logger.info("About to check if we need new translations.json")
        if self._data_needs_update():
            # Download json file
            try:
                logger.debug("Downloading {}...".format(self._json_file_url))
                url_utils.download_file(
                    self._json_file_url, str(self._json_file.resolve())
                )
            except Exception as e:
                logger.debug("Exception: {}".format(e))
            finally:
                logger.info("Finished downloading json file.")

        if not self._json_data:
            # Load json file
            try:
                logger.debug("Loading json file {}...".format(self._json_file))
                self._json_data = file_utils.load_json_object(
                    self._json_file
                )  # json_data should possibly live on its own object
            except Exception as e:
                logger.debug("Exception: {}".format(e))
            finally:
                logger.info("Finished loading json file.")

    @icontract.require(lambda self: self._json_file is not None)
    def _data_needs_update(self) -> bool:
        """
        Given the json file path, return true if it has not been
        updated within 24 hours.
        """
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


class ResourceLookup(abc.ABC):
    """
    Abstract super class that exists for documentation/clarity of
    interface. Future lookup class that implements its interface could
    be USFMResourceGraphQLLookup for example.
    """

    @abc.abstractmethod
    def lookup(self, resource: Resource) -> model.ResourceLookupDto:
        raise NotImplementedError


class USFMResourceJsonLookup(ResourceLookup):
    """ Handle lookup of USFM resources. """

    def __init__(self) -> None:
        self._resource_json_lookup = ResourceJsonLookup()

    @property
    def resource_json_lookup(self) -> ResourceJsonLookup:
        return self._resource_json_lookup

    # Make composition less arduous.
    def __getattr__(self, attribute: str) -> Any:
        return getattr(self.resource_json_lookup, attribute)

    @icontract.require(lambda self: self.resource_json_lookup.json_data is not None)
    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.require(lambda resource: resource._resource_code is not None)
    @icontract.ensure(lambda result: result is not None)
    def lookup(self, resource: Resource) -> model.ResourceLookupDto:
        """
        Given a resource, comprised of language code, e.g., 'wum', a
        resource type, e.g., 'tn', and an optional resource code,
        e.g., 'gen', return URL for resource.
        """
        resource_lookup_dto: model.ResourceLookupDto

        # Special case:
        # Ironically, for English, translations.json file only
        # contains URLs to PDF assets rather than anything useful for
        # our purposes. Therefore, we have this guard to handle
        # English resource requests separately and outside of
        # translations.json by retrieving them from their git repos.
        if resource._lang_code == "en":
            logger.info("About to look for English resource assets URL for git repo")
            return self.resource_json_lookup._get_english_git_repo_location(resource)

        # Prefer getting USFM files individually rather than
        # introducing the latency of cloning a git repo (next).
        logger.info("About to look for resource assets URL for individual USFM file.")
        resource_lookup_dto = self._try_individual_usfm_location(resource)

        # Individual USFM file was not available, now try getting it
        # from a git repo.
        if resource_lookup_dto.url is None:
            logger.info("About to look for resource assets URL for git repo.")
            resource_lookup_dto = self.resource_json_lookup._try_git_repo_location(
                resource
            )

        return resource_lookup_dto

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.require(lambda resource: resource._resource_code is not None)
    @icontract.ensure(lambda result: result.source == config.USFM)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_individual_usfm_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of USFM
        file, otherwise None.
        """
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
        url: Optional[str] = None
        jsonpath_str = config.get_individual_usfm_url_jsonpath().format(
            resource._lang_code, resource._resource_type, resource._resource_code,
        )
        urls: List[str] = self.resource_json_lookup._lookup(jsonpath_str)
        if urls is not None and len(urls) > 0:
            url = urls[0]

        return model.ResourceLookupDto(
            url=url, source=config.USFM, jsonpath=jsonpath_str
        )


class TResourceJsonLookup(ResourceLookup):
    """ Handle lookup of TN, TA, TQ, TW resources. """

    def __init__(self) -> None:
        self._resource_json_lookup = ResourceJsonLookup()

    @property
    def resource_json_lookup(self) -> ResourceJsonLookup:
        return self._resource_json_lookup

    @icontract.require(lambda self: self.resource_json_lookup.json_data is not None)
    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.ensure(lambda result: result is not None)
    def lookup(self, resource: Resource) -> model.ResourceLookupDto:
        """
        Given a resource, comprised of language code, e.g., 'wum', a
        resource type, e.g., 'tn', and an optional resource code,
        e.g., 'gen', return URL for resource.
        """
        # url: Optional[str] = None
        resource_lookup_dto: model.ResourceLookupDto

        # Ironically, for English, translations.json file only
        # contains URLs to PDF assets rather than anything useful for
        # our purposes. Therefore, we have this guard to handle
        # English resource requests separately and outside of
        # translations.json.
        if resource._lang_code == "en":
            return self.resource_json_lookup._get_english_git_repo_location(resource)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_markdown_files_level1_location(resource)
            if (
                resource_lookup_dto.url is None
            ):  # For the language in question, the resource is
                # apparently at its alternative location which we try next.
                resource_lookup_dto = self._try_markdown_files_level2_location(resource)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_markdown_files_level1_sans_resource_code_location(
                resource
            )

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_markdown_files_level2_sans_resource_code_location(
                resource
            )

        return resource_lookup_dto

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda result: result.source == config.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_markdown_files_level1_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of Markdown
        zip file, otherwise return None. Some resources bundle all
        bible content in one zip file for a particular resource type,
        instead of one zip per book. Finding these all in one zips in
        translations.json does not depend on knowing the bible book,
        i.e., the resource code, but instead just the lang_code and
        resource_type.
        """
        url: Optional[str] = None
        jsonpath_str = config.get_resource_url_level_1_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self.resource_json_lookup._lookup(jsonpath_str)
        if urls is not None and len(urls) > 0:
            url = urls[0]
        return model.ResourceLookupDto(
            url=url, source=config.ZIP, jsonpath=jsonpath_str
        )

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda result: result.source == config.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_markdown_files_level2_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of Markdown
        zip file, otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = config.get_resource_url_level_2_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self.resource_json_lookup._lookup(jsonpath_str)
        if urls is not None and len(urls) > 0:
            url = urls[0]
        return model.ResourceLookupDto(
            url=url, source=config.ZIP, jsonpath=jsonpath_str
        )

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda result: result.source == config.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_markdown_files_level1_sans_resource_code_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of the
        Markdown zip file, otherwise return None.
        """
        # Some languages, e.g., code='as', have all of their
        # translation notes, 'tn', for all chapters in all books in
        # one zip file which is found at the book level, but not at
        # the chapter level of the translations.json file.
        url: Optional[str] = None
        jsonpath_str = config.get_resource_url_level_1_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self.resource_json_lookup._lookup(jsonpath_str)
        if urls is not None and len(urls) > 0:
            url = urls[0]
        return model.ResourceLookupDto(
            url=url, source=config.ZIP, jsonpath=jsonpath_str
        )

    @icontract.require(lambda resource: resource._lang_code is not None)
    @icontract.require(lambda resource: resource._resource_type is not None)
    @icontract.ensure(lambda result: result.source == config.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_markdown_files_level2_sans_resource_code_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        For the language in question, the resource is apparently at
        its alternative location which we try next. If successful,
        return a string containing the URL of the Markdown zip file,
        otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = config.get_resource_url_level_2_jsonpath().format(
            resource._lang_code, resource._resource_type,
        )
        urls: List[str] = self.resource_json_lookup._lookup(jsonpath_str)
        if urls is not None and len(urls) > 0:
            url = urls[0]
        return model.ResourceLookupDto(
            url=url, source=config.ZIP, jsonpath=jsonpath_str
        )


class BIELHelperResourceJsonLookup:
    """ Helper class for BIEL UI to fetch values for dropdown menus. """

    def __init__(self) -> None:
        self._resource_json_lookup = ResourceJsonLookup()

    @property
    def resource_json_lookup(self) -> ResourceJsonLookup:
        return self._resource_json_lookup

    @icontract.require(lambda self: self.resource_json_lookup.json_data is not None)
    @icontract.ensure(lambda result: result is not None)
    def lang_codes(self) -> List[str]:
        """
        Convenience method that can be called from UI to get the set
        of all language codes available through API. Presumably this
        could be called to populate a dropdown menu.
        """
        codes: List[str] = []
        self.resource_json_lookup._get_data()
        for lang in self.resource_json_lookup.json_data:
            codes.append(lang["code"])
        return codes

    @icontract.require(lambda self: self.resource_json_lookup.json_data is not None)
    @icontract.ensure(lambda result: result is not None)
    @icontract.ensure(lambda result: len(result) > 0)
    def lang_codes_and_names(self) -> List[Tuple[str, str]]:
        """
        Convenience method that can be called from UI to get the set
        of all language code, name tuples available through API.
        Presumably this could be called to populate a dropdown menu.
        """
        self.resource_json_lookup._get_data()
        codes_and_names: List[Tuple[str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self.resource_json_lookup.json_data:
            codes_and_names.append((d["code"], d["name"]))
        return codes_and_names

    @icontract.ensure(lambda result: result is not None)
    @icontract.ensure(lambda result: len(result) > 0)
    def resource_types(self) -> List[str]:
        """
        Convenience method that can be called, e.g., from the UI, to
        get the set of all resource types.
        """
        self.resource_json_lookup._get_data()
        return self.resource_json_lookup._lookup(config.RESOURCE_TYPES_JSONPATH)

    @icontract.ensure(lambda result: result is not None)
    @icontract.ensure(lambda result: len(result) > 0)
    def resource_codes(self) -> List[str]:
        """
        Convenience method that can be called, e.g., from the UI, to
        get the set of all resource codes.
        """
        self.resource_json_lookup._get_data()
        return self.resource_json_lookup._lookup(config.RESOURCE_CODES_JSONPATH)