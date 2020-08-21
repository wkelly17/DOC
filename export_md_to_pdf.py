#
#  Copyright (c) 2017 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wycliffeassociates.org>

"""
This script exports tN into HTML format from DCS and generates a PDF from the HTML
"""

from typing import Optional, List
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

import markdown  # type: ignore

import bs4  # type: ignore
from usfm_tools.transform import UsfmTransform  # type: ignore

from file_utils import write_file, read_file, unzip, load_yaml_object  # type: ignore
from url_utils import download_file  # type: ignore
from bible_books import BOOK_NUMBERS  # type: ignore
from resource_lookup import ResourceJsonLookup


class TnConverter(object):
    def __init__(
        self,
        ta_tag=None,
        tn_tag=None,
        tq_tag=None,
        tw_tag=None,
        udb_tag=None,
        ulb_tag=None,
        working_dir=None,
        output_dir=None,
        lang_code=None,
        books=None,
    ) -> None:
        """
        :param ta_tag:
        :param tn_tag:
        :param tq_tag:
        :param tw_tag:
        :param udb_tag:
        :param ulb_tag:
        :param working_dir:
        :param output_dir:
        :param lang_code:
        :param books:
        """
        self.ta_tag = ta_tag
        self.tn_tag = tn_tag
        self.tq_tag = tq_tag
        self.tw_tag = tw_tag
        self.udb_tag = udb_tag
        self.ulb_tag = ulb_tag
        self.working_dir = working_dir
        self.output_dir = output_dir
        self.lang_code = lang_code
        self.books = books

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.pp = pprint.PrettyPrinter(indent=4)

        if not self.working_dir:
            self.working_dir = tempfile.mkdtemp(prefix="tn-")
        if not self.output_dir:
            self.output_dir = self.working_dir

        self.logger.debug("TEMP DIR IS {0}".format(self.working_dir))
        self.tn_dir = os.path.join(self.working_dir, "{0}_tn".format(lang_code))
        self.tw_dir = os.path.join(self.working_dir, "{0}_tw".format(lang_code))
        self.tq_dir = os.path.join(self.working_dir, "{0}_tq".format(lang_code))
        self.ta_dir = os.path.join(self.working_dir, "{0}_ta".format(lang_code))
        self.udb_dir = os.path.join(self.working_dir, "{0}_udb".format(lang_code))
        self.ulb_dir = os.path.join(self.working_dir, "{0}_ulb".format(lang_code))

        self.manifest = None

        self.book_id = None
        self.book_title = None
        self.book_number = None
        self.project = None
        self.tn_text = ""
        self.tw_text = ""
        self.tq_text = ""
        self.ta_text = ""
        self.my_rcs = []
        self.rc_references = {}
        self.resource_data = {}
        self.bad_links = {}
        self.usfm_chunks = {}
        self.version = None
        self.issued = None
        self.filename_base = None
        self.tw_refs_by_verse = index_tw_refs_by_verse(
            read_csv_as_dicts(os.path.join(self.working_dir, "tw_refs.csv"))
        )

    def run(self) -> None:
        self.setup_resource_files()
        self.manifest = load_yaml_object(os.path.join(self.tn_dir, "manifest.yaml"))
        self.version = self.manifest["dublin_core"]["version"]
        self.issued = self.manifest["dublin_core"]["issued"]
        projects = self.get_book_projects()
        for p in projects:
            self.project = p
            self.book_id = p["identifier"]
            self.book_title = p["title"].replace(" translationNotes", "")
            self.book_number = BOOK_NUMBERS[self.book_id]
            self.filename_base = "{0}_tn_{1}-{2}_v{3}".format(
                self.lang_code,
                self.book_number.zfill(2),
                self.book_id.upper(),
                self.version,
            )
            self.rc_references = {}
            self.my_rcs = []
            self.logger.info(
                "Creating tN for {0} ({1}-{2})...".format(
                    self.book_title, self.book_number, self.book_id.upper()
                )
            )

            if not os.path.isfile(
                os.path.join(self.output_dir, "{0}.html".format(self.filename_base))
            ):
                print("Getting USFM chunks...")
                self.usfm_chunks = self.get_usfm_chunks()
                if not os.path.isfile(
                    os.path.join(self.output_dir, "{0}.md".format(self.filename_base))
                ):
                    print("Processing Markdown...")
                    self.preprocess_markdown()
                print("Converting MD to HTML...")
                self.convert_md2html()
            if not os.path.isfile(
                os.path.join(self.output_dir, "{0}.pdf".format(self.filename_base))
            ):
                print("Generating PDF...")
                self.convert_html2pdf()
        self.pp.pprint(self.bad_links)

    def get_book_projects(self) -> List:
        projects = []
        if (
            not self.manifest
            or "projects" not in self.manifest
            or not self.manifest["projects"]
        ):
            return projects
        for p in self.manifest["projects"]:
            if not self.books or p["identifier"] in self.books:
                if not p["sort"]:
                    p["sort"] = BOOK_NUMBERS[p["identifier"]]
                projects.append(p)
        return sorted(projects, key=lambda k: k["sort"])

    # TODO Might consider reifying url into its own newtype
    def get_resource_url(self, resource: str, tag: str) -> str:
        return "https://git.door43.org/Door43/{0}_{1}/archive/{2}.zip".format(
            self.lang_code, resource, tag
        )

    def setup_resource_files(self):
        if not self.tn_dir:
            tn_url = self.get_resource_url("tn", self.tn_tag)
            self.extract_files_from_url(tn_url)
        if not self.tw_dir:
            tw_url = self.get_resource_url("tw", self.tw_tag)
            self.extract_files_from_url(tw_url)
        if not self.tq_dir:
            tq_url = self.get_resource_url("tq", self.tq_tag)
            self.extract_files_from_url(tq_url)
        if not self.ta_dir:
            ta_url = self.get_resource_url("ta", self.ta_tag)
            self.extract_files_from_url(ta_url)
        if not self.udb_dir:
            udb_url = self.get_resource_url("udb", self.udb_tag)
            self.extract_files_from_url(udb_url)
        if not self.ulb_dir:
            ulb_url = self.get_resource_url("ulb", self.ulb_tag)
            self.extract_files_from_url(ulb_url)
        if not os.path.isfile(os.path.join(self.working_dir, "icon-tn.png")):
            command = "curl -o {0}/icon-tn.png https://unfoldingword.org/assets/img/icon-tn.png".format(
                self.working_dir
            )
            subprocess.call(command, shell=True)

    def extract_files_from_url(self, url):
        zip_file = os.path.join(self.working_dir, url.rpartition(os.path.sep)[2])
        try:
            self.logger.debug("Downloading {0}...".format(url))
            download_file(url, zip_file)
        finally:
            self.logger.debug("finished.")
        try:
            self.logger.debug("Unzipping {0}...".format(zip_file))
            unzip(zip_file, self.working_dir)
        finally:
            self.logger.debug("finished.")

    def get_usfm_chunks(self):
        book_chunks = {}
        for resource in ["udb", "ulb"]:
            book_chunks[resource] = {}

            bible_dir = getattr(self, "{0}_dir".format(resource))
            usfm = read_file(
                os.path.join(
                    bible_dir,
                    "{0}-{1}.usfm".format(
                        BOOK_NUMBERS[self.book_id], self.book_id.upper()
                    ),
                ),
                "utf-8",
            )

            chunks = re.compile(r"\\s5\s*\n*").split(usfm)

            # Break chunks into verses
            chunks_per_verse = []
            for chunk in chunks:
                pending_chunk = None
                for line in chunk.splitlines(True):
                    # If this is a new verse and there's a pending chunk,
                    # finish it and start a new one.
                    if re.search(r"\\v", line) and pending_chunk:
                        chunks_per_verse.append(pending_chunk)
                        pending_chunk = None
                    pending_chunk = pending_chunk + line if pending_chunk else line
                # If there's a pending chunk, finish it.
                if pending_chunk:
                    chunks_per_verse.append(pending_chunk)
            chunks = chunks_per_verse

            header = chunks[0]
            book_chunks[resource]["header"] = header
            for chunk in chunks[1:]:
                if not chunk.strip():
                    continue
                c_search = re.search(
                    r"\\c[\u00A0\s](\d+)", chunk
                )  # \u00A0 no break space
                if c_search:
                    chapter = c_search.group(1)
                verses = re.findall(r"\\v[\u00A0\s](\d+)", chunk)
                if not verses:
                    continue
                first_verse = verses[0]
                last_verse = verses[-1]
                if chapter not in book_chunks[resource]:
                    book_chunks[resource][chapter] = {"chunks": []}
                data = {
                    "usfm": chunk,
                    "first_verse": first_verse,
                    "last_verse": last_verse,
                    "verses": verses,
                }
                book_chunks[resource][chapter][first_verse] = data
                book_chunks[resource][chapter]["chunks"].append(data)
        return book_chunks

    def preprocess_markdown(self):
        tn_md = self.get_tn_markdown()
        tq_md = self.get_tq_markdown()
        tw_md = self.get_tw_markdown()
        ta_md = self.get_ta_markdown()
        md = "\n\n".join([tn_md, tq_md, tw_md, ta_md])
        md = self.replace_rc_links(md)
        md = fix_links(md)
        write_file(
            os.path.join(self.output_dir, "{0}.md".format(self.filename_base)), md
        )

    def pad(self, num):
        if self.book_id == "psa":
            return str(num).zfill(3)
        return str(num).zfill(2)

    def get_tn_markdown(self):
        book_dir = os.path.join(self.tn_dir, self.book_id)

        if not os.path.isdir(book_dir):
            return ""

        # TODO Might need localization
        tn_md = '# Translation Notes\n<a id="tn-{0}"/>\n\n'.format(self.book_id)

        intro_file = os.path.join(book_dir, "front", "intro.md")
        book_has_intro = os.path.isfile(intro_file)
        if book_has_intro:
            md = read_file(intro_file)
            title = self.get_first_header(md)
            md = self.fix_tn_links(md, "intro")
            md = self.increase_headers(md)
            md = self.decrease_headers(md, 5)  # bring headers of 5 or more #'s down 1
            id_tag = '<a id="tn-{0}-front-intro"/>'.format(self.book_id)
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{0}\n".format(id_tag), md, 1)
            rc = "rc://{0}/tn/help/{1}/front/intro".format(self.lang_code, self.book_id)
            # anchor_id = "tn-{1}-front-intro".format(self.lang_code, self.book_id)
            anchor_id = "tn-{}-front-intro".format(self.book_id)  # self.lang_code,
            self.resource_data[rc] = {
                "rc": rc,
                "id": anchor_id,
                "link": "#{0}".format(anchor_id),
                "title": title,
            }
            self.my_rcs.append(rc)
            self.get_resource_data_from_rc_links(md, rc)
            md += "\n\n"
            tn_md += md

        for chapter in sorted(os.listdir(book_dir)):
            chapter_dir = os.path.join(book_dir, chapter)
            chapter = chapter.lstrip("0")
            if os.path.isdir(chapter_dir) and re.match(r"^\d+$", chapter):
                intro_file = os.path.join(chapter_dir, "intro.md")
                chapter_has_intro = os.path.isfile(intro_file)
                if chapter_has_intro:
                    md = read_file(intro_file)
                    title = self.get_first_header(md)
                    md = self.fix_tn_links(md, chapter)
                    md = self.increase_headers(md)
                    md = self.decrease_headers(
                        md, 5, 2
                    )  # bring headers of 5 or more #'s down 2
                    id_tag = '<a id="tn-{0}-{1}-intro"/>'.format(
                        self.book_id, self.pad(chapter)
                    )
                    md = re.compile(r"# ([^\n]+)\n").sub(
                        r"# \1\n{0}\n".format(id_tag), md, 1
                    )
                    rc = "rc://{0}/tn/help/{1}/{2}/intro".format(
                        self.lang_code, self.book_id, self.pad(chapter)
                    )
                    anchor_id = "tn-{0}-{1}-intro".format(
                        self.book_id, self.pad(chapter)
                    )
                    self.resource_data[rc] = {
                        "rc": rc,
                        "id": anchor_id,
                        "link": "#{0}".format(anchor_id),
                        "title": title,
                    }
                    self.my_rcs.append(rc)
                    self.get_resource_data_from_rc_links(md, rc)
                    md += "\n\n"
                    tn_md += md
                chunk_files = sorted(glob(os.path.join(chapter_dir, "[0-9]*.md")))
                for _, chunk_file in enumerate(chunk_files):
                    first_verse = os.path.splitext(os.path.basename(chunk_file))[
                        0
                    ].lstrip("0")
                    last_verse = self.usfm_chunks["ulb"][chapter][first_verse][
                        "last_verse"
                    ]
                    if first_verse != last_verse:
                        title = "{0} {1}:{2}-{3}".format(
                            self.book_title, chapter, first_verse, last_verse
                        )
                    else:
                        title = "{0} {1}:{2}".format(
                            self.book_title, chapter, first_verse
                        )
                    md = self.increase_headers(read_file(chunk_file), 3)
                    md = self.decrease_headers(
                        md, 5
                    )  # bring headers of 5 or more #'s down 1
                    md = self.fix_tn_links(md, chapter)
                    # TODO localization
                    md = md.replace("#### Translation Words", "### Translation Words")
                    anchors = ""
                    for verse in self.usfm_chunks["ulb"][chapter][first_verse][
                        "verses"
                    ]:
                        anchors += '<a id="tn-{0}-{1}-{2}"/>'.format(
                            self.book_id, self.pad(chapter), self.pad(verse)
                        )
                    pre_md = "\n## {0}\n{1}\n\n".format(title, anchors)
                    # TODO localization
                    pre_md += "### Unlocked Literal Bible\n\n[[ulb://{0}/{1}/{2}/{3}/{4}]]\n\n".format(
                        self.lang_code,
                        self.book_id,
                        self.pad(chapter),
                        self.pad(first_verse),
                        self.pad(last_verse),
                    )
                    # TODO localization
                    pre_md += "### Translation Notes\n"
                    md = "{0}\n{1}\n\n".format(pre_md, md)

                    # Add Translation Words for passage
                    tw_refs = get_tw_refs(
                        self.tw_refs_by_verse, self.book_title, chapter, first_verse
                    )
                    if tw_refs:
                        # TODO localization
                        tw_md = "### Translation Words\n\n"
                        for tw_ref in tw_refs:
                            file_ref_md = "* [{0}](rc://en/tw/dict/bible/{1}/{2})\n".format(
                                tw_ref["Term"], tw_ref["Dir"], tw_ref["Ref"]
                            )
                            tw_md += file_ref_md
                        md = "{0}\n{1}\n\n".format(md, tw_md)

                    # If we're inside a UDB bridge, roll back to the beginning of it
                    udb_first_verse = first_verse
                    udb_first_verse_ok = False
                    while not udb_first_verse_ok:
                        try:
                            _ = self.usfm_chunks["udb"][chapter][udb_first_verse][
                                "usfm"
                            ]
                            udb_first_verse_ok = True
                        except KeyError:
                            udb_first_verse_int = int(udb_first_verse) - 1
                            if udb_first_verse_int <= 0:
                                break
                            udb_first_verse = str(udb_first_verse_int)

                    # TODO localization
                    md += "### Unlocked Dynamic Bible\n\n[[udb://{0}/{1}/{2}/{3}/{4}]]\n\n".format(
                        self.lang_code,
                        self.book_id,
                        self.pad(chapter),
                        self.pad(udb_first_verse),
                        self.pad(last_verse),
                    )
                    rc = "rc://{0}/tn/help/{1}/{2}/{3}".format(
                        self.lang_code,
                        self.book_id,
                        self.pad(chapter),
                        self.pad(first_verse),
                    )
                    anchor_id = "tn-{0}-{1}-{2}".format(
                        self.book_id, self.pad(chapter), self.pad(first_verse)
                    )
                    self.resource_data[rc] = {
                        "rc": rc,
                        "id": anchor_id,
                        "link": "#{0}".format(anchor_id),
                        "title": title,
                    }
                    self.my_rcs.append(rc)
                    self.get_resource_data_from_rc_links(md, rc)
                    md += "\n\n"
                    tn_md += md

                    # TODO localization
                    links = "### Links:\n\n"
                    if book_has_intro:
                        links += "* [[rc://{0}/tn/help/{1}/front/intro]]\n".format(
                            self.lang_code, self.book_id
                        )
                    if chapter_has_intro:
                        links += "* [[rc://{0}/tn/help/{1}/{2}/intro]]\n".format(
                            self.lang_code, self.book_id, self.pad(chapter)
                        )
                    links += "* [[rc://{0}/tq/help/{1}/{2}]]\n".format(
                        self.lang_code, self.book_id, self.pad(chapter)
                    )
                    tn_md += links + "\n\n"

        self.logger.debug("tn_md is {0}".format(tn_md))
        return tn_md

    # TODO This is quite a cluster
    def get_tq_markdown(self):
        """Build tq markdown"""
        # TODO localization
        tq_md = '# Translation Questions\n<a id="tq-{0}"/>\n\n'.format(self.book_id)
        # TODO localization
        title = "{0} Translation Questions".format(self.book_title)
        rc = "rc://{0}/tq/help/{1}".format(self.lang_code, self.book_id)
        anchor_id = "tq-{0}".format(self.book_id)
        self.resource_data[rc] = {
            "rc": rc,
            "id": anchor_id,
            "link": "#{0}".format(anchor_id),
            "title": title,
        }
        self.my_rcs.append(rc)
        tq_book_dir = os.path.join(self.tq_dir, self.book_id)
        for chapter in sorted(os.listdir(tq_book_dir)):
            chapter_dir = os.path.join(tq_book_dir, chapter)
            chapter = chapter.lstrip("0")
            if os.path.isdir(chapter_dir) and re.match(r"^\d+$", chapter):
                id_tag = '<a id="tq-{0}-{1}"/>'.format(self.book_id, self.pad(chapter))
                tq_md += "## {0} {1}\n{2}\n\n".format(self.book_title, chapter, id_tag)
                # TODO localization
                title = "{0} {1} Translation Questions".format(self.book_title, chapter)
                rc = "rc://{0}/tq/help/{1}/{2}".format(
                    self.lang_code, self.book_id, self.pad(chapter)
                )
                anchor_id = "tq-{0}-{1}".format(self.book_id, self.pad(chapter))
                self.resource_data[rc] = {
                    "rc": rc,
                    "id": anchor_id,
                    "link": "#{0}".format(anchor_id),
                    "title": title,
                }
                self.my_rcs.append(rc)
                for chunk in sorted(os.listdir(chapter_dir)):
                    chunk_file = os.path.join(chapter_dir, chunk)
                    first_verse = os.path.splitext(chunk)[0].lstrip("0")
                    if os.path.isfile(chunk_file) and re.match(r"^\d+$", first_verse):
                        md = read_file(chunk_file)
                        md = self.increase_headers(md, 2)
                        md = re.compile("^([^#\n].+)$", flags=re.M).sub(
                            r'\1 [<a href="#tn-{0}-{1}-{2}">{3}:{4}</a>]'.format(
                                self.book_id,
                                self.pad(chapter),
                                self.pad(first_verse),
                                chapter,
                                first_verse,
                            ),
                            md,
                        )
                        # TODO localization
                        title = "{0} {1}:{2} Translation Questions".format(
                            self.book_title, chapter, first_verse
                        )
                        rc = "rc://{0}/tq/help/{1}/{2}/{3}".format(
                            self.lang_code,
                            self.book_id,
                            self.pad(chapter),
                            self.pad(first_verse),
                        )
                        anchor_id = "tq-{0}-{1}-{2}".format(
                            self.book_id, self.pad(chapter), self.pad(first_verse)
                        )
                        self.resource_data[rc] = {
                            "rc": rc,
                            "id": anchor_id,
                            "link": "#{0}".format(anchor_id),
                            "title": title,
                        }
                        self.my_rcs.append(rc)
                        self.get_resource_data_from_rc_links(md, rc)
                        md += "\n\n"
                        tq_md += md
        self.logger.debug("tq_md is {0}".format(tq_md))
        return tq_md

    def get_tw_markdown(self):
        # TODO localization
        tw_md = '<a id="tw-{0}"/>\n# Translation Words\n\n'.format(self.book_id)
        sorted_rcs = sorted(
            self.my_rcs, key=lambda k: self.resource_data[k]["title"].lower()
        )
        for rc in sorted_rcs:
            if "/tw/" not in rc:
                continue
            if self.resource_data[rc]["text"]:
                md = self.resource_data[rc]["text"]
            else:
                md = ""
            id_tag = '<a id="{0}"/>'.format(self.resource_data[rc]["id"])
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{0}\n".format(id_tag), md, 1)
            md = self.increase_headers(md)
            uses = self.get_uses(rc)
            if uses == "":
                continue
            md += uses
            md += "\n\n"
            tw_md += md
        # TODO localization
        tw_md = remove_md_section(tw_md, "Bible References")
        # TODO localization
        tw_md = remove_md_section(tw_md, "Examples from the Bible stories")

        self.logger.debug("tw_md is {0}".format(tw_md))
        return tw_md

    def get_ta_markdown(self):
        # TODO localization
        ta_md = '<a id="ta-{0}"/>\n# Translation Topics\n\n'.format(self.book_id)
        sorted_rcs = sorted(
            self.my_rcs, key=lambda k: self.resource_data[k]["title"].lower()
        )
        for rc in sorted_rcs:
            if "/ta/" not in rc:
                continue
            if self.resource_data[rc]["text"]:
                md = self.resource_data[rc]["text"]
            else:
                md = ""
            id_tag = '<a id="{0}"/>'.format(self.resource_data[rc]["id"])
            md = re.compile(r"# ([^\n]+)\n").sub(r"# \1\n{0}\n".format(id_tag), md, 1)
            md = self.increase_headers(md)
            md += self.get_uses(rc)
            md += "\n\n"
            ta_md += md
        self.logger.debug("ta_md is {0}".format(ta_md))
        return ta_md

    def get_uses(self, rc):
        md = ""
        if self.rc_references[rc]:
            references = []
            for reference in self.rc_references[rc]:
                if "/tn/" in reference:
                    references.append("* [[{0}]]".format(reference))
            if references:
                # TODO localization
                md += "### Uses:\n\n"
                md += "\n".join(references)
                md += "\n"
        return md

    def get_resource_data_from_rc_links(self, text, source_rc):
        for rc in re.findall(
            r"rc://[A-Z0-9/_-]+", text, flags=re.IGNORECASE | re.MULTILINE
        ):
            parts = rc[5:].split("/")
            resource = parts[1]
            path = "/".join(parts[3:])

            if resource not in ["ta", "tw"]:
                continue

            if rc not in self.my_rcs:
                self.my_rcs.append(rc)
            if rc not in self.rc_references:
                self.rc_references[rc] = []
            self.rc_references[rc].append(source_rc)

            if rc not in self.resource_data:
                title = ""
                t = ""
                anchor_id = "{0}-{1}".format(resource, path.replace("/", "-"))
                link = "#{0}".format(anchor_id)
                try:
                    file_path = os.path.join(
                        self.working_dir,
                        "{0}_{1}".format(self.lang_code, resource),
                        "{0}.md".format(path),
                    )
                    if not os.path.isfile(file_path):
                        file_path = os.path.join(
                            self.working_dir,
                            "{0}_{1}".format(self.lang_code, resource),
                            "{0}/01.md".format(path),
                        )
                    if not os.path.isfile(file_path):
                        if resource == "tw":
                            # TODO localization?
                            if path.startswith("bible/other/"):
                                # TODO localization?
                                path2 = re.sub(r"^bible/other/", r"bible/kt/", path)
                            else:
                                # TODO localization?
                                path2 = re.sub(r"^bible/kt/", r"bible/other/", path)
                            anchor_id = "{0}-{1}".format(
                                resource, path2.replace("/", "-")
                            )
                            link = "#{0}".format(anchor_id)
                            file_path = os.path.join(
                                self.working_dir,
                                "{0}_{1}".format(self.lang_code, resource),
                                "{0}.md".format(path2),
                            )
                    if os.path.isfile(file_path):
                        t = read_file(file_path)
                        if resource == "ta":
                            title_file = os.path.join(
                                os.path.dirname(file_path), "title.md"
                            )
                            question_file = os.path.join(
                                os.path.dirname(file_path), "sub-title.md"
                            )
                            if os.path.isfile(title_file):
                                title = read_file(title_file)
                            else:
                                title = self.get_first_header(t)
                            if os.path.isfile(question_file):
                                question = read_file(question_file)
                                # TODO localization?
                                question = "This page answers the question: *{0}*\n\n".format(
                                    question
                                )
                            else:
                                question = ""
                            t = "# {0}\n\n{1}{2}".format(title, question, t)
                            t = self.fix_ta_links(t, path.split("/")[0])
                        elif resource == "tw":
                            title = self.get_first_header(t)
                            t = self.fix_tw_links(t, path.split("/")[1])
                    else:
                        if rc not in self.bad_links:
                            self.bad_links[rc] = []
                        self.bad_links[rc].append(source_rc)
                except:
                    if rc not in self.bad_links:
                        self.bad_links[rc] = []
                    self.bad_links[rc].append(source_rc)
                self.resource_data[rc] = {
                    "rc": rc,
                    "link": link,
                    "id": anchor_id,
                    "title": title,
                    "text": t,
                }
                if t:
                    self.get_resource_data_from_rc_links(t, rc)

    @staticmethod
    def increase_headers(text, increase_depth=1):
        if text:
            text = re.sub(
                r"^(#+) +(.+?) *#*$",
                r"\1{0} \2".format("#" * increase_depth),
                text,
                flags=re.MULTILINE,
            )
        return text

    @staticmethod
    def decrease_headers(text, minimum_header=1, decrease=1):
        if text:
            text = re.sub(
                r"^({0}#*){1} +(.+?) *#*$".format(
                    "#" * (minimum_header - decrease), "#" * decrease
                ),
                r"\1 \2",
                text,
                flags=re.MULTILINE,
            )
        return text

    @staticmethod
    def get_first_header(text):
        lines = text.split("\n")
        if lines:
            for line in lines:
                if re.match(r"^ *#+ ", line):
                    return re.sub(r"^ *#+ (.*?) *#*$", r"\1", line)
            return lines[0]
        return "NO TITLE"

    def fix_tn_links(self, text, chapter):
        rep = {
            re.escape(
                # TODO localization
                "**[2 Thessalonians intro](../front/intro.md)"
                # TODO localization
            ): "**[2 Thessalonians intro](../front/intro.md)**",
            r"\]\(\.\./\.\./([^)]+?)(\.md)*\)": r"](rc://{0}/tn/help/\1)".format(
                self.lang_code
            ),
            r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{0}/tn/help/{1}/\1)".format(
                self.lang_code, self.book_id
            ),
            r"\]\(\./([^)]+?)(\.md)*\)": r"](rc://{0}/tn/help/{1}/{2}/\1)".format(
                self.lang_code, self.book_id, self.pad(chapter)
            ),
            r"\n__.*\|.*": r"",
        }
        for pattern, repl in rep.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE | re.MULTILINE)
        return text

    def fix_tw_links(self, text, dictionary):
        rep = {
            r"\]\(\.\./([^/)]+?)(\.md)*\)": r"](rc://{0}/tw/dict/bible/{1}/\1)".format(
                self.lang_code, dictionary
            ),
            r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{0}/tw/dict/bible/\1)".format(
                self.lang_code
            ),
        }
        for pattern, repl in rep.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text

    def fix_ta_links(self, text, manual):
        rep = {
            r"\]\(\.\./([^/)]+)/01\.md\)": r"](rc://{0}/ta/man/{1}/\1)".format(
                self.lang_code, manual
            ),
            r"\]\(\.\./\.\./([^/)]+)/([^/)]+)/01\.md\)": r"](rc://{0}/ta/man/\1/\2)".format(
                self.lang_code
            ),
            r"\]\(([^# :/)]+)\)": r"](rc://{0}/ta/man/{1}/\1)".format(
                self.lang_code, manual
            ),
        }
        for pattern, repl in rep.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text

    def replace_rc_links(self, text):
        # Change [[rc://...]] rc links, e.g. [[rc://en/tw/help/bible/kt/word]] => [God's Word](#tw-kt-word)
        rep = dict(
            (
                re.escape("[[{0}]]".format(rc)),
                "[{0}]({1})".format(
                    self.resource_data[rc]["title"].strip(),
                    self.resource_data[rc]["link"],
                ),
            )
            for rc in self.my_rcs
        )
        pattern = re.compile("|".join(list(rep.keys())))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

        # Change ].(rc://...) rc links, e.g. [Click here](rc://en/tw/help/bible/kt/word) => [Click here](#tw-kt-word)
        rep = dict(
            (re.escape("]({0})".format(rc)), "]({0})".format(info["link"]))
            for rc, info in self.resource_data.items()
        )
        pattern = re.compile("|".join(list(rep.keys())))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

        # Change rc://... rc links, e.g. rc://en/tw/help/bible/kt/word => [God's](#tw-kt-word)
        rep = dict(
            (re.escape(rc), "[{0}]({1})".format(info["title"], info["link"]))
            for rc, info in self.resource_data.items()
        )
        pattern = re.compile("|".join(list(rep.keys())))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

        return text

    def convert_md2html(self):
        html = markdown.markdown(
            read_file(
                os.path.join(self.output_dir, "{0}.md".format(self.filename_base)),
                "utf-8",
            )
        )
        html = self.replace_bible_links(html)
        write_file(
            os.path.join(self.output_dir, "{0}.html".format(self.filename_base)), html
        )

    def replace_bible_links(self, text):
        bible_links = re.findall(
            r"(?:udb|ulb)://[A-Z0-9/]+", text, flags=re.IGNORECASE | re.MULTILINE
        )
        bible_links = list(set(bible_links))
        rep = {}
        for link in sorted(bible_links):
            parts = link.split("/")
            resource = parts[0][0:3]
            chapter = parts[4].lstrip("0")
            first_verse = parts[5].lstrip("0")
            rep[link] = "<div>{0}</div>".format(
                self.get_chunk_html(resource, chapter, first_verse)
            )
        rep = dict(
            (re.escape("[[{0}]]".format(link)), html) for link, html in rep.items()
        )
        pattern = re.compile("|".join(list(rep.keys())))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
        return text

    def get_chunk_html(self, resource, chapter, verse):
        # print("html: {0}-{3}-{1}-{2}".format(resource, chapter, verse, self.book_id))
        path = tempfile.mkdtemp(
            dir=self.working_dir,
            prefix="usfm-{0}-{1}-{2}-{3}-{4}_".format(
                self.lang_code, resource, self.book_id, chapter, verse
            ),
        )
        filename_base = "{0}-{1}-{2}-{3}".format(resource, self.book_id, chapter, verse)
        try:
            chunk = self.usfm_chunks[resource][chapter][verse]["usfm"]
        except KeyError:
            chunk = ""
        usfm = self.usfm_chunks[resource]["header"]
        if "\\c" not in chunk:
            usfm += "\n\n\\c {0}\n".format(chapter)
        usfm += chunk
        write_file(os.path.join(path, filename_base + ".usfm"), usfm)
        UsfmTransform.buildSingleHtml(path, path, filename_base)
        html = read_file(os.path.join(path, filename_base + ".html"))
        shutil.rmtree(path, ignore_errors=True)
        soup = bs4.BeautifulSoup(html, "html.parser")
        header = soup.find("h1")
        if header:
            header.decompose()
        chapter = soup.find("h2")
        if chapter:
            chapter.decompose()
        html = "".join(["%s" % x for x in soup.body.contents])
        return html

    def convert_html2pdf(self):
        now = datetime.datetime.now()
        revision_date = "{}-{}-{}".format(now.year, now.month, now.day)
        command = """pandoc \
--pdf-engine="xelatex" \
--template="tools/tex/template.tex" \
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
-H "tools/tex/format.tex" \
-o "{3}/{5}.pdf" \
"{3}/{5}.html"
""".format(
            # BOOK_NUMBERS[self.book_id],  # FIXME This arg is not used
            # self.book_id.upper(),  # FIXME This arg is not used
            self.book_title,
            self.issued,
            self.version,
            self.output_dir,
            self.working_dir,
            self.filename_base,
            revision_date,
        )
        print(command)
        subprocess.call(command, shell=True)


