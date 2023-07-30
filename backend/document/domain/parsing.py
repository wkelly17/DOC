"""
This module provides an API for parsing content.
"""

import time
from glob import glob
from os import scandir
from os.path import exists, join, split
from pathlib import Path
from re import compile, sub
from typing import Mapping, Optional, Sequence, cast

import markdown
import yaml
from bs4 import BeautifulSoup
from bs4.element import Tag
from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    adjust_book_intro_headings,
    adjust_chapter_heading,
    adjust_chapter_intro_headings,
    adjust_commentary_headings,
)
from document.domain.bible_books import BOOK_NAMES, book_number
from document.domain.model import (
    BCBook,
    BCChapter,
    BookContent,
    ChapterNum,
    ChunkSizeEnum,
    HtmlContent,
    LangDirEnum,
    MarkdownContent,
    ResourceLookupDto,
    ResourceRequest,
    TNBook,
    TNChapter,
    TQBook,
    TQChapter,
    TWBook,
    TWNameContentPair,
    USFMBook,
    USFMChapter,
    VerseRef,
)
import orjson
from document.markdown_extensions import (
    link_print_transformer_preprocessor,
    link_transformer_preprocessor,
    remove_section_preprocessor,
)
from document.utils.file_utils import read_file
from document.utils.html_parsing_utils import tag_elements_between
from document.utils.tw_utils import (
    localized_translation_word,
    translation_word_filepaths,
    translation_words_dict,
    tw_resource_dir,
)
from usfm_tools import transform

logger = settings.logger(__name__)

H1, H2, H3, H4, H5 = "h1", "h2", "h3", "h4", "h5"


def ensure_paragraph_before_verses(
    usfm_file: str,
    verse_content: str,
    usfm_verse_one_file_regex: str = "^01\..*",
    chapter_marker_not_on_own_line_regex: str = r"^\\c [0-9]+ .*|\n",
    chapter_marker_not_on_own_line_with_match_groups: str = r"(^\\c [0-9]+) (.*|\n)",
    chapter_marker_not_on_own_line_repair_regex: str = r"\1\n\\p\n\2\n",
) -> str:
    """
    If verse_content has a USFM chapter marker, \c, that is not on its
    own line (violation of the USFM spec) then repair this and
    additionally add a USFM paragraph marker, \p, so that when the USFM is
    rendered to HTML the verse spans will be enclosed in a block level
    HTML element which in turn will ensure that Docx rendering is free of
    a bug wherein the verse spans are interpreted as a continuation of the
    chapter headline (as evidenced by verse content being rendered with
    the same font color and boldness as the chapter headline).

    Return the possibly updated verse_content.
    """
    if (
        compile(usfm_verse_one_file_regex).match(Path(usfm_file).name) is not None
    ):  # Verse 1 of chapter
        if (
            compile(chapter_marker_not_on_own_line_regex).match(verse_content)
            is not None
        ):  # Chapter marker not on own line
            # Make chapter marker occupy its own line and add a USFM paragraph
            # marker right after it. Why? Because I found that languages which were
            # rendering correctly in Docx had a \p USFM marker after the chapter
            # marker and languages which did not render properly (see docstring
            # above for particulars) in Docx did not have one. I changed this
            # manually on the system downloaded USFM and indeed it did solve the
            # Docx rendering issue. Presumably the 3rd party lib we use to parse
            # HTML to Docx doesn't like spans that are not contained in a block
            # level element and this effectively introduces a block level element,
            # p, right before verse content starts so that the chapter's verse
            # content is enclosed in a p HTML element once parsed from USFM to HTML.
            logger.debug(
                "Verse content that has chapter marker which is not on its own line: %s",
                verse_content,
            )
            verse_content = sub(
                chapter_marker_not_on_own_line_with_match_groups,
                chapter_marker_not_on_own_line_repair_regex,
                verse_content,
            )
            logger.debug("Updated verse content: %s", verse_content)
    return verse_content


