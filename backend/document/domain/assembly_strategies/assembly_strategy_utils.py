"""
Utility functions used by assembly_strategies.
"""

from itertools import chain, groupby, zip_longest
from re import escape, search, sub
from typing import Iterable, Mapping, Optional, Sequence

from document.config import settings
from document.domain.bible_books import BOOK_NAMES, BOOK_NUMBERS
from document.domain.model import (
    BCBook,
    BookContent,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    TWNameContentPair,
    TWUse,
    USFMBook,
    VerseRef,
)
from document.utils.tw_utils import uniq


logger = settings.logger(__name__)

H1, H2, H3, H4, H5, H6 = "h1", "h2", "h3", "h4", "h5", "h6"


def book_content_unit_lang_name(book_content_unit: BookContent) -> str:
    return book_content_unit.lang_name


def book_content_unit_resource_code(book_content_unit: BookContent) -> str:
    """Sort key that replaces a slow lambda"""
    return book_content_unit.resource_code


def book_number(
    resource_code: str,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
) -> str:
    return book_numbers[resource_code].zfill(num_zeros)


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


def chapter_intro(tn_book_content_unit: TNBook, chapter_num: int) -> HtmlContent:
    """Get the chapter intro."""
    if tn_book_content_unit and chapter_num in tn_book_content_unit.chapters:
        chapter_intro = tn_book_content_unit.chapters[chapter_num].intro_html
    else:
        chapter_intro = HtmlContent("")
    return chapter_intro


def book_intro_commentary(bc_book_content_unit: BCBook) -> HtmlContent:
    if bc_book_content_unit:
        book_intro_commentary = bc_book_content_unit.book_intro
    else:
        book_intro_commentary = HtmlContent("")
    return book_intro_commentary


def chapter_commentary(bc_book_content_unit: BCBook, chapter_num: int) -> HtmlContent:
    """Get the chapter commentary."""
    if bc_book_content_unit and chapter_num in bc_book_content_unit.chapters:
        chapter_commentary = bc_book_content_unit.chapters[chapter_num].commentary
    else:
        chapter_commentary = HtmlContent("")
    return chapter_commentary


def verses_for_chapter_tn(
    book_content_unit: TNBook, chapter_num: int
) -> Optional[dict[str, HtmlContent]]:
    """
    Return the HTML for verses that are in the chapter with
    chapter_num.
    """
    verses_html = None
    if chapter_num in book_content_unit.chapters:
        verses_html = book_content_unit.chapters[chapter_num].verses
    return verses_html


def verses_for_chapter_tq(
    book_content_unit: TQBook,
    chapter_num: int,
) -> Optional[dict[str, HtmlContent]]:
    """Return the HTML for verses in chapter_num."""
    verses_html = None
    if chapter_num in book_content_unit.chapters:
        verses_html = book_content_unit.chapters[chapter_num].verses
    return verses_html


def translation_word_links(
    book_content_unit: TWBook,
    chapter_num: int,
    verse_num: str,
    verse: HtmlContent,
    unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
    translation_word_list_item_fmt_str: str = settings.TRANSLATION_WORD_LIST_ITEM_FMT_STR,
    unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> Iterable[HtmlContent]:
    """
    Add the translation word links section which provides links from words
    used in the current verse to their definition.
    """
    uses: list[TWUse] = []
    name_content_pair: TWNameContentPair
    for name_content_pair in book_content_unit.name_content_pairs:
        # This checks that the word occurs as an exact sub-string in
        # the verse.
        if search(r"\b{}\b".format(escape(name_content_pair.localized_word)), verse):
            use = TWUse(
                lang_code=book_content_unit.lang_code,
                book_id=book_content_unit.resource_code,
                book_name=book_names[book_content_unit.resource_code],
                chapter_num=chapter_num,
                verse_num=verse_num,
                localized_word=name_content_pair.localized_word,
            )
            uses.append(use)
            # Store reference for use in 'Uses:' section that
            # comes later.
            if name_content_pair.localized_word in book_content_unit.uses:
                book_content_unit.uses[name_content_pair.localized_word].append(use)
            else:
                book_content_unit.uses[name_content_pair.localized_word] = [use]

    if uses:
        # Start list formatting
        yield unordered_list_begin_str
        # Append word links.
        uses_list_items = [
            translation_word_list_item_fmt_str.format(
                book_content_unit.lang_code,
                use.localized_word,
                use.localized_word,
            )
            for use in list(uniq(uses))  # Get the unique uses
        ]
        yield HtmlContent("\n".join(uses_list_items))
        # End list formatting
        yield unordered_list_end_str


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
    logger.debug("languages: %s", languages)
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
    # NOTE Footnotes are rendered to HTML by USFM-TOOLS at the end of each
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
