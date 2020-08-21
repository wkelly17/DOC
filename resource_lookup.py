from typing import Optional, List, Set, Dict
from file_utils import load_json_object
from url_utils import download_file
import logging
import os
from datetime import datetime, timedelta
import pprint
import tempfile

# from jsonpath_ng import jsonpath, parse  # type: ignore
# import jsonpath_ng as jp  # for calling extended methods

from jsonpath_rw import jsonpath  # type: ignore
from jsonpath_rw_ext import parse  # type: ignore
import jsonpath_rw_ext as jp  # for calling extended methods
import urllib.request, urllib.parse, urllib.error


class ResourceLookup:
    """ Abstract base class that formalizes resource lookup. Currently
    we do lookup via JSON and translations.json, but later we may use
    a GraphQL API. The interface (hopefully) doesn't have to change
    and thus call sites in client code can remain largely unchanged. """

    def data_needs_update(self) -> bool:
        raise NotImplementedError

    def lookup_tn_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_tw_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_tq_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_ta_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_ulb_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_udb_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_obs_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_obs_tn_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError

    def lookup_obs_tq_zips_for_lang(self, lang: str) -> List[str]:
        raise NotImplementedError


class ResourceJsonLookup(ResourceLookup):
    """ A class that let's you download the translations.json file and retrieve
values from it using jsonpath. """

    def __init__(
        self,
        working_dir: Optional[str] = "./",  # This is in /tools in the Docker container
        json_file_url: str = "http://bibleineverylanguage.org/wp-content/themes/bb-theme-child/data/translations.json",
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

        self.logger.debug("WORKING DIR IS {0}".format(self.working_dir))

        self.json_file: str = os.path.join(
            self.working_dir, self.json_file_url.rpartition(os.path.sep)[2]
        )

        self.logger.debug("JSON FILE IS {0}".format(self.json_file))

        self.json_data: Optional[Dict] = None

    def get_data(self) -> None:
        """ Get json data. """
        if self.data_needs_update():
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
                self.json_data = load_json_object(self.json_file)
            finally:
                self.logger.debug("finished loading json file.")

    def data_needs_update(self) -> bool:
        """ Given translations.json file path, return true if it has
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

    def lookup(self, jsonpath: str,) -> List[str]:
        """ Return jsonpath value or empty list if node doesn't exist. """
        self.get_data()
        value: List[str] = jp.match(
            jsonpath, self.json_data,
        )
        value_set: Set = set(value)
        return list(value_set)

    def lookup_tn_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for translation notes (code: 'tn'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='tn'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_tw_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for translation words (code: 'tw'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='tw'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_tq_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for translation questions (code: 'tq'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='tq'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_ta_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for translation academy (code: 'ta'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='ta'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_ulb_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for unlocked literal bible USFM (code: 'ulb'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='ulb'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_udb_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for unlocked dynamic bible USFM (code: 'udb'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='udb'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_obs_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for open bible stories (code: 'obs'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='obs'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_obs_tn_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for open bible stories translation
        notes (code: 'obs-tn'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='obs-tn'].links[?format='zip'].url".format(
                lang
            )
        )
        return zip_urls

    def lookup_obs_tq_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for open bible stories translation
        questions (code: 'obs-tq'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='obs-tq'].links[?format='zip'].url".format(
                lang
            )
        )
        return zip_urls

    # THe functions below aren't part of the API, they are just
    # experiments.
    def lookup_download_url(
        self,
        jsonpath: str = "$[?name='English'].contents[*].subcontents[*].links[?format='Download'].url",
    ) -> Optional[str]:
        """ Return json dict object for download url for lang. """
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
        """ Given a URL, url, of the form
        ../download-scripture?repo_url=https%3A%2F%2Fgit.door43.org%2Fburje_duro%2Fam_gen_text_udb&book_name=Genesis,
        return the repo_url query parameter value. """
        if url is None:
            return None
        result: dict = urllib.parse.parse_qs(url)
        result_lst: List = result[repo_url_dict_key]
        if result_lst is not None:
            return result_lst[0]
        else:
            return None


def main() -> None:
    """ Test driver. """
    lookup_svc: ResourceJsonLookup = ResourceJsonLookup()

    # test_abadi_language_lookup(lookup_svc)

    # test_wumbvu_language_lookup(lookup_svc)

    # test_another_language_lookup(lookup_svc)

    # test_english_language_lookup(lookup_svc)

    # test_three_language_lookup(lookup_svc)

    # test_all_tn_zip_urls_lookup(lookup_svc)

    # test_lookup_tn_zips_for_lang(lookup_svc, "ಕನ್ನಡ (Kannada)")

    # test_lookup_tn_zips_for_lang(lookup_svc, "Lao")

    # test_lookup_tn_zips_for_lang(lookup_svc, "Assamese")

    test_lookup_tn_zips_for_lang(lookup_svc, "Emai-Iuleha-Ora")

    # test_lookup_tw_zips_for_lang(lookup_svc, "Plateau Malagasy")

    # test_lookup_tq_zips_for_lang(lookup_svc, "മലയാളം  (Malayalam)")

    test_lookup_ta_zips_for_lang(lookup_svc, "मराठी")

    # test_lookup_ulb_zips_for_lang(lookup_svc, "Lopit")

    test_lookup_udb_zips_for_lang(lookup_svc, "मराठी")

    test_lookup_obs_zips_for_lang(lookup_svc, "मराठी")

    test_lookup_obs_tn_zips_for_lang(lookup_svc, "मराठी")

    test_lookup_obs_tq_zips_for_lang(lookup_svc, "मराठी")

    # test_lookup_all_language_names(lookup_svc)

    test_lookup_all_codes(lookup_svc)


def test_abadi_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Test Abadi language
    lang: str = "Abadi"
    jsonpath: str = "$[?name='{0}'].contents[*].subcontents[*].links[?format='Download'].url".format(
        lang
    )
    download_url: Optional[str] = lookup_svc.lookup_download_url(jsonpath)
    if download_url is not None:
        print(("Language {0} download url: {1}".format(lang, download_url)))
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(download_url)
    if repo_url is not None:
        print(("Language {0} repo_url: {1}".format(lang, repo_url)))


def test_wumbvu_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Vumbvu lang
    lang = "Wumbvu"
    jsonpath = "$[?name='{0}'].contents[*].subcontents[*].links[?format='Download'].url".format(
        lang
    )
    download_url = lookup_svc.lookup_download_url(jsonpath)
    if download_url is not None:
        print(("Language {0} download url: {1}".format(lang, download_url)))
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(download_url)
    if repo_url is not None:
        print(("Language {0} repo_url: {1}".format(lang, repo_url)))


def test_another_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Another lanugage
    lang = "አማርኛ"
    jsonpath = "$[?name='{0}'].contents[*].subcontents[*].links[?format='Download'].url".format(
        lang
    )
    download_urls: List[str] = lookup_svc.lookup_download_urls(jsonpath)
    if download_urls is not None:
        print("Language {0} download_urls: {1}".format(lang, download_urls))
        print(("Language {0} first download url: {1}".format(lang, download_urls[0])))
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(download_urls[0])
    if repo_url is not None:
        print(("Language {0} first repo repo_url: {1}".format(lang, repo_url)))


def test_english_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Test English lang. Different jsonpath for English USFM files.
    lang = "English"
    jsonpath = "$[?name='{0}'].contents[*].links[?format='Download'].url".format(lang)
    download_urls: List[str] = lookup_svc.lookup_download_urls(jsonpath)
    if download_urls is not None:
        print("Language {0} download_urls: {1}".format(lang, download_urls))
        print(("Language {0} first download url: {1}".format(lang, download_urls[0])))
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(
        download_urls[0], "/download-scripture?repo_url"
    )
    if repo_url is not None:
        print(("Language {0} first repo repo_url: {1}".format(lang, repo_url)))


def test_three_language_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # Test getting all translation notes for more than one language
    langs = ["English", "Abadi", "Assamese"]
    for lang in langs:
        download_urls: List[str] = lookup_svc.lookup_download_urls(
            "$[?name='{0}'].contents[?code='tn'].links[?format='zip'].url".format(lang),
        )
        if download_urls is not None:
            print("Language {0} download_urls: {1}".format(lang, download_urls))
        else:
            print("download_urls is None")


def test_all_tn_zip_urls_lookup(lookup_svc: ResourceJsonLookup) -> None:
    # For all languages
    download_urls: List[str] = lookup_svc.lookup(
        "$[*].contents[?code='tn'].links[?format='zip'].url",
    )
    if download_urls is not None:
        print(
            "All language download_urls having jsonpath {0} : {1}".format(
                "$[*].contents[?code='tn'].links[?format='zip'].url", download_urls
            )
        )
    else:
        print("download_urls is None")


def test_lookup_tn_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_tn_zips_for_lang(lang)
    print("Translation notes for lang {0}: {1}".format(lang, values))


def test_lookup_tw_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_tw_zips_for_lang(lang)
    print("Translation words for lang {0}: {1}".format(lang, values))


def test_lookup_tq_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_tq_zips_for_lang(lang)
    print("Translation questions for lang {0}: {1}".format(lang, values))


def test_lookup_ta_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_ta_zips_for_lang(lang)
    print("Translation acadmey for lang {0}: {1}".format(lang, values))


def test_lookup_ulb_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_ulb_zips_for_lang(lang)
    print("Unlocked literal bible for lang {0}: {1}".format(lang, values))


def test_lookup_udb_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_udb_zips_for_lang(lang)
    print("Unlocked dynamic bible for lang {0}: {1}".format(lang, values))


def test_lookup_obs_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_obs_zips_for_lang(lang)
    print("Open bible stories for lang {0}: {1}".format(lang, values))


def test_lookup_obs_tn_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_obs_tn_zips_for_lang(lang)
    print("Open bible stories translation notes for lang {0}: {1}".format(lang, values))


def test_lookup_obs_tq_zips_for_lang(lookup_svc: ResourceJsonLookup, lang: str) -> None:
    values: List[str] = lookup_svc.lookup_obs_tq_zips_for_lang(lang)
    print(
        "Open bible stories translation questions for lang {0}: {1}".format(
            lang, values
        )
    )


def test_lookup_all_language_names(lookup_svc: ResourceJsonLookup) -> None:
    values: List[str] = lookup_svc.lookup("$[*].name")
    print("Languages: {0}, # of languages: {1}".format(values, len(values)))


def test_lookup_all_codes(lookup_svc: ResourceJsonLookup) -> None:
    values: List[str] = lookup_svc.lookup("$[*].contents[*].code")
    print("Codes: {0}, # of codes: {1}".format(values, len(values)))


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
