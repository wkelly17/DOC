"""
This module provides an API for parsing content.
"""

import os
import pathlib
import re
import time
from collections.abc import Mapping, Sequence
from glob import glob
from typing import Optional, cast

import bs4
import markdown
from document.config import settings
from document.domain import bible_books, model
from document.markdown_extensions import (
    link_transformer_preprocessor,
    link_print_transformer_preprocessor,
    remove_section_preprocessor,
)
from document.utils import file_utils, html_parsing_utils, tw_utils
from usfm_tools.transform import UsfmTransform  # type: ignore

logger = settings.logger(__name__)

H1, H2, H3, H4 = "h1", "h2", "h3", "h4"


def attempt_asset_content_rescue(
    resource_dir: str,
    resource_lookup_dto: model.ResourceLookupDto,
    bible_book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
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
        "\h {}\n".format(bible_book_names[resource_lookup_dto.resource_code])
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
        html_file = os.path.join(output_dir, "{}.html".format(resource_filename_))
        assert os.path.exists(html_file)
        html_content = file_utils.read_file(html_file)
    return html_content


def book_content(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
    bc_resource_types: Sequence[str] = settings.BC_RESOURCE_TYPES,
) -> model.BookContent:
    """Build and return the HTML book content instance."""
    book_content: model.BookContent
    if resource_lookup_dto.resource_type in usfm_resource_types:
        book_content = usfm_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
    elif resource_lookup_dto.resource_type in tn_resource_types:
        book_content = tn_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
    elif resource_lookup_dto.resource_type in tq_resource_types:
        book_content = tq_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
    elif resource_lookup_dto.resource_type in tw_resource_types:
        book_content = tw_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
    elif resource_lookup_dto.resource_type in bc_resource_types:
        book_content = bc_book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )
    return book_content


def is_footnote_ref(id: str) -> bool:
    """
    Predicate function used to find links that have an href value that
    we expect footnote references to have.
    """
    return id is not None and re.compile("ref-fn-.*").match(id) is not None


