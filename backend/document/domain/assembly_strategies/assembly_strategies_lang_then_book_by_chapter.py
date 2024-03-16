from typing import Iterable, Optional

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    book_title,
    chapter_commentary,
    chapter_footnotes,
    chapter_heading,
    chapter_intro,
    chapter_content_sans_footnotes,
    language_direction_html,
    book_intro,
    tn_chapter_verses,
    tq_chapter_verses,
)

from document.domain.model import (
    BCBook,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)

logger = settings.logger(__name__)


def assemble_usfm_by_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    yield from language_direction_html(usfm_book_content_unit)
    yield from book_intro(tn_book_content_unit)
    yield from book_intro(bc_book_content_unit)
    if usfm_book_content_unit:
        yield book_title(usfm_book_content_unit.book_code)
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            yield chapter_content_sans_footnotes(chapter.content)
            yield hr
            yield from chapter_footnotes(chapter)
            yield from chapter_intro(tn_book_content_unit, chapter_num)
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
            yield from tn_chapter_verses(tn_book_content_unit, chapter_num)
            yield from tq_chapter_verses(tq_book_content_unit, chapter_num)
            # If the user chose two USFM resource types for a language. e.g., fr:
            # ulb, f10, show the second USFM content here
            if usfm_book_content_unit2:
                yield "".join(usfm_book_content_unit2.chapters[chapter_num].content)
            yield end_of_chapter_html
    yield close_direction_html


def assemble_tn_by_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    yield from language_direction_html(tn_book_content_unit)
    yield from book_intro(tn_book_content_unit)
    if tn_book_content_unit:
        for chapter_num in tn_book_content_unit.chapters:
            yield chapter_heading(tn_book_content_unit, chapter_num)
            yield from chapter_intro(tn_book_content_unit, chapter_num)
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
            yield from tn_chapter_verses(tn_book_content_unit, chapter_num)
            yield from tq_chapter_verses(tq_book_content_unit, chapter_num)
            yield end_of_chapter_html
    yield close_direction_html


def assemble_tq_by_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> Iterable[HtmlContent]:
    yield from language_direction_html(tq_book_content_unit)
    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            yield from chapter_commentary(bc_book_content_unit, chapter_num)
            yield chapter_heading(tq_book_content_unit, chapter_num)
            yield from tq_chapter_verses(tq_book_content_unit, chapter_num)
            yield end_of_chapter_html
    yield close_direction_html


# It is possible to request only TW, however TW is handled at a
# higher level so we have a no-op here.
def assemble_tw_by_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
) -> Iterable[HtmlContent]:
    yield HtmlContent("")