def attempt_asset_content_rescue(
    resource_dir: str,
    resource_lookup_dto: ResourceLookupDto,
    bible_book_names: Mapping[str, str] = BOOK_NAMES,
) -> str:
    """
    Attempt to assemble and construct parseable USFM content for USFM
    resource delivered as multiple populated directories in chapter >
    verses layout.
    """
    subdirs = [
        file
        for file in scandir(resource_dir)
        if file.is_dir()
        and file.name != ".git"
        and file.name != "front"
        and file.name != "00"
    ]
    logger.info(
        "About to create USFM content for non-conformant USFM to attempt to make it parseable."
    )
    usfm_content = []
    logger.info("Adding a USFM \id marker which the parser requires.")
    usfm_content.append(
        "\id {} Unnamed translation\n".format(resource_lookup_dto.resource_code.upper())
    )
    logger.info("Adding a USFM \ide marker which the parser requires.")
    usfm_content.append("\ide UTF-8\n")
    logger.info("Adding a USFM \h marker which the parser requires.")
    usfm_content.append(
        "\h {}\n".format(bible_book_names[resource_lookup_dto.resource_code])
    )
    for chapter_dir in sorted(subdirs, key=lambda dir_entry: dir_entry.name):
        # Get verses for chapter
        chapter_usfm_content = []
        chapter_num = chapter_dir.name
        # Add the chapter USFM marker
        # NOTE Some language's malformed USFM does provide chapter numbers, so
        # in their case we wouldn't want to also add a USFM chapter marker here.
        # For now the languages that fail to provide chapter markers
        # and are "rescued" here will no longer be provided a chapter
        # marker. This does mean that some languages which don't provide chapter
        # markers will probably render incorrectly, yet to be determined.
        # chapter_usfm_content.append("\c {}\n".format(int(chapter_num)))
        # Read the verses for this chapter
        chapter_verse_files = sorted(
            [
                file.path
                for file in scandir(chapter_dir)
                if file.is_file() and file.name != "title.txt"
            ]
        )
        for usfm_file in chapter_verse_files:
            with open(usfm_file, "r") as fin:
                verse_content = fin.read()
                verse_content = ensure_paragraph_before_verses(usfm_file, verse_content)
                chapter_usfm_content.append(verse_content)
                chapter_usfm_content.append("\n")
        # Store the chapter content into the collection of
        # all chapter's content
        usfm_content.extend(chapter_usfm_content)

    # Write the concatenated markdown content to a
    # non-clobberable filename.
    filename = join(
        resource_dir,
        "{}_{}_{}_{}.usfm".format(
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            time.time_ns(),
        ),
    )
    logger.debug("About to write filename: %s", filename)
    with open(filename, "w") as fout:
        fout.write("".join(usfm_content))
    return filename


def usfm_asset_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    output_dir: str = settings.DOCUMENT_OUTPUT_DIR,
    usfm_glob_fmt_str: str = "{}**/*.usfm",
    usfm_ending_in_txt_glob_fmt_str: str = "{}**/*.txt",
    usfm_ending_in_txt_in_subdirectoy_glob_fmt_str: str = "{}**/**/*.txt",
) -> str:
    """
    Gather and parse USFM content into HTML content and return the
    HTML content.
    """
    usfm_content_files: list[str] = []
    txt_content_files: list[str] = []

    # We don't need a manifest file to find resource assets
    # on disk. We just use globbing and then filter
    # down the list found to only include those
    # files that match the resource code, i.e., book, being requested.
    # This frees us from some of the brittleness of using manifests
    # to find files. Some resources do not provide a manifest
    # anyway.
    usfm_content_files = glob(usfm_glob_fmt_str.format(resource_dir))
    if not usfm_content_files:
        # USFM files sometimes have txt suffix instead of usfm
        txt_content_files = glob(usfm_ending_in_txt_glob_fmt_str.format(resource_dir))
        # Sometimes the txt USFM files live at another location
        if not txt_content_files:
            txt_content_files = glob(
                usfm_ending_in_txt_in_subdirectoy_glob_fmt_str.format(resource_dir)
            )

    # If desired, in the case where a manifest must be consulted
    # to determine if the file is considered usable, i.e.,
    # 'complete' or 'finished', that can also be done by comparing
    # the filtered file(s) against the manifest's 'finished' list
    # to see if it can be used. Such logic could live
    # approximately here if desired.
    content_files: list[str] = []
    if usfm_content_files:
        # Only use the content files that match the resource_code
        # in the resource request.
        content_files = [
            usfm_content_file
            for usfm_content_file in usfm_content_files
            if resource_lookup_dto.resource_code.lower()
            in str(Path(usfm_content_file).stem).lower()
        ]
    elif txt_content_files:
        # Only use the content files that match the resource_code.
        content_files = [
            txt_content_file
            for txt_content_file in txt_content_files
            if resource_lookup_dto.resource_code.lower()
            in str(txt_content_file).lower()
        ]

    html_content = ""
    if content_files:
        # Some languages, like ndh-x-chindali, provide their USFM files in
        # a git repo rather than as standalone USFM files. A USFM git repo can
        # have each USFM chapter in a separate directory and each verse in a
        # separate file in that directory. However, the parser expects one USFM
        # file per book, therefore we need to concatenate the book's USFM files
        # into one USFM file.
        if len(content_files) > 1:
            # Make the temp file our only content file.
            content_files = [
                attempt_asset_content_rescue(resource_dir, resource_lookup_dto)
            ]

        logger.debug("content_files: %s", content_files)

        resource_filename_ = resource_filename(
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
        )

        # Convert the USFM to HTML and store in file. USFM-Tools books.py can
        # raise MalformedUsfmError when the following code is called. The
        # document_generator module will catch that error but continue with
        # other resource requests in the same document request.
        t0 = time.time()
        transform.buildSingleHtmlFromFile(
            Path(content_files[0]),
            output_dir,
            resource_filename_,
        )
        t1 = time.time()
        logger.debug(
            "Time to convert USFM to HTML (parsing to AST + convert AST to HTML) for %s-%s-%s: %s",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            t1 - t0,
        )
        html_file = join(output_dir, "{}.html".format(resource_filename_))
        assert exists(html_file)
        html_content = read_file(html_file)
    return html_content


