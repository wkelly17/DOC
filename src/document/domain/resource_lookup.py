"""
This module provides an API for looking up the location of a
resource's asset files in the cloud.
"""


import abc
import logging  # For logdecorator
import os
import pathlib
from typing import Any, List, Optional, Set, Tuple
from urllib import parse as urllib_parse

import icontract
import jsonpath_rw_ext as jp

from document import config
from document.domain import model
from document.utils import file_utils, url_utils

from document.domain.resource import Resource

from logdecorator import log_on_start, log_on_end

logger = config.get_logger(__name__)


class ResourceJsonLookup:
    """
    A class that let's you retrieve values from it using jsonpath.
    Subclasses of ResourceLookup delegate to this class.
    """

    _lang_codes_names_and_resource_types: List[Tuple[str, str, List[str]]] = []

    @staticmethod
    def _initialize_lang_codes_names_and_resource_types() -> List[
        Tuple[str, str, List[str]]
    ]:
        """
        Initialize a list of available Tuple[lang_code, lang_name,
        List[resource_type]].
        """

        return BIELHelperResourceJsonLookup().lang_codes_names_and_resource_types()

    @classmethod
    def get_lang_codes_names_and_resource_types(
        cls,
    ) -> List[Tuple[str, str, List[str]]]:
        # if cls._lang_codes_names_and_resource_types is None:
        if not cls._lang_codes_names_and_resource_types:
            # fmt: off
            cls._lang_codes_names_and_resource_types = ResourceJsonLookup._initialize_lang_codes_names_and_resource_types()

        return cls._lang_codes_names_and_resource_types

    def __init__(self) -> None:
        """
        Delegate obtaining the translations.json source file to
        SourceDataFetcher class.
        """
        # NOTE This could be modified to be a Singleton
        self._source_data_fetcher = SourceDataFetcher(
            config.get_working_dir(), config.get_translations_json_location()
        )

    # Make composition less arduous.
    def __getattr__(self, attribute: str) -> Any:
        """
        Delegate method calls not on self to
        self._source_data_fetcher.
        """
        return getattr(self._source_data_fetcher, attribute)

    # @property
    # def source_data_fetcher(self) -> SourceDataFetcher:
    #     return self._source_data_fetcher

    # @property
    # def json_data(self) -> dict:
    #     return self._source_data_fetcher._json_data

    # def _get_data(self) -> None:
    #     self._source_data_fetcher._get_data()

    @icontract.require(lambda resource: resource.lang_code == "en")
    @icontract.require(lambda resource: resource.resource_type is not None)
    @icontract.ensure(lambda result: result.source == model.AssetSourceEnum.GIT)
    @icontract.ensure(lambda result: result.url is not None)
    @log_on_start(
        logging.INFO,
        "About to look for English resource assets URL for git repo",
        logger=logger,
    )
    def _get_english_git_repo_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of repo,
        otherwise return None.
        """
        url: str = config.get_english_git_repo_url(resource.resource_type)
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.GIT,
            jsonpath=None,
            lang_name="English",
            resource_type_name=config.get_english_resource_type_name(resource.resource_type),
        )

    @icontract.require(
        lambda resource: resource.lang_code is not None
        and resource.resource_type is not None
        and resource.resource_code is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.GIT
        and result.jsonpath is not None
        # and result.lang_name
    )
    @log_on_start(
        logging.INFO,
        "About to look for resource assets URL for git repo.",
        logger=logger,
    )
    def _try_git_repo_location(self, resource: Resource) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of USFM
        repo, otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = config.get_resource_download_format_jsonpath().format(
            resource.lang_code, resource.resource_type, resource.resource_code,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls:
            # Get the portion of the query string that gives
            # the repo URL
            url = self._parse_repo_url_from_json_url(urls[0])
        lang_name_jsonpath_str = config.get_resource_lang_name_jsonpath().format(
            resource.lang_code
        )
        lang_name_lst: List[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = config.get_resource_type_name_jsonpath().format(
            resource.lang_code, resource.resource_type
        )
        resource_type_name_lst: List[str] = self._lookup(resource_type_name_jsonpath_str)
        if resource_type_name_lst:
            resource_type_name = resource_type_name_lst[0]
        else:
            resource_type_name = ""
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.GIT,
            jsonpath=jsonpath_str,
            lang_name=lang_name,
            resource_type_name=resource_type_name,
        )

    @icontract.require(
        lambda self, json_path: self.json_data is not None and json_path is not None
    )
    @icontract.ensure(lambda result: result is not None)
    @log_on_start(logging.DEBUG, "json_path: {json_path}")
    def _lookup(self, json_path: str) -> List[str]:
        """Return jsonpath value or empty list if JSON node doesn't exist."""
        self._get_data()
        value: List[str] = jp.match(
            json_path, self.json_data,
        )
        logger.debug("value[:4] from translations.json: {}".format(value[:4]))
        value_set: Set = set(value)
        return list(value_set)

    @icontract.require(lambda url, repo_url_dict_key: url and repo_url_dict_key)
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
        result: dict = urllib_parse.parse_qs(url)
        result_lst: List = result[repo_url_dict_key]
        if result_lst:
            return result_lst[0]
        return None


