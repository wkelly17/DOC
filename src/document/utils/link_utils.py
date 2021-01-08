from __future__ import annotations
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
import icontract
import os
import re
import yaml

from document import config
from document.utils import file_utils, markdown_utils
from document.domain import bible_books

if TYPE_CHECKING:
    from document.domain.resource import USFMResource

import logging
import logging.config

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


@icontract.require(lambda book_id: book_id is not None)
@icontract.require(lambda num: num is not None)
def pad(book_id: str, num: str) -> str:
    if book_id == "psa":
        return num.zfill(3)
    return num.zfill(2)


def get_uses(rc_references: Dict, rc: str) -> str:
    md = ""
    if rc_references[rc]:
        references = []
        for reference in rc_references[rc]:
            if "/tn/" in reference:
                references.append("* [[{}]]".format(reference))
        if references:
            # TODO localization
            md += "### Uses:\n\n"
            md += "\n".join(references)
            md += "\n"
    return md


@icontract.require(lambda my_rcs: my_rcs is not None)
@icontract.require(lambda resource_data: resource_data is not None)
@icontract.require(lambda content: content is not None)
def replace_rc_links(my_rcs: List, resource_data: Dict, content: str) -> str:
    """
    Given a resource's markdown text, replace links of the
    form [[rc://en/tw/help/bible/kt/word]] with links of the form
    [God's Word](#tw-kt-word).
    """
    rep = dict(
        (
            re.escape("[[{}]]".format(rc)),
            "[{}]({})".format(
                resource_data[rc]["title"].strip(), resource_data[rc]["link"],
            ),
        )
        for rc in my_rcs
    )
    pattern: re.Pattern = re.compile("|".join(list(rep.keys())))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], content)

    # Change ].(rc://...) rc links, e.g. [Click here](rc://en/tw/help/bible/kt/word) => [Click here](#tw-kt-word)
    rep = dict(
        (re.escape("]({0})".format(rc)), "]({0})".format(info["link"]))
        for rc, info in resource_data.items()
    )
    pattern = re.compile("|".join(list(rep.keys())))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    # Change rc://... rc links, e.g. rc://en/tw/help/bible/kt/word => [God's](#tw-kt-word)
    rep = dict(
        (re.escape(rc), "[{}]({})".format(info["title"], info["link"]))
        for rc, info in resource_data.items()
    )
    pattern = re.compile("|".join(list(rep.keys())))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text


def fix_links(text: str) -> str:
    rep = {}

    def replace_tn_with_door43_link(match: re.Match) -> str:
        book = match.group(1)
        chapter = match.group(2)
        verse = match.group(3)
        # if book in bible_books.BOOK_NUMBERS:
        #     book_num = bible_books.BOOK_NUMBERS[book]
        # else:
        #     return None
        book_num = bible_books.BOOK_NUMBERS[book]
        if int(book_num) > 40:
            anchor_book_num = str(int(book_num) - 1)
        else:
            anchor_book_num = book_num
        url = "https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/{}-{}.html#{}-ch-{}-v-{}".format(
            book_num.zfill(2),
            book.upper(),
            anchor_book_num.zfill(3),
            chapter.zfill(3),
            verse.zfill(3),
        )
        return url

    def replace_obs_with_door43_link(match: re.Match) -> str:
        url = "https://live.door43.org/u/Door43/en_obs/b9c4f076ff/{}.html".format(
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


def fix_ta_links(lang_code: str, text: str, manual: str) -> str:
    rep = {
        r"\]\(\.\./([^/)]+)/01\.md\)": r"](rc://{0}/ta/man/{1}/\1)".format(
            lang_code, manual
        ),
        r"\]\(\.\./\.\./([^/)]+)/([^/)]+)/01\.md\)": r"](rc://{}/ta/man/\1/\2)".format(
            lang_code
        ),
        r"\]\(([^# :/)]+)\)": r"](rc://{}/ta/man/{}/\1)".format(lang_code, manual),
    }
    for pattern, repl in rep.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


@icontract.require(lambda lang_code: lang_code is not None)
@icontract.require(lambda book_id: book_id is not None)
@icontract.require(lambda text: text is not None)
@icontract.require(lambda chapter: chapter is not None)
def fix_tn_links(lang_code: str, book_id: str, text: str, chapter: str) -> str:
    rep = {
        re.escape(
            # TODO localization
            "**[2 Thessalonians intro](../front/intro.md)"
            # TODO localization
        ): "**[2 Thessalonians intro](../front/intro.md)**",
        r"\]\(\.\./\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tn/help/\1)".format(lang_code),
        r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tn/help/{}/\1)".format(
            lang_code, book_id
        ),
        r"\]\(\./([^)]+?)(\.md)*\)": r"](rc://{}/tn/help/{}/{}/\1)".format(
            lang_code, book_id, pad(book_id, chapter),
        ),
        r"\n__.*\|.*": r"",
    }
    for pattern, repl in rep.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE | re.MULTILINE)
    return text