def book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    chunk_size: str,
    include_tn_book_intros: bool,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    en_usfm_resource_types: Sequence[str] = settings.EN_USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    en_tn_resource_types: Sequence[str] = settings.EN_TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    en_tq_resource_types: Sequence[str] = settings.EN_TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
    en_tw_resource_types: Sequence[str] = settings.EN_TW_RESOURCE_TYPES,
    bc_resource_types: Sequence[str] = settings.BC_RESOURCE_TYPES,
) -> BookContent:
    """Build and return the BookContent instance."""
    book_content: BookContent
    if (
        resource_lookup_dto.resource_type in usfm_resource_types
        or resource_lookup_dto.resource_type in en_usfm_resource_types
    ):
        t0 = time.time()
        book_content = usfm_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
        t1 = time.time()
        logger.debug(
            "Time splitting HTML into chapters and verses for interleaving for %s-%s-%s: %s",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            t1 - t0,
        )
    elif (
        resource_lookup_dto.resource_type in tn_resource_types
        or resource_lookup_dto.resource_type in en_tn_resource_types
    ):
        t0 = time.time()
        book_content = tn_book_content(
            resource_lookup_dto,
            resource_dir,
            resource_requests,
            layout_for_print,
            chunk_size,
            include_tn_book_intros,
        )
        t1 = time.time()
        logger.debug(
            "Time processing and converting TN Markdown to HTML for interleaving for %s-%s-%s: %s",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            t1 - t0,
        )
    elif (
        resource_lookup_dto.resource_type in tq_resource_types
        or resource_lookup_dto.resource_type in en_tq_resource_types
    ):
        t0 = time.time()
        book_content = tq_book_content(
            resource_lookup_dto,
            resource_dir,
            resource_requests,
            layout_for_print,
            chunk_size,
        )
        t1 = time.time()
        logger.debug(
            "Time processing and converting TQ Markdown to HTML for interleaving for %s-%s-%s: %s",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            t1 - t0,
        )
    elif (
        resource_lookup_dto.resource_type in tw_resource_types
        or resource_lookup_dto.resource_type in en_tw_resource_types
    ):
        t0 = time.time()
        book_content = tw_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
        t1 = time.time()
        logger.debug(
            "Time processing, converting, and linking TW Markdown to HTML for interleaving for %s-%s-%s: %s",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            t1 - t0,
        )
    elif resource_lookup_dto.resource_type in bc_resource_types:
        t0 = time.time()
        book_content = bc_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
        t1 = time.time()
        logger.debug(
            "Time processing, converting, and linking BC Markdown to HTML for interleaving for %s-%s-%s: %s",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            t1 - t0,
        )
    return book_content


def is_footnote_ref(id: Optional[str]) -> bool:
    """
    Predicate function used to find links that have an href value that
    we expect footnote references to have.
    """
    return id is not None and compile("ref-fn-.*").match(id) is not None


