from typing import Optional, List
from file_utils import load_json_object
from url_utils import download_file
import logging
import os
import pprint
import tempfile

# from jsonpath_ng import jsonpath, parse  # type: ignore
# import jsonpath_ng as jp  # for calling extended methods

from jsonpath_rw import jsonpath  # type: ignore
from jsonpath_rw_ext import parse  # type: ignore
import jsonpath_rw_ext as jp  # for calling extended methods
import urllib.request, urllib.parse, urllib.error


# TODO Make this class use a Configuration class of its own similar
# perhaps to pysystemtrade
class ResourceJsonLookup:
    """ A class that let's you download the translations.json file and retrieve
values from it using jsonpath. """

    def __init__(
        self,
        working_dir: Optional[str] = None,
        json_file_url: str = "http://bibleineverylanguage.org/wp-content/themes/bb-theme-child/data/translations.json",
        logger: logging.Logger = None,
        pp: pprint.PrettyPrinter = None,
    ) -> None:
        # Set up logger
        if logger:
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
        if pp:
            self.pp: pprint.PrettyPrinter = pp
        else:
            self.pp: pprint.PrettyPrinter = pprint.PrettyPrinter(indent=4)

        self.working_dir = working_dir
        self.json_file_url = json_file_url

        if not self.working_dir:
            self.working_dir = tempfile.mkdtemp(prefix="json_")

        self.logger.debug("TEMP JSON DIR IS {0}".format(self.working_dir))

        # from TnConverter class - just duplicating here for now
        # self.tn_dir = os.path.join(self.working_dir, "{0}_tn".format(lang_code))
        # self.tw_dir = os.path.join(self.working_dir, "{0}_tw".format(lang_code))
        # self.tq_dir = os.path.join(self.working_dir, "{0}_tq".format(lang_code))
        # self.ta_dir = os.path.join(self.working_dir, "{0}_ta".format(lang_code))
        # self.udb_dir = os.path.join(self.working_dir, "{0}_udb".format(lang_code))
        # self.ulb_dir = os.path.join(self.working_dir, "{0}_ulb".format(lang_code))

        self.json_file: str = os.path.join(
            self.working_dir, self.json_file_url.rpartition(os.path.sep)[2]
        )

        # Download json file
        try:
            self.logger.debug("Downloading {}...".format(self.json_file_url))
            download_file(self.json_file_url, self.json_file)
        finally:
            self.logger.debug("finished downloading json file.")

        # Load json file
        try:
            self.logger.debug("Loading json file {}...".format(self.json_file))
            self.json_data = load_json_object(self.json_file)
        finally:
            self.logger.debug("finished loading json file.")

    def lookup(self, jsonpath: str,) -> List[str]:
        """ Return jsonpath value or empty list if node doesn't exist. """
        value: List[str] = jp.match(
            jsonpath, self.json_data,
        )
        return value

    def lookup_tn_zips_for_lang(self, lang: str) -> List[str]:
        """ Return zip file URLs for translation notes (code: 'tn'). """
        # Based on lang value you can use a lookup dictionary that
        # returns the jsonpath to use. This is where we handle the
        # unpredictable structure of translations.json.
        zip_urls: List[str] = self.lookup(
            "$[?name='{0}'].contents[?code='tn'].links[?format='zip'].url".format(lang)
        )
        return zip_urls

    def lookup_download_url(
        self,
        jsonpath: Optional[
            str
        ] = "$[?name='English'].contents[*].subcontents[*].links[?format='Download'].url",
    ) -> Optional[
        str
    ]:  # XXX Get the types right - does jsonpath return an empty list if it finds nothing?
        """ Return json dict object for download url for lang. """
        download_url = jp.match1(jsonpath, self.json_data,)

        return download_url

    def lookup_download_urls(
        self,
        jsonpath: Optional[
            str
        ] = "$[?name='English'].contents[*].subcontents[*].links[?format='Download'].url",
    ) -> List[
        str
    ]:  # XXX Get the types right - does jsonpath return an empty list if it finds nothing?
        """ Return json dict object for download url for lang. """
        download_urls = jp.match(jsonpath, self.json_data,)

        return download_urls

    def parse_repo_url_from_json_url(
        self, url: str, repo_url_dict_key: str = "../download-scripture?repo_url"
    ) -> Optional[str]:
        """ Given a URL, url, of the form
        ../download-scripture?repo_url=https%3A%2F%2Fgit.door43.org%2Fburje_duro%2Fam_gen_text_udb&book_name=Genesis,
        return the repo_url query parameter value. """
        result: dict = urllib.parse.parse_qs(url)
        result_lst: List = result[repo_url_dict_key]
        if result_lst is not None:
            return result_lst[0]
        else:
            return None


def main() -> None:
    """ Test driver. """
    lookup_svc: ResourceJsonLookup = ResourceJsonLookup()

    # test_lookup_tn_zips_for_lang(lookup_svc, "ಕನ್ನಡ (Kannada)")

    # test_lookup_tn_zips_for_lang(lookup_svc, "Lao")

    # test_lookup_tn_zips_for_lang(lookup_svc, "Assamese")

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

    # Test English lang. Different structure for USFM files so
    # requires different jsonaths.
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
