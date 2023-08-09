from typing import Iterable, Sequence

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    adjust_book_intro_headings,
    book_intro_commentary,
    chapter_commentary,
    chapter_intro,
    ensure_primary_usfm_books_for_different_languages_are_adjacent,
    translation_word_links,
    verses_for_chapter_tn,
    verses_for_chapter_tq,
)
from document.domain.model import (
    BCBook,
    BookContent,
    ChapterNum,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)
from document.utils.number_utils import is_even

logger = settings.logger(__name__)


def assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr(
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
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for the two column scripture left scripture
    right layout.

    Ensure that different languages' USFMs ends up next to each other
    in the two column layout.

    Discussion:

    First let's find all possible USFM combinations for two languages
    that have both a primary USFM, e.g., ulb-wa, available and a secondary
    USFM, e.g., udb-wa, available for selection:

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
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
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
        if tn_book_content_unit.intro_html:
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
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield HtmlContent(chapter_heading)

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit2, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        for verse_num in chapter.verses.keys():
            # Get lang_code of first USFM so that we can use it later
            # to make sure USFMs of the same language are on the same
            # side of the two column layout.
            lang0_code = zipped_usfm_book_content_units[0].lang_code
            # Add the interleaved USFM verses
            for idx, usfm_book_content_unit in enumerate(
                zipped_usfm_book_content_units
            ):
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
                    and verse_num in usfm_book_content_unit.chapters[chapter_num].verses
                ):
                    # lang0's USFM content units should always be on the
                    # left and lang1's should always be on the right.
                    if lang0_code == usfm_book_content_unit.lang_code:
                        yield html_column_left_begin
                    else:
                        yield html_column_right_begin

                    # Add scripture verse
                    yield usfm_book_content_unit.chapters[chapter_num].verses[verse_num]
                yield html_column_end
                if not is_even(
                    idx
                ):  # Non-even indexes signal the end of the current row.
                    yield html_row_end

            # Add the interleaved tn notes, making sure to put lang0
            # notes on the left and lang1 notes on the right.
            tn_verses = None
            for idx, tn_book_content_unit3 in enumerate(tn_book_content_units):
                tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    if is_even(idx):
                        yield html_row_begin
                    yield html_column_begin
                    yield tn_verses[verse_num]
                    yield html_column_end
            yield html_row_end

            # Add the interleaved tq questions, making sure to put lang0
            # questions on the left and lang1 questions on the right.
            tq_verses = None
            for idx, tq_book_content_unit in enumerate(tq_book_content_units):
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    if is_even(idx):
                        yield html_row_begin
                    yield html_column_begin
                    yield tq_verses[verse_num]
                    yield html_column_end
            yield html_row_end

            # Add the interleaved translation word links, making sure to put lang0
            # word links on the left and lang1 word links on the right.
            for idx, tw_book_content_unit in enumerate(tw_book_content_units):
                # Get the usfm_book_content_unit instance associated with the
                # tw_book_content_unit, i.e., having same lang_code and
                # resource_code.
                usfm_book_content_unit_lst = [
                    usfm_book_content_unit
                    for usfm_book_content_unit in usfm_book_content_units
                    if usfm_book_content_unit.lang_code
                    == tw_book_content_unit.lang_code
                    and usfm_book_content_unit.resource_code
                    == tw_book_content_unit.resource_code
                ]
                if usfm_book_content_unit_lst:
                    usfm_book_content_unit_ = usfm_book_content_unit_lst[0]
                else:
                    usfm_book_content_unit_ = None
                # Add the translation words links section.
                if (
                    usfm_book_content_unit_ is not None
                    and verse_num
                    in usfm_book_content_unit_.chapters[chapter_num].verses
                ):
                    if is_even(idx):
                        yield html_row_begin
                        yield html_column_begin

                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].verses[verse_num],
                    )
                    yield html_column_end
                else:
                    ldebug(
                        "usfm for chapter %s, verse %s likely could not be parsed by usfm parser for language %s and book %s",
                        chapter_num,
                        verse_num,
                        tw_book_content_unit.lang_code,
                        tw_book_content_unit.resource_code,
                    )
            yield html_row_end

        # Add the footnotes
        for usfm_book_content_unit in usfm_book_content_units:
            try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
            except KeyError:
                ldebug(
                    "usfm_book_content_unit: %s, does not have chapter: %s",
                    usfm_book_content_unit,
                    chapter_num,
                )
                lexception("Caught exception:")