def lang_direction(
    resource_dir: str,
    lang_code: str,
    resource_code: str,
    resource_type: str,
    manifest_glob_fmt_str: str = "{}/**/manifest.{}",
    manifest_glob_alt_fmt_str: str = "{}/manifest.{}",
) -> LangDirEnum:
    """
    Look up the language direction in the manifest file if one is
    available for this resource.
    """
    manifest_candidates = glob(manifest_glob_fmt_str.format(resource_dir, "yaml"))
    if manifest_candidates:
        with open(manifest_candidates[0], "r") as fin:
            contents = yaml.safe_load(fin)
            lang_dir = contents["dublin_core"]["language"]["direction"]
            if lang_dir == LangDirEnum.LTR:
                return LangDirEnum.LTR
            elif lang_dir == LangDirEnum.RTL:
                return LangDirEnum.RTL

    # if yaml not available then try yaml at alternative directory
    if not manifest_candidates:
        manifest_candidates = glob(
            manifest_glob_alt_fmt_str.format(resource_dir, "yaml")
        )
        if manifest_candidates:
            with open(manifest_candidates[0], "r") as fin:
                contents = yaml.safe_load(fin)
                lang_dir = contents["dublin_core"]["language"]["direction"]
                if lang_dir == LangDirEnum.LTR:
                    return LangDirEnum.LTR
                elif lang_dir == LangDirEnum.RTL:
                    return LangDirEnum.RTL

    # if yaml not available, then try json
    if not manifest_candidates:
        manifest_candidates = glob(manifest_glob_fmt_str.format(resource_dir, "json"))
        if manifest_candidates:
            with open(manifest_candidates[0], "r") as fin:
                # FIXME
                contents = orjson.loads(fin.read())
                lang_dir = contents["target_language"]["direction"]
                if lang_dir == LangDirEnum.LTR:
                    return LangDirEnum.LTR
                elif lang_dir == LangDirEnum.RTL:
                    return LangDirEnum.RTL

    # if json not available then try json at alternative directory
    if not manifest_candidates:
        manifest_candidates = glob(
            manifest_glob_alt_fmt_str.format(resource_dir, "json")
        )
        if manifest_candidates:
            with open(manifest_candidates[0], "r") as fin:
                contents = orjson.loads(fin.read())
                lang_dir = contents["target_language"]["direction"]
                if lang_dir == LangDirEnum.LTR:
                    return LangDirEnum.LTR
                elif lang_dir == LangDirEnum.RTL:
                    return LangDirEnum.RTL

    logger.debug(
        "resource_dir: %s, manifest_candidates: %s", resource_dir, manifest_candidates
    )

    # If there was no manifest, then just return LTR
    return LangDirEnum.LTR


def usfm_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    h2: str = H2,
    bs_parser_type: str = "lxml",
    css_attribute_type: str = "class",
    pattern: str = settings.VERSE_ANCHOR_ID_FMT_STR,
    format_str: str = settings.VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR,
) -> USFMBook:
    """
    First produce HTML content from USFM content through call to
    asset_content and then break the HTML content returned from that
    into a model.USFMBook data structure containing chapters, verses,
    footnotes, for use during interleaving with other resource assets.
    """
    lang_dir = lang_direction(
        resource_dir,
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_code,
        resource_lookup_dto.resource_type,
    )
    logger.debug("lang_dir: %s", lang_dir)
    html_content = usfm_asset_content(resource_lookup_dto, resource_dir)
    parser = BeautifulSoup(html_content, bs_parser_type)

    if layout_for_print:
        # Find all verse level footnote references for this chapter
        verse_footnote_refs = parser.find_all(id=is_footnote_ref)
        # Turn the found links into spans since we don't need
        # links in a printed document.
        for verse_footnote_ref in verse_footnote_refs:
            verse_number = verse_footnote_ref.i.a.string
            # Remove the link
            span = parser.new_tag("span")
            span.string = verse_number
            verse_footnote_ref.i.a.replace_with(span)

    chapter_break_tags = parser.find_all(h2, attrs={css_attribute_type: "c-num"})
    chapters: dict[ChapterNum, USFMChapter] = {}
    for chapter_break in chapter_break_tags:
        chapter_num = int(chapter_break.get_text().split()[1])
        chapter_content = tag_elements_between(
            parser.find(
                h2,
                text=compile(".* {}".format(chapter_num)),
            ),
            parser.find(
                h2,
                text=compile(".* {}".format(chapter_num + 1)),
            ),
        )
        chapter_content = [str(tag) for tag in list(chapter_content)]
        chapter_content_parser = BeautifulSoup(
            "".join(chapter_content),
            bs_parser_type,
        )
        chapter_verse_span_tags = chapter_content_parser.find_all(
            "span", attrs={css_attribute_type: "v-num"}
        )
        chapter_footnote_tag = chapter_content_parser.find(
            "div", attrs={css_attribute_type: "footnotes"}
        )
        if layout_for_print:
            if chapter_footnote_tag:
                chapter_footnote_str = str(chapter_footnote_tag)
                chapter_footnotes_parser = BeautifulSoup(
                    chapter_footnote_str, bs_parser_type
                )
                a_tags = chapter_footnotes_parser.find_all("a")
                # Now we modify the footnote links to be inactive, i.e., not links so
                # that they are suitable for printing.
                for a_tag in a_tags:
                    a_tag.name = "span"
                # Now we just set the name to one we expect (for the next expression)
                # which is executed for either case.
                chapter_footnote_tag = chapter_footnotes_parser
        chapter_footnotes = (
            HtmlContent(str(chapter_footnote_tag))
            if chapter_footnote_tag
            else HtmlContent("")
        )

        # Dictionary to hold verse number, verse value pairs.
        chapter_verses: dict[str, str] = {}
        for verse_span_tag_str in chapter_verse_span_tags:
            verse_span_tag = cast(Tag, verse_span_tag_str)
            verse_ref_, upper_bound_value = verse_ref(verse_span_tag)
            verse_content_str_ = verse_content_str(
                verse_span_tag,
                chapter_content_parser,
                book_number(resource_lookup_dto.resource_code),
                chapter_num,
                upper_bound_value,
            )
            # NOTE We now alter the span ID in verse_content_str by prepending it
            # with the lang_code for the language we are currently parsing to ensure
            # unique verse references within language scope in a multi-language
            # document.
            updated_verse_content_str = sub(
                pattern,
                format_str.format(resource_lookup_dto.lang_code),
                verse_content_str_,
            )
            chapter_verses[verse_ref_] = updated_verse_content_str
        chapters[chapter_num] = USFMChapter(
            content=adjust_chapter_heading(chapter_content),
            verses=chapter_verses,
            footnotes=chapter_footnotes,
        )
    return USFMBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapters,
        lang_direction=lang_dir,
    )