def usfm_book_content(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
    h2: str = H2,
    bs_parser_type: str = "html.parser",
    css_attribute_type: str = "class",
) -> model.USFMBook:
    html_content = asset_content(resource_lookup_dto, resource_dir)
    parser = bs4.BeautifulSoup(html_content, bs_parser_type)

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
    chapters: dict[model.ChapterNum, model.USFMChapter] = {}
    for chapter_break in chapter_break_tags:
        chapter_num = int(chapter_break.get_text().split()[1])
        chapter_content = html_parsing_utils.tag_elements_between(
            parser.find(
                h2,
                text=re.compile(".* {}".format(chapter_num)),
            ),
            parser.find(
                h2,
                text=re.compile(".* {}".format(chapter_num + 1)),
            ),
        )
        chapter_content = [str(tag) for tag in list(chapter_content)]
        chapter_content_parser = bs4.BeautifulSoup(
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
                chapter_footnotes_parser = bs4.BeautifulSoup(
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
            model.HtmlContent(str(chapter_footnote_tag))
            if chapter_footnote_tag
            else model.HtmlContent("")
        )

        # Dictionary to hold verse number, verse value pairs.
        chapter_verses: dict[str, str] = {}
        for verse_span_tag in chapter_verse_span_tags:
            (verse_ref, verse_content_str) = verse_ref_and_verse_content_str(
                book_number(resource_lookup_dto.resource_code),
                resource_lookup_dto.lang_code,
                chapter_num,
                chapter_content_parser,
                verse_span_tag,
            )
            chapter_verses[verse_ref] = verse_content_str
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


def verse_ref_and_verse_content_str(
    book_number: str,
    lang_code: str,
    chapter_num: int,
    chapter_content_parser: bs4.BeautifulSoup,
    verse_span_tag: str,
    pattern: str = settings.VERSE_ANCHOR_ID_FMT_STR,
    format_str: str = settings.VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR,
    num_zeros: int = 3,
    css_attribute_type: str = "class",
) -> tuple[str, model.HtmlContent]:
    """Return the verse_ref and verse_content_str."""
    # Rather than a single verse num, the item in
    # verse_num may be a verse range, e.g., 1-2.
    # See test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order
    # for test that triggers this situation.
    # Get the verse num from the verse HTML tag's id value.
    # NOTE: split is more performant than re.
    # See https://stackoverflow.com/questions/7501609/python-re-split-vs-split
    verse_ref = str(verse_span_tag).split("-v-")[1].split('"')[0]
    # Check for hyphen in the range
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

    # Create the lower and upper search bounds for the
    # BeautifulSoup HTML parser.
    lower_id = "{}-ch-{}-v-{}".format(
        str(book_number).zfill(num_zeros),
        str(chapter_num).zfill(num_zeros),
        verse_ref.zfill(num_zeros),
    )
    upper_id = "{}-ch-{}-v-{}".format(
        str(book_number).zfill(num_zeros),
        str(chapter_num).zfill(num_zeros),
        str(upper_bound_value).zfill(num_zeros),
    )
    # Using the upper and lower tag bounds parse a verse worth of HTML
    # content.
    lower_tag = chapter_content_parser.find(
        "span",
        attrs={css_attribute_type: "v-num", "id": lower_id},
    )
    upper_tag = chapter_content_parser.find(
        "span",
        attrs={css_attribute_type: "v-num", "id": upper_id},
    )
    # logger.debug("lower_tag: %s", lower_tag)
    # logger.debug("upper_tag: %s", upper_tag)

    # A verse span can be enclosed in a p element parent (but not always)
    # and if this is the arrangement then it is this p element that is a
    # sibling of all other chapter level content. Since
    # html-parsing_utils.tag_elements_between uses next sibling to advance
    # through document elements it is important to give it elements as
    # parameters to start with that exist at the same level in the document
    # in a sibling relationship. It turns out that the USFM to HTML parser
    # emits nearly all document elements as siblings of each other rather
    # than verses or chapters, say, being enclosed in some verse or chapter
    # level HTML element. This is because the USFM spec is necessarily open
    # to accomodate various language elements which can be combined in various
    # ways that do not enclose one another cleanly - or at least making a
    # parser that can close over all possible USFM element combinations has
    # not been created yet and I suspect can't be created. You'd have to
    # know what parsing grammar theory describes the USFM spec to
    # say definitively - something I have not yet investigated.

    # Save the original lower_tag so that we use it for some
    # corrective actions that we may need to take later.
    orig_lower_tag = lower_tag
    try:
        # logger.debug("lower_tag.parent: %s", lower_tag.parent)
        # logger.debug("upper_tag.parent: %s", upper_tag.parent)
        # The isinstance checks are to make mypy happy.
        if (
            isinstance(lower_tag, bs4.element.Tag)
            and isinstance(upper_tag, bs4.element.Tag)
            and lower_tag.parent != upper_tag.parent
        ):
            lower_tag = lower_tag.parent
            upper_tag = upper_tag.parent
    except Exception:
        # Handle case where upper_tag is None in which case the last sibling
        # element in the chapter could be footnotes. We'll set the upper_tag to
        # that footnotes node (or None if it does not exist) so that we don't
        # include footnotes in the last verse's content. Footnotes are rendered
        # after the chapter's verse content so we don't want them included
        # additionally/accidentally here.
        footnotes_for_chapter = chapter_content_parser.find("div", class_="footnotes")
        upper_tag = footnotes_for_chapter
    # finally:
    #     logger.debug("Using lower_tag: %s", lower_tag)
    #     logger.debug("Using upper_tag: %s", upper_tag)

    verse_content_tags = html_parsing_utils.tag_elements_between(
        lower_tag,
        upper_tag,
    )
    verse_content_tags = list(verse_content_tags)
    # logger.debug("len(verse_content_tags): %s", len(verse_content_tags))
    verse_content = [str(tag) for tag in verse_content_tags]
    # logger.debug("verse_content: %s", verse_content)
    verse_content_str = "".join(verse_content)
    # logger.debug("verse_content_str: %s", verse_content_str)
    # At this point verse_content_str may recapitulate previous verse spans
    # that are enclosed in the same p element as the current verse due to
    # the complexity of the HTML document being parsed (which mirrors the
    # complexity of the USFM grammar). To remedy this, we get the span id
    # for the current verse (the one that should be shown) and use it to
    # find where in the verse_content_str the current verse starts so that
    # we can effectively discard the recapitulated previous verse spans that
    # should not be shown.
    orig_lower_tag_parser = bs4.BeautifulSoup(str(orig_lower_tag), "html.parser")
    # Split the verse_content_str on the id of the span for the
    # current verse.
    span_tag: bs4.element.Tag = cast(
        bs4.element.Tag, orig_lower_tag_parser.find("span")
    )  # Make mypy happy
    # cast usage to make mypy happy again
    split_verse_content_str = verse_content_str.split(cast(str, span_tag.get("id")))
    # logger.debug("split_verse_content_str: %s", split_verse_content_str)
    # Keep the content for the current verse onward.
    verse_content_str = '<p>\n<span class="v-num" id="{}'.format(
        split_verse_content_str[-1]
    )
    # Now it can be the case, e.g., Jonah 2:2, that instead of the verse we
    # want being prepended with recapitulated verse spans we don't want to
    # show for this verse, there can also be verse spans being appended to
    # the current verse that we don't want to show. So we must detect those
    # and effectively discard them as well.
    verse_content_str_parser = bs4.BeautifulSoup(verse_content_str, "html.parser")
    verse_span_tags = verse_content_str_parser.find_all(
        "span", attrs={css_attribute_type: "v-num"}
    )
    if len(verse_span_tags) > 1:
        # cast is to make mypy happy
        first_unwanted_appended_span_tag: bs4.element.Tag = cast(
            bs4.element.Tag, verse_span_tags[1]
        )
        # cast is to make mypy happy
        verse_content_str_split = verse_content_str.split(
            str(first_unwanted_appended_span_tag)
        )
        verse_content_str = "{}</p>".format(verse_content_str_split[0])
    # At this point we alter verse_content_str span's ID by prepending the
    # lang_code to ensure unique verse references within language scope in a
    # multi-language document.
    verse_content_str = re.sub(
        pattern,
        format_str.format(lang_code),
        verse_content_str,
    )
    # logger.debug("verse_ref: %s", verse_ref)
    # logger.debug("updated verse_content_str: %s", verse_content_str)
    return str(verse_ref), model.HtmlContent(verse_content_str)


def tn_book_content(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
    chapter_dirs_glob_fmt_str: str = "{}/**/*{}/*[0-9]*",
    chapter_dirs_glob_alt_fmt_str: str = "{}/*{}/*[0-9]*",
    intro_paths_glob_fmt_str: str = "{}/*intro.md",
    intro_paths_glob_alt_fmt_str: str = "{}/*intro.txt",
    verse_paths_glob_fmt_str: str = "{}/*[0-9]*.md",
    verse_paths_glob_alt_fmt_str: str = "{}/*[0-9]*.txt",
    book_intro_paths_glob_fmt_str: str = "{}/*{}/front/intro.md",
    book_intro_paths_glob_alt_fmt_str: str = "{}/*{}/front/intro.txt",
) -> model.TNBook:
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
    chapter_verses: dict[int, model.TNChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(os.path.split(chapter_dir)[-1])
        intro_paths = glob(intro_paths_glob_fmt_str.format(chapter_dir))
        # For some languages, TN assets are stored in .txt files
        # rather than .md files.
        if not intro_paths:
            intro_paths = glob(intro_paths_glob_alt_fmt_str.format(chapter_dir))
        intro_path = intro_paths[0] if intro_paths else None
        intro_md = ""
        intro_html = ""
        if intro_path:
            intro_md = file_utils.read_file(intro_path)
            intro_html = md.convert(intro_md)
        verse_paths = sorted(glob(verse_paths_glob_fmt_str.format(chapter_dir)))
        # For some languages, TN assets are stored in .txt files
        # rather than .md files.
        if not verse_paths:
            verse_paths = sorted(glob(verse_paths_glob_alt_fmt_str.format(chapter_dir)))
        verses_html: dict[int, str] = {}
        for filepath in verse_paths:
            verse_num = int(pathlib.Path(filepath).stem)
            verse_md_content = file_utils.read_file(filepath)
            verse_html_content = md.convert(verse_md_content)
            verses_html[verse_num] = verse_html_content
        chapter_payload = model.TNChapter(intro_html=intro_html, verses=verses_html)
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


def tq_book_content(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
    chapter_dirs_glob_fmt_str: str = "{}/**/*{}/*[0-9]*",
    chapter_dirs_glob_alt_fmt_str: str = "{}/*{}/*[0-9]*",
    verse_paths_glob_fmt_str: str = "{}/*[0-9]*.md",
) -> model.TQBook:
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
    chapter_verses: dict[int, model.TQChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(os.path.split(chapter_dir)[-1])
        verse_paths = sorted(glob(verse_paths_glob_fmt_str.format(chapter_dir)))
        # NOTE For some languages, TN assets may be stored in .txt files
        # rather of .md files. Though I have not yet seen this, this
        # may also be true of TQ assets. If it is, then the following
        # commented out code would suffice.
        # if not verse_paths:
        #     verse_paths = sorted(glob("{}/*[0-9]*.txt".format(chapter_dir)))
        verses_html: dict[int, str] = {}
        for filepath in verse_paths:
            verse_num = int(pathlib.Path(filepath).stem)
            verse_md_content = file_utils.read_file(filepath)
            verse_html_content = md.convert(verse_md_content)
            verses_html[verse_num] = verse_html_content
        chapter_verses[chapter_num] = model.TQChapter(verses=verses_html)
    return model.TQBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapter_verses,
    )


def tw_book_content(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
) -> model.TWBook:
    # Create the Markdown instance once and have it use our markdown
    # extensions.
    md: markdown.Markdown = markdown_instance(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_requests,
        layout_for_print,
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
        html_word_content = re.sub(h2, h4, html_word_content)
        html_word_content = re.sub(h1, h3, html_word_content)
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


def bc_book_content(
    resource_lookup_dto: model.ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
    book_intro_glob_path_fmt_str: str = "{}/*{}/intro.md",
    chapter_dirs_glob_fmt_str: str = "{}/*{}/*[0-9]*",
    parser_type: str = "html.parser",
    url_fmt_str: str = settings.BC_ARTICLE_URL_FMT_STR,
) -> model.BCBook:
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
    book_intro_md_content = (
        file_utils.read_file(book_intro_paths[0]) if book_intro_paths else ""
    )
    book_intro_html_content = md.convert(book_intro_md_content)
    chapter_dirs = sorted(
        glob(
            chapter_dirs_glob_fmt_str.format(
                resource_dir, resource_lookup_dto.resource_code
            )
        )
    )
    chapters: dict[int, model.BCChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(pathlib.Path(chapter_dir).stem)
        chapter_commentary_md_content = file_utils.read_file(chapter_dir)
        chapter_commentary_html_content = md.convert(chapter_commentary_md_content)
        parser = bs4.BeautifulSoup(chapter_commentary_html_content, parser_type)
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
        chapters[chapter_num] = model.BCChapter(commentary=str(parser))
    return model.BCBook(
        book_intro=book_intro_html_content,
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        resource_code=resource_lookup_dto.resource_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapters,
    )


def markdown_instance(
    lang_code: str,
    resource_type: str,
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
    tw_resource_dir: Optional[str] = None,
    sections_to_remove: list[str] = settings.MARKDOWN_SECTIONS_TO_REMOVE,
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
    if not layout_for_print:  # User doesn't want to print result
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
                        translation_words_dict,
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
