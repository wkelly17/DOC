"""
This module provides an API for parsing content.
"""

import os
import pathlib
import re
import time
from collections.abc import Sequence
from glob import glob
from typing import Optional

import bs4
import markdown
from document.config import settings
from document.domain import bible_books, model
from document.markdown_extensions import (
    link_transformer_preprocessor,
    remove_section_preprocessor,
)
from document.utils import file_utils, html_parsing_utils, tw_utils
from usfm_tools.transform import UsfmTransform  # type: ignore

logger = settings.logger(__name__)

H1, H2, H3, H4 = "h1", "h2", "h3", "h4"


def attempt_asset_content_rescue(
    resource_dir: str, resource_lookup_dto: model.ResourceLookupDto
) -> str:
    """
    Attempt to assemble and construct parseable USFM content for USFM
    resource delivered as multiple populated directories in chapter >
    verses layout.
    """
    subdirs = [
        file
        for file in os.scandir(resource_dir)
        if file.is_dir()
        and file.name != ".git"
        and file.name != "front"
        and file.name != "00"
    ]
    logger.info("About to create markdown content for non-conformant USFM")
    markdown_content = []
    markdown_content.append(
        "\id {} Unnamed translation\n".format(resource_lookup_dto.resource_code.upper())
    )
    markdown_content.append("\ide UTF-8\n")
    markdown_content.append(
        "\h {}\n".format(bible_books.BOOK_NAMES[resource_lookup_dto.resource_code])
    )
    for chapter_dir in sorted(subdirs, key=lambda dir_entry: dir_entry.name):
        # Get verses for chapter
        chapter_markdown_content = []
        chapter_num = chapter_dir.name
        # Add the chapter USFM marker
        chapter_markdown_content.append("\c {}\n".format(int(chapter_num)))
        # Read the verses for this chapter
        chapter_verse_files = sorted(
            [
                file.path
                for file in os.scandir(chapter_dir)
                if file.is_file() and file.name != "title.txt"
            ]
        )
        for markdown_file in chapter_verse_files:
            with open(markdown_file, "r") as fin:
                chapter_markdown_content.append(fin.read())
                chapter_markdown_content.append("\n")
        # Store the chapter content into the collection of
        # all chapters content
        markdown_content.extend(chapter_markdown_content)

    # Write the concatenated markdown content to a
    # non-clobberable filename.
    filename = os.path.join(
        resource_dir,
        "{}_{}_{}_{}.md".format(
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.resource_code,
            time.time_ns(),
        ),
    )
    logger.debug("About to write filename: %s", filename)
    with open(filename, "w") as fout:
        fout.write("".join(markdown_content))
    return filename