def fix_links(text):
    rep = {}

    def replace_tn_with_door43_link(match):
        book = match.group(1)
        chapter = match.group(2)
        verse = match.group(3)
        if book in BOOK_NUMBERS:
            book_num = BOOK_NUMBERS[book]
        else:
            return None
        if int(book_num) > 40:
            anchor_book_num = str(int(book_num) - 1)
        else:
            anchor_book_num = book_num
        url = "https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/{0}-{1}.html#{2}-ch-{3}-v-{4}".format(
            book_num.zfill(2),
            book.upper(),
            anchor_book_num.zfill(3),
            chapter.zfill(3),
            verse.zfill(3),
        )
        return url

    def replace_obs_with_door43_link(match):
        url = "https://live.door43.org/u/Door43/en_obs/b9c4f076ff/{0}.html".format(
            match.group(1)
        )
        return url

    # convert OBS links: rc://en/tn/help/obs/15/07 => https://live.door43.org/u/Door43/en_obs/b9c4f076ff/15.html
    rep[r"rc://[^/]+/tn/help/obs/(\d+)/(\d+)"] = replace_obs_with_door43_link

    # convert tN links (NT books use USFM numbering in HTML file name, but standard book numbering in the anchor):
    # rc://en/tn/help/rev/15/07 => https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/67-REV.html#066-ch-015-v-007
    rep[r"rc://[^/]+/tn/help/(?!obs)([^/]+)/(\d+)/(\d+)"] = replace_tn_with_door43_link

    # convert RC links, e.g. rc://en/tn/help/1sa/16/02 => https://git.door43.org/Door43/en_tn/1sa/16/02.md
    rep[
        r"rc://([^/]+)/(?!tn)([^/]+)/([^/]+)/([^\s\)\]\n$]+)"
    ] = r"https://git.door43.org/Door43/\1_\2/src/master/\4.md"

    # convert URLs to links if not already
    rep[
        r'([^"\(])((http|https|ftp)://[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
    ] = r"\1[\2](\2)"

    # URLS wth just www at the start, no http
    rep[
        r'([^A-Za-z0-9"\(\/])(www\.[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
    ] = r"\1[\2](http://\2.md)"

    for pattern, repl in rep.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def remove_md_section(md, section_name):
    """ Given markdown and a section name, removes the section and the text contained in the section. """
    header_regex = re.compile("^#.*$")
    section_regex = re.compile("^#+ " + section_name)
    out_md = ""
    in_section = False
    for line in md.splitlines():
        if in_section:
            if header_regex.match(line):
                # We found a header.  The section is over.
                out_md += line + "\n"
                in_section = False
        else:
            if section_regex.match(line):
                # We found the section header.
                in_section = True
            else:
                out_md += line + "\n"
    return out_md


