from typing import Optional, List, Set, Dict
import abc
import logging
import os
from datetime import datetime, timedelta
import pprint
import tempfile

from jsonpath_rw import jsonpath  # type: ignore
from jsonpath_rw_ext import parse  # type: ignore
import jsonpath_rw_ext as jp  # for calling extended methods
import urllib.request, urllib.parse, urllib.error

# Handle running in container or as standalone script
try:
    from .file_utils import load_json_object
    from .url_utils import download_file
    from .config import get_translations_json_location
except:
    from file_utils import load_json_object
    from url_utils import download_file
    from config import get_translations_json_location


class ResourceLookup(abc.ABC):
    """ Abstract base class that formalizes resource lookup. Currently
    we do lookup via JSON and translations.json, but later we may use
    a GraphQL API. The interface (hopefully) doesn't have to change (much)
    and thus call sites in client code can remain largely unchanged. """

    @abc.abstractmethod
    def lookup(
        self, lang_code: str, resource_type: str, resource_code: Optional[str]
    ) -> List[str]:
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
    def _lookup(self, jsonpath: str,) -> List[str]:
        """ Return jsonpath value or empty list if node doesn't exist. """
        self._get_data()
        value: List[str] = jp.match(
            jsonpath, self.json_data,
        )
        value_set: Set = set(value)
        return list(value_set)

    def lookup(
        self, lang_code: str, resource_type: str, resource_code: Optional[str]
    ) -> List[str]:
        """ Given a language code, e.g., 'wum', a resource type, e.g.,
        'tn', and an optional resource code, e.g., 'gen', return URLs
        for resource. """

        assert lang_code is not None, "lang_code is required"
        assert resource_type is not None, "resource_type is required"

        if resource_code is not None:
            jsonpath_str = "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='usfm'].url".format(
                lang_code, resource_type, resource_code,
            )
        else:
            # NOTE We take the union of jsonpaths, '|', one at the
            # contents level and one at the subcontents level (because
            # the location of the resource can vary depending on
            # language).
            jsonpath_str = "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url".format(
                lang_code, resource_type,
            )
            # NOTE Using the | union join jsonpath operator below
            # resulted in no results being returned, this seems to be
            # a bug in jsonpath-rw lib.
            # jsonpath_str += " | "
            # jsonpath_str += "$[?code='{}'].contents[*].subcontents[?code='{}'].links[?format='zip'].url".format(
            #     lang_code, resource_type
            # )
        urls: List[str] = self._lookup(jsonpath_str)
        return urls

    # NOTE This method only still exists for the commented out code at
    # the end that tries a different jsonpath if the first jsonpath
    # tried yields no results (since jsonpaths unfortunately can vary
    # based on language).
    def lookup_ulb_book(self, lang_code: str, book_id: str) -> List[str]:
        """ Given a language code and book id, return file URL for unlocked literal bible USFM (code: 'ulb'). """
        download_urls: List[str] = self._lookup(
            "$[?code='{}'].contents[?code='ulb'].subcontents[?code='{}'].links[?format='usfm'].url".format(
                lang_code, book_id
            )
        )
        return download_urls
        # NOTE If 'Download' format links can be manipulated to get a
        # downloadable url then the following conditional code could
        # be used to access it since some language book combinations
        # provide this as an alternate location, e.g., lang_code: lpx,
        # code: ulb, subcontents, links, format: Download.
        # if len(download_urls) > 0:  # Success at first jsonpath.
        #     return download_urls
        # else:  # Check the other jsonpath where this resource can exist sometimes.
        #     download_urls: List[str] = self._lookup(
        #         "$[?code='{}'].contents[?code='ulb'].subcontents[?code='{}'].links[?format='Download'].url"
        #     )
        #     if download_urls is not None and len(download_urls) > 0:
        #         # Example url: https://git.door43.org/ojasi/lpx_2th_text_ulb&book_name=2%20Thessalonians
        #         download_urls = [self.parse_repo_url_from_json_url(download_urls[0])]
        #     return download_urls

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

    test_lookup_all_language_names(lookup_svc)

    test_lookup_all_codes(lookup_svc)

    test_abadi_language_lookup(lookup_svc)

    test_wumbvu_language_lookup(lookup_svc)

    test_another_language_lookup(lookup_svc)

    test_english_language_lookup(lookup_svc)

    test_three_language_lookup(lookup_svc)

    test_all_tn_zip_urls_lookup(lookup_svc)

    ## Test the API:

    test_lookup_tn_zips(lookup_svc, "kn")

    test_lookup_tn_zips(lookup_svc, "lo")

    test_lookup_tn_zips(lookup_svc, "as")

    test_lookup_tn_zips(lookup_svc, "ema")

    test_lookup_tw_zips(lookup_svc, "plt")

    test_lookup_tq_zips(lookup_svc, "ml")

    test_lookup_ta_zips(lookup_svc, "mr")

    test_lookup_ulb_zips(lookup_svc, "lpx")

    test_lookup_ulb_book(lookup_svc, "mr")

    test_lookup_udb_zips(lookup_svc, "mr")

    test_lookup_obs_zips(lookup_svc, "mr")

    test_lookup_obs_tn_zips(lookup_svc, "mr")

    test_lookup_obs_tq_zips(lookup_svc, "mr")