@icontract.require(lambda lang_code: lang_code is not None)
@icontract.require(lambda text: text is not None)
@icontract.require(lambda dictionary: dictionary is not None)
def fix_tw_links(lang_code: str, text: str, dictionary: str) -> str:
    rep = {
        r"\]\(\.\./([^/)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/{}/\1)".format(
            lang_code, dictionary
        ),
        r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/\1)".format(lang_code),
    }
    for pattern, repl in rep.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


# FIXME We may still need this.
# def _replace_bible_links(self, text: str) -> str:
#     bible_links = re.findall(
#         r"(?:udb|ulb)://[A-Z0-9/]+", text, flags=re.IGNORECASE | re.MULTILINE
#     )
#     bible_links = list(set(bible_links))
#     logger.debug("bible_links: {}".format(bible_links))
#     rep = {}
#     for link in sorted(bible_links):
#         parts = link.split("/")
#         logger.debug("parts: {}".format(parts))
#         resource_str = parts[0][0:3]
#         logger.debug("resource_str: {}".format(resource_str))
#         chapter = parts[4].lstrip("0")
#         logger.debug("chapter: {}".format(chapter))
#         first_verse = parts[5].lstrip("0")
#         logger.debug("first_verse: {}".format(first_verse))
#         rep[link] = "<div>{0}</div>".format(
#             # FIXME It looks like this presupposes that, as per
#             # the old logic path, we build links to USFM files and
#             # then later, i.e., here, actually produce the HTML
#             # from the USFM. Such presuppositions are
#             # inappropriate now.
#             self._get_chunk_html(resource_str, chapter, first_verse)
#         )
#     rep = dict(
#         (re.escape("[[{0}]]".format(link)), html) for link, html in rep.items()
#     )
#     pattern = re.compile("|".join(list(rep.keys())))
#     text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
#     return text

# FIXME Understand more deeply what and why this exists in detail.
# FIXME This legacy code is a mess of mixed up concerns. This
# method is called from tn and tq concerned code so when we move
# it it will probably have to live in a module that can be mixed
# into both TNResource and TQResource or the method itself will be
# teased apart so that conditionals are reduced and code paths
# pertaining to the instance are the only ones preserved in each
# instance's version of this method.
# @icontract.require(lambda text: text is not None)
# @icontract.require(lambda source_rc: source_rc is not None)
# def _get_resource_data_from_rc_links(self, text: str, source_rc: str) -> None:
#     for rc in re.findall(
#         r"rc://[A-Z0-9/_-]+", text, flags=re.IGNORECASE | re.MULTILINE
#     ):
#         parts = rc[5:].split("/")
#         resource_tmp = parts[1]
#         path = "/".join(parts[3:])

#         if rc not in self._my_rcs:
#             self._my_rcs.append(rc)
#         if rc not in self._rc_references:
#             self._rc_references[rc] = []
#         self._rc_references[rc].append(source_rc)

