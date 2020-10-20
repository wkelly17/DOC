#
#  Copyright (c) 2017 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wycliffeassociates.org>

"""
XFIXME This script exports tN into HTML format from DCS and generates a PDF from the HTML
"""

from typing import Any, Dict, List, Optional, Union
import os
import sys
import re
import pprint
import logging
import argparse
import tempfile
import shutil
import datetime
import subprocess
import csv
from glob import glob
import yaml


import markdown  # type: ignore

import bs4  # type: ignore
from usfm_tools.transform import UsfmTransform  # type: ignore

# Handle running in container or as standalone script
try:
    from file_utils import write_file, read_file, unzip, load_yaml_object, load_json_object  # type: ignore
    from bible_books import BOOK_NUMBERS, BOOK_NAMES  # type: ignore
    from resource_lookup import ResourceJsonLookup
    from config import (
        get_working_dir,
        get_output_dir,
        get_logging_config_file_path,
        get_icon_url,
        get_markdown_resource_types,
        get_tex_format_location,
        get_tex_template_location,
    )
    from resource_utils import (
        resource_has_markdown_files,
        # files_from_url,
    )
    from resource import (
        Resource,
        USFMResource,
        TNResource,
        TQResource,
        TAResource,
        TWResource,
        ResourceFactory,
    )
except:
    from .file_utils import write_file, read_file, unzip, load_yaml_object, load_json_object  # type: ignore
    from .bible_books import BOOK_NUMBERS, BOOK_NAMES  # type: ignore
    from .resource_lookup import ResourceJsonLookup
    from .config import (
        get_working_dir,
        get_output_dir,
        get_logging_config_file_path,
        get_icon_url,
        get_markdown_resource_types,
        get_tex_format_location,
        get_tex_template_location,
    )
    from .resource_utils import (
        resource_has_markdown_files,
        # files_from_url,
    )
    from .resource import (
        Resource,
        USFMResource,
        TNResource,
        TQResource,
        TAResource,
        TWResource,
        ResourceFactory,
    )


with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