def asset_content(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    output_dir: str = settings.output_dir(),
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
    usfm_content_files = glob("{}**/*.usfm".format(resource_dir))
    if not usfm_content_files:
        # USFM files sometimes have txt suffix instead of usfm
        txt_content_files = glob("{}**/*.txt".format(resource_dir))
        # Sometimes the txt USFM files live at another location
        if not txt_content_files:
            txt_content_files = glob("{}**/**/*.txt".format(resource_dir))

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
            in str(usfm_content_file).lower()
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
        UsfmTransform.buildSingleHtmlFromFile(
            pathlib.Path(content_files[0]),
            output_dir,
            resource_filename_,
        )
        # Read the HTML file into _content.
        html_file = "{}.html".format(os.path.join(output_dir, resource_filename_))
        assert os.path.exists(html_file)
        html_content = file_utils.read_file(html_file)
    return html_content


def initialize_verses_html(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
) -> model.BookContent:
    """Build and return the HTML content."""
    book_content: model.BookContent
    if resource_lookup_dto.resource_type in usfm_resource_types:
        book_content = initialize_verses_html_usfm(
            resource_lookup_dto, resource_dir, resource_requests
        )
    elif resource_lookup_dto.resource_type in tn_resource_types:
        book_content = initialize_verses_html_tn(
            resource_lookup_dto, resource_dir, resource_requests
        )
    elif resource_lookup_dto.resource_type in tq_resource_types:
        book_content = initialize_verses_html_tq(
            resource_lookup_dto, resource_dir, resource_requests
        )
    elif resource_lookup_dto.resource_type in tw_resource_types:
        book_content = initialize_verses_html_tw(
            resource_lookup_dto, resource_dir, resource_requests
        )
    return book_content


def initialize_verses_html_usfm(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
) -> model.USFMBook:
    html_content = asset_content(resource_lookup_dto, resource_dir)
    parser = bs4.BeautifulSoup(html_content, "html.parser")

    chapter_breaks = parser.find_all(H2, attrs={"class": "c-num"})
    localized_chapter_heading = chapter_breaks[0].get_text().split()[0]
    chapters: dict[model.ChapterNum, model.USFMChapter] = {}
    for chapter_break in chapter_breaks:
        chapter_num = int(chapter_break.get_text().split()[1])
        chapter_content = html_parsing_utils.tag_elements_between(
            parser.find(
                H2,
                text="{} {}".format(localized_chapter_heading, chapter_num),
            ),
            parser.find(
                H2,
                text="{} {}".format(localized_chapter_heading, chapter_num + 1),
            ),
        )
        chapter_content = [str(tag) for tag in list(chapter_content)]
        chapter_content_parser = bs4.BeautifulSoup(
            "".join(chapter_content),
            "html.parser",
        )
        chapter_verse_tags = chapter_content_parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        chapter_footnote_tag = chapter_content_parser.find(
            "div", attrs={"class": "footnotes"}
        )
        chapter_footnotes = (
            model.HtmlContent(str(chapter_footnote_tag))
            if chapter_footnote_tag
            else model.HtmlContent("")
        )
        # Get each verse opening span tag and then the actual verse text for
        # this chapter and enclose them each in a p element.
        chapter_verse_list = [
            "<p>{} {}</p>".format(verse, verse.next_sibling)
            for verse in chapter_verse_tags
        ]
        # Dictionary to hold verse number, verse value pairs.
        chapter_verses: dict[str, str] = {}
        for verse_element in chapter_verse_list:
            (verse_num, verse_content_str) = verse_num_and_verse_content_str(
                book_number(resource_lookup_dto.resource_code),
                resource_lookup_dto.lang_code,
                chapter_num,
                chapter_content_parser,
                verse_element,
            )
            chapter_verses[verse_num] = verse_content_str
        chapters[chapter_num] = model.USFMChapter(
            content=chapter_content,
            verses=chapter_verses,
            footnotes=chapter_footnotes,
        )
    return model.USFMBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapters,
    )


def verse_num_and_verse_content_str(
    book_number: str,
    lang_code: str,
    chapter_num: int,
    chapter_content_parser: bs4.BeautifulSoup,
    verse_element: str,
    pattern: str = settings.VERSE_ANCHOR_ID_FMT_STR,
    format_str: str = settings.VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR,
) -> tuple[str, model.HtmlContent]:
    """
    Handle some messy initialization and return the
    chapter_num and verse_content_str.
    """
    # Rather than a single verse num, the item in
    # verse_num may be a verse range, e.g., 1-2.
    # See test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order
    # for test that triggers this situation.
    # Get the verse num from the verse HTML tag's id value.
    # split is more performant than re.
    # See https://stackoverflow.com/questions/7501609/python-re-split-vs-split
    verse_num = str(verse_element).split("-v-")[1].split('"')[0]
    # Check for hyphen in the range
    verse_num_components = verse_num.split("-")
    if len(verse_num_components) > 1:
        upper_bound_value = int(verse_num_components[1]) + 1
        # Get rid of leading zeroes on first verse number
        # in range.
        verse_num_int = int(verse_num_components[0])
        # Get rid of leading zeroes on second verse number
        # in range.
        verse_num2_int = int(verse_num_components[1])
        # Recreate the verse range, now without leading
        # zeroes.
        verse_num = "{}-{}".format(str(verse_num_int), str(verse_num2_int))
        # logger.debug(
        #     "chapter_num: %s, verse_num is a verse range: %s",
        #     chapter_num,
        #     verse_num,
        # )
    else:
        upper_bound_value = int(verse_num) + 1
        # Get rid of leading zeroes.
        verse_num = str(int(verse_num))

    # Create the lower and upper search bounds for the
    # BeautifulSoup HTML parser.
    lower_id = "{}-ch-{}-v-{}".format(
        str(book_number).zfill(3),
        str(chapter_num).zfill(3),
        verse_num.zfill(3),
    )
    upper_id = "{}-ch-{}-v-{}".format(
        str(book_number).zfill(3),
        str(chapter_num).zfill(3),
        str(upper_bound_value).zfill(3),
    )
    # Using the upper and lower parse a verse worth of HTML
    # content.

    lower_tag = chapter_content_parser.find(
        "span",
        attrs={"class": "v-num", "id": lower_id},
    )
    upper_tag = chapter_content_parser.find(
        "span",
        attrs={"class": "v-num", "id": upper_id},
    )
    verse_content_tags = html_parsing_utils.tag_elements_between(
        lower_tag,
        upper_tag,
    )
    verse_content = [str(tag) for tag in list(verse_content_tags)]
    # HACK to prevent BeautifulSoup from sometimes
    # recapitulating all the verses after the current verse and
    # stuffing them into the same verse.
    verse_content_str = "".join(verse_content[:2])
    # At this point we alter verse_content_str span's ID by prepending the
    # lang_code to ensure unique verse references within language scope in a
    # multi-language document.
    verse_content_str = re.sub(
        pattern,
        format_str.format(lang_code),
        verse_content_str,
    )
    return str(verse_num), model.HtmlContent(verse_content_str)


