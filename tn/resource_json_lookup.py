from ..general_tools.file_utils import load_json_object
import tempfile
from jsonpath_rw import jsonpath
from jsonpath_rw_ext import parse

# for calling extended methods
import jsonpath_rw_ext as jp


class ResourceJsonLookup(object):
    def __init__(self, working_dir):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.pp = pprint.PrettyPrinter(indent=4)

        if not self.working_dir:
            self.working_dir = tempfile.mkdtemp(prefix="json_")
        # if not self.output_dir:
        #     self.output_dir = self.working_dir

        self.logger.debug("TEMP JSON DIR IS {0}".format(self.working_dir))

        # from TnConverter class - just duplicating here for now
        # self.tn_dir = os.path.join(self.working_dir, "{0}_tn".format(lang_code))
        # self.tw_dir = os.path.join(self.working_dir, "{0}_tw".format(lang_code))
        # self.tq_dir = os.path.join(self.working_dir, "{0}_tq".format(lang_code))
        # self.ta_dir = os.path.join(self.working_dir, "{0}_ta".format(lang_code))
        # self.udb_dir = os.path.join(self.working_dir, "{0}_udb".format(lang_code))
        # self.ulb_dir = os.path.join(self.working_dir, "{0}_ulb".format(lang_code))

        self.json_file_url = "http://bibleineverylanguage.org/wp-content/themes/bb-theme-child/data/translations.json"

        self.json_file = os.path.join(
            self.working_dir, json_file_url.rpartition(os.path.sep)[2]
        )

        # Download json file
        try:
            self.logger.debug("Downloading {}...".format(json_file_url))
            download_file(self.json_file_url, self.json_file)
        finally:
            self.logger.debug("finished.")

        # Load json file
        try:
            self.logger.debug("Loading json file {}...".format(filename))
            self.json_data = load_json_object(self.json_file)
        finally:
            self.logger.debug("finished.")

    def lookup_download_url(self, lang):
        """ Return json dict object for download url for lang. """
        return jp.match1(
            "$[?name='"
            + lang
            + "'].contents[*].subcontents[*].links[?format='Download'].url",
            json_data,
        )


# TODO Maybe we should create a class for the web service that will front
# this lookup service.


# def main():
#     """ Test driver. """

#     lookup_svc = ResourceJsonLookup(working_dir=None)
#     lang = "Abadi"
#     print("Language data {}".format(lookup_svc.lookup_download_url(lang)))


# if __name__ == "__main__":
#     main()

# Phrases from repl:

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