class DocumentGenerator(object):
    def __init__(
        self,
        resources: Dict,
        working_dir: str = get_working_dir(),
        output_dir: str = get_output_dir(),
    ) -> None:
        """
        :param resources:
        :param working_dir:
        :param output_dir:
        """
        self.working_dir = working_dir
        self.output_dir = output_dir
        # FIXME This next instance var may go away. Resource subclass
        # instances keep a reference to a ResourceJsonLookup instance.
        # Guiding principle: we don't want a bunch of these on the
        # heap unnecessarily so we'll either make ResourceJsonLookup
        # implement the singleton pattern or else we will pass in the
        # same instance reference to each resource object that is
        # created.
        # NOTE The lookup service could be (re)-implemented as a
        # singleton (or Global Object at module level for
        # Pythonicness) if desired. For now, just passing it to each
        # Resource instance at object creation.
        # FIXME self.lookup_svc will become a local var lookup_svc
        self.lookup_svc: ResourceJsonLookup = ResourceJsonLookup(self.working_dir)

        # Let's see the dictionary that was passed in for
        # informational purposes.
        logger.debug("resources: {}".format(resources))

        # FIXME Is this even necessary? I don't think that we will
        # design this to not provide a working_dir.
        if not self.working_dir:
            self.working_dir = tempfile.mkdtemp(prefix="tn-")
        if not self.output_dir:
            self.output_dir = self.working_dir

        logger.debug("Working dir is {0}".format(self.working_dir))

        # NOTE Uniquely identifies a document request that has this
        # order of resource requests where a resource request is
        # identified by lang_code, resource_type, and resource_code
        # concatenated by hyphens. This serves as a cache lookup key
        # also so that document requests having the same key can skip
        # processing and simply return the end result document if it
        # still exists.
        self._document_request_key: str = ""

        # TODO To be production worthy, we need to make this resilient
        # to errors when creating Resource instances.
        self._resources: List[Resource] = []
        for resource in resources:
            # FIXME self.lookup_svc will become a local var: lookup_svc
            self._resources.append(
                ResourceFactory(
                    self.working_dir, self.output_dir, self.lookup_svc, resource
                )
            )
            self._document_request_key += "-".join(
                [
                    resource["lang_code"],
                    resource["resource_type"],
                    resource["resource_code"],
                ]
            )

        logger.debug(
            "self._document_request_key: {}".format(self._document_request_key)
        )

        # NOTE Not all languages have tn, tw, tq, tq, udb, ulb. Some
        # have only a subset of those resources. Presumably the web UI
        # will present only valid choices per language.
        # FIXME resources could serve as a cache as well. Perhaps the
        # cache key could be an md5 hash of the resource's key/value
        # pairs. Subsequent lookups would compare a hash of an
        # incoming resource request's key/value pairs and if it was
        # already in the resources dictionary then the generation of
        # the document could be skipped (after first checking the
        # final document result was still available - container
        # redeploys could destroy cache) and return the URL to the
        # previously generated document right away.
        # FIXME resources is the incoming resource request dictionary
        # and so is per request, per instance. The cache, however,
        # would need to persist beyond each request. Perhaps it should
        # be maintained as a class variable?

    def run(self) -> None:
        self._get_unfoldingword_icon()

        # Get the resources files
        for resource in self._resources:
            resource.find_location()
            resource.get_files()

        # Initialize the resources and generate their content
        for resource in self._resources:
            resource.initialize_properties()
            resource.get_content()

        # FIXME
        if not os.path.isfile(
            os.path.join(self.output_dir, "{}.pdf".format(self._document_request_key))
            # os.path.join(self.output_dir, "{}.pdf".format(self.filename_base))
        ):
            logger.info("Generating PDF...")
            # FIXME Assemble all the HTML into one HTML and then
            # convert that HTML into a PDF.
            logger.info(
                "Yet to be done: concatenate all the HTML files that were generated into one HTML and then convert it to PDF."
            )
            # self.convert_html2pdf(resource)

        # self.tw_refs_by_verse = index_tw_refs_by_verse(
        #     read_csv_as_dicts(os.path.join(self.working_dir, "tw_refs.csv"))
        # )  # FIXME Per resource, not per DocumentGenerator instance.

        # FIXME This might have to be subsumed into resource.get_contents()
        # USFM stuff
        # if (
        #     resource._resource_file_format
        #     # "resource_file_format" in resource
        #     and resource._resource_file_format == "usfm"
        # ):
        #     # Create HTML from Markdown
        #     # Convert HTML to PDF
        #     if not os.path.isfile(
        #         os.path.join(
        #             self.output_dir, "{}.html".format(resource._filename_base)
        #         )
        #     ):

        #         # if not os.path.isfile(
        #         #     os.path.join(self.output_dir, "{0}.html".format(self.filename_base))
        #         # ):
        #         # FIXME Only get USFM if we've resource has
        #         # resource_type of USFM or if resource_file_format
        #         # is git.
        #         # FIXME We will have to decide how to handle git
        #         # containing USFM vs USFM file only in a Resource
        #         # subclass instance.
        #         # Get USFM chunks
        #         # if resource._resource_file_format in ["git", "usfm"]:
        #         #     logger.info("Getting USFM chunks...")
        #         #     # resource.update({"usfm_chunks": self.get_usfm_chunks(resource)})
        #         #     resource._usfm_chunks = resource._get_usfm_chunks()

        #         # FIXME This assumes that there will be a markdown
        #         # resource. Under the new document request system
        #         # it is possible that a user will not request any
        #         # resources that have markdown files, e.g., if the
        #         # user only requests USFM.
        #         # logger.debug(
        #         #     "resource has markdown files: {}".format(
        #         #         resource_has_markdown_files(resource)
        #         #     )
        #         # )
        #         if resource_has_markdown_files(resource) and not os.path.isfile(
        #             os.path.join(
        #                 self.output_dir, "{}.md".format(resource._filename_base)
        #             )
        #         ):
        #             # if not os.path.isfile(
        #             #     os.path.join(
        #             #         self.output_dir, "{0}.md".format(self.filename_base)
        #             #     )
        #             # ):
        #             logger.info("Processing Markdown...")
        #             self.preprocess_markdown()
        #             logger.info("Converting MD to HTML...")
        #             self.convert_md2html(resource)
        #     if not os.path.isfile(
        #         os.path.join(
        #             self.output_dir, "{}.pdf".format(resource._filename_base)
        #         )
        #         # os.path.join(self.output_dir, "{}.pdf".format(self.filename_base))
        #     ):
        #         logger.info("Generating PDF...")
        #         self.convert_html2pdf(resource)

        # # TODO When we acquire resources that are single USFM
        # # files, they do not have an associated manifest file and
        # # therefore do not have associated projects in the sense
        # # expected below. Thus, we need to detect the case when
        # # the resource_file_format is USFM and handle it
        # # differently than below.
        # projects: List[Dict[Any, Any]] = self.get_book_projects(resource)
        # logger.debug("book projects: {}".format(projects))
        # for p in projects:
        #     project: Dict[Any, Any] = p
        #     resource.update({"book_id": p["identifier"]})
        #     # self.book_id = p["identifier"]
        #     resource.update(
        #         {"book_title": p["title"].replace(" translationNotes", "")}
        #     )
        #     # self.book_title = p["title"].replace(" translationNotes", "")
        #     resource.update({"book_number": BOOK_NUMBERS[resource["book_id"]]})
        #     # self.book_number = BOOK_NUMBERS[self.book_id]
        #     # TODO This likely needs to change because of how we
        #     # build resource_dir
        #     resource.update(
        #         {
        #             "filename_base": "{}_{}_{}-{}_v{}".format(
        #                 resource["lang_code"],
        #                 resource["resource_type"],
        #                 resource["book_number"].zfill(2),
        #                 resource["book_id"].upper(),
        #                 resource["version"],
        #             )
        #         }
        #     )
        #     # self.filename_base = "{0}_tn_{1}-{2}_v{3}".format(
        #     #     self.lang_code,
        #     #     self.book_number.zfill(2),
        #     #     self.book_id.upper(),
        #     #     self.version,
        #     # )
        #     resource.update({"rc_references": {}})
        #     # self.rc_references = {}
        #     resource.update({"my_rcs": []})
        #     # self.my_rcs = []
        #     logger.debug(
        #         "Creating {} for {} ({}-{})...".format(
        #             resource["resource_type"],
        #             resource["book_title"],
        #             resource["book_number"],
        #             resource["book_id"].upper(),
        #         )
        #     )
        #     # self.logger.debug(
        #     #     "Creating tN for {0} ({1}-{2})...".format(
        #     #         self.book_title, self.book_number, self.book_id.upper()
        #     #     )
        #     # )
        #     if not os.path.isfile(
        #         os.path.join(
        #             self.output_dir, "{}.html".format(resource["filename_base"])
        #         )
        #     ):

        #         # if not os.path.isfile(
        #         #     os.path.join(self.output_dir, "{0}.html".format(self.filename_base))
        #         # ):

        #         if resource["resource_file_format"] in ["git", "usfm"]:
        #             logger.debug("Getting USFM chunks 2...")
        #             resource.update({"usfm_chunks": self.get_usfm_chunks(resource)})
        #             # self.usfm_chunks = self.get_usfm_chunks()

        #         if not os.path.isfile(
        #             os.path.join(
        #                 self.output_dir, "{}.md".format(resource["filename_base"])
        #             )
        #         ):
        #             # if not os.path.isfile(
        #             #     os.path.join(
        #             #         self.output_dir, "{0}.md".format(self.filename_base)
        #             #     )
        #             # ):
        #             logger.debug("Processing Markdown...")
        #             self.preprocess_markdown()
        #             logger.debug("Converting MD to HTML...")
        #             self.convert_md2html(resource)
        #     if not os.path.isfile(
        #         os.path.join(
        #             self.output_dir, "{}.pdf".format(resource["filename_base"])
        #         )
        #         # os.path.join(self.output_dir, "{}.pdf".format(self.filename_base))
        #     ):
        #         logger.debug("Generating PDF...")
        #         self.convert_html2pdf(resource)
        # logger.debug("self._bad_links: {}".format(self._bad_links))
        # self.pp.plogger.debug(self.bad_links)

    # # FIXME Move to the appropriate place in resource.py
    # # TODO Handle manifest.yaml, manifest.txt, and manifest.json
    # # formats - they each have different structure and keys.
    # def get_book_projects(self, resource: Dict) -> List[Dict[Any, Any]]:
    #     """ Return the sorted list of projects that are found in the
    #     manifest file for the resource. """

    #     logger.info("start...")
    #     projects: List[Dict[Any, Any]] = []
    #     # TODO
    #     # if resource["resource_manifest_type"] == "yaml" and (
    #     #     "manifest" not in resource or "projects" not in resouce["manifest"]
    #     # ):
    #     #     return projects
    #     # if resource["resource_manifest_type"] == "txt" and ("manifest" not in resource or "projects" not in resouce["manifest"]):
    #     if (
    #         "manifest" not in resource  # and not resource["manifest"]
    #         # not self.manifest
    #         or "projects" not in resource["manifest"]
    #         # or "projects" not in self.manifest
    #         # or not resource["manifest"]["projects"]
    #         # or not self.manifest["projects"]
    #     ):

    #         logger.info("empty projects check is true...")
    #         return projects
    #     for p in resource["manifest"]["projects"]:
    #         # for p in self.manifest["projects"]:
    #         # NOTE You can have a manifest.yaml file and not have a
    #         # resource_code specified, e.g., lang_code='as',
    #         # resource_type='tn', resource_code=''
    #         if (
    #             resource["resource_code"] is not None
    #             and p["identifier"] in resource["resource_code"]
    #         ):
    #             # if not self.books or p["identifier"] in self.books:
    #             if not p["sort"]:
    #                 p["sort"] = BOOK_NUMBERS[p["identifier"]]
    #             projects.append(p)
    #     return sorted(projects, key=lambda k: k["sort"])

    def _get_unfoldingword_icon(self) -> None:
        """ Get Unfolding Word's icon for display in generated PDF. """

        if not os.path.isfile(os.path.join(self.working_dir, "icon-tn.png")):
            command = "curl -o {}/icon-tn.png {}".format(
                self.working_dir, get_icon_url()
            )
            subprocess.call(command, shell=True)

    def preprocess_markdown(self) -> None:
        # FIXME We'll want get_t*_markdown to do the special things it
        # needs to do, but we'll want to use a resource in
        # resources loop in which to dispatch.
        # tn_md = ""
        # tq_md = ""
        # tw_md = ""
        # ta_md = ""
        md: str = ""
        for resource in self._resources:
            # NOTE This is possible approach, but we might get sent a
            # resource_type that is not one of tn, tq, tw, ta, e.g.,
            # obs_tn (unless of course we decide not to support
            # resources like obs which are usually PDF).
            # NOTE This is a yuck bit of conditional for now. WIP.
            # if resource["resource_type"] in ["tn", "tn-wa"]:
            #     tn_md = self.get_tn_markdown(resource)
            # elif resource["resource_type"] in ["tq", "tq-wa"]:
            #     tq_md = self.get_tq_markdown(resource)
            # elif resource["resource_type"] in ["tw", "tw-wa"]:
            #     tw_md = self.get_tw_markdown(resource)
            # elif resource["resource_type"] in ["ta", "ta-wa"]:
            #     ta_md = self.get_ta_markdown(resource)
            # FIXME The following happens not per resource, but per
            # document after all the documents resources have been
            # initialized fully, i.e., after resource.get_content()
            # md = "\n\n".join([tn_md, tq_md, tw_md, ta_md])
            # md = "\n\n".join(resource._content)
            # md = resource.replace_rc_links(md)
            # md = fix_links(md)
            md += "\n\n{}".format(resource._content)
            logger.debug(
                "About to write markdown to {}/{}".format(
                    self.output_dir, resource._filename_base
                )
            )
            write_file(
                os.path.join(self.output_dir, "{}.md".format(resource._filename_base)),
                md
                # os.path.join(self.output_dir, "{}.md".format(self.filename_base)), md
            )

    # FIXME Should this live elsewhere?
    # def replace_rc_links(self, text: str, resource) -> str:
    #     # Change [[rc://...]] rc links, e.g. [[rc://en/tw/help/bible/kt/word]] => [God's Word](#tw-kt-word)
    #     rep = dict(
    #         (
    #             re.escape("[[{0}]]".format(rc)),
    #             "[{0}]({1})".format(
    #                 # TODO update the dict mayube with this:
    #                 # resource.update({"resource_data":
    #                 # resource["resource_data"][rc]["title"].strip()})
    #                 resource._resource_data[rc]["title"].strip(),
    #                 resource._resource_data[rc]["link"],
    #             ),
    #         )
    #         for rc in self._my_rcs
    #     )
    #     pattern = re.compile("|".join(list(rep.keys())))
    #     text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    #     # Change ].(rc://...) rc links, e.g. [Click here](rc://en/tw/help/bible/kt/word) => [Click here](#tw-kt-word)
    #     rep = dict(
    #         (re.escape("]({0})".format(rc)), "]({0})".format(info["link"]))
    #         for rc, info in self._resource_data.items()
    #     )
    #     pattern = re.compile("|".join(list(rep.keys())))
    #     text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    #     # Change rc://... rc links, e.g. rc://en/tw/help/bible/kt/word => [God's](#tw-kt-word)
    #     rep = dict(
    #         (re.escape(rc), "[{0}]({1})".format(info["title"], info["link"]))
    #         # for rc, info in resource["resource_data"].items()
    #         for rc, info in self._resource_data.items()
    #     )
    #     pattern = re.compile("|".join(list(rep.keys())))
    #     text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    #     return text

    # # FIXME I think this needs to happen per document not per resource.
    # def convert_md2html(self, resource: Dict) -> None:
    #     # logger.debug(
    #     #     "About to call markdown.markdown, resource['resource_dir']: {}, resource['filename_base']: {}, resource['resource_filename']: {}".format(
    #     #         resource["resource_dir"],
    #     #         resource["filename_base"],
    #     #         resource["resource_filename"],
    #     #     )
    #     # )
    #     html = markdown.markdown(
    #         read_file(
    #             # os.path.join(
    #             #     self.output_dir,
    #             "{}/{}.md".format(
    #                 resource["resource_dir"],
    #                 resource["resource_filename"],
    #                 # resource["resource_dir"], resource["filename_base"]
    #                 #     ),
    #             ),
    #             # os.path.join(self.output_dir, "{}.md".format(self.filename_base)),
    #             "utf-8",
    #         )
    #     )
    #     html = self.replace_bible_links(html, resource)
    #     write_file(
    #         os.path.join(self.output_dir, "{}.html".format(resource["filename_base"])),
    #         html
    #         # os.path.join(self.output_dir, "{0}.html".format(self.filename_base)), html
    #     )

    # def get_chunk_html(
    #     self, resource_str: str, chapter: str, verse: str, resource: Dict
    # ) -> str:
    #     # logger.debug("html: {0}-{3}-{1}-{2}".format(resource, chapter, verse, self.book_id))
    #     path = tempfile.mkdtemp(
    #         dir=self.working_dir,
    #         prefix="usfm-{}-{}-{}-{}-{}_".format(
    #             resource["lang_code"],
    #             resource_str,
    #             resource["book_id"],
    #             chapter,
    #             verse
    #             # self.lang_code, resource, self.book_id, chapter, verse
    #         ),
    #     )
    #     filename_base = "{}-{}-{}-{}".format(
    #         resource_str, resource["book_id"], chapter, verse
    #     )
    #     # filename_base = "{0}-{1}-{2}-{3}".format(resource, self.book_id, chapter, verse)
    #     try:
    #         chunk = resource["usfm_chunks"][resource_str][chapter][verse]["usfm"]
    #         # chunk = self.usfm_chunks[resource_str][chapter][verse]["usfm"]
    #     except KeyError:
    #         chunk = ""
    #     usfm = resource["usfm_chunks"][resource_str]["header"]
    #     # usfm = self.usfm_chunks[resource_str]["header"]
    #     if "\\c" not in chunk:
    #         usfm += "\n\n\\c {0}\n".format(chapter)
    #     usfm += chunk
    #     write_file(os.path.join(path, filename_base + ".usfm"), usfm)
    #     UsfmTransform.buildSingleHtml(path, path, filename_base)
    #     html = read_file(os.path.join(path, filename_base + ".html"))
    #     shutil.rmtree(path, ignore_errors=True)
    #     soup = bs4.BeautifulSoup(html, "html.parser")
    #     header = soup.find("h1")
    #     if header:
    #         header.decompose()
    #     chapter_element: Union[
    #         bs4.element.Tag, bs4.element.NavigableString
    #     ] = soup.find("h2")
    #     if chapter_element:
    #         chapter_element.decompose()
    #     html = "".join(["%s" % x for x in soup.body.contents])
    #     return html

    def convert_html2pdf(self, resource) -> None:
        now = datetime.datetime.now()
        revision_date = "{}-{}-{}".format(now.year, now.month, now.day)
        command = """pandoc \
--pdf-engine="xelatex" \
--template={8} \
--toc \
--toc-depth=2 \
-V documentclass="scrartcl" \
-V classoption="oneside" \
-V geometry='hmargin=2cm' \
-V geometry='vmargin=3cm' \
-V title="{0}" \
-V subtitle="Translation Notes" \
-V logo="{4}/icon-tn.png" \
-V date="{1}" \
-V revision_date="{6}" \
-V version="{2}" \
-V mainfont="Raleway" \
-V sansfont="Raleway" \
-V fontsize="13pt" \
-V urlcolor="Bittersweet" \
-V linkcolor="Bittersweet" \
-H {7} \
-o "{3}/{5}.pdf" \
"{3}/{5}.html"
""".format(
            resource._book_title,
            # self.book_title,
            # resource["issued"] if "issued" in resource else "",
            resource._issued if resource._issued else "",
            # resource["version"] if "version" in resource else "",
            resource._version if resource._version else "",
            self.output_dir,
            self.working_dir,
            # resource["resource_filepath"],
            # resource["filename_base"],
            resource._filename_base,
            revision_date,
            get_tex_format_location(),
            get_tex_template_location(),
        )
        logger.debug(command)
        subprocess.call(command, shell=True)