def initialize_verses_html_tn(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
) -> model.TNBook:
    # Initialize the Python-Markdown extensions that get invoked
    # when md.convert is called.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
    )
    chapter_dirs = sorted(
        glob(
            "{}/**/*{}/*[0-9]*".format(
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
                "{}/*{}/*[0-9]*".format(
                    resource_dir,
                    resource_lookup_dto.resource_code,
                )
            )
        )
    chapter_verses: dict[int, model.TNChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(os.path.split(chapter_dir)[-1])
        intro_paths = glob("{}/*intro.md".format(chapter_dir))
        # For some languages, TN assets are stored in .txt files
        # rather of .md files.
        if not intro_paths:
            intro_paths = glob("{}/*intro.txt".format(chapter_dir))
        intro_path = intro_paths[0] if intro_paths else None
        intro_md = ""
        intro_html = ""
        if intro_path:
            intro_md = file_utils.read_file(intro_path)
            intro_html = md.convert(intro_md)
        verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
        # For some languages, TN assets are stored in .txt files
        # rather of .md files.
        if not verse_paths:
            verse_paths = sorted(glob("{}/*[0-9]*.txt".format(chapter_dir)))
        verses_html: dict[int, str] = {}
        for filepath in verse_paths:
            verse_num = int(pathlib.Path(filepath).stem)
            verse_content = ""
            verse_content = file_utils.read_file(filepath)
            verse_content = md.convert(verse_content)
            verses_html[verse_num] = verse_content
        chapter_payload = model.TNChapter(intro_html=intro_html, verses=verses_html)
        chapter_verses[chapter_num] = chapter_payload
    # Get the book intro if it exists
    book_intro_path = glob(
        "{}/*{}/front/intro.md".format(
            resource_dir,
            resource_lookup_dto.resource_code,
        )
    )
    # For some languages, TN assets are stored in .txt files
    # rather of .md files.
    if not book_intro_path:
        book_intro_path = glob(
            "{}/*{}/front/intro.txt".format(
                resource_dir, resource_lookup_dto.resource_code
            )
        )
    book_intro_html = model.HtmlContent("")
    if book_intro_path:
        book_intro_html = file_utils.read_file(book_intro_path[0])
        book_intro_html = md.convert(book_intro_html)
    return model.TNBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        intro_html=book_intro_html,
        chapters=chapter_verses,
    )


def initialize_verses_html_tq(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
) -> model.TQBook:
    # Create the Markdown instance once and have it use our markdown
    # extensions.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
    )
    chapter_dirs = sorted(
        glob(
            "{}/**/*{}/*[0-9]*".format(resource_dir, resource_lookup_dto.resource_code)
        )
    )
    # Some languages are organized differently on disk (e.g., depending
    # on if their assets were acquired as a git repo or a zip).
    # We handle this here.
    if not chapter_dirs:
        chapter_dirs = sorted(
            glob(
                "{}/*{}/*[0-9]*".format(resource_dir, resource_lookup_dto.resource_code)
            )
        )
    chapter_verses: dict[int, model.TQChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(os.path.split(chapter_dir)[-1])
        verse_paths = sorted(glob("{}/*[0-9]*.md".format(chapter_dir)))
        # NOTE For some languages, TN assets may be stored in .txt files
        # rather of .md files. Though I have not yet seen this, this
        # may also be true of TQ assets. If it is, then the following
        # commented out code would suffice.
        # if not verse_paths:
        #     verse_paths = sorted(glob("{}/*[0-9]*.txt".format(chapter_dir)))
        verses_html: dict[int, str] = {}
        for filepath in verse_paths:
            verse_num = int(pathlib.Path(filepath).stem)
            verse_content = file_utils.read_file(filepath)
            verse_content = md.convert(verse_content)
            verses_html[verse_num] = verse_content
        chapter_verses[chapter_num] = model.TQChapter(verses=verses_html)
    return model.TQBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapter_verses,
    )


