"""
This module provides an API for looking up the location of a
resource's asset files in the cloud.
"""


import abc
import logging  # For logdecorator
import os
import pathlib
from typing import Any, Optional
from urllib import parse as urllib_parse

import icontract
import jsonpath_rw_ext as jp
from logdecorator import log_on_end, log_on_start

from document.config import settings
from document.domain import model
from document.utils import file_utils, url_utils

logger = settings.logger(__name__)


class ResourceJsonLookup:
    """
    A class that let's you retrieve values from it using jsonpath.
    Subclasses of ResourceLookup delegate to this class.
    """

    _lang_codes_names_and_resource_types: list[model.CodeNameTypeTriplet] = []

    @staticmethod
    def _initialize_lang_codes_names_and_resource_types() -> list[model.CodeNameTypeTriplet]:
        """
        Initialize a list of available Tuple[lang_code, lang_name,
        List[resource_type]].
        """

        return BIELHelperResourceJsonLookup().lang_codes_names_and_resource_types()

    @classmethod
    def lang_codes_names_and_resource_types(
        cls,
    ) -> list[model.CodeNameTypeTriplet]:
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
            settings.working_dir(), settings.TRANSLATIONS_JSON_LOCATION
        )

    # Make OO composition less arduous.
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


    @icontract.require(
        lambda lang_code, resource_type, resource_code: lang_code is not None
        and resource_type is not None
        and resource_code is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.GIT
        and result.jsonpath is not None
        # and result.lang_name
    )
    def _try_git_repo_location(self, lang_code: str, resource_type: str, resource_code: str) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of USFM
        repo, otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = settings.RESOURCE_DOWNLOAD_FORMAT_JSONPATH.format(
            lang_code, resource_type, resource_code,
        )
        urls: list[str] = self._lookup(jsonpath_str)
        if urls:
            # Get the portion of the query string that gives
            # the repo URL
            url = self._parse_repo_url_from_json_url(urls[0])
        lang_name_jsonpath_str = settings.RESOURCE_LANG_NAME_JSONPATH.format(
            lang_code
        )
        lang_name_lst: list[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = settings.RESOURCE_TYPE_NAME_JSONPATH.format(
            lang_code, resource_type
        )
        resource_type_name_lst: list[str] = self._lookup(resource_type_name_jsonpath_str)
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


    @icontract.require(lambda url, repo_url_dict_key: url and repo_url_dict_key)
    def _parse_repo_url_from_json_url(
        self, url: Optional[str], repo_url_dict_key: str = settings.REPO_URL_DICT_KEY,
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
        result_lst: list = result[repo_url_dict_key]
        if result_lst:
            return result_lst[0]
        return None


    @icontract.require(
        lambda self, json_path: self.json_data is not None and json_path is not None
    )
    @icontract.ensure(lambda result: result is not None)
    @log_on_start(logging.DEBUG, "json_path: {json_path}")
    def _lookup(self, json_path: str) -> list[str]:
        """Return jsonpath value or empty list if JSON node doesn't exist."""
        # self._data()
        value: list[str] = jp.match(
            json_path, self.json_data,
        )
        logger.debug("value[:4] from translations.json: %s", value[:4])
        value_set: set = set(value)
        return list(value_set)

@icontract.require(lambda resource_type: resource_type)
@icontract.ensure(lambda result: result and result.url and result.source == model.AssetSourceEnum.GIT)
def _english_git_repo_location(
    resource_type: str
) -> model.ResourceLookupDto:
    """
    If successful, return a string containing the URL of repo,
    otherwise return None.
    """
    url: str = settings.english_git_repo_url(resource_type)
    return model.ResourceLookupDto(
        url=url,
        source=model.AssetSourceEnum.GIT,
        jsonpath=None,
        lang_name="English",
        resource_type_name=settings.english_resource_type_name(resource_type),
    )

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

        self._json_data: list = []

    @property
    def json_data(self) -> list:
        """Provide public method for other modules to access."""
        return self._json_data

    @icontract.require(
        lambda self: self._json_file_url is not None and self._json_file is not None
    )
    @icontract.ensure(lambda self: self._json_data is not None)
    def __call__(self) -> None:
        """Download json data and parse it into equivalent python objects."""
        if file_utils.source_file_needs_update(self._json_file):
            logger.debug("Downloading %s...", self._json_file_url)
            url_utils.download_file(self._json_file_url, str(self._json_file.resolve()))

        if not self._json_data:
            logger.debug("Loading json file %s...", self._json_file)
            try:
                self._json_data = file_utils.load_json_object(self._json_file)
            except Exception:
                logger.exception("Caught exception: ")


class ResourceLookup(abc.ABC):
    """
    Abstract super class that exists for documentation/clarity of
    interface. Future lookup class that implements its interface could
    be USFMResourceGraphQLLookup for example.
    """

    @abc.abstractmethod
        """
        Given a resource, comprised of language code, e.g., 'en', a
        resource type, e.g., 'ulb-wa', and a resource code, e.g., 'gen',
        return URL for resource.

        Subclasses implement.
        """
        raise NotImplementedError
    def lookup(self, lang_code: str, resource_type: str, resource_code: str) -> model.ResourceLookupDto: ...


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
        lambda lang_code, resource_type, resource_code: lang_code is not None
        and resource_type is not None
        and resource_code is not None
    )
    @icontract.ensure(lambda result: result is not None)
    @log_on_end(logging.DEBUG, "model.ResourceLookupDto: {result}", logger=logger)
    def lookup(self, lang_code: str, resource_type: str, resource_code: str) -> model.ResourceLookupDto:
        """
        Given a resource, comprised of language code, e.g., 'en', a
        resource type, e.g., 'ulb-wa', and a resource code, e.g., 'gen',
        return URL for resource.
        """
        resource_lookup_dto: model.ResourceLookupDto

        # Special case:
        # Ironically, for English, translations.json file only
        # contains URLs to PDF assets rather than anything useful for
        # our purposes. Therefore, we have this guard to handle
        # English resource requests separately and outside of
        # translations.json by retrieving them from their git repos.
        if lang_code == "en":
            return _english_git_repo_location(resource_type)

        # Prefer getting USFM files individually rather than
        # introducing the latency of cloning a git repo.
        resource_lookup_dto = self._try_individual_usfm_location(lang_code, resource_type, resource_code)

        # Individual USFM file was not available, now try getting it
        # from a git repo.
        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_git_repo_location(lang_code, resource_type, resource_code)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level1_location(lang_code, resource_type, resource_code)

        return resource_lookup_dto

    @icontract.require(
        lambda lang_code, resource_type, resource_code: lang_code is not None
        and resource_type is not None
        and resource_code is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.USFM
        and result.jsonpath is not None
        # and result.lang_name
    )
    @log_on_end(logging.DEBUG, "model.ResourceLookupDto: {result}", logger=logger)
    def _try_individual_usfm_location(
            self, lang_code: str, resource_type: str, resource_code: str
    ) -> model.ResourceLookupDto:
        """
        If successful, return a model.ResourceLookupDto subclass
        instance.
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
        jsonpath_str = settings.INDIVIDUAL_USFM_URL_JSONPATH.format(
            lang_code, resource_type, resource_code,
        )
        urls: list[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = settings.RESOURCE_LANG_NAME_JSONPATH.format(
            lang_code
        )
        lang_name_lst: list[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = settings.RESOURCE_TYPE_NAME_JSONPATH.format(
            lang_code, resource_type
        )
        resource_type_name_lst: list[str] = self._lookup(resource_type_name_jsonpath_str)
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
        lambda lang_code, resource_type, resource_code: lang_code is not None
        and resource_type is not None
        and resource_code is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.ZIP
        and result.jsonpath is not None
        # and result.lang_name
    )
    @log_on_end(logging.DEBUG, "model.ResourceLookupDto: {result}", logger=logger)
    def _try_level1_location(
            self, lang_code: str, resource_type: str, resource_code: str
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
        jsonpath_str = settings.RESOURCE_URL_LEVEL1_JSONPATH.format(
            lang_code, resource_type, resource_code,
        )
        urls: list[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = settings.RESOURCE_LANG_NAME_JSONPATH.format(
            lang_code
        )
        lang_name_lst: list[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = settings.RESOURCE_TYPE_NAME_JSONPATH.format(
            lang_code, resource_type
        )
        resource_type_name_lst: list[str] = self._lookup(resource_type_name_jsonpath_str)
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

    # Make OO composition less arduous.
    def __getattr__(self, attribute: str) -> Any:
        """
        Redirect method lookups that are not on self to
        self.resource_json_lookup.
        """
        return getattr(self._resource_json_lookup, attribute)

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.require(
        lambda lang_code, resource_type, resource_code: lang_code is not None
        and resource_type is not None
        and resource_code is not None
    )
    @icontract.ensure(lambda result: result is not None)
    def lookup(self, lang_code: str, resource_type: str, resource_code: str) -> model.ResourceLookupDto:
        """
        Given a resource, comprised of language code, e.g., 'wum', a
        resource type, e.g., 'tn', and a resource code, e.g., 'gen',
        return model.ResourceLookupDto instance for resource.
        """
        resource_lookup_dto: model.ResourceLookupDto

        # For English, translations.json file only
        # contains URLs to PDF assets rather than anything useful for
        # our purposes. Therefore, we have this guard to handle
        # English resource requests separately outside of
        # translations.json.
        if lang_code == "en":
            return _english_git_repo_location(resource_type)

        resource_lookup_dto = self._try_level1_location(lang_code, resource_type)
        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level2_location(lang_code, resource_type)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level1_sans_resource_code_location(lang_code, resource_type)

        if resource_lookup_dto.url is None:
            resource_lookup_dto = self._try_level2_sans_resource_code_location(lang_code, resource_type)

        return resource_lookup_dto

    @icontract.require(
        lambda lang_code, resource_type: lang_code is not None
        and resource_type is not None
    )
    @icontract.ensure(
        lambda result: result.source == model.AssetSourceEnum.ZIP
        and result.jsonpath is not None
    )
    def _try_level1_location(self, lang_code: str, resource_type: str) -> model.ResourceLookupDto:
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
        jsonpath_str = settings.RESOURCE_URL_LEVEL1_JSONPATH.format(
            lang_code, resource_type,
        )
        urls: list[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = settings.RESOURCE_LANG_NAME_JSONPATH.format(
            lang_code
        )
        lang_name_lst: list[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = settings.RESOURCE_TYPE_NAME_JSONPATH.format(
            lang_code, resource_type
        )
        resource_type_name_lst: list[str] = self._lookup(resource_type_name_jsonpath_str)
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

    @icontract.require(lambda lang_code, resource_type: lang_code is not None and resource_type is not None)
    @icontract.ensure(lambda result: result.source == model.AssetSourceEnum.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_level2_location(self, lang_code: str, resource_type: str) -> model.ResourceLookupDto:
        """
        If successful, return a string containing the URL of Markdown
        zip file, otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = settings.RESOURCE_URL_LEVEL2_JSONPATH.format(
            lang_code, resource_type,
        )
        urls: list[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = settings.RESOURCE_LANG_NAME_JSONPATH.format(
            lang_code
        )
        lang_name_lst: list[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = settings.RESOURCE_TYPE_NAME_JSONPATH.format(
            lang_code, resource_type
        )
        resource_type_name_lst: list[str] = self._lookup(resource_type_name_jsonpath_str)
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

    @icontract.require(lambda lang_code, resource_type: lang_code is not None and resource_type is not None)
    @icontract.ensure(lambda result: result.source == model.AssetSourceEnum.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_level1_sans_resource_code_location(
            self, lang_code: str, resource_type: str
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
        jsonpath_str = settings.RESOURCE_URL_LEVEL1_JSONPATH.format(
            lang_code, resource_type,
        )
        urls: list[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = settings.RESOURCE_LANG_NAME_JSONPATH.format(
            lang_code
        )
        lang_name_lst: list[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_lst:
            lang_name = lang_name_lst[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = settings.RESOURCE_TYPE_NAME_JSONPATH.format(
            lang_code, resource_type
        )
        resource_type_name_lst: list[str] = self._lookup(resource_type_name_jsonpath_str)
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

    @icontract.require(lambda lang_code, resource_type: lang_code is not None and resource_type is not None)
    @icontract.ensure(lambda result: result.source == model.AssetSourceEnum.ZIP)
    @icontract.ensure(lambda result: result.jsonpath is not None)
    def _try_level2_sans_resource_code_location(
            self, lang_code: str, resource_type: str
    ) -> model.ResourceLookupDto:
        """
        For the language in question, the resource is apparently at
        its alternative location which we try next. If successful,
        return a string containing the URL of the Markdown zip file,
        otherwise return None.
        """
        url: Optional[str] = None
        jsonpath_str = settings.RESOURCE_URL_LEVEL2_JSONPATH.format(
            lang_code, resource_type,
        )
        urls: list[str] = self._lookup(jsonpath_str)
        if urls:
            url = urls[0]
        lang_name_jsonpath_str = settings.RESOURCE_LANG_NAME_JSONPATH.format(
            lang_code
        )
        lang_name_results: list[str] = self._lookup(lang_name_jsonpath_str)
        if lang_name_results:
            lang_name = lang_name_results[0]
        else:
            lang_name = ""
        resource_type_name_jsonpath_str = settings.RESOURCE_TYPE_NAME_JSONPATH.format(
            lang_code, resource_type
        )
        resource_type_name_results: list[str] = self._lookup(resource_type_name_jsonpath_str)
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

    # Make OO composition less arduous.
    def __getattr__(self, attribute: str) -> Any:
        """
        Redirect method lookups that are not on self to
        self.resource_json_lookup.
        """
        return getattr(self._resource_json_lookup, attribute)

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes(self) -> list[str]:
        """
        Convenience method that can be called from UI to get the set
        of all language codes available through API. Presumably this
        could be called to populate a drop-down menu.
        """
        codes: list[str] = []
        self._get_data()
        for lang in self.json_data:
            codes.append(lang["code"])
        return codes

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes_and_names(self) -> list[tuple[str, str]]:
        """
        Convenience method that can be called from UI to get the set
        of all language code, name tuples available through API.
        Presumably this could be called to populate a drop-down menu.
        """
        self._get_data()
        codes_and_names: list[tuple[str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self.json_data:
            codes_and_names.append((d["code"], d["name"]))
        return codes_and_names

    @icontract.ensure(lambda result: result)
    def resource_types(self) -> list[str]:
        """
        Convenience method that can be called, e.g., from the UI, to
        get the set of all resource types.
        """
        return self._lookup(settings.RESOURCE_TYPES_JSONPATH)

    @icontract.ensure(lambda result: result)
    def resource_codes(self) -> list[str]:
        """
        Convenience method that can be called, e.g., from the UI, to
        get the set of all resource codes.
        """
        return self._lookup(settings.RESOURCE_CODES_JSONPATH)

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes_names_and_resource_types(self) -> list[model.CodeNameTypeTriplet]:
        """
        Convenience method that can be called to get the list
        of all tuples where each tuple consists of language code,
        language name, and list of resource types available for that
        language.

        Example usage in repl:
        >>> from document.domain import resource_lookup
        >>> data = resource_lookup.BIELHelperResourceJsonLookup().lang_codes_names_and_resource_types()
        Lookup the resource types available for zh
        >>> [pair[2] for pair in data if pair[0] == "zh"]
        [['cuv', 'tn', 'tq', 'tw']]
        """
        lang_codes_names_and_resource_types: list[model.CodeNameTypeTriplet] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for lang in self.json_data:
            resource_types: list[str] = []
            for resource_type_dict in lang["contents"]:
                try:
                    resource_type = resource_type_dict["code"]
                    resource_types.append(resource_type)
                except Exception:
                    resource_type = None
            lang_codes_names_and_resource_types.append(
                model.CodeNameTypeTriplet(lang_code=lang["code"], lang_name=lang["name"], resource_types=resource_types)
            )
        return lang_codes_names_and_resource_types

    @icontract.require(lambda self: self.json_data is not None)
    @icontract.ensure(lambda result: result)
    def lang_codes_names_resource_types_and_resource_codes(
        self,
    ) -> list[tuple[str, str, list[tuple[str, list[str]]]]]:
        """
        Convenience method that can be called to get the set
        of all tuples where each tuple consists of language code,
        language name, list of resource types available for that
        language, and the resource_codes available for each resource
        type.

        Example usage in repl:
        >>> from document.domain import resource_lookup
        >>> data = resource_lookup.BIELHelperResourceJsonLookup().lang_codes_names_resource_types_and_resource_codes()
        Lookup the resource type available for zh
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
        lang_codes_names_resource_types_and_resource_codes: list[
            tuple[str, str, list[tuple[str, list[str]]]]
        ] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for lang in self.json_data:
            resource_types: list[tuple[str, list[str]]] = []
            for resource_type_dict in lang["contents"]:
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
                except Exception:
                    resource_type = None
                resource_codes_list = resource_type_dict["subcontents"]
                resource_codes: list[str] = []
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
    def lang_codes_names_and_contents_codes(self) -> list[tuple[str, str, str]]:
        """
        Convenience test method that can be called to get the set
        of all language code, language name, contents level code as
        tuples. Contents level code is a reference to the structure of
        translations.json, e.g.:

        [
          {
            "name": "Abadi",
            "code": "kbt",
            "direction": "ltr",
            "contents": [
            {
                "name": "Bible",
                "code": "reg",    <---- contents > code
                "subcontents": [
                ...

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
        # See <project dir>/lang_codes_names_and_contents_codes_groups.json for
        output dumped to json format.
        """
        lang_codes_names_and_contents_codes: list[tuple[str, str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self.json_data:
            try:
                contents_code = d["contents"][0]["code"]
            except Exception:
                contents_code = "nil"
            lang_codes_names_and_contents_codes.append(
                (d["code"], d["name"], contents_code)
            )
        return lang_codes_names_and_contents_codes
