"""
This module provides an API for looking up the location of a
resource's asset files in the cloud and acquiring said resource
assets.
"""


import pathlib
import shutil
import subprocess
import urllib
from contextlib import closing
from os import mkdir, scandir
from os.path import exists, join, sep
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence
from urllib import parse as urllib_parse
from urllib.request import urlopen

import git
import jsonpath_rw_ext as jp  # type: ignore
from document.config import settings
from document.domain import bible_books, exceptions
from document.domain.model import (
    AssetSourceEnum,
    CodeNameTypeTriplet,
    ResourceLookupDto,
)
from document.utils.file_utils import (
    asset_file_needs_update,
    load_json_object,
    source_file_needs_update,
    unzip,
)
from fastapi import HTTPException, status
from yaml import safe_load

logger = settings.logger(__name__)

H1, H2, H3, H4 = "h1", "h2", "h3", "h4"


def download_file(
    url: str, outfile: str, user_agent: str = settings.USER_AGENT
) -> None:
    """Downloads a file from url and saves it to outfile."""
    # NOTE Host requires at least the User-Agent header.
    headers: dict[str, str] = {"User-Agent": user_agent}
    req = urllib.request.Request(url, None, headers)
    with closing(urlopen(req)) as request:
        with open(outfile, "wb") as fp:
            shutil.copyfileobj(request, fp)


def fetch_source_data(working_dir: str, json_file_url: str) -> Any:
    """
    Obtain the source data, by downloading it from json_file_url, and
    then reifying it into its JSON object form.
    """
    json_file = pathlib.Path(join(working_dir, json_file_url.rpartition(sep)[2]))
    if source_file_needs_update(json_file):
        logger.debug("Downloading %s...", json_file_url)
        download_file(json_file_url, str(json_file.resolve()))

    try:
        return load_json_object(json_file)
    except Exception:
        logger.exception("Caught exception: ")


def _lookup(
    json_path: str,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
) -> Any:
    """Return jsonpath value or empty list if JSON node doesn't exist."""
    json_data = fetch_source_data(working_dir, translations_json_location)
    value = jp.match(
        json_path,
        json_data,
    )
    value_set = set(value)
    return list(value_set)


def _parse_repo_url(
    url: str,
    repo_url_dict_key: str = settings.REPO_URL_DICT_KEY,
    alt_repo_url_dict_key: str = settings.ALT_REPO_URL_DICT_KEY,
) -> Optional[str]:
    """
    Given a URL of the form
    ../download-scripture?repo_url=https%3A%2F%2Fgit.door43.org%2Fburje_duro%2Fam_gen_text_udb&book_name=Genesis,
    return the repo_url query parameter value.
    """
    if url is None:
        return None
    result = urllib_parse.parse_qs(url)
    result_lst = []
    try:
        result_lst = result[repo_url_dict_key]
    except KeyError:
        logger.debug(
            "repo_url_dict_key: %s, is not the right key for this url: %s, trying %s key instead",
            repo_url_dict_key,
            url,
            alt_repo_url_dict_key,
        )
        result_lst = result[alt_repo_url_dict_key]
    if result_lst:
        return result_lst[0]
    return None


def _english_git_repo_location(
    lang_code: str,
    resource_type: str,
    resource_code: str,
    url: str,
    resource_type_name: str,
    asset_source_enum_kind: AssetSourceEnum = AssetSourceEnum.GIT,
) -> ResourceLookupDto:
    """Return a model.ResourceLookupDto."""
    return ResourceLookupDto(
        lang_code=lang_code,
        resource_type=resource_type,
        resource_code=resource_code,
        url=url,
        source=asset_source_enum_kind,
        jsonpath=None,
        lang_name="English",
        resource_type_name=resource_type_name,
    )


def _id_git_repo_location(
    lang_code: str,
    resource_type: str,
    resource_code: str,
    url: str,
    resource_type_name: str,
    asset_source_enum_kind: AssetSourceEnum = AssetSourceEnum.GIT,
    id_lang_name: str = settings.ID_LANGUAGE_NAME,
) -> ResourceLookupDto:
    """Return a model.ResourceLookupDto."""
    return ResourceLookupDto(
        lang_code=lang_code,
        resource_type=resource_type,
        resource_code=resource_code,
        url=url,
        source=asset_source_enum_kind,
        jsonpath=None,
        lang_name=id_lang_name,
        resource_type_name=resource_type_name,
    )


def const(url: str) -> Optional[str]:
    """Classic functional constant function."""
    return url


def _location(
    lang_code: str,
    resource_type: str,
    resource_code: str,
    jsonpath_str: str,
    lang_name_jsonpath_str: str,
    resource_type_name_jsonpath_str: str,
    asset_source_enum_kind: AssetSourceEnum,
    url_parsing_fn: Callable[[str], Optional[str]] = const,
) -> ResourceLookupDto:
    """Return a model.ResourceLookupDto."""
    # Many languages have a git repo found by
    # format='Download' that is parallel to the
    # individual, per book, USFM files.
    #
    # There is at least one language, code='ar', that has only single USFM
    # files. In that particular language, and others like it, all the
    # individual USFM files per book can also be found in a zip file,
    # $[?code='ar'].contents[?code='nav'].links[format='zip'].
    #
    # Another, yet different, example is the case of
    # $[?code="avd"] which has format="usfm" without
    # having a zip containing USFM files at the same level.
    url: Optional[str] = None
    urls = _lookup(jsonpath_str)
    if urls:
        url = url_parsing_fn(urls[0])
    lang_name_lst = _lookup(lang_name_jsonpath_str)
    if lang_name_lst:
        lang_name = lang_name_lst[0]
    else:
        lang_name = ""
    resource_type_name_lst = _lookup(resource_type_name_jsonpath_str)
    if resource_type_name_lst:
        resource_type_name = resource_type_name_lst[0]
    else:
        resource_type_name = ""
    return ResourceLookupDto(
        lang_code=lang_code,
        lang_name=lang_name,
        resource_type=resource_type,
        resource_type_name=resource_type_name,
        resource_code=resource_code,
        url=url,
        source=asset_source_enum_kind,
        jsonpath=jsonpath_str,
    )


def english_resource_type_name(
    resource_type: str,
    english_resource_type_map: Mapping[str, str] = settings.ENGLISH_RESOURCE_TYPE_MAP,
) -> str:
    """
    This is a hack to compensate for translations.json which only
    provides accurate information for non-English languages.
    """
    return english_resource_type_map[resource_type]


def id_resource_type_name(
    resource_type: str,
    id_resource_type_map: Mapping[str, str] = settings.ID_RESOURCE_TYPE_MAP,
) -> str:
    """
    This is a hack to compensate for translations.json which only
    provides accurate information for non-English languages and lang_code ID.
    """
    return id_resource_type_map[resource_type]


def english_git_repo_url(
    resource_type: str,
    english_git_repo_map: Mapping[str, str] = settings.ENGLISH_GIT_REPO_MAP,
) -> str:
    """
    This is a hack to compensate for translations.json which only
    provides accurate URLs in non-English languages.
    """
    return english_git_repo_map[resource_type]


def id_git_repo_url(
    resource_type: str,
    id_git_repo_map: Mapping[str, str] = settings.ID_GIT_REPO_MAP,
) -> str:
    """
    This is a hack to compensate for translations.json which only
    provides accurate URLs in non-English languages and lang_code ID.
    """
    return id_git_repo_map[resource_type]


def usfm_resource_lookup(
    lang_code: str,
    resource_type: str,
    resource_code: str,
    individual_usfm_url_jsonpath_fmt_str: str = settings.INDIVIDUAL_USFM_URL_JSONPATH,
    resource_lang_name_jsonpath_fmt_str: str = settings.RESOURCE_LANG_NAME_JSONPATH,
    resource_type_name_jsonpath_fmt_str: str = settings.RESOURCE_TYPE_NAME_JSONPATH,
    asset_source_enum_usfm_kind: AssetSourceEnum = AssetSourceEnum.USFM,
    asset_source_enum_git_kind: AssetSourceEnum = AssetSourceEnum.GIT,
    asset_source_enum_zip_kind: AssetSourceEnum = AssetSourceEnum.ZIP,
    resource_download_format_jsonpath_fmt_str: str = settings.RESOURCE_DOWNLOAD_FORMAT_JSONPATH,
    resource_url_level1_jsonpath_fmt_str: str = settings.RESOURCE_URL_LEVEL1_JSONPATH,
) -> ResourceLookupDto:
    """
    Given a resource, comprised of language code, e.g., 'fr', a
    resource type, e.g., 'ulb', and a resource code, e.g., 'gen',
    return model.ResourceLookupDto for resource.
    """
    resource_lookup_dto: ResourceLookupDto

    # Prefer getting USFM files individually rather than
    # introducing the latency of cloning a git repo.
    resource_lookup_dto = _location(
        lang_code,
        resource_type,
        resource_code,
        jsonpath_str=individual_usfm_url_jsonpath_fmt_str.format(
            lang_code,
            resource_type,
            resource_code,
        ),
        lang_name_jsonpath_str=resource_lang_name_jsonpath_fmt_str.format(lang_code),
        resource_type_name_jsonpath_str=resource_type_name_jsonpath_fmt_str.format(
            lang_code, resource_type
        ),
        asset_source_enum_kind=asset_source_enum_usfm_kind,
    )

    # Individual USFM file was not available, now try getting it
    # from a zip file.
    if resource_lookup_dto.url is None:
        resource_lookup_dto = _location(
            lang_code,
            resource_type,
            resource_code,
            jsonpath_str=resource_url_level1_jsonpath_fmt_str.format(
                lang_code,
                resource_type,
            ),
            lang_name_jsonpath_str=resource_lang_name_jsonpath_fmt_str.format(
                lang_code
            ),
            resource_type_name_jsonpath_str=resource_type_name_jsonpath_fmt_str.format(
                lang_code, resource_type
            ),
            asset_source_enum_kind=asset_source_enum_zip_kind,
        )

    # Zip file was not available, now try getting it
    # from a git repo (which is the slowest way to get assets).
    if resource_lookup_dto.url is None:
        resource_lookup_dto = _location(
            lang_code,
            resource_type,
            resource_code,
            jsonpath_str=resource_download_format_jsonpath_fmt_str.format(
                lang_code,
                resource_type,
                resource_code,
            ),
            lang_name_jsonpath_str=resource_lang_name_jsonpath_fmt_str.format(
                lang_code
            ),
            resource_type_name_jsonpath_str=resource_type_name_jsonpath_fmt_str.format(
                lang_code, resource_type
            ),
            asset_source_enum_kind=asset_source_enum_git_kind,
            url_parsing_fn=_parse_repo_url,
        )

    return resource_lookup_dto


