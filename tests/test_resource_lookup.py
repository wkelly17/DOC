from typing import Dict, List, Optional, Set, Tuple, Union
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

from document.utils import file_utils
from document.utils import url_utils
from document import config
from document.domain import resource_lookup
from document.domain import model
from document.domain.resource import (
    Resource,
    USFMResource,
    TNResource,
    TAResource,
    TQResource,
    TWResource,
    resource_factory,
)


# Define type alias for brevity
# AResource = Union[USFMResource, TAResource, TNResource, TQResource, TWResource]

import yaml
import logging
import logging.config

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)


logger = logging.getLogger(__name__)


def main() -> None:
    """Test driver."""
    usfm_lookup_svc = resource_lookup.USFMResourceJsonLookup()
    t_lookup_svc = resource_lookup.TResourceJsonLookup()
    biel_helper_lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()

    ## A few non-API tests that demonstrate aspects of jsonpath
    ## library or nature of data we are working with:

    if False:
        test_lookup_all_language_codes(biel_helper_lookup_svc)

    if False:
        test_lookup_all_language_codes_and_names(biel_helper_lookup_svc)

    if False:
        test_lookup_all_resource_types(biel_helper_lookup_svc)

    if False:
        test_lookup_all_resource_codes(biel_helper_lookup_svc)

    if False:
        test_all_tn_zip_urls_lookup(t_lookup_svc)

    if False:
        test_lookup_downloads_at_reg(usfm_lookup_svc)

    if False:
        test_lookup_downloads(t_lookup_svc)

    if False:
        test_lookup_downloads_not_at_reg(t_lookup_svc)

    if False:
        test_lookup_downloads_not_at_reg(usfm_lookup_svc)

    if False:
        test_lookup_downloads_not_at_reg2(t_lookup_svc)

    if False:
        test_lookup_downloads_not_at_reg2(usfm_lookup_svc)

    if False:
        test_lookup_downloads_not_at_reg3(t_lookup_svc)

    if False:
        test_lookup_downloads_not_at_reg3(usfm_lookup_svc)

    ## Test the API:

    if True:
        assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.book
        resource_requests: List[model.ResourceRequest] = []
        resource_requests.append(
            model.ResourceRequest(
                lang_code="en", resource_type="ulb-wa", resource_code="gen"
            )
        )
        resource_requests.append(
            model.ResourceRequest(
                lang_code="en", resource_type="tn-wa", resource_code="gen"
            )
        )

        resource_requests.append(
            model.ResourceRequest(
                lang_code="mr", resource_type="ulb", resource_code="gen"
            )
        )

        resource_requests.append(
            model.ResourceRequest(
                lang_code="erk-x-erakor", resource_type="reg", resource_code="eph"
            )
        )
        document_request = model.DocumentRequest(
            assembly_strategy_kind=assembly_strategy_kind,
            resource_requests=resource_requests,
        )

        for resource_request in document_request.resource_requests:
            r = resource_factory(
                config.get_working_dir(), config.get_output_dir(), resource_request
            )
            test_lookup(r)


## Test the API:


def test_lookup(resource: Resource) -> None:
    resource.find_location()
    print(
        "{}, resource_jsonpath: {}, URL: {}".format(
            resource, resource._resource_jsonpath, resource._resource_url
        )
    )
    # assert resource._resource_url


## A few non-API tests that demonstrate aspects of jsonpath
## library or nature of data we are working with or other jsonpaths
## that are not known to be needed yet:


def test_lookup_all_language_codes(
    lookup_svc: resource_lookup.BIELHelperResourceJsonLookup,
) -> None:
    values = lookup_svc.lang_codes()
    print("Language codes: {}, # of language codes: {}".format(values, len(values)))


def test_lookup_all_language_codes_and_names(
    lookup_svc: resource_lookup.BIELHelperResourceJsonLookup,
) -> None:
    values: List[Tuple[str, str]] = lookup_svc.lang_codes_and_names()
    print(
        "Language code, name tuples: {}, # of language code, name tuples: {}".format(
            values, len(values)
        )
    )


def test_lookup_all_resource_types(
    lookup_svc: resource_lookup.BIELHelperResourceJsonLookup,
) -> None:
    values: List[str] = lookup_svc.resource_types()
    print("Resource types: {}, # of resource types: {}".format(values, len(values)))


def test_lookup_all_resource_codes(
    lookup_svc: resource_lookup.BIELHelperResourceJsonLookup,
) -> None:
    values: List[str] = lookup_svc.resource_codes()
    print("Resource codes: {}, # of resource codes: {}".format(values, len(values)))


def test_lookup_downloads_at_reg(
    lookup_svc: resource_lookup.USFMResourceJsonLookup,
) -> None:
    jsonpath_str = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    print(
        "All git repos having jsonpath {} : {}, # of repos: {}".format(
            jsonpath_str, values, len(values)
        )
    )


def test_lookup_downloads(
    lookup_svc: Union[
        resource_lookup.USFMResourceJsonLookup, resource_lookup.TResourceJsonLookup
    ]
) -> None:
    """ Find all the git repos to determine all the locations they can
    be found in translations.json. """
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    print(
        "All git repos having jsonpath {} : {}, # of repos: {}".format(
            jsonpath_str, values, len(values)
        )
    )


def test_lookup_downloads_not_at_reg(
    lookup_svc: Union[
        resource_lookup.USFMResourceJsonLookup, resource_lookup.TResourceJsonLookup
    ]
) -> None:
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))
    print(
        "All git repos not found at countents[?code='reg'] having jsonpath {} : {}, # of repos: {}".format(
            jsonpath_str, result, len(result)
        )
    )


def test_lookup_downloads_not_at_reg2(
    lookup_svc: Union[
        resource_lookup.USFMResourceJsonLookup, resource_lookup.TResourceJsonLookup
    ]
) -> None:
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))
    for x, y in zip(values, values2):
        print("x: {}\n y: {}".format(x, y))


def test_lookup_downloads_not_at_reg3(
    lookup_svc: Union[
        resource_lookup.USFMResourceJsonLookup, resource_lookup.TResourceJsonLookup
    ]
) -> None:
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    jsonpath_str3 = (
        "$[*].contents[?code='ulb'].subcontents[*].links[?format='Download'].url"
    )
    values3: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str3)

    jsonpath_str4 = (
        "$[*].contents[?code='udb'].subcontents[*].links[?format='Download'].url"
    )
    values4: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str4)

    print(
        "len(values): {}, len(values2): {}, len(values3): {}, len(values4): {}, sum(values,values2,values3,values4): {}".format(
            len(values),
            len(values2),
            len(values3),
            len(values4),
            len(values2) + len(values3) + len(values4),
        )
    )


def test_all_tn_zip_urls_lookup(
    lookup_svc: Union[
        resource_lookup.USFMResourceJsonLookup, resource_lookup.TResourceJsonLookup
    ]
) -> None:
    # For all languages
    download_urls: List[str] = lookup_svc.resource_json_lookup._lookup(
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
