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
    )
    from resource_lookup import ResourceJsonLookup
    from resource import (
        # Resource,
        USFMResource,
        TNResource,
        TAResource,
        TQResource,
        TWResource,
        ResourceFactory,
    )
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
    )
    from .resource_lookup import ResourceJsonLookup
    from .resource import (
        # Resource,
        USFMResource,
        TNResource,
        TAResource,
        TQResource,
        TWResource,
        ResourceFactory,
    )

import yaml
import logging
import logging.config

with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


logger = logging.getLogger(__name__)


def main() -> None:
    """ Test driver. """

    lookup_svc: ResourceJsonLookup = ResourceJsonLookup()

    ## A few non-API tests that demonstrate aspects of jsonpath
    ## library or nature of data we are working with:

    if True:
        test_lookup_all_language_codes(lookup_svc)

        # test_lookup_all_language_names(lookup_svc)

        test_lookup_all_language_codes_and_names(lookup_svc)

        test_lookup_all_resource_types(lookup_svc)

        test_lookup_all_resource_codes(lookup_svc)

    if False:

        test_all_tn_zip_urls_lookup(lookup_svc)

        test_lookup_downloads_at_reg(lookup_svc)

        test_lookup_downloads(lookup_svc)

        test_lookup_downloads_not_at_reg(lookup_svc)

        test_lookup_downloads_not_at_reg2(lookup_svc)

    if True:
        test_lookup_downloads_not_at_reg3(lookup_svc)

    ## Test the API:

    if True:
        fixtures = {}
        fixtures["resources"] = [
            {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "lev"},
            {"lang_code": "kn", "resource_type": "tn", "resource_code": None},
            {"lang_code": "lo", "resource_type": "tn", "resource_code": None},
            {"lang_code": "as", "resource_type": "tn", "resource_code": None},
            {"lang_code": "ema", "resource_type": "tn", "resource_code": None},
            {"lang_code": "plt", "resource_type": "tw", "resource_code": None},
            {"lang_code": "ml", "resource_type": "tq", "resource_code": None},
            {"lang_code": "mr", "resource_type": "ta", "resource_code": None},
            {"lang_code": "lpx", "resource_type": "ulb", "resource_code": None},
            {"lang_code": "mr", "resource_type": "ulb", "resource_code": "gen"},
            # {"lang_code": "mr", "resource_type": "udb", "resource_code": None},
            # {"lang_code": "mr", "resource_type": "obs", "resource_code": None},
            # {"lang_code": "mr", "resource_type": "obs-tn", "resource_code": None},
            # {"lang_code": "mr", "resource_type": "obs-tq", "resource_code": None},
            {
                "lang_code": "erk-x-erakor",
                "resource_type": "reg",
                "resource_code": "eph",
            },
        ]

        for resource in fixtures["resources"]:
            # FIXME Instantiate a resource object for each resource dictionary
            # using ResourceFactory factory method/function. See
            # document_generator.py line 151 for example.
            r = ResourceFactory(
                get_working_dir(), get_working_dir(), lookup_svc, resource
            )
            test_lookup(r)


## Test the API:


def test_lookup(resource) -> None:
    resource.find_location()
    # values: List[Optional[str]] = lookup_svc.lookup(resource)
    print(
        "Language {}, resource_type: {}, resource_code: {}, resource_jsonpath: {}, URL: {}".format(
            # resource["lang_code"],
            resource._lang_code,
            # resource["resource_type"],
            resource._resource_type,
            # resource["resource_code"],
            resource._resource_code,
            # resource["resource_jsonpath"],
            resource._resource_jsonpath,
            resource._resource_url
            # values,
        )
    )


## A few non-API tests that demonstrate aspects of jsonpath
## library or nature of data we are working with or other jsonpaths
## that are not known to be needed yet:


def test_lookup_all_language_codes(lookup_svc: ResourceJsonLookup) -> None:
    values: List[Optional[str]] = lookup_svc.lang_codes()
    print("Language codes: {}, # of language codes: {}".format(values, len(values)))


# def test_lookup_all_language_names(lookup_svc: ResourceJsonLookup) -> None:
#     values: List[Optional[str]] = lookup_svc.lang_names()
#     print("Language names: {}, # of language names: {}".format(values, len(values)))


def test_lookup_all_language_codes_and_names(lookup_svc: ResourceJsonLookup) -> None:
    values: List[
        Tuple[Optional[str], Optional[str]]
    ] = lookup_svc.lang_codes_and_names()
    print(
        "Language code, name tuples: {}, # of language code, name tuples: {}".format(
            values, len(values)
        )
    )


def test_lookup_all_resource_types(lookup_svc: ResourceJsonLookup) -> None:
    values: List[Optional[str]] = lookup_svc.resource_types()
    print("Resource types: {}, # of resource types: {}".format(values, len(values)))


def test_lookup_all_resource_codes(lookup_svc: ResourceJsonLookup) -> None:
    values: List[Optional[str]] = lookup_svc.resource_codes()
    print("Resource codes: {}, # of resource codes: {}".format(values, len(values)))


def test_lookup_downloads_at_reg(lookup_svc: ResourceJsonLookup) -> None:
    jsonpath_str = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values: List[Optional[str]] = lookup_svc._lookup(jsonpath_str)

    print(
        "All git repos having jsonpath {} : {}, # of repos: {}".format(
            jsonpath_str, values, len(values)
        )
    )


def test_lookup_downloads(lookup_svc: ResourceJsonLookup) -> None:
    """ Find all the git repos to determine all the locations they can
    be found in translations.json. """
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[Optional[str]] = lookup_svc._lookup(jsonpath_str)

    print(
        "All git repos having jsonpath {} : {}, # of repos: {}".format(
            jsonpath_str, values, len(values)
        )
    )


