"""
This module provides an API for parsing content.
"""

import time
from glob import glob
from os import scandir
from os.path import exists, join, split
from pathlib import Path
from re import compile, sub
from typing import Callable, Mapping, Optional, Sequence, cast

import markdown
import orjson
import yaml
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
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
            # marker right after it. Why? Because languages which render correctly
            # in Docx have a \p USFM marker after the chapter marker and languages
            # which did not render properly (see docstring above for particulars) in
            # Docx did not have one. Presumably the 3rd party lib we use to parse
            # HTML to Docx doesn't like spans that are not contained in a block
            # level element.
            verse_content = sub(
                chapter_marker_not_on_own_line_with_match_groups,
                chapter_marker_not_on_own_line_repair_regex,
                verse_content,
            )
    return verse_content


def attempt_to_make_usfm_parseable(
    resource_dir: str,
    resource_lookup_dto: ResourceLookupDto,
    bible_book_names: Mapping[str, str] = BOOK_NAMES,
) -> str:
    """
    Attempt to assemble and construct parseable USFM content for USFM
    resource delivered as multiple chapter directories containing verse
    content files.
    """
    logger.info(
        "About to create USFM content for non-conformant USFM to attempt to make it parseable."
    )
    usfm_content = []
    logger.info("Adding a USFM \id marker which the parser requires.")
    usfm_content.append(
        "\id {} Unnamed translation\n".format(resource_lookup_dto.book_code.upper())
    )
    logger.info("Adding a USFM \ide marker which the parser requires.")
    usfm_content.append("\ide UTF-8\n")
    logger.info("Adding a USFM \h marker which the parser requires.")
    usfm_content.append(
        "\h {}\n".format(bible_book_names[resource_lookup_dto.book_code])
    )
    subdirs = [
        file
        for file in scandir(resource_dir)
        if file.is_dir()
        and file.name != ".git"
        and file.name != "front"
        and file.name != "00"
    ]
    for chapter_dir in sorted(subdirs, key=lambda dir_entry: dir_entry.name):
        chapter_usfm_content = []
        chapter_num = chapter_dir.name
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
        usfm_content.extend(chapter_usfm_content)

    # Write the concatenated markdown content to a
    # non-clobberable filename.
    filename = join(
        resource_dir,
        "{}_{}_{}_{}.usfm".format(
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
            time.time_ns(),
        ),
    )
    logger.debug("About to write filename: %s", filename)
    with open(filename, "w") as fout:
        fout.write("".join(usfm_content))
    return filename


def find_usfm_files(
    resource_dir: str,
    usfm_glob_fmt_str: str = "{}**/*.usfm",
    usfm_ending_in_txt_glob_fmt_str: str = "{}**/*.txt",
    usfm_ending_in_txt_in_subdirectory_glob_fmt_str: str = "{}**/**/*.txt",
) -> list[str]:
    # We don't need a manifest file to find resource assets on disk. Instead
    # we use globbing and then filter down the list found to only include
    # those files that match the book code being requested. Some resources
    # do not provide a manifest. The downside to this is that we don't
    # consult the "finished" section of the manifest file.
    usfm_files = glob(usfm_glob_fmt_str.format(resource_dir))
    if not usfm_files:
        # USFM files sometimes have txt suffix instead of usfm
        usfm_files = glob(usfm_ending_in_txt_glob_fmt_str.format(resource_dir))
        # Sometimes the txt USFM files live at another location
        if not usfm_files:
            usfm_files = glob(
                usfm_ending_in_txt_in_subdirectory_glob_fmt_str.format(resource_dir)
            )
    return usfm_files


def filter_usfm_files(
    content_files: list[str],
    book_code: str,
    usfm_suffix: str = ".usfm",
    txt_suffix: str = ".txt",
) -> list[str]:
    suffix_of_content_files = str(Path(content_files[0]).suffix)
    if suffix_of_content_files == usfm_suffix:
        return [
            content_file
            for content_file in content_files
            if book_code.lower() in str(Path(content_file).stem).lower()
        ]
    elif suffix_of_content_files == txt_suffix:
        return [
            content_file
            for content_file in content_files
            if book_code.lower() in str(content_file).lower()
        ]
    return []


