from typing import Iterable, Sequence

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    adjust_book_intro_headings,
    book_title,
    chapter_commentary,
    chapter_footnotes,
    chapter_intro,
    chapter_content_sans_footnotes,
    ensure_primary_usfm_books_for_different_languages_are_adjacent,
    language_direction_html,
    book_intro,
    tn_chapter_verses,
    tq_chapter_verses,
)
from document.domain.model import (
    BCBook,
    BookContent,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)
from document.utils.number_utils import is_even

logger = settings.logger(__name__)


def assemble_usfm_by_chapter_2c_sl_sr(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    html_row_begin: str = settings.HTML_ROW_BEGIN,
    html_column_begin: str = settings.HTML_COLUMN_BEGIN,
    html_column_left_begin: str = settings.HTML_COLUMN_LEFT_BEGIN,
    html_column_right_begin: str = settings.HTML_COLUMN_RIGHT_BEGIN,
    html_column_end: str = settings.HTML_COLUMN_END,
    html_row_end: str = settings.HTML_ROW_END,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for the two column scripture left scripture
    right layout.

    Ensure that different languages' USFMs ends up next to each other
    in the two column layout.

    Discussion:

    First let's find all possible USFM combinations for two languages
    that have both a primary USFM, e.g., ulb, available and a secondary
    USFM, e.g., udb, available for selection:

    primary_lang0, primary_lang1, secondary_lang0, secondary_lang1

    0                 0                0             1
    0                 0                1             0
    0                 0                1             1
    0                 1                0             0
    0                 1                0             1
    0                 1                1             0
    0                 1                1             1
    1                 0                0             0
    1                 0                0             1
    1                 0                1             0
    1                 0                1             1
    1                 1                0             1
    1                 1                1             0
    1                 1                1             1

    of which we can eliminate those that do not have the minimum of
    two languages and eliminate those that do not have USFMs
    for both languages yielding:

    primary_lang0, primary_lang1, secondary_lang0, secondary_lang1

    0                 0                1             1
    0                 1                1             0
    0                 1                1             1
    1                 0                0             1
    1                 0                1             1
    1                 1                0             1
    1                 1                1             0
    1                 1                1             1

    Let's now reorder columns to make the subsequent step easier:

    primary_lang0, secondary_lang0, primary_lang1, secondary_lang1

    0                   1             0              1
    0                   1             1              0
    0                   1             1              1
    1                   0             0              1
    1                   1             0              1
    1                   0             1              1
    1                   1             1              0
    1                   1             1              1

    which yields the following possible USFM layouts when we fix
    that lang0 always appears on the left and lang1 always appears on
    the right of the two column layout:

    secondary_lang0     | secondary_lang1

    or

    secondary_lang0     | primary_lang1

    or

    secondary_lang0     | primary_lang1
                        | secondary_lang1

    or

    primary_lang0       | secondary_lang1

    or

    primary_lang0       | secondary_lang1
    secondary_lang0     |

    or

    primary_lang0       | primary_lang1
                        | secondary_lang1

    or

    primary_lang0       | primary_lang1
    secondary_lang0     |

    or

    primary_lang0       | primary_lang1
    secondary_lang0     | secondary_lang1
    """

    ldebug = logger.debug
    lexception = logger.exception

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)
    # Order USFM book content units so that they are in language pairs
    # for side by side display.
    zipped_usfm_book_content_units = (
        ensure_primary_usfm_books_for_different_languages_are_adjacent(
            usfm_book_content_units
        )
    )
    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        if tn_book_content_unit.book_intro:
            yield from language_direction_html(tn_book_content_unit)
            book_intro_ = tn_book_content_unit.book_intro
            yield adjust_book_intro_headings(book_intro_)
            yield close_direction_html
    for bc_book_content_unit in bc_book_content_units:
        yield from book_intro(bc_book_content_unit)
    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    if usfm_with_most_chapters:
        yield book_title(usfm_with_most_chapters.book_code)
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield chapter_heading
        for tn_book_content_unit2 in tn_book_content_units:
            yield from language_direction_html(tn_book_content_unit2)
            yield from chapter_intro(tn_book_content_unit2, chapter_num)
            yield close_direction_html
        for bc_book_content_unit in bc_book_content_units:
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
        # Get lang_code of first USFM so that we can use it later
        # to make sure USFMs of the same language are on the same
        # side of the two column layout.
        lang0_code = zipped_usfm_book_content_units[0].lang_code
        # Add the interleaved USFM verses
        for idx, usfm_book_content_unit in enumerate(zipped_usfm_book_content_units):
            # The conditions for beginning a row are a simple
            # result of the fact that we can have between 2 and 4
            # non-None USFM content units in the collection one of which
            # could be a None (due to an earlier use of
            # itertools.zip_longest in the call to
            # ensure_primary_usfm_books_for_different_languages_are_adjacent)
            # in the case when there are 3 non-None items, but 4
            # total counting the None.
            if is_even(idx) or idx == 3:
                yield html_row_begin

            if (
                usfm_book_content_unit
                and chapter_num in usfm_book_content_unit.chapters
            ):
                # lang0's USFM content units should always be on the
                # left and lang1's should always be on the right.
                if lang0_code == usfm_book_content_unit.lang_code:
                    yield html_column_left_begin
                else:
                    yield html_column_right_begin

                yield from language_direction_html(usfm_book_content_unit)
                yield chapter_content_sans_footnotes(
                    usfm_book_content_unit.chapters[chapter_num].content
                )
                yield from chapter_footnotes(
                    usfm_book_content_unit.chapters[chapter_num]
                )
                yield close_direction_html
            yield html_column_end
            if not is_even(idx):  # Non-even indexes signal the end of the current row.
                yield html_row_end
        # Add the interleaved tn notes, making sure to put lang0
        # notes on the left and lang1 notes on the right.
        tn_verses = None
        for idx, tn_book_content_unit3 in enumerate(tn_book_content_units):
            tn_verses = list(tn_chapter_verses(tn_book_content_unit3, chapter_num))
            if tn_verses:
                if is_even(idx):
                    yield html_row_begin
                yield html_column_begin
                yield from language_direction_html(tn_book_content_unit3)
                yield "".join(tn_verses)
                yield close_direction_html
                yield html_column_end
        yield html_row_end
        # Add the interleaved tq questions, making sure to put lang0
        # questions on the left and lang1 questions on the right.
        tq_verses = None
        for idx, tq_book_content_unit in enumerate(tq_book_content_units):
            tq_verses = list(tq_chapter_verses(tq_book_content_unit, chapter_num))
            if tq_verses:
                if is_even(idx):
                    yield html_row_begin
                yield html_column_begin
                yield from language_direction_html(tq_book_content_unit)
                yield "".join(tq_verses)
                yield close_direction_html
                yield html_column_end
        yield html_row_end
        yield html_row_end


def assemble_usfm_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource exists, one column
    layout.
    """

    ldebug = logger.debug
    lexception = logger.exception

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)
    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # if tn_book_content_unit.book_intro:
        yield from language_direction_html(tn_book_content_unit)
        book_intro_ = "".join(list(book_intro(tn_book_content_unit)))
        book_intro_adj = adjust_book_intro_headings(book_intro_)
        yield book_intro_adj
        yield close_direction_html
    for bc_book_content_unit in bc_book_content_units:
        yield from book_intro(bc_book_content_unit)
    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed
    # to the user.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    yield book_title(usfm_with_most_chapters.book_code)
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        for usfm_book_content_unit in usfm_book_content_units:
            if chapter_num in usfm_book_content_unit.chapters:
                yield from language_direction_html(usfm_book_content_unit)
                yield chapter_content_sans_footnotes(
                    usfm_book_content_unit.chapters[chapter_num].content
                )
                yield hr
                yield from chapter_footnotes(
                    usfm_book_content_unit.chapters[chapter_num]
                )
                yield close_direction_html
        for tn_book_content_unit2 in tn_book_content_units:
            yield from language_direction_html(tn_book_content_unit2)
            yield from chapter_intro(tn_book_content_unit2, chapter_num)
            yield close_direction_html
        for bc_book_content_unit in bc_book_content_units:
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
        # Add the interleaved tn notes
        tn_verses = None
        for tn_book_content_unit3 in tn_book_content_units:
            tn_verses = list(tn_chapter_verses(tn_book_content_unit3, chapter_num))
            # if tn_verses:
            yield from language_direction_html(tn_book_content_unit3)
            yield "".join(tn_verses)
            yield close_direction_html
        tq_verses = None
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = list(tq_chapter_verses(tq_book_content_unit, chapter_num))
            # if tq_verses:
            yield from language_direction_html(tq_book_content_unit)
            yield "".join(tq_verses)
            yield close_direction_html
        yield end_of_chapter_html