def verse_ref(verse_span_tag: Tag) -> tuple[str, int]:
    """Return the verse_ref value."""
    # Rather than a single verse num, the item in
    # verse_num may be a verse range, e.g., 1-2.
    # See test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_*
    # tests for tests that trigger this situation.
    # Get the verse ref from the verse HTML tag's id value.
    verse_ref = str(verse_span_tag).split("-v-")[1].split('"')[0]
    # Check for hyphen in the range whose presence would indicate that
    # verse ref is a verse range rather than a single verse.
    verse_ref_components = verse_ref.split("-")
    if len(verse_ref_components) > 1:  # This is a verse ref for a verse range
        upper_bound_value = int(verse_ref_components[1]) + 1
        # Get rid of leading zeroes on first verse number
        # in range.
        verse_num_int = int(verse_ref_components[0])
        # Get rid of leading zeroes on second verse number
        # in range.
        verse_num2_int = int(verse_ref_components[1])
        # Recreate the verse range, now without leading
        # zeroes.
        verse_ref = "{}-{}".format(str(verse_num_int), str(verse_num2_int))
    else:  # This is a verse ref for a single verse
        upper_bound_value = int(verse_ref) + 1
        # Get rid of leading zeroes.
        verse_ref = str(int(verse_ref))
    return verse_ref, upper_bound_value


def verse_content_str(
    lower_tag: Tag,
    chapter_content_parser: BeautifulSoup,
    book_number: str,
    chapter_num: int,
    upper_bound_value: int,
    num_zeros: int = 3,
    css_attribute_type: str = "class",
) -> str:
    """Return the content, i.e., text, of the verse(s)."""
    upper_id = "{}-ch-{}-v-{}".format(
        str(book_number).zfill(num_zeros),
        str(chapter_num).zfill(num_zeros),
        str(upper_bound_value).zfill(num_zeros),
    )
    upper_tag = chapter_content_parser.find(
        "span",
        attrs={css_attribute_type: "v-num", "id": upper_id},
    )

    # Ensure that chapter footnotes are not accidentally included with
    # verses from end of chapter.
    if upper_tag is None:
        # We'll set the upper_tag to footnotes node (or None if it does not
        # exist) so that we don't include footnotes in the last verse's content.
        # Footnotes are rendered in HTML by USFM-TOOLS after the chapter's verse
        # content so we don't want them included additionally/accidentally here
        # also.
        footnotes_for_chapter = chapter_content_parser.find("div", class_="footnotes")
        upper_tag = footnotes_for_chapter

    chapter_components = str(chapter_content_parser).split(str(lower_tag))
    section_components = chapter_components[1].split(str(upper_tag))
    verse_content_str = "{}{}".format(lower_tag, section_components[0])
    return verse_content_str