def assemble_usfm_as_iterator_for_book_then_lang_1c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column layout verse interleaved HTML wherein at
    least one USFM resource exists, and other resources may exist.
    """

    ldebug = logger.debug
    lexception = logger.exception

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        if tn_book_content_unit.intro_html:
            # Add the book intro
            book_intro = tn_book_content_unit.intro_html
            book_intro = adjust_book_intro_headings(book_intro)
            yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump.
    # Realize the most amount of content displayed to user.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield HtmlContent(chapter_heading)

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit2, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        for verse_num in chapter.verses.keys():
            # Add the interleaved USFM verses
            for usfm_book_content_unit in usfm_book_content_units:
                if (
                    chapter_num in usfm_book_content_unit.chapters
                    and verse_num in usfm_book_content_unit.chapters[chapter_num].verses
                ):
                    # Add scripture verse
                    yield usfm_book_content_unit.chapters[chapter_num].verses[verse_num]

            # Add the interleaved tn notes
            tn_verses = None
            for tn_book_content_unit3 in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield tn_verses[verse_num]

            # Add the interleaved tq questions
            tq_verses = None
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]

            # Add the interleaved translation word links
            for tw_book_content_unit in tw_book_content_units:
                # Get the usfm_book_content_unit instance associated with the
                # tw_book_content_unit, i.e., having same lang_code and
                # resource_code.
                usfm_book_content_unit_lst = [
                    usfm_book_content_unit
                    for usfm_book_content_unit in usfm_book_content_units
                    if usfm_book_content_unit.lang_code
                    == tw_book_content_unit.lang_code
                    and usfm_book_content_unit.resource_code
                    == tw_book_content_unit.resource_code
                ]
                if usfm_book_content_unit_lst:
                    usfm_book_content_unit_ = usfm_book_content_unit_lst[0]
                else:
                    usfm_book_content_unit_ = None
                # Add the translation words links section.
                if (
                    usfm_book_content_unit_ is not None
                    and verse_num
                    in usfm_book_content_unit_.chapters[chapter_num].verses
                ):
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].verses[verse_num],
                    )
                else:
                    ldebug(
                        "usfm for chapter %s, verse %s likely could not be parsed by usfm parser for language %s and book %s",
                        chapter_num,
                        verse_num,
                        tw_book_content_unit.lang_code,
                        tw_book_content_unit.resource_code,
                    )

        # Add the footnotes
        for usfm_book_content_unit in usfm_book_content_units:
            try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
            except KeyError:
                ldebug(
                    "usfm_book_content_unit: %s, does not have chapter: %s",
                    usfm_book_content_unit,
                    chapter_num,
                )
                lexception("Caught exception:")


def assemble_usfm_as_iterator_for_book_then_lang_1c_c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column compact layout verse interleaved HTML
    wherein at least one USFM resource exists, and other resources may
    exist.
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
        if tn_book_content_unit.intro_html:
            # Add the book intro
            book_intro = tn_book_content_unit.intro_html
            book_intro = adjust_book_intro_headings(book_intro)
            yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed
    # to user.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield HtmlContent(chapter_heading)

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield HtmlContent(chapter_intro(tn_book_content_unit2, chapter_num))

        for bc_book_content_unit in bc_book_content_units:
            # Add the commentary for chapter.
            yield HtmlContent(chapter_commentary(bc_book_content_unit, chapter_num))

        for verse_num in chapter.verses.keys():
            # Add the interleaved USFM verses
            for usfm_book_content_unit in usfm_book_content_units:
                if (
                    chapter_num in usfm_book_content_unit.chapters
                    and verse_num in usfm_book_content_unit.chapters[chapter_num].verses
                ):
                    # Add scripture verse
                    yield usfm_book_content_unit.chapters[chapter_num].verses[verse_num]

            # Add the interleaved tn notes
            tn_verses = None
            for tn_book_content_unit3 in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield tn_verses[verse_num]

            # Add the interleaved tq questions
            tq_verses = None
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]

        # Add the footnotes
        for usfm_book_content_unit in usfm_book_content_units:
            try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
            except KeyError:
                ldebug(
                    "usfm_book_content_unit: %s, does not have chapter: %s",
                    usfm_book_content_unit,
                    chapter_num,
                )
                lexception("Caught exception:")


def assemble_tn_as_iterator_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the one column compact layout verse interleaved HTML
    wherein at least one tn resource exists, and other non-USFM
    resources may exist.
    """

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        if tn_book_content_unit.intro_html:
            # Add the book intro
            book_intro = tn_book_content_unit.intro_html
            book_intro = adjust_book_intro_headings(book_intro)
            yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

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

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump to realize the
        # most amount of content displayed to user.
        tn_with_most_verses = max(
            tn_book_content_units,
            key=lambda tn_book_content_unit: tn_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tn_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tn notes
            for tn_book_content_unit in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield tn_verses[verse_num]

            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]


def assemble_tn_as_iterator_for_book_then_lang_c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the compact layout HTML for a 'by verse' strategy wherein at least
    tn_book_content_units exists, and other non-USFM resources may exist.
    """
    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        if tn_book_content_unit.intro_html:
            # Add the book intro
            book_intro = tn_book_content_unit.intro_html
            book_intro = adjust_book_intro_headings(book_intro)
            yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    def chapters_key(tn_book_content_unit: TNBook) -> list[ChapterNum]:
        return list(tn_book_content_unit.chapters.keys())

    # Use the tn_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed
    # to user.
    tn_with_most_chapters = max(tn_book_content_units, key=chapters_key)
    for chapter_num in tn_with_most_chapters.chapters.keys():
        yield HtmlContent("Chapter {}".format(chapter_num))

        # Add chapter intro for each language
        for tn_book_content_unit in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield from chapter_intro(tn_book_content_unit, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add chapter commentary.
            yield from chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump to realize the
        # most amount of content displayed to user.
        tn_with_most_verses = max(
            tn_book_content_units,
            key=lambda tn_book_content_unit: tn_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tn_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tn notes
            for tn_book_content_unit in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield tn_verses[verse_num]

            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]


def assemble_tq_as_iterator_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least
    tq_book_content_units exists, and TQ, and TW may exist.
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

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump to realize the
        # most amount of content displayed to user.
        tq_with_most_verses = max(
            tq_book_content_units,
            key=lambda tq_book_content_unit: tq_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tq_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]


def assemble_tq_as_iterator_for_book_then_lang_c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least
    tq_book_content_units exists, and TQ, and TW may exist.
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
            # Add chapter commentary
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump to realize the
        # most amount of content displayed to user.
        tq_with_most_verses = max(
            tq_book_content_units,
            key=lambda tq_book_content_unit: tq_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tq_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]


def assemble_tw_as_iterator_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """Construct the HTML for BC and TW."""

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add the bible commentary
    for bc_book_content_unit in bc_book_content_units:
        yield bc_book_content_unit.book_intro
        for chapter in bc_book_content_unit.chapters.values():
            yield chapter.commentary
