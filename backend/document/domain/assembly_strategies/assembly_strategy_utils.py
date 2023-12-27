"""
Utility functions used by assembly_strategies.
"""

from functools import singledispatch
from itertools import chain, groupby, zip_longest
from re import escape, search, sub
from typing import Iterable, Mapping, Optional, Sequence

from document.config import settings
from document.domain.bible_books import BOOK_NAMES, BOOK_NUMBERS
from document.domain.model import (
    BCBook,
    BookContent,
    HtmlContent,
    LangDirEnum,
    TNBook,
    TQBook,
    TWBook,
    TWNameContentPair,
    TWUse,
    USFMBook,
    USFMChapter,
    VerseRef,
)
from document.utils.tw_utils import uniq

logger = settings.logger(__name__)

H1, H2, H3, H4, H5, H6 = "h1", "h2", "h3", "h4", "h5", "h6"


def book_content_unit_lang_name(book_content_unit: BookContent) -> str:
    return book_content_unit.lang_name


def book_content_unit_book_code(book_content_unit: BookContent) -> str:
    """Sort key that replaces a slow lambda"""
    return book_content_unit.book_code


def chapter_footnotes(
    chapter: USFMChapter,
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    if chapter.footnotes:
        yield footnotes_heading
        yield chapter.footnotes
        yield hr
    else:
        yield HtmlContent("")


def book_number(
    book_code: str,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
) -> HtmlContent:
    return book_numbers[book_code].zfill(num_zeros)


@singledispatch
def chapter_heading(
    book_content_unit: TQBook | TNBook,
    chapter_num: int,
    num_zeros: int = settings.NUM_ZEROS,
    fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
) -> HtmlContent:
    return HtmlContent(
        fmt_str.format(
            book_content_unit.lang_code,
            book_number(book_content_unit.book_code),
            str(chapter_num).zfill(num_zeros),
            chapter_num,
        )
    )


@chapter_heading.register
def _(
    book_content_unit: TNBook,
    chapter_num: int,
    num_zeros: int = settings.NUM_ZEROS,
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
) -> HtmlContent:
    return HtmlContent(
        chapter_header_fmt_str.format(
            book_content_unit.lang_code,
            book_number(book_content_unit.book_code),
            str(chapter_num).zfill(num_zeros),
            chapter_num,
        )
    )


@chapter_heading.register
def _(
    book_content_unit: TQBook,
    chapter_num: int,
    num_zeros: int = settings.NUM_ZEROS,
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
) -> HtmlContent:
    return HtmlContent(
        chapter_header_fmt_str.format(
            book_content_unit.lang_code,
            book_number(book_content_unit.book_code),
            str(chapter_num).zfill(num_zeros),
            chapter_num,
        )
    )


def first_usfm_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[USFMBook]:
    """
    Return the first USFMBook instance, if any, contained in book_content_units,
    else return None.
    """
    usfm_books = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, USFMBook)
    ]
    return usfm_books[0] if usfm_books else None


def second_usfm_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[USFMBook]:
    """
    Return the second USFMBook instance, if any, contained in book_content_units,
    else return None.
    """
    usfm_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, USFMBook)
    ]
    return usfm_book_content_units[1] if len(usfm_book_content_units) > 1 else None


def tn_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[TNBook]:
    """
    Return the TNBook instance, if any, contained in book_content_units,
    else return None.
    """
    tn_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, TNBook)
    ]
    return tn_book_content_units[0] if tn_book_content_units else None


def tw_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[TWBook]:
    """
    Return the TWBook instance, if any, contained in book_content_units,
    else return None.
    """
    tw_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, TWBook)
    ]
    return tw_book_content_units[0] if tw_book_content_units else None


def tq_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[TQBook]:
    """
    Return the TQBook instance, if any, contained in book_content_units,
    else return None.
    """
    tq_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, TQBook)
    ]
    return tq_book_content_units[0] if tq_book_content_units else None


def bc_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[BCBook]:
    """
    Return the BCBook instance, if any, contained in book_content_units,
    else return None.
    """
    bc_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, BCBook)
    ]
    return bc_book_content_units[0] if bc_book_content_units else None