def t_resource_lookup(
    lang_code: str,
    resource_type: str,
    resource_code: str,
    lang_name_jsonpath_fmt_str: str = settings.RESOURCE_LANG_NAME_JSONPATH,
    resource_type_name_jsonpath_fmt_str: str = settings.RESOURCE_TYPE_NAME_JSONPATH,
    resource_url_level1_jsonpath_fmt_str: str = settings.RESOURCE_URL_LEVEL1_JSONPATH,
    resource_url_level2_jsonpath_fmt_str: str = settings.RESOURCE_URL_LEVEL2_JSONPATH,
    asset_source_enum_kind: AssetSourceEnum = AssetSourceEnum.ZIP,
) -> ResourceLookupDto:
    """
    Given a non-English language resource, comprised of language code,
    e.g., 'wum', a resource type, e.g., 'tn', and a resource code,
    e.g., 'gen', return a model.ResourceLookupDto instance for
    resource.
    """
    resource_lookup_dto: ResourceLookupDto

    resource_lookup_dto = _location(
        lang_code,
        resource_type,
        resource_code,
        jsonpath_str=resource_url_level1_jsonpath_fmt_str.format(
            lang_code,
            resource_type,
        ),
        lang_name_jsonpath_str=lang_name_jsonpath_fmt_str.format(lang_code),
        resource_type_name_jsonpath_str=resource_type_name_jsonpath_fmt_str.format(
            lang_code, resource_type
        ),
        asset_source_enum_kind=asset_source_enum_kind,
    )
    if resource_lookup_dto.url is None:
        resource_lookup_dto = _location(
            lang_code,
            resource_type,
            resource_code,
            jsonpath_str=resource_url_level2_jsonpath_fmt_str.format(
                lang_code,
                resource_type,
            ),
            lang_name_jsonpath_str=lang_name_jsonpath_fmt_str.format(lang_code),
            resource_type_name_jsonpath_str=resource_type_name_jsonpath_fmt_str.format(
                lang_code, resource_type
            ),
            asset_source_enum_kind=asset_source_enum_kind,
        )

    if resource_lookup_dto.url is None:
        resource_lookup_dto = _location(
            lang_code,
            resource_type,
            resource_code,
            jsonpath_str=resource_url_level1_jsonpath_fmt_str.format(
                lang_code,
                resource_type,
            ),
            lang_name_jsonpath_str=lang_name_jsonpath_fmt_str.format(lang_code),
            resource_type_name_jsonpath_str=resource_type_name_jsonpath_fmt_str.format(
                lang_code, resource_type
            ),
            asset_source_enum_kind=asset_source_enum_kind,
        )

    if resource_lookup_dto.url is None:
        resource_lookup_dto = _location(
            lang_code,
            resource_type,
            resource_code,
            jsonpath_str=resource_url_level2_jsonpath_fmt_str.format(
                lang_code,
                resource_type,
            ),
            lang_name_jsonpath_str=lang_name_jsonpath_fmt_str.format(lang_code),
            resource_type_name_jsonpath_str=resource_type_name_jsonpath_fmt_str.format(
                lang_code, resource_type
            ),
            asset_source_enum_kind=asset_source_enum_kind,
        )

    return resource_lookup_dto


def lang_codes(
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    lang_code_filter_list: Sequence[str] = settings.LANG_CODE_FILTER_LIST,
) -> Iterable[Any]:
    """
    Convenience method that can be called from UI to get the set
    of all language codes available through API. Presumably this
    could be called to populate a drop-down menu.
    """
    data = fetch_source_data(working_dir, translations_json_location)
    for lang in [lang for lang in data if lang["code"] not in lang_code_filter_list]:
        yield lang["code"]


def lang_codes_and_names(
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    lang_code_filter_list: Sequence[str] = settings.LANG_CODE_FILTER_LIST,
) -> Sequence[tuple[str, str]]:
    """
    Convenience method that can be called from UI to get the set
    of all language code, name tuples available through API.
    Presumably this could be called to populate a drop-down menu.

    >>> from document.domain import resource_lookup
    >>> data = resource_lookup.lang_codes_and_names()
    >>> data[0]
    ('abz', 'Abui (Abui)')
    """
    data = fetch_source_data(working_dir, translations_json_location)
    values = [
        (d["code"], "{} ({})".format(d["name"], d["englishName"]))
        for d in [lang for lang in data if lang["code"] not in lang_code_filter_list]
    ]
    return sorted(values, key=lambda value: value[1])


def lang_codes_and_names_for_v1(
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    gateway_languages: Sequence[str] = settings.GATEWAY_LANGUAGES,
    lang_code_filter_list: Sequence[str] = settings.LANG_CODE_FILTER_LIST,
) -> Sequence[tuple[str, str]]:
    """
    Convenience method that can be called from UI to get the set
    of gateway only (for v1) language code, name tuples available
    through API.

    >>> from document.domain import resource_lookup
    >>> data = resource_lookup.lang_codes_and_names_for_v1()
    >>> data[0]
    ('am', 'Amharic (Amharic)')
    """
    data = fetch_source_data(working_dir, translations_json_location)
    values = [
        (d["code"], "{} ({})".format(d["name"], d["englishName"]))
        for d in [
            lang
            for lang in data
            if lang["code"] in gateway_languages
            and lang["code"] not in lang_code_filter_list
        ]
    ]
    return sorted(values, key=lambda value: value[1])


def resource_types(jsonpath_str: str = settings.RESOURCE_TYPES_JSONPATH) -> Any:
    """
    Convenience method that can be called, e.g., from the UI, to
    get the set of all resource types.
    >>> from document.domain import resource_lookup
    >>> sorted(resource_lookup.resource_types())
    ['Reg', 'avd', 'bc', 'blv', 'cuv', 'dot', 'f10', 'nav', 'nva', 'reg', 'rg', 'rlv', 'ta', 'ta-wa', 'tn', 'tn-wa', 'tq', 'tq-wa', 'tw', 'tw-wa', 'udb', 'udb-wa', 'ugnt', 'uhb', 'ulb', 'ulb-wa']
    """
    return _lookup(jsonpath_str)


def resource_types_for_v1(
    jsonpath_str: str = settings.RESOURCE_TYPES_JSONPATH,
    v1_version_approved_resource_types: Sequence[
        str
    ] = settings.V1_APPROVED_RESOURCE_TYPES,
) -> Any:
    """
    Convenience method that can be called, e.g., from the UI, to
    get the set of resource types approved for v1 release that are available in translations.json.
    >>> from document.domain import resource_lookup
    >>> sorted(resource_lookup.resource_types_for_v1())
    ['cuv', 'nav', 'reg', 'tn', 'tn-wa', 'ugnt', 'ulb', 'ulb-wa']
    """
    # Filter the resource types available to be only USFM and TN
    # types that have been approved for v1 release.
    return [
        resource_type
        for resource_type in _lookup(jsonpath_str)
        if resource_type in v1_version_approved_resource_types
    ]


