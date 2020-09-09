from typing import Optional, List, Set, Dict
import abc
import logging
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
    from .file_utils import load_json_object
    from .url_utils import download_file
    from .config import (
        get_translations_json_location,
        get_individual_usfm_url_jsonpath,
        get_resource_url_level_1_jsonpath,
        get_resource_url_level_2_jsonpath,
        get_resource_download_format_jsonpath,
    )
except:
    from file_utils import load_json_object
    from url_utils import download_file
    from config import (
        get_translations_json_location,
        get_individual_usfm_url_jsonpath,
        get_resource_url_level_1_jsonpath,
        get_resource_url_level_2_jsonpath,
        get_resource_download_format_jsonpath,
    )


class ResourceLookup(abc.ABC):
    """ Abstract base class that formalizes resource lookup. Currently
    we do lookup via JSON and translations.json, but later we may use
    a GraphQL API. The interface (hopefully) doesn't have to change (much)
    and thus call sites in client code can remain largely unchanged. """

    @abc.abstractmethod
    def lookup(self, resource: Dict) -> List[Optional[str]]:
        raise NotImplementedError


class ResourceJsonLookup(ResourceLookup):
    """ A class that let's you download the translations.json file and retrieve
values from it using jsonpath. """

    def __init__(
        self,
        working_dir: Optional[str] = "./",  # This is in /tools in the Docker container
        json_file_url: str = get_translations_json_location(),
        logger: logging.Logger = None,
        pp: pprint.PrettyPrinter = None,
    ) -> None:
        # Set up logger
        if logger is not None:
            self.logger: logging.Logger = logger
        else:
            self.logger: logging.Logger = logging.getLogger()
            self.logger.setLevel(logging.DEBUG)
            ch: logging.StreamHandler = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter: logging.Formatter = logging.Formatter(
                "%(levelname)s - %(message)s"
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        # Set up the pretty printer
        if pp is not None:
            self.pp: pprint.PrettyPrinter = pp
        else:
            self.pp: pprint.PrettyPrinter = pprint.PrettyPrinter(indent=4)

        self.working_dir = working_dir
        self.json_file_url = json_file_url

        if not self.working_dir:
            self.logger.debug("Creating working dir")
            self.working_dir = tempfile.mkdtemp(prefix="json_")

        self.logger.debug("WORKING DIR IS {}".format(self.working_dir))

        self.json_file: str = os.path.join(
            self.working_dir, self.json_file_url.rpartition(os.path.sep)[2]
        )

        self.logger.debug("JSON FILE IS {}".format(self.json_file))

        self.json_data: Optional[Dict] = None

    # protected access level
    def _get_data(self) -> None:
        """ Download json data and parse it into equivalent python objects. """
        if self._data_needs_update():
            # Download json file
            try:
                self.logger.debug("Downloading {}...".format(self.json_file_url))
                download_file(self.json_file_url, self.json_file)
            finally:
                self.logger.debug("finished downloading json file.")

        if self.json_data is None:
            # Load json file
            try:
                self.logger.debug("Loading json file {}...".format(self.json_file))
                self.json_data = load_json_object(
                    self.json_file
                )  # json_data should possibly live on its own object
            finally:
                self.logger.debug("finished loading json file.")

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

    # protected access level
    def _lookup(self, jsonpath: str,) -> List[Optional[str]]:
        """ Return jsonpath value or empty list if node doesn't exist. """
        self._get_data()
        value: List[str] = jp.match(
            jsonpath, self.json_data,
        )
        value_set: Set = set(value)
        return list(value_set)

    # NOTE Some target languages only provide a resource at
    # $[*].contents[?name='reg'].links[?format='Download']. In that
    # case, grab the repo url from repo_url part of query string. Then
    # perhaps you'd want to use gitea to get the repo.
    # TODO Research: Do 'Read on Web' format resources have an associated git
    # repo if they don't have a sibling 'Download' format URL? I
    # looked at "erk-x-erakor" for intance and there one can see there
    # is no symmetry between the 'Read on Web' and 'Download' format
    # URLs that can be extrapolated to other language resources;
    # perhaps it can to a subset, but the relationship between the
    # 'Read on Web' and 'Download' format URLs seems to vary by
    # language.
    #
    def lookup(self, resource: Dict,) -> List[Optional[str]]:
        """ Given a resource, comprised of language code, e.g., 'wum',
        a resource type, e.g., 'tn', and an optional resource code,
        e.g., 'gen', return URLs for resource. """

        assert resource["lang_code"] is not None, "lang_code is required"
        assert resource["resource_type"] is not None, "resource_type is required"

        urls: List[Optional[str]] = []

        if (
            resource["resource_code"] is not None
        ):  # User has likely specified a book of the bible, try first
            # to get the resource from a git repo.
            jsonpath_str = get_resource_download_format_jsonpath().format(
                resource["lang_code"], "reg", resource["resource_code"]
            )
            urls = self._lookup(jsonpath_str)
            if urls is not None and len(urls) > 0:
                # Get the portion of the query string that gives
                # the repo URL
                urls = [self.parse_repo_url_from_json_url(urls[0])]
            if (
                urls is not None and len(urls) == 0
            ):  # Resource not found, next try to get from download URL.
                jsonpath_str = get_individual_usfm_url_jsonpath().format(
                    resource["lang_code"],
                    resource["resource_type"],
                    resource["resource_code"],
                )
                urls = self._lookup(jsonpath_str)
        else:  # User has not specified a particular book of the bible
            jsonpath_str = get_resource_url_level_1_jsonpath().format(
                resource["lang_code"], resource["resource_type"],
            )
            urls = self._lookup(jsonpath_str)
            if (
                urls is not None and len(urls) == 0
            ):  # For the language in question, the resource is apparently at a different location which we try next.
                jsonpath_str = get_resource_url_level_2_jsonpath().format(
                    resource["lang_code"], resource["resource_type"],
                )
                urls = self._lookup(jsonpath_str)
        # NOTE Some resources will be fetched via gitea and others by
        # downloading the URL. How do we specify this to the code
        # responsible for downloading or cloning if the lookup is
        # separate. Perhaps this class should be renamed and manage
        # both lookup and acquisition.

        return urls

    # The functions below aren't part of the API, they are just
    # experiments:

    def lookup_download_url(
        self,
        jsonpath: str = "$[?name='English'].contents[*].subcontents[*].links[?format='Download'].url",
    ) -> Optional[str]:
        """ Return json dict object for download url for jsonpath. """
        download_url = jp.match1(jsonpath, self.json_data,)

        return download_url

    def lookup_download_urls(
        self,
        jsonpath: Optional[
            str
        ] = "$[?name='English'].contents[*].subcontents[*].links[?format='Download'].url",
    ) -> List[str]:
        """ Return json dict object for download url for lang. """
        download_urls = jp.match(jsonpath, self.json_data,)

        return download_urls

    def parse_repo_url_from_json_url(
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


def main() -> None:
    """ Test driver. """

    lookup_svc: ResourceJsonLookup = ResourceJsonLookup()

    ## A few non-API tests that demonstrate aspects of jsonpath
    ## library or nature of data we are working with:

    if False:
        test_lookup_all_language_names(lookup_svc)

        test_lookup_all_codes(lookup_svc)

        test_abadi_language_lookup(lookup_svc)

        test_wumbvu_language_lookup(lookup_svc)

        test_another_language_lookup(lookup_svc)

        test_english_language_lookup(lookup_svc)

        test_three_language_tn_lookup(lookup_svc)

        test_all_tn_zip_urls_lookup(lookup_svc)

    ## Test the API:

    if True:
        fixtures = {}
        fixtures["resources"] = [
            {"lang_code": "kn", "resource_type": "tn", "resource_code": None},
            {"lang_code": "lo", "resource_type": "tn", "resource_code": None},
            {"lang_code": "as", "resource_type": "tn", "resource_code": None},
            {"lang_code": "ema", "resource_type": "tn", "resource_code": None},
            {"lang_code": "plt", "resource_type": "tw", "resource_code": None},
            {"lang_code": "ml", "resource_type": "tq", "resource_code": None},
            {"lang_code": "mr", "resource_type": "ta", "resource_code": None},
            {"lang_code": "lpx", "resource_type": "ulb", "resource_code": None},
            {"lang_code": "mr", "resource_type": "ulb", "resource_code": "gen"},
            {"lang_code": "mr", "resource_type": "udb", "resource_code": None},
            {"lang_code": "mr", "resource_type": "obs", "resource_code": None},
            {"lang_code": "mr", "resource_type": "obs-tn", "resource_code": None},
            {"lang_code": "mr", "resource_type": "obs-tq", "resource_code": None},
            {
                "lang_code": "erk-x-erakor",
                "resource_type": "reg",
                "resource_code": "eph",
            },
        ]

        for resource in fixtures["resources"]:
            test_lookup(lookup_svc, resource)


## Test the API:


def test_lookup(lookup_svc: ResourceJsonLookup, resource) -> None:
    values: List[Optional[str]] = lookup_svc.lookup(resource)
    print(
        "Language {}, resource_type: {}, resource_code: {}, values: {}".format(
            resource["lang_code"],
            resource["resource_type"],
            resource["resource_code"],
            values,
        )
    )


## A few non-API tests that demonstrate aspects of jsonpath
## library or nature of data we are working with or other jsonpaths
## that are not known to be needed yet:


def test_lookup_all_language_names(lookup_svc: ResourceJsonLookup) -> None:
    values: List[Optional[str]] = lookup_svc._lookup("$[*].name")
    print("Languages: {}, # of languages: {}".format(values, len(values)))


def test_lookup_all_codes(lookup_svc: ResourceJsonLookup) -> None:
    values: List[Optional[str]] = lookup_svc._lookup("$[*].contents[*].code")
    print("Codes: {}, # of codes: {}".format(values, len(values)))


def test_abadi_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Test Abadi language
    lang_code: str = "kbt"
    jsonpath: str = "$[?code='{}'].contents[*].subcontents[*].links[?format='Download'].url".format(
        lang_code
    )
    download_url: Optional[str] = lookup_svc.lookup_download_url(jsonpath)
    if download_url is not None:
        print(("Language code {} download url: {}".format(lang_code, download_url)))
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(download_url)
    if repo_url is not None:
        print(("Language code {} repo_url: {}".format(lang_code, repo_url)))


def test_wumbvu_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Vumbvu lang
    lang_code: str = "wum"
    jsonpath = "$[?code='{}'].contents[*].subcontents[*].links[?format='Download'].url".format(
        lang_code
    )
    download_url = lookup_svc.lookup_download_url(jsonpath)
    if download_url is not None:
        print(("Language code {} download url: {}".format(lang_code, download_url)))
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(download_url)
    if repo_url is not None:
        print(("Language code {} repo_url: {}".format(lang_code, repo_url)))


def test_another_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Another lanugage
    lang_code: str = "am"
    jsonpath = "$[?code='{}'].contents[*].subcontents[*].links[?format='Download'].url".format(
        lang_code
    )
    download_urls: List[str] = lookup_svc.lookup_download_urls(jsonpath)
    if download_urls is not None:
        print("Language code {} download_urls: {}".format(lang_code, download_urls))
        print(
            (
                "Language code {} first download url: {}".format(
                    lang_code, download_urls[0]
                )
            )
        )
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(download_urls[0])
    if repo_url is not None:
        print(("Language code {} first repo repo_url: {}".format(lang_code, repo_url)))


def test_english_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Test English lang. Different jsonpath for English USFM files.
    lang: str = "en"
    jsonpath = "$[?code='{}'].contents[*].links[?format='Download'].url".format(lang)
    download_urls: List[str] = lookup_svc.lookup_download_urls(jsonpath)
    if download_urls is not None and len(download_urls) > 0:
        print("Language {} download_urls: {}".format(lang, download_urls))
        print(("Language {} first download url: {}".format(lang, download_urls[0])))
        repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(
            download_urls[0], "/download-scripture?repo_url"
        )
        if repo_url is not None:
            print(("Language {} first repo repo_url: {}".format(lang, repo_url)))


def test_three_language_tn_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Test getting all translation notes for more than one language
    langs: List[str] = ["English", "Abadi", "Assamese"]
    for lang in langs:
        download_urls: List[str] = lookup_svc.lookup_download_urls(
            "$[?name='{}'].contents[?code='tn'].links[?format='zip'].url".format(lang),
        )
        if download_urls is not None and len(download_urls) == 0:
            download_urls = lookup_svc.lookup_download_urls(
                "$[?name='{}'].contents[*].subcontents[?code='tn'].links[?format='zip'].url".format(
                    lang
                ),
            )

        print("Language {} translation notes : {}".format(lang, download_urls))


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
