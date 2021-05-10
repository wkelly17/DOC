from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import icontract

from document import config
from document.domain import bible_books
from document.utils import file_utils, markdown_utils


logger = config.get_logger(__name__)


@icontract.require(lambda book_id, num: book_id is not None and num is not None)
def pad(book_id: str, num: str) -> str:
    """
    If book_id equals 'psa', i.e., Psalms, then pad num by 3 spaces.
    Otherwise pad num by 2 spaces.
    """
    if book_id == "psa":
        return num.zfill(3)
    return num.zfill(2)


@icontract.require(lambda rc_references, rc: rc_references is not None and rc)
def get_uses(rc_references: Dict, rc: str) -> str:
    """
    Return Translation Note references for references at key rc as
    Markdown with a level 3 header 'Uses:' prepended.
    """
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


@icontract.require(
    lambda my_rcs, resource_data, content: my_rcs is not None
    and resource_data is not None
    and content is not None
)
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
    text = pattern.sub(lambda match: rep[re.escape(match.group(0))], content)

    # Change ].(rc://...) rc links, e.g. [Click here](rc://en/tw/help/bible/kt/word) => [Click here](#tw-kt-word)
    rep = dict(
        (re.escape("]({0})".format(rc)), "]({0})".format(info["link"]))
        for rc, info in resource_data.items()
    )
    pattern = re.compile("|".join(list(rep.keys())))
    text = pattern.sub(lambda match: rep[re.escape(match.group(0))], text)

    # Change rc://... rc links, e.g. rc://en/tw/help/bible/kt/word => [God's](#tw-kt-word)
    rep = dict(
        (re.escape(rc), "[{}]({})".format(info["title"], info["link"]))
        for rc, info in resource_data.items()
    )
    pattern = re.compile("|".join(list(rep.keys())))
    return pattern.sub(lambda match: rep[re.escape(match.group(0))], text)


def replace_tn_with_door43_link(match: re.Match) -> str:
    book = match.group(1)
    chapter = match.group(2)
    verse = match.group(3)
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


# NOTE Not used anymore.
# def replace_obs_with_door43_link(match: re.Match) -> str:
#     url = "https://live.door43.org/u/Door43/en_obs/b9c4f076ff/{}.html".format(
#         match.group(1)
#     )
#     return url


@icontract.require(lambda text: text)
@icontract.ensure(lambda result: result)
def transform_rc_links(text: str) -> str:
    """
    Transform rc:// style links found in text according to a set of
    ad-hoc substitution rules.

    Rules:

        * Convert OBS links.
          Example:
          rc://en/tn/help/obs/15/07 →
          https://live.door43.org/u/Door43/en_obs/b9c4f076ff/15.html
        * Convert TN links (NT books use USFM numbering in HTML file
          name, but standard book numbering in the anchor).
          Example:
          rc://en/tn/help/rev/15/07 →
          https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/67-REV.html#066-ch-015-v-007
        * Convert HTTP/HTTPS/FTP URLs to Markdown links if not already.
          Example:
          '([^"\(])((http|https|ftp)://[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])' →
          "\1[\2](\2)"
        * To URLS with just www and no http at the start prepend http://
    """
    rep = {}

    # Convert OBS links.
    # Example: rc://en/tn/help/obs/15/07 => https://live.door43.org/u/Door43/en_obs/b9c4f076ff/15.html
    rep[
        r"rc://[^/]+/tn/help/obs/(\d+)/(\d+)"
    ] = r"https://live.door43.org/u/Door43/en_obs/b9c4f076ff/\1.html"

    # Convert TN links (NT books use USFM numbering in HTML file name, but standard book numbering in the anchor):
    # Example:
    # rc://en/tn/help/rev/15/07 => https://live.door43.org/u/Door43/en_ulb/c0bd11bad0/67-REV.html#066-ch-015-v-007
    rep[r"rc://[^/]+/tn/help/(?!obs)([^/]+)/(\d+)/(\d+)"] = replace_tn_with_door43_link  # type: ignore

    # Convert more TN links.
    # Example: rc://en/tn/help/1sa/16/02 => https://git.door43.org/Door43/en_tn/1sa/16/02.md
    rep[
        r"rc://([^/]+)/(?!tn)([^/]+)/([^/]+)/([^\s\)\]\n$]+)"
    ] = r"https://git.door43.org/Door43/\1_\2/src/master/\4.md"

    # Convert HTTP/HTTPS/FTP URLs to Markdown links if not already.
    rep[
        r'([^"\(])((http|https|ftp)://[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
    ] = r"\1[\2](\2)"

    # URLS with just www at the start and no http get http:// prepended to them.
    rep[
        r'([^A-Za-z0-9"\(\/])(www\.[A-Za-z0-9\/\?&_\.:=#-]+[A-Za-z0-9\/\?&_:=#-])'
    ] = r"\1[\2](http://\2.md)"

    for pattern, repl in rep.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