class SourceDataFetcher:
    """
    This class obtains the translations.json file, from which we do
    our lookups.

    SourceDataFetcher is delegated to from ResourceJsonLookup (or its
    subclasses) any one of which act as a Fascade to this class for client
    code.
    """

    def __init__(self, working_dir: str, json_file_url: str) -> None:
        self._working_dir = working_dir
        self._json_file_url = json_file_url

        logger.info("Working dir is {}".format(self._working_dir))

        self._json_file = pathlib.Path(
            os.path.join(
                self._working_dir, self._json_file_url.rpartition(os.path.sep)[2]
            )
        )

        # logger.info("JSON file is {}".format(self._json_file))

        self._json_data: List = []

    @property
    def json_data(self) -> List:
        """Provide public method for other modules to access."""
        return self._json_data

    @icontract.require(
        lambda self: self._json_file_url is not None and self._json_file is not None
    )
    @icontract.ensure(lambda self: self._json_data is not None)
    @log_on_start(
        logging.INFO, "About to check if we need new translations.json", logger=logger
    )
    def _get_data(self) -> None:
        """Download json data and parse it into equivalent python objects."""
        if file_utils.source_file_needs_update(self._json_file):
            logger.debug("Downloading {}...".format(self._json_file_url))
            url_utils.download_file(self._json_file_url, str(self._json_file.resolve()))

        if not self._json_data:
            logger.debug("Loading json file {}...".format(self._json_file))
            # FIXME We may want to catch a possible exception here as
            # load_json_object and its delegated function do not
            # handle them.
            # try:
            self._json_data = file_utils.load_json_object(self._json_file)
            # except Exception as exc:
            #     logger.debug("Exception: {}".format(exc))
            # finally:
            #     logger.info("Finished loading json file.")


class ResourceLookup(abc.ABC):
    """
    Abstract super class that exists for documentation/clarity of
    interface. Future lookup class that implements its interface could
    be USFMResourceGraphQLLookup for example.
    """

    @abc.abstractmethod
    def lookup(self, resource: Resource) -> model.ResourceLookupDto:
        """
        Given a resource, comprised of language code, e.g., 'en', a
        resource type, e.g., 'ulb-wa', and a resource code, e.g., 'gen',
        return URL for resource.

        Subclasses implement.
        """
        raise NotImplementedError