#         if rc not in self._resource_data:
#             title = ""
#             t = ""
#             anchor_id = "{}-{}".format(resource_tmp, path.replace("/", "-"))
#             link = "#{}".format(anchor_id)
#             try:
#                 file_path = os.path.join(
#                     self._working_dir,
#                     "{}_{}".format(self.lang_code, resource_tmp),
#                     "{}.md".format(path),
#                 )
#                 if not os.path.isfile(file_path):
#                     file_path = os.path.join(
#                         self._working_dir,
#                         "{}_{}".format(self.lang_code, resource_tmp),
#                         "{}/01.md".format(path),
#                     )
#                 if not os.path.isfile(file_path):
#                     # TODO localization?
#                     if path.startswith("bible/other/"):
#                         # TODO localization?
#                         path2 = re.sub(r"^bible/other/", r"bible/kt/", path)
#                     else:
#                         # TODO localization?
#                         path2 = re.sub(r"^bible/kt/", r"bible/other/", path)
#                     anchor_id = "{}-{}".format(
#                         resource_tmp, path2.replace("/", "-")
#                     )
#                     link = "#{}".format(anchor_id)
#                     file_path = os.path.join(
#                         self._working_dir,
#                         "{}_{}".format(self.lang_code, resource_tmp),
#                         "{}.md".format(path2),
#                     )
#                 if os.path.isfile(file_path):
#                     t = file_utils.read_file(file_path)
#                     title = get_first_header(t)
#                     t = self._fix_tw_links(t, path.split("/")[1])
#                 else:
#                     # TODO bad_links doesn't exist yet, but should
#                     # be on resources dict.
#                     if rc not in self._bad_links:
#                         self._bad_links[rc] = []
#                     self._bad_links[rc].append(source_rc)
#             except:
#                 # TODO
#                 if rc not in self._bad_links:
#                     self._bad_links[rc] = []
#                 self._bad_links[rc].append(source_rc)
#             self._resource_data[rc] = {
#                 "rc": rc,
#                 "link": link,
#                 "id": anchor_id,
#                 "title": title,
#                 "text": t,
#             }
#             if t:
#                 self._get_resource_data_from_rc_links(t, rc)


# FIXME What to return from function and when?
@icontract.require(lambda lang_code: lang_code is not None)
@icontract.require(lambda my_rcs: my_rcs is not None)
@icontract.require(lambda rc_references: rc_references is not None)
@icontract.require(lambda resource_data: resource_data is not None)
@icontract.require(lambda bad_links: bad_links is not None)
@icontract.require(lambda working_dir: working_dir is not None)
@icontract.require(lambda text: text is not None)
@icontract.require(lambda source_rc: source_rc is not None)
def get_resource_data_from_rc_links(
    lang_code: str,
    my_rcs: List,
    rc_references: Dict,
    resource_data: Dict,
    bad_links: Dict,
    working_dir: str,
    text: str,
    source_rc: str,
):
    for rc in re.findall(
        r"rc://[A-Z0-9/_-]+", text, flags=re.IGNORECASE | re.MULTILINE
    ):
        parts = rc[5:].split("/")
        resource = parts[1]
        path = "/".join(parts[3:])

        logger.debug("resource from regexp: {}".format(resource))

        if resource not in ["ta", "tw"]:
            continue

        if rc not in my_rcs:
            my_rcs.append(rc)
        if rc not in rc_references:
            rc_references[rc] = []
        rc_references[rc].append(source_rc)

        if rc not in resource_data:
            title = ""
            t = ""
            anchor_id = "{0}-{1}".format(resource, path.replace("/", "-"))
            link = "#{}".format(anchor_id)
            try:
                file_path = os.path.join(
                    working_dir,
                    "{}_{}".format(lang_code, resource),
                    "{}.md".format(path),
                )
                if not os.path.isfile(file_path):
                    file_path = os.path.join(
                        working_dir,
                        "{}_{}".format(lang_code, resource),
                        "{}/01.md".format(path),
                    )
                if not os.path.isfile(file_path):
                    if resource == "tw":
                        if path.startswith("bible/other/"):
                            path2 = re.sub(r"^bible/other/", r"bible/kt/", path)
                        else:
                            path2 = re.sub(r"^bible/kt/", r"bible/other/", path)
                        anchor_id = "{0}-{1}".format(resource, path2.replace("/", "-"))
                        link = "#{0}".format(anchor_id)
                        file_path = os.path.join(
                            working_dir,
                            "{}_{}".format(lang_code, resource),
                            "{}.md".format(path2),
                        )
                if os.path.isfile(file_path):
                    t = file_utils.read_file(file_path)
                    if resource == "ta":
                        title_file = os.path.join(
                            os.path.dirname(file_path), "title.md"
                        )
                        question_file = os.path.join(
                            os.path.dirname(file_path), "sub-title.md"
                        )
                        if os.path.isfile(title_file):
                            title = file_utils.read_file(title_file)
                        else:
                            title = markdown_utils.get_first_header(t)
                        if os.path.isfile(question_file):
                            question = file_utils.read_file(question_file)
                            question = "This page answers the question: *{0}*\n\n".format(
                                question
                            )
                        else:
                            question = ""
                        t = "# {0}\n\n{1}{2}".format(title, question, t)
                        t = fix_ta_links(lang_code, t, path.split("/")[0])
                    elif resource == "tw":
                        title = markdown_utils.get_first_header(t)
                        t = fix_tw_links(lang_code, t, path.split("/")[1])
                else:
                    if rc not in bad_links:
                        bad_links[rc] = []
                    bad_links[rc].append(source_rc)
            except:
                if rc not in bad_links:
                    bad_links[rc] = []
                bad_links[rc].append(source_rc)
            resource_data[rc] = {
                "rc": rc,
                "link": link,
                "id": anchor_id,
                "title": title,
                "text": t,
            }
            if t:
                get_resource_data_from_rc_links(
                    lang_code,
                    my_rcs,
                    rc_references,
                    resource_data,
                    bad_links,
                    working_dir,
                    t,
                    rc,
                )