def adjust_book_intro_headings(
    book_intro: str,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
    h6: str = H6,
) -> HtmlContent:
    """Change levels on headings."""
    # Move the H2 out of the way, we'll deal with it last.
    book_intro = sub(h2, h6, book_intro)
    book_intro = sub(h1, h2, book_intro)
    book_intro = sub(h3, h4, book_intro)
    book_intro = sub(h2, h3, book_intro)
    # Now adjust the temporary H6s.
    return HtmlContent(sub(h6, h3, book_intro))


def adjust_chapter_intro_headings(
    chapter_intro: str,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
    h5: str = H5,
    h6: str = H6,
) -> HtmlContent:
    """Change levels on headings."""
    # Move the H4 out of the way, we'll deal with it last.
    chapter_intro = sub(h4, h6, chapter_intro)
    chapter_intro = sub(h3, h4, chapter_intro)
    chapter_intro = sub(h1, h3, chapter_intro)
    chapter_intro = sub(h2, h4, chapter_intro)
    # Now adjust the temporary H6s.
    return HtmlContent(sub(h6, h5, chapter_intro))


def adjust_commentary_headings(
    chapter_commentary: str,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
    h5: str = H5,
    h6: str = H6,
) -> HtmlContent:
    """Change levels on headings."""
    # logger.debug("commentary parser: %s", parser)
    # Move the H4 out of the way, we'll deal with it last.
    chapter_commentary = sub(h4, h6, chapter_commentary)
    chapter_commentary = sub(h3, h4, chapter_commentary)
    chapter_commentary = sub(h1, h3, chapter_commentary)
    chapter_commentary = sub(h2, h4, chapter_commentary)
    # Now adjust the temporary H6s.
    return HtmlContent(sub(h6, h5, chapter_commentary))