def convert_usfm_to_html(
    content_file: Optional[str], output_dir: str, resource_filename: str
) -> None:
    """
    Invoke the usfm_tools parser to parse the USFM file, if it exists,
    into HTML and store on disk.

    N.B. USFM-Tools books.py can raise MalformedUsfmError when the
    following code is called. The document_generator module will catch
    that error but continue with other resource requests in the same
    document request.
    """
    if content_file:
        transform.buildSingleHtmlFromFile(
            Path(content_file),
            output_dir,
            resource_filename,
        )


def usfm_asset_file(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    usfm_glob_fmt_str: str = "{}**/*.usfm",
    usfm_ending_in_txt_glob_fmt_str: str = "{}**/*.txt",
    usfm_ending_in_txt_in_subdirectory_glob_fmt_str: str = "{}**/**/*.txt",
) -> Optional[str]:
    """
    Find the USFM asset and return its path as string. Returns an
    empty string if path not found.
    """
    usfm_files = find_usfm_files(resource_dir)
    filtered_usfm_files: list[str] = []
    if usfm_files:
        filtered_usfm_files = filter_usfm_files(
            usfm_files, resource_lookup_dto.book_code
        )
    if filtered_usfm_files:
        # Some languages, like ndh-x-chindali, provide their USFM files in
        # a git repo rather than as standalone USFM files. A USFM git repo can
        # have each USFM chapter in a separate directory and each verse in a
        # separate file in that directory. However, the parser expects one USFM
        # file per book, therefore we need to concatenate the book's USFM files
        # into one USFM file.
        if len(filtered_usfm_files) > 1:
            return attempt_to_make_usfm_parseable(resource_dir, resource_lookup_dto)
        else:
            return filtered_usfm_files[0]
    return None


def usfm_asset_html(
    content_file: Optional[str],
    resource_lookup_dto: ResourceLookupDto,
    output_dir: str = settings.DOCUMENT_OUTPUT_DIR,
) -> Optional[str]:
    """
    Parse USFM asset content into HTML and return HTML as string.
    """
    resource_filename_ = resource_filename(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_lookup_dto.book_code,
    )

    t0 = time.time()
    convert_usfm_to_html(content_file, output_dir, resource_filename_)
    t1 = time.time()
    logger.debug(
        "Time to convert USFM to HTML (parsing to AST + convert AST to HTML) for %s-%s-%s: %s",
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_lookup_dto.book_code,
        t1 - t0,
    )
    html_file = join(output_dir, f"{resource_filename_}.html")

    if exists(html_file):
        html_content = read_file(html_file)
        return html_content
    return None


def usfm_chapter_verses(
    chapter_verse_span_tags: list[Tag],
    chapter_content_parser: BeautifulSoup,
    resource_lookup_dto: ResourceLookupDto,
    chapter_num: int,
    pattern: str,
    format_str: str,
) -> dict[str, str]:
    # Dictionary to hold verse number, verse value pairs.
    chapter_verses = {}
    for verse_span_tag in chapter_verse_span_tags:
        verse_ref_, upper_bound_value = verse_ref(verse_span_tag)
        verse_content_str_ = verse_content_str(
            verse_span_tag,
            chapter_content_parser,
            book_number(resource_lookup_dto.book_code),
            chapter_num,
            upper_bound_value,
        )
        # We now alter the span ID in verse_content_str_ by prepending it
        # with the lang_code for the language we are currently parsing to ensure
        # unique verse references within language scope in a multi-language
        # document.
        updated_verse_content_str = sub(
            pattern,
            format_str.format(resource_lookup_dto.lang_code),
            verse_content_str_,
        )
        chapter_verses[verse_ref_] = updated_verse_content_str
    return chapter_verses