# # FIXME Such a cluster
# def fix_links(text):
#     rep = {}

#     def replace_tn_with_door43_link(match):
#         book = match.group(1)
#         chapter = match.group(2)
#         verse = match.group(3)
#         if book in BOOK_NUMBERS:
#             book_num = BOOK_NUMBERS[book]
#         else:
#             return None
#         if int(book_num) > 40:
#             anchor_book_num = str(int(book_num) - 1)
#         else:
#             anchor_book_num = book_num
#         url = "https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/{}-{}.html#{}-ch-{}-v-{}".format(
#             book_num.zfill(2),
#             book.upper(),
#             anchor_book_num.zfill(3),
#             chapter.zfill(3),
#             verse.zfill(3),
#         )
#         return url

#     def replace_obs_with_door43_link(match):
#         url = "https://live.door43.org/u/Door43/en_obs/b9c4f076ff/{}.html".format(
#             match.group(1)
#         )
#         return url

#     # convert OBS links: rc://en/tn/help/obs/15/07 => https://live.door43.org/u/Door43/en_obs/b9c4f076ff/15.html
#     rep[r"rc://[^/]+/tn/help/obs/(\d+)/(\d+)"] = replace_obs_with_door43_link

#     # convert tN links (NT books use USFM numbering in HTML file name, but standard book numbering in the anchor):
#     # rc://en/tn/help/rev/15/07 => https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/67-REV.html#066-ch-015-v-007
#     rep[r"rc://[^/]+/tn/help/(?!obs)([^/]+)/(\d+)/(\d+)"] = replace_tn_with_door43_link

