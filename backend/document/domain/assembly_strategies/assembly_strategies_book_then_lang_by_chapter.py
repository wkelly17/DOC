from re import search
from typing import Iterable, Mapping, Sequence

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    # partition_verses_content_in_half,
    adjust_book_intro_headings,
    book_intro_commentary,
    chapter_commentary,
    chapter_intro,
    chapter_verse_content_sans_footnotes,
    ensure_primary_usfm_books_for_different_languages_are_adjacent,
    verses_for_chapter_tn,
    verses_for_chapter_tq,
)
from document.domain.bible_books import BOOK_NAMES
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


def assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
    html_row_begin: str = settings.HTML_ROW_BEGIN,
    html_column_begin: str = settings.HTML_COLUMN_BEGIN,
    html_column_left_begin: str = settings.HTML_COLUMN_LEFT_BEGIN,
    html_column_right_begin: str = settings.HTML_COLUMN_RIGHT_BEGIN,
    html_column_end: str = settings.HTML_COLUMN_END,
    html_row_end: str = settings.HTML_ROW_END,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_name_fmt_str: str = settings.BOOK_NAME_FMT_STR,
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

    # Sort resources by language
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
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    if usfm_with_most_chapters:
        # Book title centered
        # TODO One day book title could be localized.
        yield book_name_fmt_str.format(
            book_names[usfm_with_most_chapters.resource_code]
        )

    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield chapter_heading

        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit2, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

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

                # Add scripture chapter
                yield chapter_verse_content_sans_footnotes(
                    usfm_book_content_unit.chapters[chapter_num].content
                )
                # Add the footnotes
                # try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
                # except KeyError:
                #     ldebug(
                #         "usfm_book_content_unit: %s, does not have chapter: %s",
                #         usfm_book_content_unit,
                #         chapter_num,
                #     )
                #     lexception("Caught exception:")

            yield html_column_end
            if not is_even(idx):  # Non-even indexes signal the end of the current row.
                yield html_row_end

        # Add the interleaved tn notes, making sure to put lang0
        # notes on the left and lang1 notes on the right.
        tn_verses = None
        for idx, tn_book_content_unit3 in enumerate(tn_book_content_units):
            tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
            if tn_verses:
                if is_even(idx):
                    yield html_row_begin
                yield html_column_begin
                yield "".join(tn_verses.values())
                yield html_column_end
        yield html_row_end

        # Add the interleaved tq questions, making sure to put lang0
        # questions on the left and lang1 questions on the right.
        tq_verses = None
        for idx, tq_book_content_unit in enumerate(tq_book_content_units):
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
            # Add TQ verse content, if any
            if tq_verses:
                if is_even(idx):
                    yield html_row_begin
                yield html_column_begin
                yield "".join(tq_verses.values())  # [verse_num]
                yield html_column_end
        yield html_row_end

        yield html_row_end


def assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
    tn_verse_notes_enclosing_div_fmt_str: str = settings.TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR,
    tq_heading_fmt_str: str = settings.TQ_HEADING_FMT_STR,
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    # html_row_begin: str = settings.HTML_ROW_BEGIN,
    # html_column_begin: str = settings.HTML_COLUMN_BEGIN,
    # html_column_left_begin: str = settings.HTML_COLUMN_LEFT_BEGIN,
    # html_column_right_begin: str = settings.HTML_COLUMN_RIGHT_BEGIN,
    # html_column_end: str = settings.HTML_COLUMN_END,
    # html_row_end: str = settings.HTML_ROW_END,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_name_fmt_str: str = settings.BOOK_NAME_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource exists, one column
    layout.
    """

    ldebug = logger.debug
    lexception = logger.exception

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield book_intro
        yield hr

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)
        yield hr

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed
    # to the user.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    if usfm_with_most_chapters:
        # Book title centered
        # TODO One day book title could be localized.
        yield book_name_fmt_str.format(
            book_names[usfm_with_most_chapters.resource_code]
        )

    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        # chapter_heading = HtmlContent("")
        # chapter_heading = chapter.content[0]
        # yield HtmlContent(chapter_heading)

        # Add the interleaved USFM chapter
        for usfm_book_content_unit in usfm_book_content_units:
            if chapter_num in usfm_book_content_unit.chapters:
                # Add scripture chapter
                # yield "".join(usfm_book_content_unit.chapters[chapter_num].content)

                # Add scripture chapter
                yield chapter_verse_content_sans_footnotes(
                    usfm_book_content_unit.chapters[chapter_num].content
                )
                yield hr

                # try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
                    yield hr
                # except KeyError:
                #     ldebug(
                #         "usfm_book_content_unit: %s, does not have chapter: %s",
                #         usfm_book_content_unit,
                #         chapter_num,
                #     )
                #     lexception("Caught exception:")

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit2, chapter_num)
            yield hr

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)
            yield hr

        # Add the interleaved tn notes
        tn_verses = None
        for tn_book_content_unit3 in tn_book_content_units:
            tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
            if tn_verses:
                # Divide TN verse notes across two columns.
                # wkthmltopdf can't handle css column-count directive so we overcome
                # that here manually by creating our own two column layout.
                # (
                #     left_half_tn_verses,
                #     right_half_tn_verses,
                # ) = partition_verses_content_in_half(list(tn_verses.values()))

                ## left_half_tn_verses = list(tn_verses.values())[
                ##     0 : int(len(tn_verses.keys()) / 2) + 1
                ## ]
                ## right_half_tn_verses = list(tn_verses.values())[
                ##     int(len(tn_verses.keys()) / 2) + 1 : -1
                ## ]
                # yield html_row_begin
                # yield html_column_left_begin
                # yield "".join(left_half_tn_verses)
                # yield html_column_end
                # yield html_column_right_begin
                # yield "".join(right_half_tn_verses)
                # yield html_column_end
                # yield html_row_end
                yield tn_verse_notes_enclosing_div_fmt_str.format(
                    "".join(tn_verses.values())
                )
                yield hr

        # Add the interleaved tq questions
        tq_verses = None
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
            # Add TQ verse content, if any
            if tq_verses:
                # yield tq_heading_fmt_str.format(tq_book_content_unit.resource_type_name)
                # Divide TQ verse notes across two columns.
                # wkthmltopdf can't handle css column-count directive so we overcome
                # that here manually by creating our own two column layout.
                # (
                #     left_half_tq_verses,
                #     right_half_tq_verses,
                # ) = partition_verses_content_in_half(list(tq_verses.values()))

                ## left_half_tq_verses = list(tq_verses.values())[
                ##     0 : int(len(tq_verses.keys()) / 2) + 1
                ## ]
                ## right_half_tq_verses = list(tq_verses.values())[
                ##     int(len(tq_verses.keys()) / 2) + 1 : -1
                ## ]
                # yield html_row_begin
                # yield html_column_left_begin
                # yield "".join(left_half_tq_verses)
                # yield html_column_end
                # yield html_column_right_begin
                # yield "".join(right_half_tq_verses)
                # yield html_column_end
                # yield html_row_end
                yield tq_heading_and_questions_fmt_str.format(
                    tq_book_content_unit.resource_type_name,
                    "".join(tq_verses.values()),
                )
                yield hr
        yield end_of_chapter_html


def assemble_tn_as_iterator_by_chapter_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    tq_heading_fmt_str: str = settings.TQ_HEADING_FMT_STR,
    # html_row_begin: str = settings.HTML_ROW_BEGIN,
    # html_column_begin: str = settings.HTML_COLUMN_BEGIN,
    # html_column_left_begin: str = settings.HTML_COLUMN_LEFT_BEGIN,
    # html_column_right_begin: str = settings.HTML_COLUMN_RIGHT_BEGIN,
    # html_column_end: str = settings.HTML_COLUMN_END,
    # html_row_end: str = settings.HTML_ROW_END,
    tn_verse_notes_enclosing_div_fmt_str: str = settings.TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR,
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tn_book_content_units exists.
    """

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield book_intro
        yield hr

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)
        yield hr

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
            # Add the translation notes chapter intro.
            yield from chapter_intro(tn_book_content_unit, chapter_num)
            yield hr

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)
            yield hr

        # Add the interleaved tn notes
        for tn_book_content_unit in tn_book_content_units:
            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if tn_verses:
                # Divide TN verse notes across two columns.
                # wkthmltopdf can't handle css column-count directive so we overcome
                # that here manually by creating our own two column layout.
                # (
                #     left_half_tn_verses,
                #     right_half_tn_verses,
                # ) = partition_verses_content_in_half(list(tn_verses.values()))

                ## left_half_tn_verses = list(tn_verses.values())[
                ##     0 : int(len(tn_verses.keys()) / 2) + 1
                ## ]
                ## right_half_tn_verses = list(tn_verses.values())[
                ##     int(len(tn_verses.keys()) / 2) + 1 : -1
                ## ]
                # yield html_row_begin
                # yield html_column_left_begin
                # yield "".join(left_half_tn_verses)
                # yield html_column_end
                # yield html_column_right_begin
                # yield "".join(right_half_tn_verses)
                # yield html_column_end
                # yield html_row_end
                yield tn_verse_notes_enclosing_div_fmt_str.format(
                    "".join(tn_verses.values())
                )
                yield hr

        # Add the interleaved tq questions
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
            # Add TQ verse content, if any
            if tq_verses:
                # yield tq_heading_fmt_str.format(tq_book_content_unit.resource_type_name)
                # Divide TQ verse notes across two columns.
                # wkthmltopdf can't handle css column-count directive so we overcome
                # that here manually by creating our own two column layout.
                # (
                #     left_half_tq_verses,
                #     right_half_tq_verses,
                # ) = partition_verses_content_in_half(list(tq_verses.values()))

                ## left_half_tq_verses = list(tq_verses.values())[
                ##     0 : int(len(tq_verses.keys()) / 2) + 1
                ## ]
                ## right_half_tq_verses = list(tq_verses.values())[
                ##     int(len(tq_verses.keys()) / 2) + 1 : -1
                ## ]
                # yield html_row_begin
                # yield html_column_left_begin
                # yield "".join(left_half_tq_verses)
                # yield html_column_end
                # yield html_column_right_begin
                # yield "".join(right_half_tq_verses)
                # yield html_column_end
                # yield html_row_end
                yield tq_heading_and_questions_fmt_str.format(
                    tq_book_content_unit.resource_type_name,
                    "".join(tq_verses.values()),
                )
                yield hr
        yield end_of_chapter_html