class USFMResourceJsonLookup(ResourceLookup):
    """Handle lookup of USFM resources."""

    def __init__(self) -> None:
        self._resource_json_lookup = ResourceJsonLookup()

    # NOTE Using __getattr__ instead of this, leaving this for documentation.
    # @property
    # def resource_json_lookup(self) -> ResourceJsonLookup:
    #     return self._resource_json_lookup

    # Make OO composition less arduous.
    def __getattr__(self, attribute: str) -> Any:
        """
        Redirect method lookups that are not on self to
        self._resource_json_lookup.
        """
        return getattr(self._resource_json_lookup, attribute)

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.require(
        lambda resource: resource.lang_code is not None
        and resource.resource_type is not None
        and resource.resource_code is not None
    )
    @icontract.ensure(lambda result: result is not None)
    @log_on_end(logging.DEBUG, "model.ResourceLookupDto: {result}", logger=logger)
    def lookup(self, resource: Resource) -> model.ResourceLookupDto:
        """
        Given a resource, comprised of language code, e.g., 'en', a
        resource type, e.g., 'ulb-wa', and a resource code, e.g., 'gen',
        return URL for resource.
        """

        # Get a list wherein each element is a tuple comprised of the
        # language code, language name, and the list of resource types
        # that are actually available for request for that language.
        data: List[Tuple[str, str, List[str]]] = ResourceJsonLookup.get_lang_codes_names_and_resource_types()
        if data:
            resource_types_for_language = [tuple[2] for tuple in data if tuple[0] == resource.lang_code][0]
            # Check that resource is requesting a resource type that is
            # actually available for the language.
            if not resource.resource_type in resource_types_for_language:
                # On second thought, let's not raise an
                # exceptions.IncompatibleREsourceTypeRequestError exception here. For
                # now, we are better off logging the error and returning a
                # model.ResourceLookupDto whose instance vars are initialized to None.
                # raise exceptions.IncompatibleResourceTypeRequestError("{} requested a resource type that is not available for this language. The resource types available are {}".format(resource, resource_types_for_language))

                # Instead of raising an exception let's just make the value proposition
                # for this code be to log unavailable resource types. Eventually this
                # could be developed more fully and queries by BIEL to preclude a user
                # from ever being given the chance to request any resource that does not
                # exist in the first place.
                logger.debug("{} requested a resource type that is not available for this language. The resource types available are {}".format(resource, resource_types_for_language))

        resource_lookup_dto: model.ResourceLookupDto

        # Special case:
        # Ironically, for English, translations.json file only
        # contains URLs to PDF assets rather than anything useful for
        # our purposes. Therefore, we have this guard to handle
        # English resource requests separately and outside of
        # translations.json by retrieving them from their git repos.
        if resource.lang_code == "en":
            return self._get_english_git_repo_location(resource)

        # Prefer getting USFM files individually rather than
        # introducing the latency of cloning a git repo.
        resource_lookup_dto = self._try_individual_usfm_location(resource)

        # Individual USFM file was not available, now try getting it
        # from a git repo.
        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_git_repo_location(resource)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level1_location(resource)

        return resource_lookup_dto

    @icontract.require(
        lambda resource: resource.lang_code is not None
        and resource.resource_type is not None
        and resource.resource_code is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.USFM
        and result.jsonpath is not None
        # and result.lang_name
    )
    @log_on_start(
        logging.INFO,
        "About to look for resource assets URL for individual USFM file.",
        logger=logger,
    )
    @log_on_end(logging.DEBUG, "model.ResourceLookupDto: {result}", logger=logger)
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
            resource.lang_code, resource.resource_type, resource.resource_code,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = config.get_resource_lang_name_jsonpath().format(
            resource.lang_code
        )
        lang_name_lst: List[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = config.get_resource_type_name_jsonpath().format(
            resource.lang_code, resource.resource_type
        )
        resource_type_name_lst: List[str] = self._lookup(resource_type_name_jsonpath_str)
        if resource_type_name_lst:
            resource_type_name = resource_type_name_lst[0]
        else:
            resource_type_name = ""
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.USFM,
            jsonpath=jsonpath_str,
            lang_name=lang_name,
            resource_type_name=resource_type_name,
        )

    @icontract.require(
        lambda resource: resource.lang_code is not None
        and resource.resource_type is not None
        and resource.resource_code is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.ZIP
        and result.jsonpath is not None
        # and result.lang_name
    )
    @log_on_start(
        logging.INFO,
        "About to look for resource assets URL for zipped USFM file.",
        logger=logger,
    )
    @log_on_end(logging.DEBUG, "model.ResourceLookupDto: {result}", logger=logger)
    def _try_level1_location(
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
        jsonpath_str = config.get_resource_url_level1_jsonpath().format(
            resource.lang_code, resource.resource_type, resource.resource_code,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = config.get_resource_lang_name_jsonpath().format(
            resource.lang_code
        )
        lang_name_lst: List[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = config.get_resource_type_name_jsonpath().format(
            resource.lang_code, resource.resource_type
        )
        resource_type_name_lst: List[str] = self._lookup(resource_type_name_jsonpath_str)
        if resource_type_name_lst:
            resource_type_name = resource_type_name_lst[0]
        else:
            resource_type_name = ""
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.ZIP,
            jsonpath=jsonpath_str,
            lang_name=lang_name,
            resource_type_name=resource_type_name,
        )

class TResourceJsonLookup(ResourceLookup):
    """Handle lookup of TN, TA, TQ, TW resources."""

    def __init__(self) -> None:
        self._resource_json_lookup = ResourceJsonLookup()

    # @property
    # def resource_json_lookup(self) -> ResourceJsonLookup:
    #     return self._resource_json_lookup

    # Make composition less arduous.
    def __getattr__(self, attribute: str) -> Any:
        """
        Redirect method lookups that are not on self to
        self.resource_json_lookup.
        """
        return getattr(self._resource_json_lookup, attribute)

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.require(
        lambda resource: resource.lang_code is not None
        and resource.resource_type is not None
        and resource.resource_code is not None
    )
    @icontract.ensure(lambda result: result is not None)
    def lookup(self, resource: Resource) -> model.ResourceLookupDto:
        """
        Given a resource, comprised of language code, e.g., 'wum', a
        resource type, e.g., 'tn', and a resource code, e.g., 'gen',
        return URL for resource.
        """
        resource_lookup_dto: model.ResourceLookupDto

        # For English, translations.json file only
        # contains URLs to PDF assets rather than anything useful for
        # our purposes. Therefore, we have this guard to handle
        # English resource requests separately outside of
        # translations.json.
        if resource.lang_code == "en":
            return self._get_english_git_repo_location(resource)

        resource_lookup_dto = self._try_level1_location(resource)
        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level2_location(resource)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level1_sans_resource_code_location(resource)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level2_sans_resource_code_location(resource)

        return resource_lookup_dto

    @icontract.require(
        lambda resource: resource.lang_code is not None
        and resource.resource_type is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.ZIP
        and result.jsonpath is not None
    )
    def _try_level1_location(self, resource: Resource) -> model.ResourceLookupDto:
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
        jsonpath_str = config.get_resource_url_level1_jsonpath().format(
            resource.lang_code, resource.resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = config.get_resource_lang_name_jsonpath().format(
            resource.lang_code
        )
        lang_name_lst: List[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = config.get_resource_type_name_jsonpath().format(
            resource.lang_code, resource.resource_type
        )
        resource_type_name_lst: List[str] = self._lookup(resource_type_name_jsonpath_str)
        if resource_type_name_lst:
            resource_type_name = resource_type_name_lst[0]
        else:
            resource_type_name = ""
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.ZIP,
            jsonpath=jsonpath_str,
            lang_name=lang_name,
            resource_type_name=resource_type_name,
        )

    @icontract.require(lambda resource: resource.lang_code is not None)
    @icontract.require(lambda resource: resource.resource_type is not None)
    @icontract.ensure(lambda result: result.source == model.AssetSourceEnum.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_level2_location(self, resource: Resource) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of Markdown
        zip file, otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = config.get_resource_url_level2_jsonpath().format(
            resource.lang_code, resource.resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = config.get_resource_lang_name_jsonpath().format(
            resource.lang_code
        )
        lang_name_lst: List[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = config.get_resource_type_name_jsonpath().format(
            resource.lang_code, resource.resource_type
        )
        resource_type_name_lst: List[str] = self._lookup(resource_type_name_jsonpath_str)
        if resource_type_name_lst:
            resource_type_name = resource_type_name_lst[0]
        else:
            resource_type_name = ""
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.ZIP,
            jsonpath=jsonpath_str,
            lang_name=lang_name,
            resource_type_name=resource_type_name,
        )

    @icontract.require(lambda resource: resource.lang_code is not None)
    @icontract.require(lambda resource: resource.resource_type is not None)
    @icontract.ensure(lambda result: result.source == model.AssetSourceEnum.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_level1_sans_resource_code_location(
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
        jsonpath_str = config.get_resource_url_level1_jsonpath().format(
            resource.lang_code, resource.resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = config.get_resource_lang_name_jsonpath().format(
            resource.lang_code
        )
        lang_name_lst: List[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = config.get_resource_type_name_jsonpath().format(
            resource.lang_code, resource.resource_type
        )
        resource_type_name_lst: List[str] = self._lookup(resource_type_name_jsonpath_str)
        if resource_type_name_lst:
            resource_type_name = resource_type_name_lst[0]
        else:
            resource_type_name = ""
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.ZIP,
            jsonpath=jsonpath_str,
            lang_name=lang_name,
            resource_type_name=resource_type_name,
        )

    @icontract.require(lambda resource: resource.lang_code is not None)
    @icontract.require(lambda resource: resource.resource_type is not None)
    @icontract.ensure(lambda result: result.source == model.AssetSourceEnum.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_level2_sans_resource_code_location(
        self, resource: Resource
    ) -> model.ResourceLookupDto:
        """
        For the language in question, the resource is apparently at
        its alternative location which we try next. If successful,
        return a string containing the URL of the Markdown zip file,
        otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = config.get_resource_url_level2_jsonpath().format(
            resource.lang_code, resource.resource_type,
        )
        urls: List[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = config.get_resource_lang_name_jsonpath().format(
            resource.lang_code
        )
        lang_name_results: List[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_results:
            lang_name = lang_name_results[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = config.get_resource_type_name_jsonpath().format(
            resource.lang_code, resource.resource_type
        )
        resource_type_name_results: List[str] = self._lookup(resource_type_name_jsonpath_str)
        if resource_type_name_results:
            resource_type_name = resource_type_name_results[0]
        else:
            resource_type_name = ""
        return model.ResourceLookupDto(
            url=url,
            source=model.AssetSourceEnum.ZIP,
            jsonpath=jsonpath_str,
            lang_name=lang_name,
            resource_type_name=resource_type_name,
        )


class BIELHelperResourceJsonLookup:
    """Helper class for BIEL UI to fetch values for dropdown menus."""

    def __init__(self) -> None:
        self._resource_json_lookup = ResourceJsonLookup()

    # @property
    # def resource_json_lookup(self) -> ResourceJsonLookup:
    #     return self._resource_json_lookup

    # Make composition less arduous.
    def __getattr__(self, attribute: str) -> Any:
        """
        Redirect method lookups that are not on self to
        self.resource_json_lookup.
        """
        return getattr(self._resource_json_lookup, attribute)

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes(self) -> List[str]:
        """
        Convenience method that can be called from UI to get the set
        of all language codes available through API. Presumably this
        could be called to populate a drop-down menu.
        """
        codes: List[str] = []
        self._get_data()
        for lang in self.json_data:
            codes.append(lang["code"])
        return codes

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes_and_names(self) -> List[Tuple[str, str]]:
        """
        Convenience method that can be called from UI to get the set
        of all language code, name tuples available through API.
        Presumably this could be called to populate a drop-down menu.
        """
        self._get_data()
        codes_and_names: List[Tuple[str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self.json_data:
            codes_and_names.append((d["code"], d["name"]))
        return codes_and_names

    @icontract.ensure(lambda result: result)
    def resource_types(self) -> List[str]:
        """
        Convenience method that can be called, e.g., from the UI, to
        get the set of all resource types.
        """
        self._get_data()
        return self._lookup(config.RESOURCE_TYPES_JSONPATH)

    @icontract.ensure(lambda result: result)
    def resource_codes(self) -> List[str]:
        """
        Convenience method that can be called, e.g., from the UI, to
        get the set of all resource codes.
        """
        self._get_data()
        return self._lookup(config.RESOURCE_CODES_JSONPATH)

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes_names_and_resource_types(self) -> List[Tuple[str, str, List[str]]]:
        """
        Convenience method that can be called to get the list
        of all tuples where each tuple consists of language code,
        language name, and list of resource types available for that
        language.

        Example usage in repl:
        >>> from document.domain import resource_lookup
        >>> data = resource_lookup.BIELHelperResourceJsonLookup().lang_codes_names_and_resource_types()
        # Lookup the resource type available for zh
        >>> [pair[2] for pair in data if pair[0] == "zh"]
        [['cuv', 'tn', 'tq', 'tw']]
        """
        self._get_data()
        lang_codes_names_and_resource_types: List[Tuple[str, str, List[str]]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for lang in self.json_data:
            resource_types: List[str] = []
            for resource_type_dict in lang["contents"]:
                try:
                    resource_type = resource_type_dict["code"]
                    resource_types.append(resource_type)
                except:
                    resource_type = None
            lang_codes_names_and_resource_types.append(
                (lang["code"], lang["name"], resource_types)
            )
        return lang_codes_names_and_resource_types

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes_names_resource_types_and_resource_codes(
        self,
    ) -> List[Tuple[str, str, List[Tuple[str, List[str]]]]]:
        """
        Convenience method that can be called to get the set
        of all tuples where each tuple consists of language code,
        language name, list of resource types available for that
        language, and the resource_codes available for each resource
        type.

        Example usage in repl:
        >>> from document.domain import resource_lookup
        >>> data = resource_lookup.BIELHelperResourceJsonLookup().lang_codes_names_resource_types_and_resource_codes()
        # Lookup the resource type available for zh
        >>> [pair[2] for pair in data if pair[0] == "zh"]
        [[('cuv', ['gen', 'exo', 'lev', 'num', 'deu', 'jos', 'jdg', 'rut',
        '1sa', '2sa', '1ki', '2ki', '1ch', '2ch', 'ezr', 'neh', 'est',
        'job', 'psa', 'pro', 'ecc', 'sng', 'isa', 'jer', 'lam', 'ezk',
        'dan', 'hos', 'jol', 'amo', 'oba', 'jon', 'mic', 'nam', 'hab',
        'zep', 'hag', 'zec', 'mal', 'mat', 'mrk', 'luk', 'jhn', 'act',
        'rom', '1co', '2co', 'gal', 'eph', 'php', 'col', '1th', '2th',
        '1ti', '2ti', 'tit', 'phm', 'heb', 'jas', '1pe', '2pe', '1jn',
        '2jn', '3jn', 'jud', 'rev']), ('tn', []), ('tq', []), ('tw',
        [])]]
        """
        self._get_data()
        lang_codes_names_resource_types_and_resource_codes: List[
            Tuple[str, str, List[Tuple[str, List[str]]]]
        ] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for lang in self.json_data:
            resource_types: List[Tuple[str, List[str]]] = []
            for resource_type_dict in lang["contents"]:
                # breakpoint()
                # Usage of dpath at this point:
                # (Pdb) import dpath.util
                # (Pdb) dpath.util.search(resource_type_dict, "subcontents/0/code")
                # {'subcontents': [{'code': '2co'}]}
                # (Pdb) dpath.util.search(resource_type_dict, "subcontents")
                # {'subcontents': [{'name': '2 Corinthians', 'category': 'bible-nt', 'code': '2co', 'sort': 48, 'links': [{'url': 'http://read.bibletranslationtools.org/u/Southern./kbt_2co_text_reg/92731d1550/', 'format': 'Read on Web'}, {'url': '../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', 'format': 'Download'}]}]}
                # (Pdb) dpath.util.search(resource_type_dict, "subcontents")["subcontents"]
                # [{'name': '2 Corinthians', 'category': 'bible-nt', 'code': '2co', 'sort': 48, 'links': [{'url': 'http://read.bibletranslationtools.org/u/Southern./kbt_2co_text_reg/92731d1550/', 'format': 'Read on Web'}, {'url': '../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', 'format': 'Download'}]}]
                # (Pdb) interact
                # >>> for x in dpath.util.search(resource_type_dict, "subcontents")["subcontents"]:
                # ...   print(x["code"])
                # ...
                # 2co
                try:
                    resource_type = resource_type_dict["code"]
                except:
                    resource_type = None
                resource_codes_list = resource_type_dict["subcontents"]
                resource_codes: List[str] = []
                for resource_code_dict in resource_codes_list:
                    resource_code = resource_code_dict["code"]
                    resource_codes.append(resource_code)
                if resource_type is not None:
                    resource_types.append((resource_type, resource_codes))
            lang_codes_names_resource_types_and_resource_codes.append(
                (lang["code"], lang["name"], resource_types)
            )
        return lang_codes_names_resource_types_and_resource_codes

    # NOTE Only used for debugging and testing. Not part of long-term
    # API.
    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes_names_and_contents_codes(self) -> List[Tuple[str, str, str]]:
        """
        Convenience test method that can be called to get the set
        of all language code, language name, contents level code as
        tuples.

        Example usage in repl:
        >>> from document.domain import resource_lookup
        >>> data = resource_lookup.BIELHelperResourceJsonLookup().lang_codes_names_and_contents_codes()
        >>> [(pair[0], pair[1]) for pair in data if pair[2] == "nil"]
        [('grc', 'Ancient Greek'), ('acq', 'لهجة تعزية-عدنية'), ('gaj-x-ymnk', 'Gadsup Yomunka'), ('mve', 'مارواري (Pakistan)'), ('lus', 'Lushai'), ('mor', 'Moro'), ('tig', 'Tigre')]
        # Other possible queries:
        >>> [(pair[0], pair[1]) for pair in data if pair[2] == "reg"]
        >>> [(pair[0], pair[1]) for pair in data if pair[2] == "ulb"]
        >>> [(pair[0], pair[1]) for pair in data if pair[2] == "cuv"]
        >>> [(pair[0], pair[1]) for pair in data if pair[2] == "udb"]
        >>> [(pair[0], pair[1]) for pair in data if pair[2] == "udb"]
        # Lookup the resource type available for zh
        >>> [pair[2] for pair in data if pair[0] == "zh"]
        ['cuv']
        >>> data = sorted(data, key=lambda tuple: tuple[2])
        >>> import itertools
        >>> [tuple[0] for tuple in list(itertools.groupby(data, key=lambda tuple: tuple[2]))]
        # 'nil' is None
        >>> ['cuv', 'dkl', 'kar', 'nil', 'pdb', 'reg', 'rg', 'tn', 'tw', 'udb', 'ugnt', 'uhb', 'ulb', 'ulb-wa', 'ust']
        >>> for resource_type in [tuple[0] for tuple in list(itertools.groupby(data, key=lambda tuple: tuple[2]))]:
        ...   [(resource_type, pair[0], pair[1]) for pair in data if pair[2] == resource_type]
        ...
        # See <project
        dir>/lang_codes_names_and_contents_codes_groups.json for
        output dumped to json format.
        """
        self._get_data()
        lang_codes_names_and_contents_codes: List[Tuple[str, str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self.json_data:
            try:
                contents_code = d["contents"][0]["code"]
            except:
                contents_code = "nil"
            lang_codes_names_and_contents_codes.append(
                (d["code"], d["name"], contents_code)
            )
        # breakpoint()
        return lang_codes_names_and_contents_codes