@icontract.require(lambda lang_code: lang_code is not None)
@icontract.require(lambda book_id: book_id is not None)
@icontract.require(lambda book_has_intro: book_has_intro is not None)
@icontract.require(lambda chapter_has_intro: chapter_has_intro is not None)
@icontract.require(lambda chapter: chapter is not None)
def initialize_tn_links(
    lang_code: str,
    book_id: str,
    book_has_intro: bool,
    chapter_has_intro: bool,
    chapter: str,
) -> str:
    # TODO localization
    links = "### Links:\n\n"
    if book_has_intro:
        links += "* [[rc://{}/tn/help/{}/front/intro]]\n".format(lang_code, book_id)
    if chapter_has_intro:
        links += "* [[rc://{0}/tn/help/{1}/{2}/intro]]\n".format(
            lang_code, book_id, pad(book_id, chapter),
        )
    links += "* [[rc://{0}/tq/help/{1}/{2}]]\n".format(
        lang_code, book_id, pad(book_id, chapter),
    )
    return links


# FIXME Add icontract requirements
def initialize_tn_chapter_verse_links(
    usfm_resource: USFMResource, book_id: str, chapter: str, first_verse: str
) -> str:
    anchors = ""
    try:
        for verse in usfm_resource._usfm_chunks["ulb"][chapter][first_verse]["verses"]:
            anchors += '<a id="tn-{}-{}-{}"/>'.format(
                book_id, pad(book_id, chapter), pad(book_id, verse),
            )
    except:
        pass  # TODO
    logger.debug("anchors: {}".format(anchors))
    return anchors


# FIXME Add icontract requirements
def initialize_tn_chapter_files(
    book_id: str, book_title: str, lang_code: str, chunk_file: str, chapter: str
) -> Tuple[str, Optional[str], str, str]:
    first_verse = os.path.splitext(os.path.basename(chunk_file))[0].lstrip("0")
    # FIXME TNResource doesn't have self._usfm_chunks
    # logger.debug("self._usfm_chunks: {}".format(self._usfm_chunks))
    # if bool(self._usfm_chunks):
    #     last_verse = self._usfm_chunks["ulb"][chapter][first_verse]["last_verse"]
    # else:
    #     last_verse = None
    last_verse = None
    if last_verse is not None and first_verse != last_verse:
        title = "{} {}:{}-{}".format(
            book_title,
            chapter,
            first_verse,
            last_verse
            # self.book_title, chapter, first_verse, last_verse
        )
    else:
        title = "{} {}:{}".format(
            book_title,
            chapter,
            first_verse
            # self.book_title, chapter, first_verse
        )
    md = markdown_utils.increase_headers(file_utils.read_file(chunk_file), 3)
    # bring headers of 5 or more #'s down 1
    md = markdown_utils.decrease_headers(md, 5)
    md = fix_tn_links(lang_code, book_id, md, chapter)
    # TODO localization
    md = md.replace("#### Translation Words", "### Translation Words")
    return (first_verse, last_verse, title, md)
