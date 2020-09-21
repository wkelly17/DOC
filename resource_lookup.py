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

import yaml
import logging
import logging.config

with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


logger = logging.getLogger(__name__)


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
        working_dir: Optional[
            str
        ] = get_working_dir(),  # This is in /tools in the Docker container
        json_file_url: str = get_translations_json_location(),
    ) -> None:

        self.working_dir = working_dir
        self.json_file_url = json_file_url

        if not self.working_dir:
            logger.info("Creating working dir")
            self.working_dir = tempfile.mkdtemp(prefix="json_")

        logger.info("Working dir is {}".format(self.working_dir))

        self.json_file: str = os.path.join(
            self.working_dir, self.json_file_url.rpartition(os.path.sep)[2]
        )

        logger.info("JSON file is {}".format(self.json_file))

        self.json_data: Optional[Dict] = None

    # protected access level
    def _get_data(self) -> None:
        """ Download json data and parse it into equivalent python objects. """
        if self._data_needs_update():
            # Download json file
            try:
                logger.info("Downloading {}...".format(self.json_file_url))
                download_file(self.json_file_url, self.json_file)
            finally:
                logger.info("finished downloading json file.")

        if self.json_data is None:
            # Load json file
            try:
                logger.info("Loading json file {}...".format(self.json_file))
                self.json_data = load_json_object(
                    self.json_file
                )  # json_data should possibly live on its own object
            finally:
                logger.info("finished loading json file.")

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
        logger.info("jsonpath: {}".format(jsonpath))
        value: List[str] = jp.match(
            jsonpath, self.json_data,
        )
        value_set: Set = set(value)
        return list(value_set)

    # protected access level
    def _parse_repo_url_from_json_url(
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

    # NOTE Some target languages only provide a resource at
    # $[*].contents[?name='reg'].links[?format='Download']. In that
    # case, grab the repo url from repo_url part of query string. Then
    # perhaps you'd want to use gitea to get the repo or git clone
    # directly with depth 1.
    # TODO Research: Do 'Read on Web' format resources have an associated git
    # repo if they don't have a sibling 'Download' format URL? I
    # looked at "erk-x-erakor" for intance and there one can see there
    # is no symmetry between the 'Read on Web' and 'Download' format
    # URLs that can be extrapolated to other language resources;
    # perhaps it can to a subset, but the relationship between the
    # 'Read on Web' and 'Download' format URLs seems to vary by
    # language.
    def lookup(self, resource: Dict) -> List[Optional[str]]:
        """ Given a resource, comprised of language code, e.g., 'wum',
        a resource type, e.g., 'tn', and an optional resource code,
        e.g., 'gen', return URLs for resource. """

        # logger.info('resource["resource_code"]: {}'.format(resource["resource_code"]))
        resource["resource_code"] = (
            None if not resource["resource_code"] else resource["resource_code"]
        )
        # logger.info('resource["resource_code"]: {}'.format(resource["resource_code"]))

        assert resource["lang_code"] is not None, "lang_code is required"
        assert resource["resource_type"] is not None, "resource_type is required"
        # assert resource["resource_code"] is None or (
        #     resource["resource_code"] is not None
        #     and not resource["resource_code"].strip()
        # ), "resource_code can't be an empty string"

        urls: List[Optional[str]] = []

        # NOTE format='Download' can point to reg, ulb, udb git repos.
        # format='usfm' points to single USFM files.
        if (
            resource["resource_code"] is not None
        ):  # User has likely specified a book of the bible, try first to get the resource from a git repo.
            # logger.debug(
            #     "resource[resource_code]: {}".format(resource["resource_code"])
            # )
            if resource["resource_type"] in ["reg", "ulb", "udb"]:
                jsonpath_str = get_resource_download_format_jsonpath().format(
                    resource["lang_code"],
                    resource["resource_type"],
                    resource["resource_code"],
                )
                urls = self._lookup(jsonpath_str)
                if urls is not None and len(urls) > 0:
                    # Get the portion of the query string that gives
                    # the repo URL
                    urls = [self._parse_repo_url_from_json_url(urls[0])]

            if (urls is not None and len(urls) == 0) or resource[
                "resource_type"
            ] not in [
                "reg",
                "ulb",
                "udb",
            ]:  # Resource not found, next try to get from download CDN/URL.
                # NOTE Many languages have a git repo found by
                # format='Download' that is parallel to the
                # individual, per book, USFM files and in that case
                # the git repo should be preferred. But there is at
                # least one language, code='ar', that has only single
                # USFM files. In that particular language all the
                # individual USFM files per book can also be found in
                # a zip file,
                # $[?coee='ar'].contents[?code='nav'].links[format='zip'],
                # which also contains the manifest.yaml file.
                # That language is the only one with a
                # contents[?code='nav'].
                # Another, yet different, example is the case of
                # $[?code="avd"] which has format="usfm" without
                # having a zip containing USFM files at the same level.
                jsonpath_str = get_individual_usfm_url_jsonpath().format(
                    resource["lang_code"],
                    resource["resource_type"],
                    resource["resource_code"],
                )
                urls = self._lookup(jsonpath_str)
        else:  # User has not specified a resource_code and thus has
            # not specified a particular book of the bible.
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
        # Store the jsonpath that was used as it will be used to
        # determine how to acquire the resource, e.g., if a jsonpath
        # was used that points to a git repo then the git client will
        # be used otherwise we download from a CDN.
        resource.update({"resource_jsonpath": jsonpath_str})

        return urls

    def lang_codes(self) -> List[Optional[str]]:
        """ Convenience method that can be called from UI to get the
        set of all language codes available through API. Presumably
        this could be called to populate a dropdown menu. """
        # return list(sorted(set(self._lookup("$[*].code"))))
        self._get_data()
        codes: List[str] = []
        for lang in self.json_data:
            codes.append(lang["code"])
        # return self._lookup("$[*].code")
        return codes

    # NOTE We really would only need lang_codes and
    # lang_codes_and_names, especially since there are a different
    # number of codes than names, so they should not be decoupled when
    # names are desired. Thus, commented out for now.
    # def lang_names(self) -> List[Optional[str]]:
    #     # FIXME This method is SLOW. Language codes and names are
    #     # not in a one to one relationship and so we have to
    #     # specifically lookup the name for the code which means we
    #     # have to do a jsonpath lookup for every language code.
    #     # Massive use of the heap plus jsonpath processing time.
    #     """ Convenience method that can be called from UI to get the
    #     set of all language names available through API. Presumably
    #     this could be called to populate a dropdown menu. """
    #     codes: List[Optional[str]] = self.lang_codes()
    #     names: List[str] = []
    #     for code in codes:
    #         name_arr = self._lookup("$[?code='{}'].name".format(code))
    #         if name_arr is not None and len(name_arr):
    #             names.append(name_arr[0])
    #         else:
    #             names.append("Name not provided")
    #     return names

    def lang_codes_and_names(self) -> List[Tuple[str, str]]:
        """ Convenience method that can be called from UI to get the
        set of all language code, name tuples available through API.
        Presumably this could be called to populate a dropdown menu.
        """
        self._get_data()
        codes_and_names: List[Tuple[str, str]] = []
        # Using jsonpath in a loop here was prohibitively slow so we
        # use the dictionary in this case.
        for d in self.json_data:
            codes_and_names.append((d["code"], d["name"]))
        return codes_and_names

    def resource_types(self) -> List[Optional[str]]:
        """ Convenience method that can be called, e.g., from the UI,
        to get the set of all resource types. """
        return self._lookup("$[*].contents[*].code")

    def resource_codes(self) -> List[Optional[str]]:
        """ Convenience method that can be called, e.g., from the UI,
        to get the set of all resource codes. """
        return self._lookup("$[*].contents[*].subcontents[*].code")


# class ResourceAcquirer():
#     """ A class that let's you download the resource. """
#     # """ Abstract base class that formalizes resource acquisition. Currently
#     # resources have URLs that point to either a git repository or to a
#     # CDN location. """

#     # @abc.abstractmethod
#     def acquire(self, resource: Dict) -> List[Optional[str]]:


class ResourceAcquirer(object):
    def __init__(
        self,
        resource: Dict,
        working_dir: Optional[str] = "./",  # This is in /tools in the Docker container
        logger: logging.Logger = None,
        pp: pprint.PrettyPrinter = None,
    ) -> None:
        self.working_dir = working_dir
        self.resource = resource
        self.logger = logger
        self.pp = pp

    def acquire(self) -> None:
        pass


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
        "Language {}, resource_type: {}, resource_code: {}, resource_jsonpath: {}, values: {}".format(
            resource["lang_code"],
            resource["resource_type"],
            resource["resource_code"],
            resource["resource_jsonpath"],
            values,
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