def tn_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    chunk_size: str,
    include_tn_book_intros: bool,
    chapter_dirs_glob_fmt_str: str = "{}/**/*{}/*[0-9]*",
    chapter_dirs_glob_alt_fmt_str: str = "{}/*{}/*[0-9]*",
    intro_paths_glob_fmt_str: str = "{}/*intro.md",
    intro_paths_glob_alt_fmt_str: str = "{}/*intro.txt",
    verse_paths_glob_fmt_str: str = "{}/*[0-9]*.md",
    verse_paths_glob_alt_fmt_str: str = "{}/*[0-9]*.txt",
    book_intro_paths_glob_fmt_str: str = "{}/*{}/front/intro.md",
    book_intro_paths_glob_alt_fmt_str: str = "{}/*{}/front/intro.txt",
    h1: str = H1,
    h5: str = H5,
    verse_label_fmt_str: str = "<h4>{} {}:{}</h4>\n{}",
) -> TNBook:

    lang_dir = lang_direction(
        resource_dir,
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_code,
        resource_lookup_dto.resource_type,
    )
    logger.debug("lang_dir: %s", lang_dir)
    # Initialize the Python-Markdown extensions that get invoked
    # when md.convert is called.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
    )
    chapter_dirs = sorted(
        glob(
            chapter_dirs_glob_fmt_str.format(
                resource_dir,
                resource_lookup_dto.resource_code,
            )
        )
    )
    # Some languages are organized differently on disk (e.g., depending
    # on if their assets were acquired as a git repo or a zip).
    # We handle this here.
    if not chapter_dirs:
        chapter_dirs = sorted(
            glob(
                chapter_dirs_glob_alt_fmt_str.format(
                    resource_dir,
                    resource_lookup_dto.resource_code,
                )
            )
        )
    chapter_verses: dict[int, TNChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(split(chapter_dir)[-1])
        intro_paths = glob(intro_paths_glob_fmt_str.format(chapter_dir))
        # For some languages, TN assets are stored in .txt files
        # rather than .md files.
        if not intro_paths:
            intro_paths = glob(intro_paths_glob_alt_fmt_str.format(chapter_dir))
        intro_path = intro_paths[0] if intro_paths else None
        intro_md = ""
        intro_html = ""
        if intro_path:
            intro_md = read_file(intro_path)
            intro_html = md.convert(intro_md)
        verse_paths = sorted(glob(verse_paths_glob_fmt_str.format(chapter_dir)))
        # For some languages, TN assets are stored in .txt files
        # rather than .md files.
        if not verse_paths:
            verse_paths = sorted(glob(verse_paths_glob_alt_fmt_str.format(chapter_dir)))
        verses_html: dict[VerseRef, str] = {}
        for filepath in verse_paths:
            verse_ref = Path(filepath).stem
            verse_md_content = read_file(filepath)
            verse_html_content = md.convert(verse_md_content)
            adjusted_verse_html_content = sub(h1, h5, verse_html_content)
            # Chapter chunking needs verse level labeling
            if chunk_size == ChunkSizeEnum.CHAPTER:
                verses_html[verse_ref] = verse_label_fmt_str.format(
                    BOOK_NAMES[resource_lookup_dto.resource_code],
                    chapter_num,
                    str(int(verse_ref)) if "0" in verse_ref else verse_ref,
                    adjusted_verse_html_content,
                )
            else:
                verses_html[verse_ref] = adjusted_verse_html_content
        adjusted_intro_html = adjust_chapter_intro_headings(intro_html)
        chapter_payload = TNChapter(intro_html=adjusted_intro_html, verses=verses_html)
        chapter_verses[chapter_num] = chapter_payload
    # Get the book intro if it exists
    book_intro_path = glob(
        book_intro_paths_glob_fmt_str.format(
            resource_dir,
            resource_lookup_dto.resource_code,
        )
    )
    # For some languages, TN assets are stored in .txt files
    # rather of .md files.
    if not book_intro_path:
        book_intro_path = glob(
            book_intro_paths_glob_alt_fmt_str.format(
                resource_dir, resource_lookup_dto.resource_code
            )
        )
    adjusted_book_intro_html = HtmlContent("")
    if book_intro_path and include_tn_book_intros:
        book_intro_html = read_file(book_intro_path[0])
        book_intro_html = md.convert(book_intro_html)
        adjusted_book_intro_html = adjust_book_intro_headings(book_intro_html)
    return TNBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        intro_html=adjusted_book_intro_html,
        chapters=chapter_verses,
        lang_direction=lang_dir,
    )