def initialize_verses_html_tw(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
) -> model.TWBook:
    # Create the Markdown instance once and have it use our markdown
    # extensions.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        resource_dir,
    )
    translation_word_filepaths = tw_utils.translation_word_filepaths(resource_dir)
    name_content_pairs: list[model.TWNameContentPair] = []
    for translation_word_filepath in translation_word_filepaths:
        translation_word_content = model.MarkdownContent(
            file_utils.read_file(translation_word_filepath)
        )
        # Translation words are bidirectional. By that I mean that when you are
        # at a verse there follows, after translation questions, links to the
        # translation words that occur in that verse. But then when you navigate
        # to the word by clicking such a link, at the end of the resulting
        # translation word note there is a section called 'Uses:' that also has
        # links back to the verses wherein the word occurs.
        localized_translation_word = tw_utils.localized_translation_word(
            translation_word_content
        )
        html_word_content = md.convert(translation_word_content)
        # Make adjustments to the HTML here.
        html_word_content = re.sub(H2, H4, html_word_content)
        html_word_content = re.sub(H1, H3, html_word_content)
        name_content_pairs.append(
            model.TWNameContentPair(
                localized_word=localized_translation_word, content=html_word_content
            )
        )

    # Make mypy --strict happy; mypy doesn't pick up types in a
    # lambda.
    def sort_key(name_content_pair: model.TWNameContentPair) -> str:
        return name_content_pair.localized_word

    return model.TWBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        # Sort the name content pairs by localized translation word
        name_content_pairs=sorted(name_content_pairs, key=sort_key),
    )


def markdown_instance(
    lang_code: str,
    resource_type: str,
    resource_requests: Sequence[model.ResourceRequest],
    tw_resource_dir: Optional[str] = None,
) -> markdown.Markdown:
    """
    Initialize and return a markdown.Markdown instance that can be
    used to convert Markdown content to HTML content. This mainly
    exists to implement the Law of Demeter and to clean up the
    code of TResource subclasses by DRYing things up.
    """
    if not tw_resource_dir:
        tw_resource_dir = tw_utils.tw_resource_dir(lang_code)
    translation_words_dict = tw_utils.translation_words_dict(tw_resource_dir)
    return markdown.Markdown(
        extensions=[
            remove_section_preprocessor.RemoveSectionExtension(),
            link_transformer_preprocessor.LinkTransformerExtension(
                lang_code=[lang_code, "Language code for resource"],
                resource_requests=[
                    resource_requests,
                    "The list of resource requests contained in the document request.",
                ],
                translation_words_dict=[
                    translation_words_dict,
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


def book_number(resource_code: str) -> str:
    """
    Return the book number associated with the resource_code, e.g., gen ->
    01.
    """
    return bible_books.BOOK_NUMBERS[resource_code]
