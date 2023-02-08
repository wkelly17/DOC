from typing import Iterable, Mapping, Optional

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    book_intro_commentary,
    book_number,
    chapter_commentary,
    chapter_intro,
    translation_word_links,
    verses_for_chapter_tn,
    verses_for_chapter_tq,
)
from document.domain.bible_books import BOOK_NUMBERS
from document.domain.model import (
    BCBook,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)

logger = settings.logger(__name__)


def assemble_by_usfm_as_iterator_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column 'by verse' HTML wherein at least one USFM
    resource (e.g., ulb, nav, cuv, etc.) exists, and TN, TQ, TW, BC, and a
    second USFM (e.g., probably always udb) may exist. If only one USFM
    exists then it will be used as the first USFM resource even if it is
    of udb resource type. Non-USFM resources, e.g., TN, TQ, TW, and BC
    will reference (and link where applicable) the first USFM resource.
    The second USFM resource is displayed last in this interleaving
    strategy.
    """

    if tn_book_content_unit:
        yield from tn_book_content_unit.intro_html

    if bc_book_content_unit:
        yield book_intro_commentary(bc_book_content_unit)

    if usfm_book_content_unit:
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading
            tn_verses = None
            tq_verses = None
            if tn_book_content_unit:
                # Add the translation notes chapter intro.
                yield chapter_intro(tn_book_content_unit, chapter_num)
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if bc_book_content_unit:
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                if usfm_book_content_unit2:
                    # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
                    # Add scripture verse
                    if (
                        chapter_num in usfm_book_content_unit2.chapters
                        and verse_num
                        in usfm_book_content_unit2.chapters[chapter_num].verses
                    ):
                        verse_ = usfm_book_content_unit2.chapters[chapter_num].verses[
                            verse_num
                        ]
                        yield verse_

                # Add TN verse content, if any
                if (
                    tn_book_content_unit
                    and tn_verses is not None
                    and tn_verses
                    and verse_num in tn_verses
                ):
                    yield tn_verses[verse_num]
                # Add TQ verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]

                if tw_book_content_unit:
                    # Add the translation words links section.
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        verse,
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes

    if not usfm_book_content_unit and usfm_book_content_unit2:
        # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
        for (
            chapter_num_,
            chapter_,
        ) in usfm_book_content_unit2.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter_.content[0]
            yield chapter_heading
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter_.verses.items():
                # Add scripture verse
                yield verse


def assemble_by_usfm_as_iterator_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column compact HTML wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, TW, BC, and a second USFM (e.g.,
    probably always udb) may exist. If only one USFM exists then it will
    be used as the first USFM resource even if it is of udb resource type.
    Non-USFM resources, e.g., TN, TQ, TW and BC will reference (and link
    where applicable) the first USFM resource. The second USFM resource is
    displayed last in this interleaving strategy.
    """

    if tn_book_content_unit:
        yield tn_book_content_unit.intro_html

    if bc_book_content_unit:
        yield book_intro_commentary(bc_book_content_unit)

    if usfm_book_content_unit:
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading
            tn_verses = None
            tq_verses = None
            if tn_book_content_unit:
                # Add the translation notes chapter intro.
                yield chapter_intro(tn_book_content_unit, chapter_num)

                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if bc_book_content_unit:
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                if usfm_book_content_unit2:
                    # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
                    # Add scripture verse
                    if (
                        chapter_num in usfm_book_content_unit2.chapters
                        and verse_num
                        in usfm_book_content_unit2.chapters[chapter_num].verses
                    ):
                        verse_ = usfm_book_content_unit2.chapters[chapter_num].verses[
                            verse_num
                        ]
                        yield verse_

                # Add TN verse content, if any
                if (
                    tn_book_content_unit
                    and tn_verses is not None
                    and tn_verses
                    and verse_num in tn_verses
                ):
                    yield tn_verses[verse_num]
                # Add TQ verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes

    if not usfm_book_content_unit and usfm_book_content_unit2:
        # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
        for (
            chapter_num_,
            chapter_,
        ) in usfm_book_content_unit2.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter_.content[0]
            yield chapter_heading
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter_.verses.items():
                # Add scripture verse
                yield verse