def test_lookup_downloads_not_at_reg(lookup_svc: ResourceJsonLookup) -> None:
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[Optional[str]] = lookup_svc._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[Optional[str]] = lookup_svc._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))
    print(
        "All git repos not found at countents[?code='reg'] having jsonpath {} : {}, # of repos: {}".format(
            jsonpath_str, result, len(result)
        )
    )


def test_lookup_downloads_not_at_reg2(lookup_svc: ResourceJsonLookup) -> None:
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[Optional[str]] = lookup_svc._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[Optional[str]] = lookup_svc._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))
    for x, y in zip(values, values2):
        print("x: {}\n y: {}".format(x, y))
    # print(
    #     "# of values: {}, # of values2: {}, All git repos not found at countents[?code='reg'] having jsonpath {} : {}, # of repos: {}".format(
    #         len(values), len(values2), jsonpath_str, result, len(result)
    #     )
    # )


def test_lookup_downloads_not_at_reg3(lookup_svc: ResourceJsonLookup) -> None:
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[Optional[str]] = lookup_svc._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[Optional[str]] = lookup_svc._lookup(jsonpath_str2)

    jsonpath_str3 = (
        "$[*].contents[?code='ulb'].subcontents[*].links[?format='Download'].url"
    )
    values3: List[Optional[str]] = lookup_svc._lookup(jsonpath_str3)

    jsonpath_str4 = (
        "$[*].contents[?code='udb'].subcontents[*].links[?format='Download'].url"
    )
    values4: List[Optional[str]] = lookup_svc._lookup(jsonpath_str4)

    print(
        "len(values): {}, len(values2): {}, len(values3): {}, len(values4): {}, sum(values,values2,values3,values4): {}".format(
            len(values),
            len(values2),
            len(values3),
            len(values4),
            len(values2) + len(values3) + len(values4),
        )
    )


def test_all_tn_zip_urls_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # For all languages
    download_urls: List[Optional[str]] = lookup_svc._lookup(
        "$[*].contents[?code='tn'].links[?format='zip'].url",
    )
    if download_urls is not None:
        print(
            "All translation notes having jsonpath {} : {}".format(
                "$[*].contents[?code='tn'].links[?format='zip'].url", download_urls
            )
        )
    else:
        print("download_urls is None")


if __name__ == "__main__":
    main()

# Phrases from repl that work:

# >>> json_data[0]["contents"][0]["subcontents"][0]["links"][1]["url"]

# >>> for d in json_data:
# >>>   print(d["code"])
# # imports from jsonpath

# >>> jp.match1("code", json_data[0])
# u'kbt'

# >>> jp.match1("code", json_data[0]["contents"][0])
# u'reg'

# >>> jp.match1("code", json_data[0]["contents"][0]["subcontents"][0])
# u'2co'
# jp.match("$[*].contents", json_data[0])

# >>> jp.match("$[*].contents", json_data[0])
# jp.match("$[*].contents", json_data[0])
# [[{u'subcontents': [{u'sort': 48, u'category': u'bible-nt', u'code': u'2co', u'name': u'2 Corinthians', u'links': [{u'url': u'http://read.bibletranslationtools.org/u/Southern./kbt_2co_text_reg/92731d1550/', u'format': u'Read on Web'}, {u'url': u'../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', u'format': u'Download'}]}], u'code': u'reg', u'name': u'Bible', u'links': [], u'subject': u'Bible'}]]

# >>> jp.match("$[*].contents[*].subcontents", json_data[0])
# jp.match("$[*].contents[*].subcontents", json_data[0])
# [[{u'sort': 48, u'category': u'bible-nt', u'code': u'2co', u'name': u'2 Corinthians', u'links': [{u'url': u'http://read.bibletranslationtools.org/u/Southern./kbt_2co_text_reg/92731d1550/', u'format': u'Read on Web'}, {u'url': u'../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', u'format': u'Download'}]}]]

# >>> jp.match("$[*].contents[*].subcontents[*].links", json_data[0])
# jp.match("$[*].contents[*].subcontents[*].links", json_data[0])
# [[{u'url': u'http://read.bibletranslationtools.org/u/Southern./kbt_2co_text_reg/92731d1550/', u'format': u'Read on Web'}, {u'url': u'../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', u'format': u'Download'}]]

# >>> jp.match("$[*].contents[*].subcontents[*].links[1]", json_data[0])
# jp.match("$[*].contents[*].subcontents[*].links[1]", json_data[0])
# [{u'url': u'../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', u'format': u'Download'}]

# >>> jp.match1("$[?name='" + "Abadi" + "'].contents[*].subcontents[*].links", json_data)
# jp.match1("$[?name='" + "Abadi" + "'].contents[*].subcontents[*].links", json_data)
# [{u'url': u'http://read.bibletranslationtools.org/u/Southern./kbt_2co_text_reg/92731d1550/', u'format': u'Read on Web'}, {u'url': u'../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', u'format': u'Download'}]

# >>> jp.match1("$[?name='" + "Abadi" + "'].contents[*].subcontents[*].links[?format='Download']", json_data)
# jp.match1("$[?name='" + "Abadi" + "'].contents[*].subcontents[*].links[?format='Download']", json_data)
# {u'url': u'../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians', u'format': u'Download'}

# >>> jp.match1("$[?name='" + "Abadi" + "'].contents[*].subcontents[*].links[?format='Download'].url", json_data)
# jp.match1("$[?name='" + "Abadi" + "'].contents[*].subcontents[*].links[?format='Download'].url", json_data)
# u'../download-scripture?repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fsouthern.%2Fkbt_2co_text_reg&book_name=2%20Corinthians'