def remove_links(parser: BeautifulSoup) -> None:
    """
    Turn HTML links into spans
    """
    a_tags = parser.find_all("a")
    # Now we modify the footnote links to be inactive, i.e., suitable for printing.
    for a_tag in a_tags:
        a_tag.name = "span"


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
    First produce HTML content from USFM content and then break the
    HTML content returned into a model.USFMBook data structure containing
    chapters, verses, footnotes, for use during interleaving with other
    resource assets.
    """
    lang_dir = lang_direction(resource_dir)
    logger.debug("Language direction: %s", lang_dir)
    content_file = usfm_asset_file(resource_lookup_dto, resource_dir)
    logger.debug("content_file: %s", content_file)
    html_content = usfm_asset_html(content_file, resource_lookup_dto)
    if html_content:
        parser = BeautifulSoup(html_content, bs_parser_type)
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

            if layout_for_print:
                remove_links(chapter_content_parser)

            chapter_footnote_tag = chapter_content_parser.find(
                "div", attrs={css_attribute_type: "footnotes"}
            )

            # Dictionary to hold verse number, verse value pairs.
            chapter_verses_ = usfm_chapter_verses(
                chapter_verse_span_tags,
                chapter_content_parser,
                resource_lookup_dto,
                chapter_num,
                pattern,
                format_str,
            )
            chapters[chapter_num] = USFMChapter(
                content=adjust_chapter_heading(chapter_content),
                verses=chapter_verses_,
                footnotes=HtmlContent(str(chapter_footnote_tag))
                if chapter_footnote_tag
                else HtmlContent(""),
            )
            return USFMBook(
                lang_code=resource_lookup_dto.lang_code,
                lang_name=resource_lookup_dto.lang_name,
                book_code=resource_lookup_dto.book_code,
                resource_type_name=resource_lookup_dto.resource_type_name,
                chapters=chapters,
                lang_direction=lang_dir,
            )
    return USFMBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters={},
        lang_direction=lang_dir,
    )


def load_manifest(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def lang_direction(
    resource_dir: str,
    manifest_glob_fmt_str: str = "{}/**/manifest.{}",
    manifest_glob_alt_fmt_str: str = "{}/manifest.{}",
) -> LangDirEnum:
    """
    Look up the language direction in the manifest file if one is
    available for this resource.
    """
    # Try to find manifest yaml at typical directory
    manifest_candidates = glob(manifest_glob_fmt_str.format(resource_dir, "yaml"))
    if not manifest_candidates:
        # Now try to find manifest yaml at parent directory of typical directory
        manifest_candidates = glob(
            manifest_glob_alt_fmt_str.format(resource_dir, "yaml")
        )
        if not manifest_candidates:
            # Some languages provide their manifest in json format.
            # Try to find manifest json at typical directory
            manifest_candidates = glob(
                manifest_glob_fmt_str.format(resource_dir, "json")
            )
            if not manifest_candidates:
                # Try to find manifest json at parent directory of typical directory
                manifest_candidates = glob(
                    manifest_glob_alt_fmt_str.format(resource_dir, "json")
                )


    if manifest_candidates:
        candidate = manifest_candidates[0]
        contents = {}
        lang_dir = ""
        suffix = str(Path(candidate).suffix)
        if suffix == "yaml":
            contents = yaml.safe_load(load_manifest(candidate))
            lang_dir = contents["dublin_core"]["language"]["direction"]
        elif suffix == "json":
            contents = orjson.loads(load_manifest(candidate))
            lang_dir = contents["target_language"]["direction"]

        if lang_dir == LangDirEnum.RTL.value:
            return LangDirEnum.RTL

    # There was no manifest or the direction in the manifest is LTR
    return LangDirEnum.LTR


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


def glob_chapter_dirs(
    resource_dir: str,
    book_code: str,
    glob_in_subdirs_fmt_str: str = "{}/**/*{}/*[0-0]*",
    glob_fmt_str: str = "{}/*{}/*[0-0]*",
) -> list[str]:
    # Some languages are organized differently on disk (e.g., depending
    # on if their assets were acquired as a git repo or a zip).
    chapter_dirs = sorted(glob(glob_in_subdirs_fmt_str.format(resource_dir, book_code)))
    if not chapter_dirs:
        chapter_dirs = sorted(glob(glob_fmt_str.format(resource_dir, book_code)))
    return chapter_dirs


def tn_chapter_verses(
    resource_dir: str, book_code: str, md: markdown.Markdown
) -> dict[int, TNChapter]:
    chapter_dirs = sorted(glob_chapter_dirs(resource_dir, book_code))
    chapter_verses = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(Path(chapter_dir).name)
        intro_html = tn_intro_html(chapter_dir, md)
        intro_html = intro_html if intro_html else ""
        verses_html = tn_verses_html(chapter_dir, book_code, md)
        chapter_verses[chapter_num] = TNChapter(
            intro_html=intro_html, verses=verses_html
        )
    return chapter_verses


def tn_intro_html(
    chapter_dir: str,
    md: markdown.Markdown,
    glob_md_fmt_str: str = "{}/*intro.md",
    glob_txt_fmt_str: str = "{}/*intro.txt",
) -> Optional[str]:
    intro_paths = sorted(glob(glob_md_fmt_str.format(chapter_dir)))
    if not intro_paths:
        intro_paths = sorted(glob(glob_txt_fmt_str.format(chapter_dir)))
    return md.convert(read_file(intro_paths[0])) if intro_paths else None


def adjust_html_tags(html_content: str) -> str:
    return html_content.replace(H1, H5)


def adjust_book_intro(
    resource_dir: str, book_code: str, md: markdown.Markdown, include: bool
) -> str:
    book_intro_paths = sorted(glob(f"{resource_dir}/*{book_code}/front/intro.md"))
    if not book_intro_paths:
        book_intro_paths = sorted(glob(f"{resource_dir}/*{book_code}/front/intro.txt"))
    book_intro_html = (
        read_file(book_intro_paths[0]) if book_intro_paths and include else ""
    )
    return md.convert(book_intro_html)


def tn_verses_html(
    chapter_dir: str,
    book_code: str,
    md: markdown.Markdown,
    book_names: Mapping[str, str] = BOOK_NAMES,
    verse_fmt_str: str = "<h4>{} {}</h4>\n{}",
    glob_md_fmt_str: str = "{}/*[0-9]*.md",
    glob_txt_fmt_str: str = "{}/*[0-9]*.md",
) -> dict[VerseRef, str]:
    verse_paths = sorted(glob(glob_md_fmt_str.format(chapter_dir)))
    if not verse_paths:
        verse_paths = sorted(glob(glob_txt_fmt_str.format(chapter_dir)))
    verses_html = {}
    for filepath in verse_paths:
        verse_ref = Path(filepath).stem
        verse_md_content = read_file(filepath)
        verse_html_content = md.convert(verse_md_content)
        adjusted_verse_html_content = adjust_html_tags(verse_html_content)
        verses_html[verse_ref] = verse_fmt_str.format(
            book_names[book_code], verse_ref, adjusted_verse_html_content
        )
    return verses_html


def tn_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    include_tn_book_intros: bool = False,
) -> TNBook:
    lang_dir = lang_direction(resource_dir)
    md = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
    )
    chapter_verses = tn_chapter_verses(resource_dir, resource_lookup_dto.book_code, md)
    adjusted_book_intro = adjust_book_intro(
        resource_dir, resource_lookup_dto.book_code, md, include_tn_book_intros
    )
    return TNBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        book_intro=adjusted_book_intro,
        chapters=chapter_verses,
        lang_direction=lang_dir,
    )


def tq_chapter_verses(
    resource_dir: str,
    book_code: str,
    md: markdown.Markdown,
    book_names: Mapping[str, str] = BOOK_NAMES,
    verse_paths_glob_fmt_str: str = "{}/*[0-9]*.md",
    h1: str = H1,
    h5: str = H5,
    verse_label_fmt_str: str = "<h4>{} {}:{}</h4>\n{}",
) -> dict[int, TQChapter]:
    chapter_dirs = sorted(glob_chapter_dirs(resource_dir, book_code))
    chapter_verses = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(split(chapter_dir)[-1])
        verse_paths = sorted(glob(verse_paths_glob_fmt_str.format(chapter_dir)))
        verses_html: dict[VerseRef, str] = {}
        for filepath in verse_paths:
            verse_ref = Path(filepath).stem
            verse_md_content = read_file(filepath)
            verse_html_content = md.convert(verse_md_content)
            adjusted_verse_html_content = sub(h1, h5, verse_html_content)
            verses_html[verse_ref] = verse_label_fmt_str.format(
                book_names[book_code],
                chapter_num,
                str(int(verse_ref)) if "0" in verse_ref else verse_ref,
                adjusted_verse_html_content,
            )
            chapter_verses[chapter_num] = TQChapter(verses=verses_html)
    return chapter_verses


def tq_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
) -> TQBook:
    lang_dir = lang_direction(resource_dir)
    md = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
    )
    chapter_verses = tq_chapter_verses(resource_dir, resource_lookup_dto.book_code, md)
    return TQBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapter_verses,
        lang_direction=lang_dir,
    )


def tw_sort_key(name_content_pair: TWNameContentPair) -> str:
    return name_content_pair.localized_word


def tw_name_content_pairs(
    resource_dir: str,
    md: markdown.Markdown,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
) -> list[TWNameContentPair]:
    translation_word_filepaths_: list[str] = translation_word_filepaths(resource_dir)
    name_content_pairs: list[TWNameContentPair] = []
    for translation_word_filepath in translation_word_filepaths_:
        translation_word_content = MarkdownContent(read_file(translation_word_filepath))
        localized_translation_word_ = localized_translation_word(
            translation_word_content
        )
        html_word_content = md.convert(translation_word_content)
        html_word_content = sub(h2, h4, html_word_content)
        html_word_content = sub(h1, h3, html_word_content)
        name_content_pairs.append(
            TWNameContentPair(localized_translation_word_, html_word_content)
        )

    return sorted(name_content_pairs, key=tw_sort_key)


def tw_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
) -> TWBook:
    lang_dir = lang_direction(resource_dir)
    md = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
        resource_dir,
    )
    name_content_pairs = tw_name_content_pairs(resource_dir, md)
    return TWBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        name_content_pairs=name_content_pairs,
        lang_direction=lang_dir,
    )


def bc_book_intro_html_content(
    resource_dir: str,
    book_code: str,
    md: markdown.Markdown,
    book_intro_glob_path_fmt_str: str = "{}/*{}/intro.md",
) -> str:
    book_intro_paths = glob(
        book_intro_glob_path_fmt_str.format(resource_dir, book_code)
    )
    book_intro_md_content = read_file(book_intro_paths[0]) if book_intro_paths else ""
    book_intro_html_content = md.convert(book_intro_md_content)
    adjusted_book_intro_html_content = adjust_commentary_headings(
        book_intro_html_content
    )
    return adjusted_book_intro_html_content


def bc_chapters(
    resource_dir: str,
    book_code: str,
    md: markdown.Markdown,
    chapter_dirs_glob_fmt_str: str = "{}/*{}/*[0-9]*",
    parser_type: str = "html.parser",
    url_fmt_str: str = settings.BC_ARTICLE_URL_FMT_STR,
) -> dict[int, BCChapter]:
    chapter_dirs = sorted(
        glob(chapter_dirs_glob_fmt_str.format(resource_dir, book_code))
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
    return chapters


def bc_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
) -> BCBook:
    # Create the Markdown instance once and have it use our markdown
    # extensions.
    md = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
    )
    return BCBook(
        book_intro=bc_book_intro_html_content(
            resource_dir, resource_lookup_dto.book_code, md
        ),
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=bc_chapters(resource_dir, resource_lookup_dto.book_code, md),
    )


# Define a mapping from resource types to corresponding functions
RESOURCE_TYPE_FUNCTIONS: dict[str, Callable[..., BookContent]] = {
    **{typ: usfm_book_content for typ in settings.ALL_USFM_RESOURCE_TYPES},
    **{typ: tn_book_content for typ in settings.ALL_TN_RESOURCE_TYPES},
    **{typ: tq_book_content for typ in settings.ALL_TQ_RESOURCE_TYPES},
    **{typ: tw_book_content for typ in settings.ALL_TW_RESOURCE_TYPES},
    **{typ: bc_book_content for typ in settings.BC_RESOURCE_TYPES},
}


def book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
) -> Optional[BookContent]:
    """Build and return the BookContent instance."""
    for resource_type_, content_func in RESOURCE_TYPE_FUNCTIONS.items():
        if resource_lookup_dto.resource_type in resource_type_:
            return content_func(
                resource_lookup_dto,
                resource_dir,
                resource_requests,
                layout_for_print,
            )
    return None


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


def resource_filename(lang_code: str, resource_type: str, book_code: str) -> str:
    """
    Return the formatted resource_filename given lang_code,
    resource_type, and book_code.
    """
    return "{}_{}_{}".format(lang_code, resource_type, book_code)