## Test the API:


def test_lookup_tn_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "tn", None)
    print("Translation notes for lang_code {}: {}".format(lang_code, values))


def test_lookup_tw_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "tw", None)
    print("Translation words for lang_code {}: {}".format(lang_code, values))


def test_lookup_tq_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "tq", None)
    print("Translation questions for lang_code {}: {}".format(lang_code, values))


def test_lookup_ta_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "ta", None)
    print("Translation academy for lang_code {}: {}".format(lang_code, values))


def test_lookup_ulb_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "ulb", None)
    print("Unlocked literal bible for lang_code {}: {}".format(lang_code, values))


def test_lookup_ulb_book(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "ulb", "gen")
    print(
        "Unlocked literal bible for lang_code {} and book {}: {}".format(
            lang_code, "gen", values
        )
    )


def test_lookup_udb_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "udb", None)
    print("Unlocked dynamic bible for lang_code {}: {}".format(lang_code, values))


def test_lookup_obs_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "obs", None)
    print("Open bible stories for lang_code {}: {}".format(lang_code, values))


def test_lookup_obs_tn_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "obs-tn", None)
    print(
        "Open bible stories translation notes for lang_code {}: {}".format(
            lang_code, values
        )
    )


def test_lookup_obs_tq_zips(lookup_svc: ResourceJsonLookup, lang_code: str) -> None:
    values: List[str] = lookup_svc.lookup(lang_code, "obs-tq", None)
    print(
        "Open bible stories translation questions for lang_code {}: {}".format(
            lang_code, values
        )
    )


def test_lookup_all_language_names(lookup_svc: ResourceJsonLookup) -> None:
    values: List[str] = lookup_svc._lookup("$[*].name")
    print("Languages: {}, # of languages: {}".format(values, len(values)))


def test_lookup_all_codes(lookup_svc: ResourceJsonLookup) -> None:
    values: List[str] = lookup_svc._lookup("$[*].contents[*].code")
    print("Codes: {}, # of codes: {}".format(values, len(values)))


## A few non-API tests that demonstrate aspects of jsonpath
## library or nature of data we are working with or other jsonpaths
## that are not known to be needed yet:


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


def test_three_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Test getting all translation notes for more than one language
    langs: List[str] = ["English", "Abadi", "Assamese"]
    for lang in langs:
        download_urls: List[str] = lookup_svc.lookup_download_urls(
            "$[?name='{}'].contents[?code='tn'].links[?format='zip'].url".format(lang),
        )
        if download_urls is not None:
            print("Language {} download_urls: {}".format(lang, download_urls))
        else:
            print("download_urls is None")


def test_all_tn_zip_urls_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # For all languages
    download_urls: List[str] = lookup_svc._lookup(
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