def tq_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    chunk_size: str,
    chapter_dirs_glob_fmt_str: str = "{}/**/*{}/*[0-9]*",
    chapter_dirs_glob_alt_fmt_str: str = "{}/*{}/*[0-9]*",
    verse_paths_glob_fmt_str: str = "{}/*[0-9]*.md",
    h1: str = H1,
    h5: str = H5,
    verse_label_fmt_str: str = "<h4>{} {}:{}</h4>\n{}",
) -> TQBook:
    lang_dir = lang_direction(
        resource_dir,
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_code,
        resource_lookup_dto.resource_type,
    )

    # Create the Markdown instance once and have it use our markdown
    # extensions.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
    )
    chapter_dirs = sorted(
        glob(
            chapter_dirs_glob_fmt_str.format(
                resource_dir, resource_lookup_dto.resource_code
            )
        )
    )
    # Some languages are organized differently on disk (e.g., depending
    # on if their assets were acquired as a git repo or a zip).
    # We handle this here.
    if not chapter_dirs:
        chapter_dirs = sorted(
            glob(
                chapter_dirs_glob_alt_fmt_str.format(
                    resource_dir, resource_lookup_dto.resource_code
                )
            )
        )
    chapter_verses: dict[int, TQChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(split(chapter_dir)[-1])
        verse_paths = sorted(glob(verse_paths_glob_fmt_str.format(chapter_dir)))
        # NOTE For some languages, TN assets may be stored in .txt files
        # rather of .md files. Though I have not yet seen this, this
        # may also be true of TQ assets. If it is, then the following
        # commented out code would suffice.
        # if not verse_paths:
        #     verse_paths = sorted(glob("{}/*[0-9]*.txt".format(chapter_dir)))
        verses_html: dict[VerseRef, str] = {}
        for filepath in verse_paths:
            verse_ref = Path(filepath).stem
            verse_md_content = read_file(filepath)
            verse_html_content = md.convert(verse_md_content)
            adjusted_verse_html_content = sub(h1, h5, verse_html_content)
            # Chapter chunking needs verse level labeling
            if chunk_size == ChunkSizeEnum.CHAPTER:
                verses_html[verse_ref] = verse_label_fmt_str.format(
                    BOOK_NAMES[resource_lookup_dto.resource_code],
                    chapter_num,
                    str(int(verse_ref)) if "0" in verse_ref else verse_ref,
                    adjusted_verse_html_content,
                )
            else:
                verses_html[verse_ref] = adjusted_verse_html_content
        chapter_verses[chapter_num] = TQChapter(verses=verses_html)
    return TQBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapter_verses,
        lang_direction=lang_dir,
    )


def tw_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
) -> TWBook:
    lang_dir = lang_direction(
        resource_dir,
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_code,
        resource_lookup_dto.resource_type,
    )

    # Create the Markdown instance once and have it use our markdown
    # extensions.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
        resource_dir,
    )
    translation_word_filepaths_: list[str] = translation_word_filepaths(resource_dir)
    name_content_pairs: list[TWNameContentPair] = []
    for translation_word_filepath in translation_word_filepaths_:
        translation_word_content = MarkdownContent(read_file(translation_word_filepath))
        # Translation words are bidirectional. By that I mean that when you are
        # at a verse there follows, after translation questions, links to the
        # translation words that occur in that verse. But then when you navigate
        # to the word by clicking such a link, at the end of the resulting
        # translation word note there is a section called 'Uses:' that also has
        # links back to the verses wherein the word occurs.
        localized_translation_word_ = localized_translation_word(
            translation_word_content
        )
        html_word_content = md.convert(translation_word_content)
        # Make adjustments to the HTML here.
        html_word_content = sub(h2, h4, html_word_content)
        html_word_content = sub(h1, h3, html_word_content)
        name_content_pairs.append(
            TWNameContentPair(localized_translation_word_, html_word_content)
        )

    # Make mypy --strict happy; mypy doesn't pick up types in a
    # lambda.
    def sort_key(name_content_pair: TWNameContentPair) -> str:
        return name_content_pair.localized_word

    return TWBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        # Sort the name content pairs by localized translation word
        name_content_pairs=sorted(name_content_pairs, key=sort_key),
        lang_direction=lang_dir,
    )