@icontract.require(lambda lang_code, text, manual: lang_code and text and manual)
@icontract.ensure(lambda result: result)
def fix_ta_links(lang_code: str, text: str, manual: str) -> str:
    r"""
    Transform the second half of various Markdown links according to a
    set of ad-hoc substitution rules.

    Rules:

      * "\]\(\.\./([^/)]+)/01\.md\)" → "](rc://{lang_code}/ta/man/{manual}/\1)"
      * "\]\(\.\./\.\./([^/)]+)/([^/)]+)/01\.md\)" → "](rc://{lang_code}/ta/man/\1/\2)"
      * "\]\(([^# :/)]+)\)" → "](rc://{lang_code}/ta/man/{manual}/\1)"
    """
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


@icontract.require(
    lambda lang_code, book_id, text, chapter: lang_code and book_id and text and chapter
)
def fix_tn_links(lang_code: str, book_id: str, text: str, chapter: str) -> str:
    r"""
    Transform the second half of various Markdown links according to a
    set of ad-hoc substitution rules.

    Rules:

      * "**[2 Thessalonians intro](../front/intro.md)" → "**[2 Thessalonians intro](../front/intro.md)**"
      * "\]\(\.\./\.\./([^)]+?)(\.md)*\)" → "](rc://{lang_code}/tn/help/\1)"
      * "\]\(\.\./([^)]+?)(\.md)*\)" → "](rc://{lang_code}/tn/help/{book_id}/\1)"
      * "\]\(\./([^)]+?)(\.md)*\)" → "](rc://{lang_code}/tn/help/{book_id}/{book_id}/\1)"
      * "\n__.*\|.*" → ""
    """
    rep = {
        re.escape(
            "**[2 Thessalonians intro](../front/intro.md)"
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


@icontract.require(
    lambda lang_code, text, dictionary: lang_code and text and dictionary is not None
)
def fix_tw_links(lang_code: str, text: str, dictionary: str) -> str:
    """
    Transform the second half of various Markdown links according to a
    set of ad-hoc substitution rules.

    Rules:
      * "\]\(\.\./([^/)]+?)(\.md)*\)" → "](rc://{lang_code}/tw/dict/bible/{dictionary}/\1)"
      * "\]\(\.\./([^)]+?)(\.md)*\)" → "](rc://{lang_code}/tw/dict/bible/\1)"
    """
    rep = {
        r"\]\(\.\./([^/)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/{}/\1)".format(
            lang_code, dictionary
        ),
        r"\]\(\.\./([^)]+?)(\.md)*\)": r"](rc://{}/tw/dict/bible/\1)".format(lang_code),
    }
    for pattern, repl in rep.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


@icontract.require(
    lambda lang_code, my_rcs, rc_references, resource_data, bad_links, working_dir, text, source_rc: lang_code
    and rc_references is not None
    and resource_data is not None
    and bad_links is not None
    and working_dir
    and text
    and source_rc is not None
)
def get_resource_data_from_rc_links(
    lang_code: str,
    my_rcs: List,
    rc_references: Dict,
    resource_data: Dict,
    bad_links: Dict,
    working_dir: str,
    text: str,
    source_rc: str,
) -> None:
    """
    Summary: Overall purpose of this function: find ta or tw rc links in the text passed
    in and use them to build filepaths that point to Markdown files
    where further information can be found like:
    1. The tile of the

    This function is called with text coming from Translation Notes book intro Markdown
    content, Translation Notes chapter intro Markdown content, and
    Translation Questions chapter content.

    This function finds TW and TA rc links in the text content
    (mentioned in previous paragraph), finds Markdown files associated
    with them and using those Markdown files' content, forms
    attributes associated with them. These various attributes are then
    collected into various data structures for later use.

    FIXME This function is a serious legacy cluster needing to be
    broken up. Many of its conditional paths could possibly, pending
    further in depth analysis, live in their respective resource
    instance's class, e.g., TAResource and TNResource.
    """
    # Find all rc links in the text passed into the function.
    for rc in re.findall(
        r"rc://[A-Z0-9/_-]+", text, flags=re.IGNORECASE | re.MULTILINE
    ):
        parts = rc[5:].split("/")
        # Separate out the resource type from first part of the rc
        # link.
        resource_type = parts[1]
        # Create a file path base out of the first parts of the rc link.
        path = "/".join(parts[3:])

        logger.debug("resource from regexp: {}".format(resource_type))

        # We only process ta and tw resource links in this function.
        if resource_type not in ["ta", "tw"]:
            continue

        # Keep a running collection of rc links in a my_rcs list.
        if rc not in my_rcs:
            my_rcs.append(rc)
        # Also save the rc link in a rc_references dictionary as a
        # key.
        if rc not in rc_references:
            rc_references[rc] = []
        # In the rc_references dictionary at the rc key store the
        # source_rc link.
        rc_references[rc].append(source_rc)

        # If the rc link is not yet in the resource_data dictionary...
        if rc not in resource_data:
            title = ""
            markdown_file_content = ""
            # Create an anchor link to the TA or TW resource.
            anchor_id = "{}-{}".format(resource_type, path.replace("/", "-"))
            anchor_link = "#{}".format(anchor_id)
            # A lot of file path testing ahead which could through
            # some exceptions. FIXME Identify all the exceptions that
            # could occur and narrow to those as narrowly as possibly
            # instead of this gigantic try block.
            try:
                # Get file path to the TW or TA resource's Markdown
                # file: {working_dir}/{lang_code}_{ta|tw}/{path}.md.
                # FIXME Resource's already know their location
                # in _resource_dir. Further globbing can find the
                # associated resource file. See initialize_from_assets
                # for n example.
                file_path = os.path.join(
                    working_dir,
                    "{}_{}".format(lang_code, resource_type),
                    "{}.md".format(path),
                )
                # If the previous filepath doesn't exist then try
                # another location:
                # {working_dir}/{lang_code}_{ta|tw}/01.md.
                # FIXME Resource's are found with globbing in the new
                # system so conditional logic like this is obviated.
                if not os.path.isfile(file_path):
                    file_path = os.path.join(
                        working_dir,
                        "{}_{}".format(lang_code, resource_type),
                        "{}/01.md".format(path),
                    )
                # If the previous file_path is not found yet again,
                # then...
                if not os.path.isfile(file_path):
                    # If the resource type is tw...
                    if resource_type == "tw":
                        # If the path starts with bible/other then
                        # replace it with bible/kt
                        if path.startswith("bible/other/"):
                            path2 = re.sub(r"^bible/other/", r"bible/kt/", path)
                        # Otherwise, replace bible/kt with bible/other
                        else:
                            path2 = re.sub(r"^bible/kt/", r"bible/other/", path)
                        # Create the anchor link for the TA or TW
                        # resource Markdown file.
                        anchor_id = "{}-{}".format(
                            resource_type, path2.replace("/", "-")
                        )
                        anchor_link = "#{0}".format(anchor_id)
                        file_path = os.path.join(
                            working_dir,
                            "{}_{}".format(lang_code, resource_type),
                            "{}.md".format(path2),
                        )
                # If we've now found the file_path for the resource
                # currently under consideration, ta or tw, then read
                # in the file.
                if os.path.isfile(file_path):
                    markdown_file_content = file_utils.read_file(file_path)
                    # If the current resource has type ta
                    if resource_type == "ta":
                        # Form the path to the title file which
                        # should be located in the same directory as
                        # the the file_path we've currently verified
                        # exists.
                        title_file = os.path.join(
                            os.path.dirname(file_path), "title.md"
                        )
                        # Form the path to the sub-title Markdown file
                        # which should also be in the same directory
                        # as the file_path.
                        question_file = os.path.join(
                            os.path.dirname(file_path), "sub-title.md"
                        )
                        # See if the title file exists at the
                        # title_file path that we formed above...
                        if os.path.isfile(title_file):
                            # Now go ahead and actually read in the title
                            # from the title Markdown file.
                            title = file_utils.read_file(title_file)
                        else:
                            # Apparently the title file doesn't exist
                            # so we'll get something that works as a
                            # title by grabbing the first Markdown
                            # header content in the Markdown file
                            # located at file_path.
                            title = markdown_utils.get_first_header(
                                markdown_file_content
                            )
                        # Likewise, check if the question_file
                        # exists...
                        if os.path.isfile(question_file):
                            # If the question_file path does exist
                            # then read in the question file.
                            question = file_utils.read_file(question_file)
                            # Now form a question phrase to be used
                            # below.
                            question = "This page answers the question: *{}*\n\n".format(
                                question
                            )
                        else:
                            # The question file didn't exist so we'll
                            # make the question content empty.
                            question = ""
                        # Now let's create a level 1 Markdown headline
                        # and its content that has the title as the
                        # headline and the question phrase we created
                        # above followed by the link to the Markdown
                        # file that was located at file_path, i.e.,
                        # the ta resource's Markdown file path
                        # that we worked hard at guessing at the top
                        # of this function.
                        markdown_file_content = "# {}\n\n{}{}".format(
                            title, question, markdown_file_content
                        )
                        # Now call fix_ta_links on the ta
                        # markdown_file which will transform certain
                        # ta links according to a set of ad-hoc rules.
                        markdown_file_content = fix_ta_links(
                            lang_code, markdown_file_content, path.split("/")[0]
                        )
                    # On the other hand, if the current resource is a
                    # tw resource...
                    elif resource_type == "tw":
                        # Create a title from the markdown_file's
                        # first Markdown header.
                        title = markdown_utils.get_first_header(markdown_file_content)
                        # And then do some link transformations on tw
                        # links contained in markdown_file.
                        markdown_file_content = fix_tw_links(
                            lang_code, markdown_file_content, path.split("/")[1]
                        )

                # If we've not found the file_path for the resource
                # currently under consideration, ta or tw...
                else:
                    # If the current rc link is not currently in
                    # bad_links dictionary then add it as a key into
                    # bad_links with an empty value.
                    if rc not in bad_links:
                        bad_links[rc] = []
                    # Append the source_rc to bad_links dictionary at
                    # key rc.
                    bad_links[rc].append(source_rc)
            except:
                if rc not in bad_links:
                    bad_links[rc] = []
                bad_links[rc].append(source_rc)
            # Now store all the data that we have have created
            # associated with this resource into the resource_data
            # dictionary with rc as the key.
            resource_data[rc] = {
                "rc": rc,
                "link": anchor_link,
                "id": anchor_id,
                "title": title,
                "text": markdown_file_content,
            }
            # If we found markdown_file earlier in this function let's
            # call ourself again. TODO
            if markdown_file_content:
                get_resource_data_from_rc_links(
                    lang_code,
                    my_rcs,
                    rc_references,
                    resource_data,
                    bad_links,
                    working_dir,
                    markdown_file_content,
                    rc,
                )


@icontract.require(
    lambda usfm_chunks, book_id, chapter, first_verse: usfm_chunks
    and book_id
    and chapter
    and first_verse
)
@icontract.ensure(lambda result: result)
def initialize_tn_chapter_verse_anchor_links(
    usfm_chunks: Dict, book_id: str, chapter: str, first_verse: str
) -> str:
    """
    Return Markdown/HTML string of anchor links for verses for book
    identified by book_id and chapter.
    """
    anchors = ""
    try:
        for verse in usfm_chunks["ulb"][chapter][first_verse]["verses"]:
            anchors += '<a id="tn-{}-{}-{}"/>'.format(
                book_id, pad(book_id, chapter), pad(book_id, verse),
            )
    except ValueError:
        return ""
    logger.debug("anchors: {}".format(anchors))
    return anchors


@icontract.require(
    lambda book_id, book_title, lang_code, chapter_chunk_file, chapter: book_id
    and book_title
    and lang_code
    and chapter_chunk_file
    and chapter
)
@icontract.ensure(lambda result: result is not None)
def initialize_tn_chapter_files(
    book_id: str, book_title: str, lang_code: str, chapter_chunk_file: str, chapter: str
) -> Tuple[str, Optional[str], str, str]:
    """
    TODO
    """
    first_verse = os.path.splitext(os.path.basename(chapter_chunk_file))[0].lstrip("0")
    # FIXME TNResource doesn't have self._usfm_chunks
    # logger.debug("self._usfm_chunks: {}".format(self._usfm_chunks))
    # if bool(self._usfm_chunks):
    #     last_verse = self._usfm_chunks["ulb"][chapter][first_verse]["last_verse"]
    # else:
    #     last_verse = None
    last_verse = None  # HACK due to commented out code above
    if last_verse is not None and first_verse != last_verse:
        title = "{} {}:{}-{}".format(book_title, chapter, first_verse, last_verse)
    else:
        title = "{} {}:{}".format(book_title, chapter, first_verse)
    md = markdown_utils.increase_headers(file_utils.read_file(chapter_chunk_file), 3)
    # bring headers of 5 or more #'s down 1
    md = markdown_utils.decrease_headers(md, 5)
    md = fix_tn_links(lang_code, book_id, md, chapter)
    md = md.replace("#### Translation Words", "### Translation Words")
    return first_verse, last_verse, title, md


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