def chapter_intro(
    book_content_unit: Optional[TNBook],
    chapter_num: int,
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    """Get the chapter intro."""
    if book_content_unit and chapter_num in book_content_unit.chapters:
        yield book_content_unit.chapters[chapter_num].intro_html
        yield hr
    else:
        yield HtmlContent("")


def book_title(
    book_code: str,
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> str:
    return fmt_str.format(book_names[book_code])


@singledispatch
def book_intro(
    book_content_unit: Optional[BCBook | TNBook],
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    if book_content_unit and book_content_unit.book_intro:
        yield book_content_unit.book_intro
        yield hr
    else:
        yield HtmlContent("")


@book_intro.register
def _(
    book_content_unit: Optional[BCBook],
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    if book_content_unit and book_content_unit.book_intro:
        yield book_content_unit.book_intro
        yield hr
    else:
        yield HtmlContent("")


@book_intro.register
def _(
    book_content_unit: Optional[TNBook],
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    if book_content_unit and book_content_unit.book_intro:
        yield book_content_unit.book_intro
        yield hr
    else:
        yield HtmlContent("")


def chapter_commentary(
    book_content_unit: Optional[BCBook],
    chapter_num: int,
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    """Get the chapter commentary."""
    if book_content_unit and chapter_num in book_content_unit.chapters:
        yield book_content_unit.chapters[chapter_num].commentary
        yield hr
    else:
        yield HtmlContent("")


@singledispatch
def language_direction_html(
    book_content_unit: Optional[USFMBook | TNBook | TQBook],
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
) -> Iterable[str]:
    if book_content_unit and book_content_unit.lang_direction == LangDirEnum.RTL:
        yield rtl_direction_html
    else:
        yield ltr_direction_html


@language_direction_html.register
def _(
    book_content_unit: Optional[TNBook],
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
) -> Iterable[str]:
    if book_content_unit and book_content_unit.lang_direction == LangDirEnum.RTL:
        yield rtl_direction_html
    else:
        yield ltr_direction_html


@language_direction_html.register
def _(
    book_content_unit: Optional[TQBook],
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
) -> Iterable[str]:
    if book_content_unit and book_content_unit.lang_direction == LangDirEnum.RTL:
        yield rtl_direction_html
    else:
        yield ltr_direction_html


def tn_chapter_verses(
    book_content_unit: Optional[TNBook],
    chapter_num: int,
    fmt_str: str = settings.TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR,
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    """
    Return the HTML for verses that are in the chapter with
    chapter_num.
    """
    verses_html = None
    if book_content_unit and chapter_num in book_content_unit.chapters:
        tn_verses = book_content_unit.chapters[chapter_num].verses
        yield fmt_str.format("".join(tn_verses.values()))
        yield hr
    else:
        yield HtmlContent("")


def tq_chapter_verses(
    book_content_unit: Optional[TQBook],
    chapter_num: int,
    fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    hr: HtmlContent = HtmlContent("<hr/>"),
) -> Iterable[HtmlContent]:
    """Return the HTML for verses in chapter_num."""
    verses_html = None
    if book_content_unit and chapter_num in book_content_unit.chapters:
        tq_verses = book_content_unit.chapters[chapter_num].verses
        yield fmt_str.format(
            book_content_unit.resource_type_name,
            "".join(tq_verses.values()),
        )
        yield hr
    else:
        yield HtmlContent("")


def languages_in_books(
    usfm_book_content_units: Sequence[BookContent],
) -> Sequence[str]:
    """Return the distinct languages in the usfm_book_content_units."""
    languages = sorted(
        list(
            set(
                [
                    lang_group[0]
                    for lang_group in groupby(
                        usfm_book_content_units,
                        key=lambda unit: unit.lang_code,
                    )
                ]
            )
        )
    )
    return languages


def ensure_primary_usfm_books_for_different_languages_are_adjacent(
    usfm_book_content_units: Sequence[USFMBook],
) -> Sequence[USFMBook]:
    """
    Interleave/zip USFM book content units such that they are
    juxtaposed language to language in pairs.
    """
    languages = languages_in_books(usfm_book_content_units)
    # Get book content units for language 0.
    usfm_lang0_book_content_units = [
        usfm_book_content_unit
        for usfm_book_content_unit in usfm_book_content_units
        if usfm_book_content_unit.lang_code == languages[0]
    ]
    # Get book content units for language 1.
    try:
        usfm_lang1_book_content_units = [
            usfm_book_content_unit
            for usfm_book_content_unit in usfm_book_content_units
            if usfm_book_content_unit.lang_code == languages[1]
        ]
    except IndexError as exc:
        logger.debug("Error: %s", exc)
        return usfm_lang0_book_content_units
    else:
        return list(
            # Flatten iterable of tuples into regular flat iterable.
            chain.from_iterable(
                # Interleave the two different languages' usfm units.
                zip_longest(
                    usfm_lang0_book_content_units, usfm_lang1_book_content_units
                )
            )
        )


def adjust_chapter_heading(
    chapter_content: list[str],
    h2: str = H2,
    h3: str = H3,
) -> list[HtmlContent]:
    """Change chapter label from h2 to h3."""
    # Move the H4 out of the way, we'll deal with it last.
    return [sub(h2, h3, chapter_component) for chapter_component in chapter_content]


def chapter_content_sans_footnotes(chapter_content: Sequence[HtmlContent]) -> str:
    """
    Return chapter content sans footnotes at end of each chapter.
    """
    # Footnotes are rendered to HTML by USFM-TOOLS at the end of each
    # chapter's verse content. So, we have to make sure we remove footnotes
    # from the end of chapter content when displaying chapter verse content
    # because we display footnotes explicitly later below.
    #
    # Find the index of where footnotes occur at the end of
    # chapter.content, if the chapter has footnotes.
    index_of_footnotes = 0
    for idx, element in enumerate(chapter_content):
        if search("footnotes", element):
            index_of_footnotes = idx

    # Now let's interleave USFM chapter.
    if index_of_footnotes != 0:  # chapter_content includes footnote
        chapter_content_sans_footnotes = chapter_content[0 : index_of_footnotes - 1]
        return "".join(chapter_content_sans_footnotes)
    else:
        return "".join(chapter_content)


if __name__ == "__main__":

    # To run the doctests in the this module, in the root of the project do:
    # python backend/document/domain/resource_lookup.py
    # or
    # python backend/document/domain/resource_lookup.py -v
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
