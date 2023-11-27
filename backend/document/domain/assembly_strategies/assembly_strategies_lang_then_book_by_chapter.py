from re import search
from typing import Iterable, Mapping, Optional

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    book_intro_commentary,
    book_number,
    chapter_commentary,
    chapter_intro,
    chapter_content_sans_footnotes,
    verses_for_chapter_tn,
    verses_for_chapter_tq,
)
from document.domain.bible_books import BOOK_NUMBERS, BOOK_NAMES
from document.domain.model import (
    BCBook,
    HtmlContent,
    LangDirEnum,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
    VerseRef,
)

logger = settings.logger(__name__)


def assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
    tn_verse_notes_enclosing_div_fmt_str: str = settings.TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR,
    tq_heading_fmt_str: str = settings.TQ_HEADING_FMT_STR,
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_name_fmt_str: str = settings.BOOK_NAME_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, TW, and a second USFM (e.g.,
    probably always udb) may exist. If only one USFM exists then it will
    be used as the first USFM resource even if it is of udb resource type.
    Non-USFM resources, e.g., TN, TQ, and TW will reference (and link
    where applicable) the first USFM resource. The second USFM resource is
    displayed last in this interleaving strategy.
    """

    if (
        usfm_book_content_unit
        and usfm_book_content_unit.lang_direction == LangDirEnum.RTL
    ):
        yield rtl_direction_html
    else:
        yield ltr_direction_html

    if tn_book_content_unit and tn_book_content_unit.intro_html:
        yield tn_book_content_unit.intro_html
        yield hr

    if bc_book_content_unit:
        yield book_intro_commentary(bc_book_content_unit)
        yield hr

    if usfm_book_content_unit:
        # Book title centered
        # TODO One day book title could be localized.
        yield book_name_fmt_str.format(book_names[usfm_book_content_unit.book_code])
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            # chapter_heading = HtmlContent("")
            # chapter_heading = chapter.content[0]
            # yield chapter_heading
            tn_verses: Optional[dict[VerseRef, HtmlContent]] = None
            tq_verses: Optional[dict[VerseRef, HtmlContent]] = None

            yield chapter_content_sans_footnotes(chapter.content)
            yield hr

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes
                yield hr
            if tn_book_content_unit:
                # Add the translation notes chapter intro.
                yield chapter_intro(tn_book_content_unit, chapter_num)
                yield hr
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if bc_book_content_unit:
                yield chapter_commentary(bc_book_content_unit, chapter_num)
                yield hr
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Add TN verse content, if any
            if tn_book_content_unit and tn_verses is not None and tn_verses:
                yield tn_verse_notes_enclosing_div_fmt_str.format(
                    "".join(tn_verses.values())
                )
                yield hr

            # Add TQ verse content, if any
            if tq_book_content_unit and tq_verses:
                yield tq_heading_and_questions_fmt_str.format(
                    tq_book_content_unit.resource_type_name,
                    "".join(tq_verses.values()),
                )
                yield hr

            # Here we return the whole chapter's worth of verses for the secondary usfm
            if usfm_book_content_unit2:
                yield "".join(usfm_book_content_unit2.chapters[chapter_num].content)

            yield end_of_chapter_html

        yield close_direction_html


def assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
    tn_verse_notes_enclosing_div_fmt_str: str = settings.TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR,
    tq_heading_fmt_str: str = settings.TQ_HEADING_FMT_STR,
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN, TQ,
    and TW exists.
    """

    if tn_book_content_unit and tn_book_content_unit.lang_direction == LangDirEnum.RTL:
        yield rtl_direction_html
    else:
        yield ltr_direction_html

    if tn_book_content_unit and tn_book_content_unit.intro_html:
        yield tn_book_content_unit.intro_html
        yield hr

        for chapter_num in tn_book_content_unit.chapters:
            # How to get chapter heading for Translation notes when USFM is not
            # requested? For now we'll use non-localized chapter heading. Add in the
            # USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tn_book_content_unit.lang_code,
                    book_number(tn_book_content_unit.book_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit, chapter_num)

            if bc_book_content_unit:
                # Add the chapter commentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)
                yield hr

            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Add TN verse content, if any
            if tn_book_content_unit and tn_verses is not None and tn_verses:
                yield tn_verse_notes_enclosing_div_fmt_str.format(
                    "".join(tn_verses.values())
                )
                yield hr

            # Add TQ verse content, if any
            if tq_book_content_unit and tq_verses:
                yield tq_heading_and_questions_fmt_str.format(
                    tq_book_content_unit.resource_type_name,
                    "".join(tq_verses.values()),
                )
                yield hr
            yield end_of_chapter_html

        yield close_direction_html


def assemble_tq_tw_for_by_chapter_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = settings.NUM_ZEROS,
    tq_heading_fmt_str: str = settings.TQ_HEADING_FMT_STR,
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ and
    TW exists.
    """
    if tq_book_content_unit and tq_book_content_unit.lang_direction == LangDirEnum.RTL:
        yield rtl_direction_html
    else:
        yield ltr_direction_html

    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            if bc_book_content_unit:
                # Add chapter commmentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)
                yield hr
            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.book_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Add TQ verse content, if any
            if tq_verses:
                yield tq_heading_and_questions_fmt_str.format(
                    tq_book_content_unit.resource_type_name,
                    "".join(tq_verses.values()),
                )
            yield end_of_chapter_html

        yield close_direction_html


# NOTE It is possible to request only TW, however TW is handled at a
# higher level so we essentially have a no-op here.
def assemble_tw_as_iterator_by_chapter_for_lang_then_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
) -> Iterable[HtmlContent]:
    """Construct the HTML for a 'by chapter' strategy wherein only TW exists."""
    yield HtmlContent("")