def bc_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    book_intro_glob_path_fmt_str: str = "{}/*{}/intro.md",
    chapter_dirs_glob_fmt_str: str = "{}/*{}/*[0-9]*",
    parser_type: str = "html.parser",
    url_fmt_str: str = settings.BC_ARTICLE_URL_FMT_STR,
) -> BCBook:
    # Create the Markdown instance once and have it use our markdown
    # extensions.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
    )
    book_intro_paths = glob(
        book_intro_glob_path_fmt_str.format(
            resource_dir, resource_lookup_dto.resource_code
        )
    )
    book_intro_md_content = read_file(book_intro_paths[0]) if book_intro_paths else ""
    book_intro_html_content = md.convert(book_intro_md_content)
    chapter_dirs = sorted(
        glob(
            chapter_dirs_glob_fmt_str.format(
                resource_dir, resource_lookup_dto.resource_code
            )
        )
    )
    chapters: dict[int, BCChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(Path(chapter_dir).stem)
        chapter_commentary_md_content = read_file(chapter_dir)
        chapter_commentary_html_content = md.convert(chapter_commentary_md_content)
        parser = BeautifulSoup(chapter_commentary_html_content, parser_type)
        if chapter_num == 1:
            # Change the chapter heading to indicate that it is
            # commentary.
            h1 = parser.find("h1")
            if h1:
                h1.append(" Commentary")
        # Replace relative links to bible commentary articles with
        # absolute links to the same resource online.
        for link in parser.find_all("a"):
            old_link_ref = link.get("href")
            new_link_ref = url_fmt_str.format(old_link_ref[3:])
            new_link = parser.new_tag("a", href=new_link_ref, target="_blank")
            new_link.string = link.string
            link.parent.a.replace_with(new_link)
        chapters[chapter_num] = BCChapter(
            commentary=adjust_commentary_headings(str(parser))
        )
    adjusted_book_intro_html_content = adjust_commentary_headings(
        book_intro_html_content
    )
    return BCBook(
        book_intro=adjusted_book_intro_html_content,
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapters,
    )


def markdown_instance(
    lang_code: str,
    resource_type: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    tw_resource_dir_: Optional[str] = None,
    sections_to_remove: list[str] = settings.MARKDOWN_SECTIONS_TO_REMOVE,
) -> markdown.Markdown:
    """
    Initialize and return a markdown.Markdown instance that can be
    used to convert Markdown content to HTML content. This mainly
    exists to implement the Law of Demeter and to clean up the
    code of TResource subclasses by DRYing things up.
    """
    if not tw_resource_dir_:
        tw_resource_dir_ = tw_resource_dir(lang_code)
    translation_words_dict_ = translation_words_dict(tw_resource_dir_)
    if not layout_for_print:  # User doesn't want to compact layout
        return markdown.Markdown(
            extensions=[
                remove_section_preprocessor.RemoveSectionExtension(
                    sections_to_remove=[
                        sections_to_remove,
                        "Markdown sections to remove",
                    ]
                ),
                link_transformer_preprocessor.LinkTransformerExtension(
                    lang_code=[lang_code, "Language code for resource"],
                    resource_requests=[
                        resource_requests,
                        "The list of resource requests contained in the document request.",
                    ],
                    translation_words_dict=[
                        translation_words_dict_,
                        "Dictionary mapping translation word asset file name sans suffix to translation word asset file path.",
                    ],
                ),
            ]
        )
    # User set layout_for_print to True, so don't bother to link
    # things since we are printing.
    return markdown.Markdown(
        extensions=[
            remove_section_preprocessor.RemoveSectionExtension(
                sections_to_remove=[sections_to_remove, "Markdown sections to remove"]
            ),
            link_print_transformer_preprocessor.LinkPrintTransformerExtension(
                lang_code=[lang_code, "Language code for resource"],
                resource_requests=[
                    resource_requests,
                    "The list of resource requests contained in the document request.",
                ],
                translation_words_dict=[
                    translation_words_dict_,
                    "Dictionary mapping translation word asset file name sans suffix to translation word asset file path.",
                ],
            ),
        ]
    )


def resource_filename(lang_code: str, resource_type: str, resource_code: str) -> str:
    """
    Return the formatted resource_filename given lang_code,
    resource_type, and resource_code.
    """
    return "{}_{}_{}".format(lang_code, resource_type, resource_code)