def assemble_tq_as_iterator_by_chapter_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    tq_heading_fmt_str: str = settings.TQ_HEADING_FMT_STR,
    # html_row_begin: str = settings.HTML_ROW_BEGIN,
    # html_column_begin: str = settings.HTML_COLUMN_BEGIN,
    # html_column_left_begin: str = settings.HTML_COLUMN_LEFT_BEGIN,
    # html_column_right_begin: str = settings.HTML_COLUMN_RIGHT_BEGIN,
    # html_column_end: str = settings.HTML_COLUMN_END,
    # html_row_end: str = settings.HTML_ROW_END,
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tq_book_content_units exists.
    """

    # Sort resources by language
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
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)
            yield hr

        # Add the interleaved tq questions
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
            # Add TQ verse content, if any
            if tq_verses:
                # yield tq_heading_fmt_str.format(tq_book_content_unit.resource_type_name)
                # Divide TQ verse notes across two columns.
                # wkthmltopdf can't handle css column-count directive so we overcome
                # that here manually by creating our own two column layout.
                # (
                #     left_half_tq_verses,
                #     right_half_tq_verses,
                # ) = partition_verses_content_in_half(list(tq_verses.values()))

                ## left_half_tq_verses = list(tq_verses.values())[
                ##     0 : int(len(tq_verses.keys()) / 2) + 1
                ## ]
                ## right_half_tq_verses = list(tq_verses.values())[
                ##     int(len(tq_verses.keys()) / 2) + 1 : -1
                ## ]
                # yield html_row_begin
                # yield html_column_left_begin
                # yield "".join(left_half_tq_verses)
                # yield html_column_end
                # yield html_column_right_begin
                # yield "".join(right_half_tq_verses)
                # yield html_column_end
                # yield html_row_end
                yield tq_heading_and_questions_fmt_str.format(
                    tq_book_content_unit.resource_type_name,
                    "".join(tq_verses.values()),
                )
                yield hr
        yield end_of_chapter_html


def assemble_tw_as_iterator_by_chapter_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
) -> Iterable[HtmlContent]:
    """Construct the HTML for BC and TW."""

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add the bible commentary
    for bc_book_content_unit in bc_book_content_units:
        yield bc_book_content_unit.book_intro
        yield hr
        for chapter in bc_book_content_unit.chapters.values():
            yield chapter.commentary
            yield hr
            yield end_of_chapter_html