def assemble_usfm_tq_tw_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column HTML for a 'by verse' strategy wherein
    USFM exists and TQ and TW may exist.
    """

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                # Add TN verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]
                if tw_book_content_unit:
                    # Add the translation words links section
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        verse,
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tq_tw_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column compact HTML for a 'by verse' strategy
    wherein USFM exists, and TQ, and TW may exist.
    """

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                # Add TN verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tw_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column HTML for a 'by verse' strategy wherein
    USFM and TW exist.
    """

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                if tw_book_content_unit:
                    # Add the translation words links section
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        verse,
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tw_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column compact HTML for a 'by verse' strategy
    wherein USFM and TW exist.
    """

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tq_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the one column HTML for a 'by verse' strategy wherein
    only USFM and TQ exist.
    """

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its
            # translation note if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                # Add TQ verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield tq_verses[verse_num]

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_tn_as_iterator_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN, TQ,
    and TW exists.
    """

    if tn_book_content_unit:
        yield tn_book_content_unit.intro_html

        for chapter_num in tn_book_content_unit.chapters:
            # How to get chapter heading for Translation notes when USFM is not
            # requested? For now we'll use non-localized chapter heading. Add in the
            # USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tn_book_content_unit.lang_code,
                    book_number(tn_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit, chapter_num)

            if bc_book_content_unit:
                # Add the chapter commentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)

            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's get all the verse level content.
            # iterator = tn_verses or tq_verses
            # if iterator:
            if tn_verses:
                for verse_num, verse in tn_verses.items():
                    # Add TN verse content, if any
                    if tn_verses and verse_num in tn_verses:
                        yield tn_verses[verse_num]

                    # Add TQ verse content, if any
                    if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                        yield tq_verses[verse_num]
                    if tw_book_content_unit:
                        # Add the translation words links section.
                        yield from translation_word_links(
                            tw_book_content_unit,
                            chapter_num,
                            verse_num,
                            verse,
                        )


def assemble_tn_as_iterator_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN, TQ,
    and TW exists.
    """
    if tn_book_content_unit:
        yield tn_book_content_unit.intro_html

        for chapter_num in tn_book_content_unit.chapters:
            # How to get chapter heading for Translation notes when USFM is not
            # requested? For now we'll use non-localized chapter heading. Add in the
            # USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tn_book_content_unit.lang_code,
                    book_number(tn_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit, chapter_num)

            if bc_book_content_unit:
                # Add the chapter commentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)

            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            if tn_verses:
                for verse_num, verse in tn_verses.items():
                    # Add TN verse content, if any
                    if tn_verses and verse_num in tn_verses:
                        yield tn_verses[verse_num]

                    # Add TQ verse content, if any
                    if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                        yield tq_verses[verse_num]


def assemble_tq_as_iterator_for_lang_then_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only TQ exists."""
    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            if bc_book_content_unit:
                # Add chapter commentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)

            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's get all the verse translation notes available.
            if tq_verses:
                for verse_num, verse in tq_verses.items():
                    yield verse


def assemble_tq_tw_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ and
    TW exists.
    """

    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            if bc_book_content_unit:
                # Add chapter commmentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            if tq_verses:
                for verse_num, verse in tq_verses.items():
                    yield verse

                    if tw_book_content_unit:
                        # Add the translation words links section.
                        yield from translation_word_links(
                            tw_book_content_unit,
                            chapter_num,
                            verse_num,
                            verse,
                        )


def assemble_tq_tw_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ and
    TW exists.
    """

    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            if bc_book_content_unit:
                # Add chapter commmentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            if tq_verses:
                for verse_num, verse in tq_verses.items():
                    yield verse


# NOTE It is possible to request only TW, however TW is handled at a
# higher level so we essentially have a no-op here.
def assemble_tw_as_iterator_for_lang_then_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
) -> Iterable[HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only TW exists."""
    yield HtmlContent("")