def assemble_tn_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tn_book_content_units exists.
    """

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        yield from language_direction_html(tn_book_content_unit)
        book_intro_ = book_intro(tn_book_content_unit)
        book_intro_adj = adjust_book_intro_headings("".join(book_intro_))
        yield book_intro_adj
        yield close_direction_html
    for bc_book_content_unit in bc_book_content_units:
        yield from book_intro(bc_book_content_unit)
    # Use the tn_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed
    # to user.
    tn_with_most_chapters = max(
        tn_book_content_units,
        key=lambda tn_book_content_unit: tn_book_content_unit.chapters.keys(),
    )
    for chapter_num in tn_with_most_chapters.chapters.keys():
        yield HtmlContent("Chapter {}".format(chapter_num))
        # Add chapter intro for each language
        for tn_book_content_unit in tn_book_content_units:
            yield from language_direction_html(tn_book_content_unit)
            yield from chapter_intro(tn_book_content_unit, chapter_num)
            yield close_direction_html
        for bc_book_content_unit in bc_book_content_units:
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
        # Add the interleaved tn notes
        for tn_book_content_unit in tn_book_content_units:
            tn_verses = list(tn_chapter_verses(tn_book_content_unit, chapter_num))
            yield from language_direction_html(tn_book_content_unit)
            yield "".join(tn_verses)
            yield close_direction_html
        # Add the interleaved tq questions
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = list(tq_chapter_verses(tq_book_content_unit, chapter_num))
            yield from language_direction_html(tq_book_content_unit)
            yield "".join(tq_verses)
            yield close_direction_html
        yield end_of_chapter_html


def assemble_tq_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tq_book_content_units exists.
    """

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)
    # Use the tq_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed to user.
    tq_with_most_chapters = max(
        tq_book_content_units,
        key=lambda tq_book_content_unit: tq_book_content_unit.chapters.keys(),
    )
    for chapter_num in tq_with_most_chapters.chapters.keys():
        yield HtmlContent("Chapter {}".format(chapter_num))
        for bc_book_content_unit in bc_book_content_units:
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
        # Add the interleaved tq questions
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = list(tq_chapter_verses(tq_book_content_unit, chapter_num))
            yield from language_direction_html(tq_book_content_unit)
            yield "".join(tq_verses)
            yield close_direction_html
        yield end_of_chapter_html


def assemble_tw_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
) -> Iterable[HtmlContent]:
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)
    for bc_book_content_unit in bc_book_content_units:
        yield from book_intro(bc_book_content_unit)
        for chapter_num, chapter in bc_book_content_unit.chapters.items():
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
            yield end_of_chapter_html