#     # convert RC links, e.g. rc://en/tn/help/1sa/16/02 => https://git.door43.org/Door43/en_tn/1sa/16/02.md
#     rep[
#         r"rc://([^/]+)/(?!tn)([^/]+)/([^/]+)/([^\s\)\]\n$]+)"
#     ] = r"https://git.door43.org/Door43/\1_\2/src/master/\4.md"

#     # convert URLs to links if not already
#     rep[
#         r'([^"\(])((http|https|ftp)://[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
#     ] = r"\1[\2](\2)"

#     # URLS wth just www at the start, no http
#     rep[
#         r'([^A-Za-z0-9"\(\/])(www\.[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
#     ] = r"\1[\2](http://\2.md)"

#     for pattern, repl in rep.items():
#         text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
#     return text


def read_csv_as_dicts(filename: str) -> List:
    """ Returns a list of dicts, each containing the contents of a row of
        the given csv file. The CSV file is assumed to have a header row with
        the field names. """
    rows = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def index_tw_refs_by_verse(tw_refs: List) -> dict:
    """ Returns a dictionary of books -> chapters -> verses, where each
        verse is a list of rows for that verse. """
    tw_refs_by_verse: dict = {}
    for tw_ref in tw_refs:
        book = tw_ref["Book"]
        chapter = tw_ref["Chapter"]
        verse = tw_ref["Verse"]
        if book not in tw_refs_by_verse:
            tw_refs_by_verse[book] = {}
        if chapter not in tw_refs_by_verse[book]:
            tw_refs_by_verse[book][chapter] = {}
        if verse not in tw_refs_by_verse[book][chapter]:
            tw_refs_by_verse[book][chapter][verse] = []

        # # Check for duplicates -- not sure if we need this yet
        # folder = tw_ref["Dir"]
        # reference = tw_ref["Ref"]
        # found_duplicate = False
        # for existing_tw_ref in tw_refs_by_verse[book][chapter][verse]:
        #     if existing_tw_ref["Dir"] == folder and existing_tw_ref["Ref"] == reference:
        #         logger.debug("Found duplicate: ", book, chapter, verse, folder, reference)
        #         found_duplicate = True
        #         break
        # if found_duplicate:
        #     continue

        tw_refs_by_verse[book][chapter][verse].append(tw_ref)
    return tw_refs_by_verse