def read_csv_as_dicts(filename):
    """ Returns a list of dicts, each containing the contents of a row of
        the given csv file. The CSV file is assumed to have a header row with
        the field names. """
    rows = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def index_tw_refs_by_verse(tw_refs):
    """ Returns a dictionary of books -> chapters -> verses, where each
        verse is a list of rows for that verse. """
    tw_refs_by_verse = {}
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
        #         print("Found duplicate: ", book, chapter, verse, folder, reference)
        #         found_duplicate = True
        #         break
        # if found_duplicate:
        #     continue

        tw_refs_by_verse[book][chapter][verse].append(tw_ref)
    return tw_refs_by_verse


def get_tw_refs(tw_refs_by_verse, book, chapter, verse):
    """ Returns a list of refs for the given book, chapter, verse, or
        empty list if no matches. """
    if book not in tw_refs_by_verse:
        return []
    if chapter not in tw_refs_by_verse[book]:
        return []
    if verse not in tw_refs_by_verse[book][chapter]:
        return []
    return tw_refs_by_verse[book][chapter][verse]


def main(
    ta_tag: str,
    tn_tag: str,
    tq_tag: str,
    tw_tag: str,
    udb_tag: str,
    ulb_tag: str,
    working_dir,
    output_dir,
    lang_code: str,
    books,
) -> None:
    """
    :param ta_tag:
    :param tn_tag:
    :param tq_tag:
    :param tw_tag:
    :param udb_tag:
    :param ulb_tag:
    :param lang_code:
    :param books:
    :param working_dir:
    :param output_dir:
    :return:
    """

    tn_converter = TnConverter(
        ta_tag,
        tn_tag,
        tq_tag,
        tw_tag,
        udb_tag,
        ulb_tag,
        working_dir,
        output_dir,
        lang_code,
        books,
    )
    tn_converter.run()

    # Let's test our json lookup service on something
    lookup_svc: ResourceJsonLookup = ResourceJsonLookup(
        logger=tn_converter.logger, pp=tn_converter.pp
    )
    lang: str = "Abadi"
    download_url: Optional[str] = lookup_svc.lookup_download_url(lang)
    if download_url is not None:
        print(("Language {0} download url: {1}".format(lang, download_url)))
    repo_url: Optional[str] = lookup_svc.parse_repo_url_from_json_url(download_url)
    if repo_url is not None:
        print(("Language {0} repo_url: {1}".format(lang, repo_url)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-l",
        "--lang",
        dest="lang_code",
        default="en",
        required=False,
        help="Language Code",
    )
    parser.add_argument(
        "-b",
        "--book_id",
        dest="books",
        nargs="+",
        default=None,
        required=False,
        help="Bible Book(s)",
    )
    parser.add_argument(
        "-w",
        "--working",
        dest="working_dir",
        default=False,
        required=False,
        help="Working Directory",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        default=False,
        required=False,
        help="Output Directory",
    )
    parser.add_argument(
        "--ta-tag", dest="ta", default="v9", required=False, help="tA Tag"
    )
    parser.add_argument(
        "--tn-tag", dest="tn", default="v11", required=False, help="tN Tag"
    )
    parser.add_argument(
        "--tq-tag", dest="tq", default="v9", required=False, help="tQ Tag"
    )
    parser.add_argument(
        "--tw-tag", dest="tw", default="v8", required=False, help="tW Tag"
    )
    parser.add_argument(
        "--udb-tag", dest="udb", default="v12", required=False, help="UDB Tag"
    )
    parser.add_argument(
        "--ulb-tag", dest="ulb", default="v12", required=False, help="ULB Tag"
    )
    args = parser.parse_args(sys.argv[1:])
    main(
        args.ta,
        args.tn,
        args.tq,
        args.tw,
        args.udb,
        args.ulb,
        args.working_dir,
        args.output_dir,
        args.lang_code,
        args.books,
    )