# FIXME Remove when no longer needed.
def resource_types_for_langs(
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> Iterable[tuple[str, Sequence[Any]]]:
    """
    Utility function for investigating which languages have more than
    one USFM resource type as this relates to a bug I need to handle.

    Commenting out for now so that I can run other doctests as this takes a while.
    >>> # from document.domain import resource_lookup
    >>> # data = resource_lookup.resource_types_for_langs()
    >>> # list(data)
    [('grc', ['ulb', 'ugnt']), ('plt-x-antaifasy', ['ulb', 'reg']), ('lai-x-bandya', ['ulb', 'reg']), ('xdy-x-batangkawa', ['udb', 'reg']), ('byn', ['ulb', 'reg']), ('beu', ['ulb', 'reg']), ('bou', ['ulb', 'reg']), ('set-x-csentani', ['udb', 'reg']), ('iba-x-ketungau', ['ulb', 'reg']), ('xdy-x-senduruhan', ['ulb', 'udb', 'reg']), ('dic', ['ulb', 'reg']), ('cfa-x-dijim', ['ulb', 'reg']), ('ish', ['ulb', 'reg']), ('ee', ['ulb', 'reg']), ('fr', ['ulb', 'tw', 'tq', 'tn', 'f10']), ('kna-x-gasi', ['ulb', 'reg']), ('gux-x-gourmantche', ['ulb', 'reg']), ('gu', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('han', ['ulb', 'reg']), ('hav', ['ulb', 'reg']), ('hi', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('kpo', ['ulb', 'reg']), ('ilo', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('jni', ['ulb', 'reg']), ('ldl', ['ulb', 'reg']), ('kbp', ['ulb', 'reg']), ('kxh', ['ulb', 'reg']), ('gqa-x-kabinda', ['ulb', 'reg']), ('shr-x-kigweshe', ['ulb', 'reg']), ('hav-x-kihavuidjui', ['ulb', 'reg']), ('kkq-x-kikubere', ['ulb', 'reg']), ('shr-x-kilinjalinja', ['ulb', 'reg']), ('tbt-x-kirhinyihinyi', ['ulb', 'reg']), ('kmq', ['ulb', 'reg']), ('las', ['ulb', 'reg']), ('es-419', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('wew-x-loli', ['ulb', 'reg']), ('lpx', ['ulb', 'reg']), ('sie-x-makoma', ['ulb', 'reg']), ('bzc', ['ulb', 'reg']), ('zmb-x-mamba', ['ulb', 'reg']), ('mr', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('mgw', ['ulb', 'udb', 'reg']), ('hna', ['ulb', 'reg']), ('mwn-MW-namwanga', ['ulb', 'reg']), ('ne', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('nij', ['udb', 'reg']), ('nbh', ['ulb', 'reg']), ('ngq', ['ulb', 'reg']), ('or', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('pnb', ['ulb', 'reg']), ('saw', ['udb', 'reg']), ('sze', ['ulb', 'udb', 'reg']), ('plt-x-sihanaka', ['ulb', 'reg']), ('ors-x-oranglau', ['udb', 'reg']), ('suw', ['ulb', 'udb', 'reg']), ('tl', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('kcg-x-takad', ['ulb', 'reg']), ('tal', ['ulb', 'reg']), ('kcg', ['ulb', 'reg']), ('utu', ['ulb', 'reg']), ('vi', ['ulb', 'udb', 'tw', 'tq', 'tn']), ('mlp-x-wasabamal', ['ulb', 'reg']), ('ybl', ['ulb', 'reg'])]
    """
    langs = lang_codes()
    for lang in langs:
        resource_types = resource_types_for_lang(lang)
        usfm_resource_types_for_lang = [
            resource_type
            for resource_type in resource_types
            if resource_type in usfm_resource_types
        ]
        if len(usfm_resource_types_for_lang) > 1:
            yield (lang, resource_types)


def resource_types_for_lang(
    lang_code: str,
    jsonpath_str: str = settings.RESOURCE_TYPES_FOR_LANG_JSONPATH,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    en_tn_resource_types: Sequence[str] = settings.EN_TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
    bc_resource_types: Sequence[str] = settings.BC_RESOURCE_TYPES,
) -> Sequence[Any]:
    """
    Convenience method that can be called, e.g., from the UI, to
    get the set of all resource types for a particular lang_code.
    """
    # Add bible commentary resource types to set of resource types for
    # language if the language is English as only English has bible
    # commentary available at this time. Preferrably we'd get all resource
    # types from the _lookup function which gets it data from
    # translations.json currently, but unfortunately, translations.json does
    # not include bible commentary as a resource type. As such this is
    # somewhat of a hack and should probably be addressed in the data
    # pipeline such that English bible commentary info is added to
    # translations.json.
    resource_types_list = (
        _lookup(jsonpath_str.format(lang_code)) + bc_resource_types
        if lang_code == "en"
        else _lookup(jsonpath_str.format(lang_code))
    )
    resource_types = [
        resource_type
        for resource_type in resource_types_list
        if resource_type in usfm_resource_types
        or (
            resource_type in en_tn_resource_types
            if lang_code == "en"
            else resource_type in tn_resource_types
        )
        or resource_type in tq_resource_types
        or resource_type in tw_resource_types
        or resource_type in bc_resource_types
    ]
    return sorted(resource_types, reverse=True)


def resource_types_and_names_for_lang(
    lang_code: str,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    english_resource_type_map: Mapping[str, str] = settings.ENGLISH_RESOURCE_TYPE_MAP,
    id_resource_type_map: Mapping[str, str] = settings.ID_RESOURCE_TYPE_MAP,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
) -> list[tuple[str, str]]:
    """
    Convenience method that can be called from UI to get the set
    of all resource type, name tuples for a given language available
    through API. Presumably this could be called to populate a
    drop-down menu.

    >>> from document.domain import resource_lookup
    >>> from document.config import settings
    >>> import logging
    >>> import sys
    >>> logger.addHandler(logging.StreamHandler(sys.stdout))
    >>> import pprint
    >>> # pprint.pprint(resource_lookup.resource_codes_and_types_for_lang("fr"))
    >>> pprint.pprint(resource_lookup.resource_types_and_names_for_lang("en"))
    [('ulb-wa', 'Unlocked Literal Bible (ULB)'),
     ('tn-wa', 'ULB Translation Notes'),
     ('tq-wa', 'ULB Translation Questions'),
     ('tw-wa', 'ULB Translation Words'),
     ('bc-wa', 'Bible Commentary')]
    >>> pprint.pprint(resource_lookup.resource_types_and_names_for_lang("es-419"))
    [('tn', 'Translation Notes (tn)'),
     ('tq', 'Translation Questions (tq)'),
     ('tw', 'Translation Words (tw)'),
     ('ulb', 'Español Latino Americano ULB (ulb)')]

    >>> pprint.pprint(sorted([(lang_code,resource_lookup.resource_types_and_names_for_lang(lang_code)) for lang_code in settings.GATEWAY_LANGUAGES], key=lambda group: group[0]))
    [('am',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('arb',
      [('nav', 'New Arabic Version (Ketab El Hayat) (nav)'),
       ('tw', 'Translation Words (tw)')]),
     ('as',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Assamese Unlocked Literal Bible (ulb)')]),
     ('bn',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Bengali Unlocked Literal Bible (ulb)')]),
     ('ceb',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Cebuano Unlocked Literal Bible (ulb)')]),
     ('en',
      [('ulb-wa', 'Unlocked Literal Bible (ULB)'),
       ('tn-wa', 'ULB Translation Notes'),
       ('tq-wa', 'ULB Translation Questions'),
       ('tw-wa', 'ULB Translation Words'),
       ('bc-wa', 'Bible Commentary')]),
     ('es-419',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Español Latino Americano ULB (ulb)')]),
     ('fa',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Henry Martyn Open Source Bible (1876) (ulb)')]),
     ('fr',
      [('f10', 'French Louis Segond 1910 Bible (f10)'),
       ('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'French ULB (ulb)')]),
     ('gu',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Gujarati Unlocked Literal Bible (ulb)')]),
     ('ha',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Hausa (ulb)')]),
     ('hi',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Hindi (ulb)')]),
     ('id',
      [('ayt', 'Bahasa Indonesian Bible (ayt)'),
       ('tn', 'Translation Helps (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)')]),
     ('ilo',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Ilocano (ulb)')]),
     ('km',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Khmer (ulb)')]),
     ('kn',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Kannada Unlocked Literal Bible (ulb)')]),
     ('lo',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Lao ULB (ulb)')]),
     ('ml',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Malayalam (ulb)')]),
     ('mr',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Marathi (ulb)')]),
     ('my',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Burmese Judson Bible (ulb)')]),
     ('ne',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Nepali (ulb)')]),
     ('or',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Oriya Unlocked Literal Bible (ulb)')]),
     ('pa',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Punjabi Unlocked Literal Bible (ulb)')]),
     ('plt',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Plateau Malagasy Unlocked Literal Bible (ulb)')]),
     ('pmy',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)')]),
     ('pt-br',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Brazilian Portuguese Unlocked Literal Bible (ulb)')]),
     ('ru',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Russian Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Russian Unlocked Literal Bible (ulb)')]),
     ('sw',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Swahili Unlocked Literal Bible (ulb)')]),
     ('ta',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Tamil (ulb)')]),
     ('te',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Telugu (ulb)')]),
     ('th',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('tl',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Tagalog Unlocked Literal Bible (ulb)')]),
     ('tpi', [('ulb', 'Tok Pisin Unlocked Literal Bible (ulb)')]),
     ('ur', [('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('ur-deva',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Urdu (ulb)')]),
     ('vi',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Vietnamese Unlocked Literal Bible (ulb)')]),
     ('zh',
      [('cuv', '新标点和合本 (cuv)'),
       ('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)')])]

    >>> pprint.pprint(sorted([(lang_code,resource_lookup.resource_types_and_names_for_lang(lang_code)) for lang_code in settings.GATEWAY_LANGUAGES if lang_code not in settings.LANG_CODE_FILTER_LIST], key=lambda group: group[0]))
    [('am',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('arb',
      [('nav', 'New Arabic Version (Ketab El Hayat) (nav)'),
       ('tw', 'Translation Words (tw)')]),
     ('as',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Assamese Unlocked Literal Bible (ulb)')]),
     ('bn',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Bengali Unlocked Literal Bible (ulb)')]),
     ('ceb',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Cebuano Unlocked Literal Bible (ulb)')]),
     ('en',
      [('ulb-wa', 'Unlocked Literal Bible (ULB)'),
       ('tn-wa', 'ULB Translation Notes'),
       ('tq-wa', 'ULB Translation Questions'),
       ('tw-wa', 'ULB Translation Words'),
       ('bc-wa', 'Bible Commentary')]),
     ('es-419',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Español Latino Americano ULB (ulb)')]),
     ('fr',
      [('f10', 'French Louis Segond 1910 Bible (f10)'),
       ('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'French ULB (ulb)')]),
     ('gu',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Gujarati Unlocked Literal Bible (ulb)')]),
     ('ha',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Hausa (ulb)')]),
     ('hi',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Hindi (ulb)')]),
     ('id',
      [('ayt', 'Bahasa Indonesian Bible (ayt)'),
       ('tn', 'Translation Helps (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)')]),
     ('ilo',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Ilocano (ulb)')]),
     ('km',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Khmer (ulb)')]),
     ('kn',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Kannada Unlocked Literal Bible (ulb)')]),
     ('lo',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Lao ULB (ulb)')]),
     ('ml',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Malayalam (ulb)')]),
     ('mr',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Marathi (ulb)')]),
     ('my',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Burmese Judson Bible (ulb)')]),
     ('ne',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Nepali (ulb)')]),
     ('or',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Oriya Unlocked Literal Bible (ulb)')]),
     ('pa',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Punjabi Unlocked Literal Bible (ulb)')]),
     ('plt',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Plateau Malagasy Unlocked Literal Bible (ulb)')]),
     ('pt-br',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Brazilian Portuguese Unlocked Literal Bible (ulb)')]),
     ('ru',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Russian Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Russian Unlocked Literal Bible (ulb)')]),
     ('sw',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Swahili Unlocked Literal Bible (ulb)')]),
     ('ta',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Tamil (ulb)')]),
     ('te',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Telugu (ulb)')]),
     ('th',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('tl',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Tagalog Unlocked Literal Bible (ulb)')]),
     ('tpi', [('ulb', 'Tok Pisin Unlocked Literal Bible (ulb)')]),
     ('ur', [('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('ur-deva',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Unlocked Literal Bible - Urdu (ulb)')]),
     ('vi',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)'),
       ('ulb', 'Vietnamese Unlocked Literal Bible (ulb)')]),
     ('zh',
      [('cuv', '新标点和合本 (cuv)'),
       ('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)')])]

    >>> pprint.pprint(sorted([(lang_code,resource_lookup.resource_types_and_names_for_lang(lang_code)) for lang_code in settings.GATEWAY_LANGUAGES if lang_code in settings.LANG_CODE_FILTER_LIST], key=lambda group: group[0]))
    [('fa',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Henry Martyn Open Source Bible (1876) (ulb)')]),
     ('pmy',
      [('tn', 'Translation Notes (tn)'),
       ('tq', 'Translation Questions (tq)'),
       ('tw', 'Translation Words (tw)')])]

    >>> sorted([lang_code for lang_code in settings.GATEWAY_LANGUAGES if lang_code not in settings.LANG_CODE_FILTER_LIST])
    ['am', 'arb', 'as', 'bn', 'ceb', 'en', 'es-419', 'fr', 'gu', 'ha', 'hi', 'id', 'ilo', 'km', 'kn', 'lo', 'ml', 'mr', 'my', 'ne', 'or', 'pa', 'plt', 'pt-br', 'ru', 'sw', 'ta', 'te', 'th', 'tl', 'tpi', 'ur', 'ur-deva', 'vi', 'zh']
    >>> sorted([lang_code for lang_code in settings.GATEWAY_LANGUAGES if lang_code in settings.LANG_CODE_FILTER_LIST])
    ['fa', 'pmy']


    List of GL languages and their translations.json listed resource
    types (filtered, but including udb and f10) USFM and (all) TN
    types that translations.json lists as available for the GL
    languages:

    >>> data = resource_lookup.fetch_source_data(settings.RESOURCE_ASSETS_DIR, settings.TRANSLATIONS_JSON_LOCATION)
    >>> values = []
    >>> for item in [lang for lang in data if lang["code"] in settings.GATEWAY_LANGUAGES]:
    ...    values.append(
    ...        (item["code"],
    ...           [
    ...               resource_type["code"]
    ...               for resource_type in item["contents"]
    ...               if (
    ...                   resource_type["code"] in settings.EN_USFM_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.USFM_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.EN_TN_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.TN_RESOURCE_TYPES
    ...               )
    ...           ]
    ...        )
    ...    )
    >>> sorted_values = sorted(values, key=lambda value: value[0])
    >>> pprint.pprint(sorted_values)
    [('am', ['tn', 'ulb']),
     ('arb', ['nav']),
     ('as', ['tn', 'ulb']),
     ('bn', ['tn', 'ulb']),
     ('ceb', ['tn', 'ulb']),
     ('en', ['ulb-wa', 'tn-wa', 'tn']),
     ('es-419', ['tn', 'ulb']),
     ('fa', ['tn', 'ulb']),
     ('fr', ['tn', 'ulb', 'f10']),
     ('gu', ['tn', 'ulb']),
     ('ha', ['tn', 'ulb']),
     ('hi', ['tn', 'ulb']),
     ('id', ['tn']),
     ('ilo', ['tn', 'ulb']),
     ('km', ['tn', 'ulb']),
     ('kn', ['tn', 'ulb']),
     ('lo', ['tn', 'ulb']),
     ('ml', ['tn', 'ulb']),
     ('mr', ['tn', 'ulb']),
     ('my', ['tn', 'ulb']),
     ('ne', ['tn', 'ulb']),
     ('or', ['tn', 'ulb']),
     ('pa', ['tn', 'ulb']),
     ('plt', ['tn', 'ulb']),
     ('pmy', ['tn']),
     ('pt-br', ['tn', 'ulb']),
     ('ru', ['tn', 'ulb']),
     ('sw', ['tn', 'ulb']),
     ('ta', ['tn', 'ulb']),
     ('te', ['tn', 'ulb']),
     ('th', ['tn', 'ulb']),
     ('tl', ['tn', 'ulb']),
     ('tpi', ['ulb']),
     ('ur', ['ulb']),
     ('ur-deva', ['tn', 'ulb']),
     ('vi', ['tn', 'ulb']),
     ('zh', ['cuv', 'tn'])]

    Here we experiment with returning only (filtered more aggressively
    to remove all secondary USFMs, i.e., udb and f10 for fr) USFM and
    (all) TN types that translations.json lists as available for the
    GL languages:

    >>> data = resource_lookup.fetch_source_data(settings.RESOURCE_ASSETS_DIR, settings.TRANSLATIONS_JSON_LOCATION)
    >>> values = []
    >>> for item in [lang for lang in data if lang["code"] in settings.GATEWAY_LANGUAGES]:
    ...    values.append(
    ...        (item["code"],
    ...           [
    ...               resource_type["code"]
    ...               for resource_type in item["contents"]
    ...               if (
    ...                   resource_type["code"] in settings.EN_USFM_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.USFM_RESOURCE_TYPES_MINUS_SECONDARY
    ...                   or resource_type["code"] in settings.EN_TN_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.TN_RESOURCE_TYPES
    ...               )
    ...           ]
    ...        )
    ...    )
    >>> sorted_values = sorted(values, key=lambda value: value[0])
    >>> pprint.pprint(sorted_values)
    [('am', ['tn', 'ulb']),
     ('arb', ['nav']),
     ('as', ['tn', 'ulb']),
     ('bn', ['tn', 'ulb']),
     ('ceb', ['tn', 'ulb']),
     ('en', ['ulb-wa', 'tn-wa', 'tn']),
     ('es-419', ['tn', 'ulb']),
     ('fa', ['tn', 'ulb']),
     ('fr', ['tn', 'ulb']),
     ('gu', ['tn', 'ulb']),
     ('ha', ['tn', 'ulb']),
     ('hi', ['tn', 'ulb']),
     ('id', ['tn']),
     ('ilo', ['tn', 'ulb']),
     ('km', ['tn', 'ulb']),
     ('kn', ['tn', 'ulb']),
     ('lo', ['tn', 'ulb']),
     ('ml', ['tn', 'ulb']),
     ('mr', ['tn', 'ulb']),
     ('my', ['tn', 'ulb']),
     ('ne', ['tn', 'ulb']),
     ('or', ['tn', 'ulb']),
     ('pa', ['tn', 'ulb']),
     ('plt', ['tn', 'ulb']),
     ('pmy', ['tn']),
     ('pt-br', ['tn', 'ulb']),
     ('ru', ['tn', 'ulb']),
     ('sw', ['tn', 'ulb']),
     ('ta', ['tn', 'ulb']),
     ('te', ['tn', 'ulb']),
     ('th', ['tn', 'ulb']),
     ('tl', ['tn', 'ulb']),
     ('tpi', ['ulb']),
     ('ur', ['ulb']),
     ('ur-deva', ['tn', 'ulb']),
     ('vi', ['tn', 'ulb']),
     ('zh', ['cuv', 'tn'])]
    >>> [tuple for tuple in sorted_values if len(tuple[1]) == 1]
    [('arb', ['nav']), ('id', ['tn']), ('pmy', ['tn']), ('tpi', ['ulb']), ('ur', ['ulb'])]


    Of the GL languages that have only USFM or TN, but not both, do we want to filter them out or just produce the document using just USFM or just TN (whatever is available for that language) since you have specified that the user is not to be allowed to choose resource types in v1 release?

    """
    if lang_code == "en":
        return [(key, value) for key, value in english_resource_type_map.items()]
    if lang_code == "id":
        return [(key, value) for key, value in id_resource_type_map.items()]

    data = fetch_source_data(working_dir, translations_json_location)
    for item in [lang for lang in data if lang["code"] == lang_code]:
        values = [
            (
                resource_type["code"],
                "{} ({})".format(resource_type["name"], resource_type["code"]),
            )
            for resource_type in item["contents"]
            if (
                resource_type["code"] in usfm_resource_types
                or resource_type["code"] in tn_resource_types
                or resource_type["code"] in tq_resource_types
                or resource_type["code"] in tw_resource_types
            )
        ]
    return sorted(values, key=lambda value: value[0])


def resource_types_and_names_for_lang_for_v1_release(
    lang_code: str,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    english_resource_type_map: Mapping[
        str, str
    ] = settings.ENGLISH_RESOURCE_TYPE_MAP_USFM_AND_TN_ONLY,
    id_resource_type_map: Mapping[
        str, str
    ] = settings.ID_RESOURCE_TYPE_MAP_USFM_AND_TN_ONLY,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES_MINUS_SECONDARY,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
) -> list[tuple[str, str]]:
    """
    Convenience method that can be called from UI to get the set
    of all resource type, name tuples for a given language available
    through API. Presumably this could be called to populate a
    drop-down menu.

    >>> from document.domain import resource_lookup
    >>> from document.config import settings
    >>> import logging
    >>> import sys
    >>> logger.addHandler(logging.StreamHandler(sys.stdout))
    >>> import pprint
    >>> # pprint.pprint(resource_lookup.resource_codes_and_types_for_lang_for_v1_release("fr"))
    >>> pprint.pprint(resource_lookup.resource_types_and_names_for_lang_for_v1_release("en"))
    [('ulb-wa', 'Unlocked Literal Bible (ULB)'), ('tn-wa', 'ULB Translation Notes')]
    >>> pprint.pprint(resource_lookup.resource_types_and_names_for_lang_for_v1_release("es-419"))
    [('tn', 'Translation Notes (tn)'),
     ('ulb', 'Español Latino Americano ULB (ulb)')]

    >>> pprint.pprint(sorted([(lang_code,resource_lookup.resource_types_and_names_for_lang_for_v1_release(lang_code)) for lang_code in settings.GATEWAY_LANGUAGES], key=lambda group: group[0]))
    [('am',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('arb', [('nav', 'New Arabic Version (Ketab El Hayat) (nav)')]),
     ('as',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Assamese Unlocked Literal Bible (ulb)')]),
     ('bn',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Bengali Unlocked Literal Bible (ulb)')]),
     ('ceb',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Cebuano Unlocked Literal Bible (ulb)')]),
     ('en',
      [('ulb-wa', 'Unlocked Literal Bible (ULB)'),
       ('tn-wa', 'ULB Translation Notes')]),
     ('es-419',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Español Latino Americano ULB (ulb)')]),
     ('fa',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Henry Martyn Open Source Bible (1876) (ulb)')]),
     ('fr', [('tn', 'Translation Notes (tn)'), ('ulb', 'French ULB (ulb)')]),
     ('gu',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Gujarati Unlocked Literal Bible (ulb)')]),
     ('ha',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Hausa (ulb)')]),
     ('hi',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Hindi (ulb)')]),
     ('id',
      [('ayt', 'Bahasa Indonesian Bible (ayt)'), ('tn', 'Translation Helps')]),
     ('ilo',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Ilocano (ulb)')]),
     ('km',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Khmer (ulb)')]),
     ('kn',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Kannada Unlocked Literal Bible (ulb)')]),
     ('lo', [('tn', 'Translation Notes (tn)'), ('ulb', 'Lao ULB (ulb)')]),
     ('ml',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Malayalam (ulb)')]),
     ('mr',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Marathi (ulb)')]),
     ('my',
      [('tn', 'Translation Notes (tn)'), ('ulb', 'Burmese Judson Bible (ulb)')]),
     ('ne',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Nepali (ulb)')]),
     ('or',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Oriya Unlocked Literal Bible (ulb)')]),
     ('pa',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Punjabi Unlocked Literal Bible (ulb)')]),
     ('plt',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Plateau Malagasy Unlocked Literal Bible (ulb)')]),
     ('pmy', [('tn', 'Translation Notes (tn)')]),
     ('pt-br',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Brazilian Portuguese Unlocked Literal Bible (ulb)')]),
     ('ru',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Russian Unlocked Literal Bible (ulb)')]),
     ('sw',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Swahili Unlocked Literal Bible (ulb)')]),
     ('ta',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Tamil (ulb)')]),
     ('te',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Telugu (ulb)')]),
     ('th',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('tl',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Tagalog Unlocked Literal Bible (ulb)')]),
     ('tpi', [('ulb', 'Tok Pisin Unlocked Literal Bible (ulb)')]),
     ('ur', [('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('ur-deva',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Urdu (ulb)')]),
     ('vi',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Vietnamese Unlocked Literal Bible (ulb)')]),
     ('zh', [('cuv', '新标点和合本 (cuv)'), ('tn', 'Translation Notes (tn)')])]

    >>> pprint.pprint(sorted([(lang_code,resource_lookup.resource_types_and_names_for_lang_for_v1_release(lang_code)) for lang_code in settings.GATEWAY_LANGUAGES if lang_code not in settings.LANG_CODE_FILTER_LIST], key=lambda group: group[0]))
    [('am',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('arb', [('nav', 'New Arabic Version (Ketab El Hayat) (nav)')]),
     ('as',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Assamese Unlocked Literal Bible (ulb)')]),
     ('bn',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Bengali Unlocked Literal Bible (ulb)')]),
     ('ceb',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Cebuano Unlocked Literal Bible (ulb)')]),
     ('en',
      [('ulb-wa', 'Unlocked Literal Bible (ULB)'),
       ('tn-wa', 'ULB Translation Notes')]),
     ('es-419',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Español Latino Americano ULB (ulb)')]),
     ('fr', [('tn', 'Translation Notes (tn)'), ('ulb', 'French ULB (ulb)')]),
     ('gu',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Gujarati Unlocked Literal Bible (ulb)')]),
     ('ha',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Hausa (ulb)')]),
     ('hi',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Hindi (ulb)')]),
     ('id',
      [('ayt', 'Bahasa Indonesian Bible (ayt)'), ('tn', 'Translation Helps')]),
     ('ilo',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Ilocano (ulb)')]),
     ('km',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Khmer (ulb)')]),
     ('kn',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Kannada Unlocked Literal Bible (ulb)')]),
     ('lo', [('tn', 'Translation Notes (tn)'), ('ulb', 'Lao ULB (ulb)')]),
     ('ml',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Malayalam (ulb)')]),
     ('mr',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Marathi (ulb)')]),
     ('my',
      [('tn', 'Translation Notes (tn)'), ('ulb', 'Burmese Judson Bible (ulb)')]),
     ('ne',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Nepali (ulb)')]),
     ('or',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Oriya Unlocked Literal Bible (ulb)')]),
     ('pa',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Punjabi Unlocked Literal Bible (ulb)')]),
     ('plt',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Plateau Malagasy Unlocked Literal Bible (ulb)')]),
     ('pt-br',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Brazilian Portuguese Unlocked Literal Bible (ulb)')]),
     ('ru',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Russian Unlocked Literal Bible (ulb)')]),
     ('sw',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Swahili Unlocked Literal Bible (ulb)')]),
     ('ta',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Tamil (ulb)')]),
     ('te',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Telugu (ulb)')]),
     ('th',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('tl',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Tagalog Unlocked Literal Bible (ulb)')]),
     ('tpi', [('ulb', 'Tok Pisin Unlocked Literal Bible (ulb)')]),
     ('ur', [('ulb', 'Unlocked Literal Bible (ULB) (ulb)')]),
     ('ur-deva',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Unlocked Literal Bible - Urdu (ulb)')]),
     ('vi',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Vietnamese Unlocked Literal Bible (ulb)')]),
     ('zh', [('cuv', '新标点和合本 (cuv)'), ('tn', 'Translation Notes (tn)')])]

    >>> pprint.pprint(sorted([(lang_code,resource_lookup.resource_types_and_names_for_lang_for_v1_release(lang_code)) for lang_code in settings.GATEWAY_LANGUAGES if lang_code in settings.LANG_CODE_FILTER_LIST], key=lambda group: group[0]))
    [('fa',
      [('tn', 'Translation Notes (tn)'),
       ('ulb', 'Henry Martyn Open Source Bible (1876) (ulb)')]),
     ('pmy', [('tn', 'Translation Notes (tn)')])]

    >>> sorted([lang_code for lang_code in settings.GATEWAY_LANGUAGES if lang_code not in settings.LANG_CODE_FILTER_LIST])
    ['am', 'arb', 'as', 'bn', 'ceb', 'en', 'es-419', 'fr', 'gu', 'ha', 'hi', 'id', 'ilo', 'km', 'kn', 'lo', 'ml', 'mr', 'my', 'ne', 'or', 'pa', 'plt', 'pt-br', 'ru', 'sw', 'ta', 'te', 'th', 'tl', 'tpi', 'ur', 'ur-deva', 'vi', 'zh']
    >>> sorted([lang_code for lang_code in settings.GATEWAY_LANGUAGES if lang_code in settings.LANG_CODE_FILTER_LIST])
    ['fa', 'pmy']


    List of GL languages and their translations.json listed resource
    types (filtered, but including udb and f10) USFM and (all) TN
    types that translations.json lists as available for the GL
    languages:

    >>> data = resource_lookup.fetch_source_data(settings.RESOURCE_ASSETS_DIR, settings.TRANSLATIONS_JSON_LOCATION)
    >>> values = []
    >>> for item in [lang for lang in data if lang["code"] in settings.GATEWAY_LANGUAGES]:
    ...    values.append(
    ...        (item["code"],
    ...           [
    ...               resource_type["code"]
    ...               for resource_type in item["contents"]
    ...               if (
    ...                   resource_type["code"] in settings.EN_USFM_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.USFM_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.EN_TN_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.TN_RESOURCE_TYPES
    ...               )
    ...           ]
    ...        )
    ...    )
    >>> sorted_values = sorted(values, key=lambda value: value[0])
    >>> pprint.pprint(sorted_values)
    [('am', ['tn', 'ulb']),
     ('arb', ['nav']),
     ('as', ['tn', 'ulb']),
     ('bn', ['tn', 'ulb']),
     ('ceb', ['tn', 'ulb']),
     ('en', ['ulb-wa', 'tn-wa', 'tn']),
     ('es-419', ['tn', 'ulb']),
     ('fa', ['tn', 'ulb']),
     ('fr', ['tn', 'ulb', 'f10']),
     ('gu', ['tn', 'ulb']),
     ('ha', ['tn', 'ulb']),
     ('hi', ['tn', 'ulb']),
     ('id', ['tn']),
     ('ilo', ['tn', 'ulb']),
     ('km', ['tn', 'ulb']),
     ('kn', ['tn', 'ulb']),
     ('lo', ['tn', 'ulb']),
     ('ml', ['tn', 'ulb']),
     ('mr', ['tn', 'ulb']),
     ('my', ['tn', 'ulb']),
     ('ne', ['tn', 'ulb']),
     ('or', ['tn', 'ulb']),
     ('pa', ['tn', 'ulb']),
     ('plt', ['tn', 'ulb']),
     ('pmy', ['tn']),
     ('pt-br', ['tn', 'ulb']),
     ('ru', ['tn', 'ulb']),
     ('sw', ['tn', 'ulb']),
     ('ta', ['tn', 'ulb']),
     ('te', ['tn', 'ulb']),
     ('th', ['tn', 'ulb']),
     ('tl', ['tn', 'ulb']),
     ('tpi', ['ulb']),
     ('ur', ['ulb']),
     ('ur-deva', ['tn', 'ulb']),
     ('vi', ['tn', 'ulb']),
     ('zh', ['cuv', 'tn'])]

    Here we experiment with returning only (filtered more aggressively
    to remove all secondary USFMs, i.e., udb and f10 for fr) USFM and
    (all) TN types that translations.json lists as available for the
    GL languages:

    >>> data = resource_lookup.fetch_source_data(settings.RESOURCE_ASSETS_DIR, settings.TRANSLATIONS_JSON_LOCATION)
    >>> values = []
    >>> for item in [lang for lang in data if lang["code"] in settings.GATEWAY_LANGUAGES]:
    ...    values.append(
    ...        (item["code"],
    ...           [
    ...               resource_type["code"]
    ...               for resource_type in item["contents"]
    ...               if (
    ...                   resource_type["code"] in settings.EN_USFM_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.USFM_RESOURCE_TYPES_MINUS_SECONDARY
    ...                   or resource_type["code"] in settings.EN_TN_RESOURCE_TYPES
    ...                   or resource_type["code"] in settings.TN_RESOURCE_TYPES
    ...               )
    ...           ]
    ...        )
    ...    )
    >>> sorted_values = sorted(values, key=lambda value: value[0])
    >>> pprint.pprint(sorted_values)
    [('am', ['tn', 'ulb']),
     ('arb', ['nav']),
     ('as', ['tn', 'ulb']),
     ('bn', ['tn', 'ulb']),
     ('ceb', ['tn', 'ulb']),
     ('en', ['ulb-wa', 'tn-wa', 'tn']),
     ('es-419', ['tn', 'ulb']),
     ('fa', ['tn', 'ulb']),
     ('fr', ['tn', 'ulb']),
     ('gu', ['tn', 'ulb']),
     ('ha', ['tn', 'ulb']),
     ('hi', ['tn', 'ulb']),
     ('id', ['tn']),
     ('ilo', ['tn', 'ulb']),
     ('km', ['tn', 'ulb']),
     ('kn', ['tn', 'ulb']),
     ('lo', ['tn', 'ulb']),
     ('ml', ['tn', 'ulb']),
     ('mr', ['tn', 'ulb']),
     ('my', ['tn', 'ulb']),
     ('ne', ['tn', 'ulb']),
     ('or', ['tn', 'ulb']),
     ('pa', ['tn', 'ulb']),
     ('plt', ['tn', 'ulb']),
     ('pmy', ['tn']),
     ('pt-br', ['tn', 'ulb']),
     ('ru', ['tn', 'ulb']),
     ('sw', ['tn', 'ulb']),
     ('ta', ['tn', 'ulb']),
     ('te', ['tn', 'ulb']),
     ('th', ['tn', 'ulb']),
     ('tl', ['tn', 'ulb']),
     ('tpi', ['ulb']),
     ('ur', ['ulb']),
     ('ur-deva', ['tn', 'ulb']),
     ('vi', ['tn', 'ulb']),
     ('zh', ['cuv', 'tn'])]
    >>> [tuple for tuple in sorted_values if len(tuple[1]) == 1]
    [('arb', ['nav']), ('id', ['tn']), ('pmy', ['tn']), ('tpi', ['ulb']), ('ur', ['ulb'])]


    Of the GL languages that have only USFM or TN, but not both, do we want to filter them out or just produce the document using just USFM or just TN (whatever is available for that language) since you have specified that the user is not to be allowed to choose resource types in v1 release?

    """
    if lang_code == "en":
        return [(key, value) for key, value in english_resource_type_map.items()]
    if lang_code == "id":
        return [(key, value) for key, value in id_resource_type_map.items()]

    data = fetch_source_data(working_dir, translations_json_location)
    for item in [lang for lang in data if lang["code"] == lang_code]:
        values = [
            (
                resource_type["code"],
                "{} ({})".format(resource_type["name"], resource_type["code"]),
            )
            for resource_type in item["contents"]
            if (
                resource_type["code"] in usfm_resource_types
                or resource_type["code"] in tn_resource_types
            )
        ]
    return sorted(values, key=lambda value: value[0])


def supported_language_scoped_resource_type(
    lang_code: str,
    resource_type: str,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    en_tn_resource_types: Sequence[str] = settings.EN_TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
) -> bool:
    """
    Check if resource_type is a TN, TQ, TW type.
    """
    if (
        (
            resource_type in en_tn_resource_types
            if lang_code == "en"
            else resource_type in tn_resource_types
        )
        or resource_type in tq_resource_types
        or resource_type in tw_resource_types
    ):
        return True
    return False


def supported_resource_type(
    lang_code: str,
    resource_type: str,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    en_tn_resource_types: Sequence[str] = settings.EN_TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
    bc_resource_types: Sequence[str] = settings.BC_RESOURCE_TYPES,
) -> bool:
    """
    Check if resource_type complies with the resource types we currently support.
    """
    if (
        resource_type in usfm_resource_types
        or (
            resource_type in en_tn_resource_types
            if lang_code == "en"
            else resource_type in tn_resource_types
        )
        or resource_type in tq_resource_types
        or resource_type in tw_resource_types
        or resource_type in bc_resource_types
    ):
        return True
    return False


def shared_resource_types(
    lang_code: str,
    resource_codes: Sequence[str],
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    english_resource_type_map: Mapping[str, str] = settings.ENGLISH_RESOURCE_TYPE_MAP,
    id_resource_type_map: Mapping[str, str] = settings.ID_RESOURCE_TYPE_MAP,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    lang_code_filter_list: Sequence[str] = settings.LANG_CODE_FILTER_LIST,
) -> list[tuple[str, str]]:
    """
    Given a language code and a list of resource_codes, return the
    collection of resource types available.

    >>> from document.domain import resource_lookup
    >>> list(resource_lookup.shared_resource_types("en", ["2co"]))
    [('ulb-wa', 'Unlocked Literal Bible (ULB)'), ('tn-wa', 'ULB Translation Notes'), ('tq-wa', 'ULB Translation Questions'), ('tw-wa', 'ULB Translation Words'), ('bc-wa', 'Bible Commentary')]
    >>> list(resource_lookup.shared_resource_types("kbt", ["2co"]))
    [('reg', 'Bible (reg)')]
    >>> list(resource_lookup.shared_resource_types("pt-br", ["gen"]))
    [('tn', 'Translation Notes (tn)'), ('tq', 'Translation Questions (tq)'), ('tw', 'Translation Words (tw)'), ('ulb', 'Brazilian Portuguese Unlocked Literal Bible (ulb)')]
    >>> list(resource_lookup.shared_resource_types("fr", ["gen"]))
    [('f10', 'French Louis Segond 1910 Bible (f10)'), ('tn', 'Translation Notes (tn)'), ('tq', 'Translation Questions (tq)'), ('tw', 'Translation Words (tw)')]
    >>> list(resource_lookup.shared_resource_types("es-419", ["gen"]))
    [('tn', 'Translation Notes (tn)'), ('tq', 'Translation Questions (tq)'), ('tw', 'Translation Words (tw)'), ('ulb', 'Español Latino Americano ULB (ulb)')]
    >>> list(resource_lookup.shared_resource_types("id", ["mat"]))
    [('ayt', 'Bahasa Indonesian Bible (ayt)'), ('tn', 'Translation Helps (tn)'), ('tq', 'Translation Questions (tq)'), ('tw', 'Translation Words (tw)')]

    """

    if lang_code == "en":
        return [(key, value) for key, value in english_resource_type_map.items()]
    if lang_code == "id":
        return [(key, value) for key, value in id_resource_type_map.items()]

    values = []
    data = fetch_source_data(working_dir, translations_json_location)
    # Get the resource types for lang0
    # rcfrt = resource_types_for_resource_codes(data, lang_code, resource_codes)
    for item in [lang for lang in data if lang["code"] == lang_code]:
        for resource_type in item["contents"]:
            # NOTE An issue that may need to be addressed though is that some resources
            # may not provide the full list of resource codes actually available in
            # the translations.json file. In such cases it would be necessary to
            # actually acquire the asset and then look for the manifest file or glob
            # the files to see if the resource code is provided. I had experimental
            # code checked in which addresses this, but which I am not using
            # currently (and may never be). See git history for this module.
            selected_resource_types_for_resource_codes = [
                resource_code
                for resource_code in resource_type["subcontents"]
                if resource_code["code"] in resource_codes
            ]
            # Determine if suitable link(s) exist for "contents"-scoped resource
            # types We use this in the conditional below to assert that TN, TQ, and
            # TW resource types have a downloadable or cloneable asset and thus
            # should be included as avaiable resource types along with book specific
            # assets like those for USFM, BC.
            links_for_resource_type = [
                link
                for link in resource_type["links"]
                if link["format"] == "zip"
                or link["format"] == "Download"
                and link["url"]
            ]
            if (
                supported_resource_type(lang_code, resource_type["code"])
                # Check If there are resource codes associated with this resource type
                # which conincide with the resource codes that the user selected.
                and (
                    selected_resource_types_for_resource_codes
                    or (
                        supported_language_scoped_resource_type(
                            lang_code, resource_type["code"]
                        )
                        and links_for_resource_type
                    )
                )
            ):
                values.append(
                    (
                        resource_type["code"],
                        "{} ({})".format(resource_type["name"], resource_type["code"]),
                    )
                )

    return sorted(values, key=lambda value: value[0])


def shared_resource_types_for_v1(
    lang_code: str,
    resource_codes: Sequence[str],
    v1_approved_resource_types: Sequence[str] = settings.V1_APPROVED_RESOURCE_TYPES,
) -> list[tuple[str, str]]:
    """
    Given a language code and a list of resource_codes, return the
    collection of resource types available.

    >>> from document.domain import resource_lookup
    >>> list(resource_lookup.shared_resource_types_for_v1("en", ["2co"]))
    [('ulb-wa', 'Unlocked Literal Bible (ULB)'), ('tn-wa', 'ULB Translation Notes')]
    >>> list(resource_lookup.shared_resource_types_for_v1("pt-br", ["gen"]))
    [('tn', 'Translation Notes (tn)'), ('ulb', 'Brazilian Portuguese Unlocked Literal Bible (ulb)')]
    >>> list(resource_lookup.shared_resource_types_for_v1("fr", ["gen"]))
    [('tn', 'Translation Notes (tn)')]
    >>> list(resource_lookup.shared_resource_types_for_v1("es-419", ["gen"]))
    [('tn', 'Translation Notes (tn)'), ('ulb', 'Español Latino Americano ULB (ulb)')]
    """
    resource_types_and_names = [
        resource_type_and_name
        for resource_type_and_name in shared_resource_types(lang_code, resource_codes)
        if resource_type_and_name[0] in v1_approved_resource_types
    ]
    return resource_types_and_names


def shared_resource_codes(
    lang0_code: str, lang1_code: str
) -> Sequence[tuple[str, str]]:
    """
    Given two language codes, return the intersection of resource
    codes between the two languages.

    >>> from document.domain import resource_lookup
    >>> # Hack to ignore logging output: https://stackoverflow.com/a/33400983/3034580
    >>> # FIXME kbt shouldn't be obtainable due to an invalid URL in translations.json
    >>> ();data = resource_lookup.shared_resource_codes("pt-br", "kbt");() # doctest: +ELLIPSIS
    (...)
    >>> list(data)
    [('2co', '2 Corinthians')]
    """
    # Get resource codes for reach language.
    lang0_resource_codes = resource_codes_for_lang(lang0_code)
    lang1_resource_codes = resource_codes_for_lang(lang1_code)

    # Find intersection of resource codes:
    return [
        (x, y)
        for x, y in lang0_resource_codes
        if x in [s for s, t in lang1_resource_codes]
    ]


def resource_codes_for_lang(
    lang_code: str,
    jsonpath_str: str = settings.RESOURCE_CODES_FOR_LANG_JSONPATH,
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
    book_numbers: Mapping[str, str] = bible_books.BOOK_NUMBERS,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> Sequence[tuple[str, str]]:
    """
    Convenience method that can be called, e.g., from the UI, to
    get the set of all resource codes for a particular lang_code.

    >>> from document.domain import resource_lookup
    >>> # Hack to ignore logging output causing doctest failure: https://stackoverflow.com/a/33400983/3034580
    >>> ();data = resource_lookup.resource_codes_for_lang("fr");() # doctest:+ELLIPSIS
    (...)
    >>> list(data)
    [('gen', 'Genesis'), ('exo', 'Exodus'), ('lev', 'Leviticus'), ('num', 'Numbers'), ('deu', 'Deuteronomy'), ('jos', 'Joshua'), ('jdg', 'Judges'), ('rut', 'Ruth'), ('1sa', '1 Samuel'), ('2sa', '2 Samuel'), ('1ki', '1 Kings'), ('2ki', '2 Kings'), ('1ch', '1 Chronicles'), ('2ch', '2 Chronicles'), ('ezr', 'Ezra'), ('neh', 'Nehemiah'), ('est', 'Esther'), ('job', 'Job'), ('psa', 'Psalms'), ('pro', 'Proverbs'), ('ecc', 'Ecclesiastes'), ('sng', 'Song of Solomon'), ('isa', 'Isaiah'), ('jer', 'Jeremiah'), ('lam', 'Lamentations'), ('ezk', 'Ezekiel'), ('dan', 'Daniel'), ('hos', 'Hosea'), ('jol', 'Joel'), ('amo', 'Amos'), ('oba', 'Obadiah'), ('jon', 'Jonah'), ('mic', 'Micah'), ('nam', 'Nahum'), ('hab', 'Habakkuk'), ('zep', 'Zephaniah'), ('hag', 'Haggai'), ('zec', 'Zechariah'), ('mal', 'Malachi'), ('mat', 'Matthew'), ('mrk', 'Mark'), ('luk', 'Luke'), ('jhn', 'John'), ('act', 'Acts'), ('rom', 'Romans'), ('1co', '1 Corinthians'), ('2co', '2 Corinthians'), ('gal', 'Galatians'), ('eph', 'Ephesians'), ('php', 'Philippians'), ('col', 'Colossians'), ('1th', '1 Thessalonians'), ('2th', '2 Thessalonians'), ('1ti', '1 Timothy'), ('2ti', '2 Timothy'), ('tit', 'Titus'), ('phm', 'Philemon'), ('heb', 'Hebrews'), ('jas', 'James'), ('1pe', '1 Peter'), ('2pe', '2 Peter'), ('1jn', '1 John'), ('2jn', '2 John'), ('3jn', '3 John'), ('jud', 'Jude'), ('rev', 'Revelation')]
    >>> ();data = resource_lookup.resource_codes_for_lang("id");() # doctest:+ELLIPSIS
    (...)
    >>> list(data)
    [('gen', 'Genesis'), ('exo', 'Exodus'), ('lev', 'Leviticus'), ('num', 'Numbers'), ('deu', 'Deuteronomy'), ('jos', 'Joshua'), ('jdg', 'Judges'), ('rut', 'Ruth'), ('1sa', '1 Samuel'), ('2sa', '2 Samuel'), ('1ki', '1 Kings'), ('2ki', '2 Kings'), ('1ch', '1 Chronicles'), ('2ch', '2 Chronicles'), ('ezr', 'Ezra'), ('neh', 'Nehemiah'), ('est', 'Esther'), ('job', 'Job'), ('psa', 'Psalms'), ('pro', 'Proverbs'), ('ecc', 'Ecclesiastes'), ('sng', 'Song of Solomon'), ('isa', 'Isaiah'), ('jer', 'Jeremiah'), ('lam', 'Lamentations'), ('ezk', 'Ezekiel'), ('dan', 'Daniel'), ('hos', 'Hosea'), ('jol', 'Joel'), ('amo', 'Amos'), ('oba', 'Obadiah'), ('jon', 'Jonah'), ('mic', 'Micah'), ('nam', 'Nahum'), ('hab', 'Habakkuk'), ('zep', 'Zephaniah'), ('hag', 'Haggai'), ('zec', 'Zechariah'), ('mal', 'Malachi'), ('mat', 'Matthew'), ('mrk', 'Mark'), ('luk', 'Luke'), ('jhn', 'John'), ('act', 'Acts'), ('rom', 'Romans'), ('1co', '1 Corinthians'), ('2co', '2 Corinthians'), ('gal', 'Galatians'), ('eph', 'Ephesians'), ('php', 'Philippians'), ('col', 'Colossians'), ('1th', '1 Thessalonians'), ('2th', '2 Thessalonians'), ('1ti', '1 Timothy'), ('2ti', '2 Timothy'), ('tit', 'Titus'), ('phm', 'Philemon'), ('heb', 'Hebrews'), ('jas', 'James'), ('1pe', '1 Peter'), ('2pe', '2 Peter'), ('1jn', '1 John'), ('2jn', '2 John'), ('3jn', '3 John'), ('jud', 'Jude'), ('rev', 'Revelation')]
    """
    if lang_code == "id":
        return [
            (resource_code, book_names[resource_code])
            for resource_code in book_names.keys()
        ]
    else:
        resource_codes = [
            (resource_code, book_names[resource_code])
            for resource_code in _lookup(jsonpath_str.format(lang_code))
            if resource_code
        ]
        return sorted(
            resource_codes,
            key=lambda resource_code_name_pair: book_numbers[
                resource_code_name_pair[0]
            ],
        )


# NOTE An alternative/experimental (different approach), yet ultimately non-performant version.
# def resource_codes_for_lang(
#     lang_code: str,
#     jsonpath_str: str = settings.RESOURCE_CODES_FOR_LANG_JSONPATH,
#     book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
#     book_numbers: Mapping[str, str] = bible_books.BOOK_NUMBERS,
#     working_dir: str = settings.RESOURCE_ASSETS_DIR,
#     translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
#     usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
# ) -> Sequence[tuple[str, str]]:
#     """
#     Convenience method that can be called, e.g., from the UI, to
#     get the set of all resource codes for a particular lang_code.

#     >>> from document.domain import resource_lookup
#     >>> # Hack to ignore logging output: https://stackoverflow.com/a/33400983/3034580
#     >>> ();data = resource_lookup.resource_codes_for_lang("fr");() # doctest:+ELLIPSIS
#     (...)
#     >>> list(data)
#     [('gen', 'Genesis'), ('exo', 'Exodus'), ('lev', 'Leviticus'), ('num', 'Numbers'), ('deu', 'Deuteronomy'), ('jos', 'Joshua'), ('jdg', 'Judges'), ('rut', 'Ruth'), ('1sa', '1 Samuel'), ('2sa', '2 Samuel'), ('1ki', '1 Kings'), ('2ki', '2 Kings'), ('1ch', '1 Chronicles'), ('2ch', '2 Chronicles'), ('ezr', 'Ezra'), ('neh', 'Nehemiah'), ('est', 'Esther'), ('job', 'Job'), ('psa', 'Psalms'), ('pro', 'Proverbs'), ('ecc', 'Ecclesiastes'), ('sng', 'Song of Solomon'), ('isa', 'Isaiah'), ('jer', 'Jeremiah'), ('lam', 'Lamentations'), ('ezk', 'Ezekiel'), ('dan', 'Daniel'), ('hos', 'Hosea'), ('jol', 'Joel'), ('amo', 'Amos'), ('oba', 'Obadiah'), ('jon', 'Jonah'), ('mic', 'Micah'), ('nam', 'Nahum'), ('hab', 'Habakkuk'), ('zep', 'Zephaniah'), ('hag', 'Haggai'), ('zec', 'Zechariah'), ('mal', 'Malachi'), ('mat', 'Matthew'), ('mrk', 'Mark'), ('luk', 'Luke'), ('jhn', 'John'), ('act', 'Acts'), ('rom', 'Romans'), ('1co', '1 Corinthians'), ('2co', '2 Corinthians'), ('gal', 'Galatians'), ('eph', 'Ephesians'), ('php', 'Philippians'), ('col', 'Colossians'), ('1th', '1 Thessalonians'), ('2th', '2 Thessalonians'), ('1ti', '1 Timothy'), ('2ti', '2 Timothy'), ('tit', 'Titus'), ('phm', 'Philemon'), ('heb', 'Hebrews'), ('jas', 'James'), ('1pe', '1 Peter'), ('2pe', '2 Peter'), ('1jn', '1 John'), ('2jn', '2 John'), ('3jn', '3 John'), ('jud', 'Jude'), ('rev', 'Revelation')]
#     """
#     results = resource_codes_and_types_for_lang(lang_code)
#     usfm_resource_type_with_max_resource_codes: list[tuple[str, str, str]] = []
#     usfm_keys = [key for key in results.keys() if key in usfm_resource_types]
#     if (
#         usfm_keys and len(usfm_keys) > 1
#     ):  # More than one USFM type is available for lang_code
#         # logger.debug("usfm_keys: %s", usfm_keys)
#         # logger.debug(
#         #     "resource_codes for %s: %s",
#         #     usfm_keys[0],
#         #     [code for code, name, link in results[usfm_keys[0]]],
#         # )
#         # logger.debug(
#         #     "resource_codes for %s: %s",
#         #     usfm_keys[1],
#         #     [code for code, name, link in results[usfm_keys[1]]],
#         # )
#         usfm_resource_type_with_max_resource_codes = max(
#             [results[usfm_keys[0]], results[usfm_keys[1]]], key=lambda entry: len(entry)
#         )
#     elif (
#         usfm_keys and len(usfm_keys) == 1
#     ):  # Just one USFM type is available for lang_code
#         usfm_resource_type_with_max_resource_codes = results[usfm_keys[0]]

#     resource_codes = [
#         (code, name) for code, name, link in usfm_resource_type_with_max_resource_codes
#     ]
#     logger.debug("resource_codes: %s", resource_codes)
#     return sorted(
#         resource_codes,
#         key=lambda resource_code_name_pair: book_numbers[resource_code_name_pair[0]],
#     )


def resource_codes(jsonpath_str: str = settings.RESOURCE_CODES_JSONPATH) -> Any:
    """
    Convenience method that can be called, e.g., from the UI, to
    get the set of all resource codes.
    """
    return _lookup(jsonpath_str)


def lang_codes_names_and_resource_types(
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
) -> Iterable[CodeNameTypeTriplet]:
    """
    Convenience method that can be called to get the list of all
    tuples containing language code, language name, and list of
    resource types available for that language.

    Example usage in repl:
    >>> from document.domain import resource_lookup
    >>> data = resource_lookup.lang_codes_names_and_resource_types()
    >>> # Lookup the resource types available for zh
    >>> [triplet.resource_types for triplet in data if triplet.lang_code == "zh"][-1]
    ['cuv', 'tn', 'tq', 'tw']
    """
    # Using jsonpath in a loop here was prohibitively slow so we
    # use the dictionary in this case.
    for lang in fetch_source_data(working_dir, translations_json_location):
        resource_types: list[str] = []
        for resource_type_dict in lang["contents"]:
            try:
                resource_type = resource_type_dict["code"]
                resource_types.append(resource_type)
            except Exception:
                resource_type = None
            yield CodeNameTypeTriplet(
                lang_code=lang["code"],
                lang_name=lang["name"],
                resource_types=resource_types,
            )


def lang_codes_names_resource_types_and_resource_codes(
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
) -> Iterable[tuple[str, str, Sequence[tuple[str, Sequence[str]]]]]:
    """
    Convenience method that can be called to get the set
    of all tuples containing language code,
    language name, list of resource types available for that
    language, and the resource_codes available for each resource
    type.

    Example usage in repl:
    >>> from document.domain import resource_lookup
    >>> data = resource_lookup.lang_codes_names_resource_types_and_resource_codes()
    >>> # Lookup the resource type available for zh
    >>> [triplet[2] for triplet in data if triplet[0] == "zh"][-1] # doctest: +NORMALIZE_WHITESPACE
    [('cuv', ['gen', 'exo', 'lev', 'num', 'deu', 'jos', 'jdg', 'rut',
    '1sa', '2sa', '1ki', '2ki', '1ch', '2ch', 'ezr', 'neh', 'est',
    'job', 'psa', 'pro', 'ecc', 'sng', 'isa', 'jer', 'lam', 'ezk',
    'dan', 'hos', 'jol', 'amo', 'oba', 'jon', 'mic', 'nam', 'hab',
    'zep', 'hag', 'zec', 'mal', 'mat', 'mrk', 'luk', 'jhn', 'act',
    'rom', '1co', '2co', 'gal', 'eph', 'php', 'col', '1th', '2th',
    '1ti', '2ti', 'tit', 'phm', 'heb', 'jas', '1pe', '2pe', '1jn',
    '2jn', '3jn', 'jud', 'rev']), ('tn', []), ('tq', []), ('tw',
    [])]
    """
    # Using jsonpath in a loop here was prohibitively slow so we
    # use the dictionary in this case.
    for lang in fetch_source_data(working_dir, translations_json_location):
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
            yield (lang["code"], lang["name"], resource_types)


# NOTE Only used for debugging and testing. Not part of long-term
# API.
def lang_codes_names_and_contents_codes(
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
) -> Sequence[tuple[str, str, str]]:
    """
    Convenience test method that can be called to get the set of all
    language codes, their associated language names, and contents level
    codes as tuples. Contents level code is a reference to the structure
    of translations.json, e.g.:

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

    Example usage (and doctest) in repl:

    >>> from document.domain import resource_lookup
    >>> data = resource_lookup.lang_codes_names_and_contents_codes()
    >>> # [(triplet[0], triplet[1]) for triplet in data if triplet[2] == "nil"]
    >>> #[('hr', 'hrvatski jezik'), ('gaj-x-ymnk', 'Gadsup Yomunka'), ('hu', 'magyar'), ('lus', 'Lushai'), ('mor', 'Moro'), ('sr-Latn', 'Serbian'), ('tem', 'Timne'), ('tig', 'Tigre')]
    >>> # Other possible queries:
    >>> # [(triplet[0], triplet[1]) for triplet in data if triplet[2] == "reg"]
    >>> # [(triplet[0], triplet[1]) for triplet in data if triplet[2] == "ulb"]
    >>> # [(triplet[0], triplet[1]) for triplet in data if triplet[2] == "cuv"]
    >>> # [(triplet[0], triplet[1]) for triplet in data if triplet[2] == "udb"]
    >>> # [(triplet[0], triplet[1]) for triplet in data if triplet[2] == "udb"]
    >>> # Lookup the resource type available for zh
    >>> [triplet[2] for triplet in data if triplet[0] == "zh"]
    ['cuv']
    >>> data = sorted(data, key=lambda triplet: triplet[2])
    >>> import itertools
    >>> [triplet[0] for triplet in list(itertools.groupby(data, key=lambda triplet: triplet[2]))]
    ['cuv', 'reg', 'rg', 'tn', 'tw', 'udb', 'ugnt', 'uhb', 'ulb', 'ulb-wa']
    >>> # 'nil' is None
    >>> # Another example query
    # >>> for resource_type in [triplet[0] for triplet in list(itertools.groupby(data, key=lambda triplet: triplet[2]))]:
    # ...   [(resource_type, triplet[0], triplet[1]) for triplet in data if triplet[2] == resource_type]
    >>> # See <project dir>/lang_codes_names_and_contents_codes_groups.json for output dumped to json format.
    """
    lang_codes_names_and_contents_codes: list[tuple[str, str, str]] = []
    # Using jsonpath in a loop here was prohibitively slow so we
    # use the dictionary in this case.
    for d in fetch_source_data(working_dir, translations_json_location):
        try:
            contents_code = d["contents"][0]["code"]
        except Exception:
            contents_code = "nil"
        lang_codes_names_and_contents_codes.append(
            (d["code"], d["name"], contents_code)
        )
    return lang_codes_names_and_contents_codes


def resource_lookup_dto(
    lang_code: str,
    resource_type: str,
    resource_code: str,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    en_usfm_resource_types: Sequence[str] = settings.EN_USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    en_tn_resource_types: Sequence[str] = settings.EN_TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    en_tq_resource_types: Sequence[str] = settings.EN_TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
    en_tw_resource_types: Sequence[str] = settings.EN_TW_RESOURCE_TYPES,
    bc_resource_types: Sequence[str] = settings.BC_RESOURCE_TYPES,
) -> ResourceLookupDto:
    """
    Get the model.ResourceLookupDto instance for the given lang_code,
    resource_type, resource_code combination.

    >>> from document.domain import resource_lookup
    >>> dto = resource_lookup.resource_lookup_dto("id","ayt","tit")
    >>> dto
    ResourceLookupDto(lang_code='id', lang_name='Bahasa Indonesian', resource_type='ayt', resource_type_name='Bahasa Indonesian Bible (ayt)', resource_code='tit', url='https://content.bibletranslationtools.org/WA-Catalog/id_ayt', source=<AssetSourceEnum.GIT: 'git'>, jsonpath=None)
    >>> dto = resource_lookup.resource_lookup_dto("id","tn","tit")
    >>> dto
    ResourceLookupDto(lang_code='id', lang_name='Bahasa Indonesian', resource_type='tn', resource_type_name='Translation Helps (tn)', resource_code='tit', url='https://content.bibletranslationtools.org/WA-Catalog/id_tn', source=<AssetSourceEnum.GIT: 'git'>, jsonpath=None)
    """
    # For English, with the exception of tn resource type, translations.json
    # file only contains URLs to PDF assets rather than anything useful for
    # our purposes with a few inconsistent exceptions. Therefore, we have
    # this guard to handle English resource requests separately outside of
    # translations.json.
    if lang_code == "en":
        if (
            resource_type in en_usfm_resource_types
            or resource_type in en_tn_resource_types
            or resource_type in en_tq_resource_types
            or resource_type in en_tw_resource_types
            or resource_type in bc_resource_types
        ):
            return _english_git_repo_location(
                lang_code,
                resource_type,
                resource_code,
                url=english_git_repo_url(resource_type),
                resource_type_name=english_resource_type_name(resource_type),
            )
        else:  # This would be an invalid English resource type
            raise exceptions.InvalidDocumentRequestException(
                message="{} resource type requested is invalid.".format(resource_type)
            )
    elif lang_code == "id":
        if (
            resource_type in usfm_resource_types
            or resource_type in tn_resource_types
            or resource_type in tq_resource_types
            or resource_type in tw_resource_types
        ):
            return _id_git_repo_location(
                lang_code,
                resource_type,
                resource_code,
                url=id_git_repo_url(resource_type),
                resource_type_name=id_resource_type_name(resource_type),
            )
        else:  # This would be an invalid ID resource type
            raise exceptions.InvalidDocumentRequestException(
                message="{} resource type requested is invalid.".format(resource_type)
            )

    else:  # Non-English lang_code
        if resource_type in usfm_resource_types:
            return usfm_resource_lookup(lang_code, resource_type, resource_code)
        elif (
            resource_type in tn_resource_types
            or resource_type in tq_resource_types
            or resource_type in tw_resource_types
        ):
            return t_resource_lookup(lang_code, resource_type, resource_code)
        else:
            raise exceptions.InvalidDocumentRequestException(
                message="{} resource type requested is invalid.".format(resource_type)
            )


def provision_asset_files(resource_lookup_dto: ResourceLookupDto) -> str:
    """
    Prepare the resource directory and then download the
    resource's file assets into that directory. Return resource_dir.
    """
    prepare_resource_directory(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_code,
        resource_lookup_dto.resource_type,
    )
    return acquire_resource_assets(resource_lookup_dto)


def resource_directory(
    lang_code: str,
    resource_code: str,
    resource_type: str,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
) -> str:
    """Return the resource directory for the resource_lookup_dto."""
    return join(
        working_dir,
        "{}_{}_{}".format(lang_code, resource_code, resource_type),
    )


def prepare_resource_directory(
    lang_code: str, resource_code: str, resource_type: str
) -> None:
    """
    If it doesn't exist yet, create the directory for the
    resource where it will be downloaded to.
    """

    resource_dir = resource_directory(lang_code, resource_code, resource_type)

    if not exists(resource_dir):
        logger.debug("About to create directory %s", resource_dir)
        try:
            mkdir(resource_dir)
        except FileExistsError:
            logger.exception("Directory {} already existed".format(resource_dir))
        else:
            logger.debug("Created directory %s", resource_dir)


def acquire_resource_assets(resource_lookup_dto: ResourceLookupDto) -> str:
    """
    Download or git clone resource and unzip resulting file if it
    is a zip file. Return the resource_dir path.
    """

    resource_dir = resource_directory(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_code,
        resource_lookup_dto.resource_type,
    )
    if (
        resource_lookup_dto.url is not None
    ):  # We know that resource_url is not None because of how we got here, but mypy isn't convinced. Let's convince mypy.
        resource_filepath = join(
            resource_dir,
            resource_lookup_dto.url.rpartition(sep)[2],
        )

        logger.debug("resource_filepath: %s", resource_filepath)
        # Check if resource assets need updating otherwise use
        # what we already have on disk.
        if asset_file_needs_update(resource_filepath):
            if is_git(resource_lookup_dto.source):
                clone_git_repo(resource_lookup_dto.url, resource_filepath)
            else:
                download_asset(resource_lookup_dto.url, resource_filepath)

            if is_zip(resource_lookup_dto.source):
                unzip_asset(
                    resource_lookup_dto.lang_code,
                    resource_lookup_dto.resource_code,
                    resource_lookup_dto.resource_type,
                    resource_filepath,
                )
        else:
            logger.debug("Cache hit for %s", resource_filepath)
        if is_git(resource_lookup_dto.source) or is_zip(resource_lookup_dto.source):
            # When a git repo is cloned or when a zip file is
            # unzipped, a subdirectory of resource_dir is created
            # as a result. Update resource_dir to point to that
            # subdirectory.
            resource_dir = update_resource_dir(
                resource_lookup_dto.lang_code,
                resource_lookup_dto.resource_code,
                resource_lookup_dto.resource_type,
            )
    return resource_dir


def unzip_asset(
    lang_code: str, resource_code: str, resource_type: str, resource_filepath: str
) -> None:
    """Unzip the asset in its resource directory."""
    resource_dir = resource_directory(lang_code, resource_code, resource_type)
    logger.debug("Unzipping %s into %s", resource_filepath, resource_dir)
    unzip(resource_filepath, resource_dir)
    logger.info("Unzipping finished.")


def clone_git_repo(
    url: str,
    resource_filepath: str,
    branch: Optional[str] = None,
    use_git_cli: bool = settings.USE_GIT_CLI,
) -> None:
    """
    Clone the git repo. If the repo was previously cloned but
    the ASSET_CACHING_PERIOD has expired then delete the repo and
    clone it again to get updates.
    """
    if exists(resource_filepath):
        logger.debug(
            "About to delete pre-existing git repo %s in order to recreate it due to cache staleness.",
            resource_filepath,
        )
        try:
            shutil.rmtree(resource_filepath)
        except OSError:
            logger.debug(
                "Directory %s was not removed due to an error.",
                resource_filepath,
            )
            logger.exception("Caught exception: ")
    if use_git_cli:
        if branch:  # CLient specified a particular branch
            command = "git clone --depth=1 --branch '{}' '{}' '{}'".format(
                branch, url, resource_filepath
            )
        else:
            command = "git clone --depth=1 '{}' '{}'".format(url, resource_filepath)
        logger.debug("Attempting to clone into %s ...", resource_filepath)
        try:
            subprocess.call(command, shell=True)
        except subprocess.SubprocessError:
            logger.debug("git command: %s", command)
            logger.debug("git clone failed!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="git clone failed",
            )
        else:
            logger.debug("git command: %s", command)
            logger.debug("git clone succeeded.")
    else:
        logger.debug("Attempting to clone into %s ...", resource_filepath)
        try:
            if branch:  # CLient specified a particular branch
                git.repo.Repo.clone_from(
                    url=url,
                    to_path=resource_filepath,
                    multi_options=["--depth=1", "--branch '{}'".format(branch)],
                )
            else:
                git.repo.Repo.clone_from(
                    url=url,
                    to_path=resource_filepath,
                    multi_options=["--depth=1"],
                )

            # with git_clone_options(...) ?
            #   pygit2.clone_repository(url, resource_filepath)
        except Exception:
            # except pygit2.errors.GitError:
            logger.debug("git clone failed!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="git clone failed",
            )
        else:
            logger.debug("git clone succeeded.")


def download_asset(url: str, resource_filepath: str) -> None:
    """Download the asset."""
    logger.debug("Downloading %s into %s", url, resource_filepath)
    # TODO Might want to retry after some acceptable interval if there is a
    # failure here due to network issues. It has happened very occasionally
    # during testing that there has been a hiccup with the network at this
    # point but succeeded on retry of the same test.
    download_file(str(url), resource_filepath)
    logger.info("Downloading finished.")


def update_resource_dir(lang_code: str, resource_code: str, resource_type: str) -> str:
    """
    Update resource_dir to point to the first subdirectory of
    resource_dir found.

    Why? When a git repo is cloned or when a zip file is unzipped,
    a subdirectory of resource_dir is created as a result. Update
    resource_dir to point to that subdirectory.
    """
    resource_dir = resource_directory(lang_code, resource_code, resource_type)
    subdirs = [
        file.path
        for file in scandir(resource_dir)
        if file.is_dir()
        and "{}_{}_{}".format(lang_code, resource_code, resource_type) in file.path
    ]
    if subdirs:
        resource_dir = subdirs[0]
        logger.debug(
            "resource_dir updated: %s",
            resource_dir,
        )
    return resource_dir


def is_zip(
    resource_source: AssetSourceEnum,
    asset_source_enum_kind: str = AssetSourceEnum.ZIP,
) -> bool:
    """Return true if resource_source is equal to 'zip'."""
    return resource_source == asset_source_enum_kind


def is_git(
    resource_source: AssetSourceEnum,
    asset_source_enum_kind: str = AssetSourceEnum.GIT,
) -> bool:
    """Return true if resource_source is equal to 'git'."""
    return resource_source == asset_source_enum_kind


if __name__ == "__main__":

    # To run the doctests in the this module, in the root of the project do:
    # python backend/document/domain/resource_lookup.py
    # or
    # python backend/document/domain/resource_lookup.py -v
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
