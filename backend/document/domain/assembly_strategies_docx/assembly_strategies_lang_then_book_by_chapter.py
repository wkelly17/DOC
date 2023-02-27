from typing import Iterable, Mapping, Optional

import re
import time
from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    book_intro_commentary,
    book_number,
    chapter_commentary,
    chapter_intro,
    verses_for_chapter_tn,
    verses_for_chapter_tq,
)
from document.domain.bible_books import BOOK_NUMBERS, BOOK_NAMES
from document.domain.model import (
    BCBook,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
    VerseRef,
)
from docx import Document  # type: ignore
from docxtpl import DocxTemplate  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore
from docx.enum.section import WD_SECTION  # type: ignore
from docx.oxml.ns import qn  # type: ignore
from docxcompose.composer import Composer  # type: ignore

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
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_name_fmt_str: str = settings.BOOK_NAME_FMT_STR,
) -> Composer:
    """
    Construct the Docx wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, TW, and a second USFM (e.g.,
    udb, f10, etc.) may exist. Non-USFM resources, e.g., TN, TQ, and
    TW will reference (and link where applicable) the first USFM resource.
    The second USFM resource is displayed last in this interleaving
    strategy.
    """
    html_to_docx = HtmlToDocx()
    doc = Document()
    composer = Composer(doc)

    one_column_html = []
    if tn_book_content_unit:
        if tn_book_content_unit.intro_html:
            one_column_html.append(tn_book_content_unit.intro_html)

    # NOTE For v1 UI release this bc_book_content_unit will be None
    if bc_book_content_unit:
        if bc_book_content_unit.book_intro:
            # NOTE You might want a label before the commentary book intro
            one_column_html.append(bc_book_content_unit.book_intro)

    if usfm_book_content_unit:
        # Book title centered
        # TODO One day book title could be localized.
        one_column_html.append(
            book_name_fmt_str.format(book_names[usfm_book_content_unit.resource_code])
        )

    if one_column_html:
        subdoc = html_to_docx.parse_html_string("".join(one_column_html))
        composer.append(subdoc)

    if usfm_book_content_unit:
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            one_column_html = []
            # NOTE Commenting out heading since USFM comes before TN verse notes and
            # includes its own chapter heading. # Add in the USFM chapter heading.
            # chapter_heading = HtmlContent("")
            # chapter_heading = chapter.content[0]
            # one_column_html.append(chapter_heading)

            tn_verses: Optional[dict[VerseRef, HtmlContent]] = None
            tq_verses: Optional[dict[VerseRef, HtmlContent]] = None
            chapter_intro_ = HtmlContent("")
            chapter_commentary_ = HtmlContent("")
            if tn_book_content_unit:
                chapter_intro_ = chapter_intro(tn_book_content_unit, chapter_num)
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if bc_book_content_unit:
                chapter_commentary_ = chapter_commentary(
                    bc_book_content_unit, chapter_num
                )
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # NOTE Footnotes are rendered to HTML by USFM-TOOLS after the chapter's
            # verse content so we don't want them included additionally/accidentally
            # here also since we explicitly include footnotes after this. Later, if
            # we ditch the verse level interleaving, we can move this into the
            # parsing module.
            #
            # Find the index of where footnotes occur at the end of
            # chapter.content, if the chapter has footnotes.
            index_of_footnotes = 0
            for idx, element in enumerate(chapter.content):
                if re.search("footnotes", element):
                    index_of_footnotes = idx

            # Now let's interleave USFM chapter.
            if index_of_footnotes != 0:  # chapter.content includes footnote
                chapter_content_sans_footnotes = chapter.content[
                    0 : index_of_footnotes - 1
                ]
                one_column_html.append("".join(chapter_content_sans_footnotes))
            else:
                one_column_html.append("".join(chapter.content))

            # Add scripture footnotes if available
            if chapter.footnotes:
                one_column_html.append(
                    "{}{}".format(footnotes_heading, chapter.footnotes)
                )

            if chapter_intro_:
                one_column_html.append(chapter_intro_)
            if chapter_commentary_:  # NOTE For v1, chapter_commentary_ should be None
                one_column_html.append(chapter_commentary_)

            if one_column_html:
                # Get ready for one column again (this matters the 2-Nth times in the loop).
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type

                # Set to one column layout for subdocument to be added next.
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "1")

                subdoc = html_to_docx.parse_html_string("".join(one_column_html))
                composer.append(subdoc)

            # Add TN verse content, if any
            if tn_book_content_unit and tn_verses is not None and tn_verses:
                # Start new section for different (two) column layout.
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "2")
                cols.set(
                    qn("w:space"), "10"
                )  # Set space between columns to 10 points ->0.01"

                subdoc = html_to_docx.parse_html_string(
                    tn_verse_notes_enclosing_div_fmt_str.format(
                        "".join(tn_verses.values()),
                    )
                )
                composer.append(subdoc)

            # NOTE For v1 UI release this bc_book_content_unit will be None.
            #
            # Add TQ verse content, if any.
            if tq_book_content_unit and tq_verses is not None and tq_verses:
                # Start new section for two column layout
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "2")
                cols.set(
                    qn("w:space"), "10"
                )  # Set space between columns to 10 points ->0.01"

                subdoc = html_to_docx.parse_html_string(
                    tq_heading_and_questions_fmt_str.format(
                        tq_book_content_unit.resource_type_name,
                        "".join(tq_verses.values()),
                    )
                )
                composer.append(subdoc)

            # TODO Get feedback on whether we should allow a user to select a primary _and_
            # a secondary USFM resource. If we want to limit the user to only one USFM per
            # document then we would want to control that in the UI and maybe also at the API
            # level. The API level control should be implemented in the DocumentRequest
            # validation.
            #
            # NOTE For v1 UI release this usfm_book_content_unit2 will be None.
            if usfm_book_content_unit2:
                # Here we return the whole chapter's worth of verses for the secondary usfm
                subdoc = html_to_docx.parse_html_string(
                    "".join(usfm_book_content_unit2.chapters[chapter_num].content)
                )
                composer.append(subdoc)

    return composer


# NOTE For the simple UI, this won't be an option because it will require USFM.
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
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
) -> Composer:
    """
    Construct the Docx for a 'by chapter' strategy wherein USFM is not
    being request, but TN is requested and TQ and TW may also be
    requested.
    """
    html_to_docx = HtmlToDocx()
    doc = Document()
    composer = Composer(doc)

    one_column_html = []
    if tn_book_content_unit:
        if tn_book_content_unit.intro_html:
            # Add the chapter intro
            one_column_html.append(tn_book_content_unit.intro_html)
            # subdoc = html_to_docx.parse_html_string(tn_book_content_unit.intro_html)
            # composer.append(subdoc)

        # NOTE For v1 UI release this bc_book_content_unit will be None
        if bc_book_content_unit:
            if bc_book_content_unit.book_intro:
                # NOTE You might want a label before the commentary book intro
                one_column_html.append(bc_book_content_unit.book_intro)

        if one_column_html:
            subdoc = html_to_docx.parse_html_string("".join(one_column_html))
            composer.append(subdoc)

        for chapter_num in tn_book_content_unit.chapters:
            # How to get chapter heading for Translation notes when USFM is not
            # requested? For now we'll use non-localized chapter heading.
            #
            # Add in the chapter heading.
            one_column_html = []
            one_column_html.append(
                chapter_header_fmt_str.format(
                    tn_book_content_unit.lang_code,
                    book_number(tn_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Add the translation notes chapter intro.
            one_column_html.append(chapter_intro(tn_book_content_unit, chapter_num))

            if bc_book_content_unit:
                # Add the chapter commentary.
                one_column_html.append(
                    chapter_commentary(bc_book_content_unit, chapter_num)
                )

            if one_column_html:
                # Get ready for one column again (at top of loop)
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type

                # Set to one column layout for subdocument to be added next.
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "1")

                subdoc = html_to_docx.parse_html_string("".join(one_column_html))
                composer.append(subdoc)

            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Add TN verse content, if any
            if tn_book_content_unit and tn_verses is not None and tn_verses:
                # Start new section for different (two) column layout.
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type

                # Set to two column layout for subdocument to be added next.
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "2")
                cols.set(
                    qn("w:space"), "10"
                )  # Set space between columns to 10 points ->0.01"

                subdoc = html_to_docx.parse_html_string(
                    tn_verse_notes_enclosing_div_fmt_str.format(
                        "".join(tn_verses.values()),
                    )
                )
                composer.append(subdoc)

            # Add TQ verse content, if any
            if tq_book_content_unit and tq_verses:
                # Start new section for different (two) column layout.
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type

                # Set to two column layout for subdocument to be added next.
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "2")
                cols.set(
                    qn("w:space"), "10"
                )  # Set space between columns to 10 points ->0.01"

                subdoc = html_to_docx.parse_html_string(
                    tq_heading_and_questions_fmt_str.format(
                        tq_book_content_unit.resource_type_name,
                        "".join(tq_verses.values()),
                    )
                )
                composer.append(subdoc)

    return composer


# NOTE For the v1 UI, you have to choose USFM so this will not execute
# for that version.
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
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
) -> Composer:
    """
    Construct the HTML for a 'by chapter' strategy wherein only TQ and
    TW exists.
    """
    html_to_docx = HtmlToDocx()
    doc = Document()
    composer = Composer(doc)

    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            one_column_html = []
            if bc_book_content_unit:
                # Add chapter commmentary.
                one_column_html.append(
                    chapter_commentary(bc_book_content_unit, chapter_num)
                )

            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            one_column_html.append(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )
            if one_column_html:
                # Get ready for one column again (at top of loop)
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type

                # Set to one column layout for subdocument to be added next.
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "1")

                subdoc = html_to_docx.parse_html_string("".join(one_column_html))
                composer.append(subdoc)

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Add TQ verse content, if any
            if tq_verses:
                # Start new section for different (two) column layout.
                new_section = doc.add_section(WD_SECTION.CONTINUOUS)
                new_section.start_type

                # Set to two column layout for subdocument to be added next.
                sectPr = new_section._sectPr
                cols = sectPr.xpath("./w:cols")[0]
                cols.set(qn("w:num"), "2")
                cols.set(
                    qn("w:space"), "10"
                )  # Set space between columns to 10 points ->0.01"

                subdoc = html_to_docx.parse_html_string(
                    tq_heading_and_questions_fmt_str.format(
                        tq_book_content_unit.resource_type_name,
                        "".join(tq_verses.values()),
                    )
                )
                composer.append(subdoc)

    return composer


# NOTE For the v1 UI, this will never execute since TW is not an
# option in that version.
def assemble_tw_as_iterator_by_chapter_for_lang_then_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
) -> Iterable[HtmlContent]:

    """
    This function handles the following dispatch table
    cases in the assembly_strategies_lang_then_book
    module:

    - TW only
    - BC and TW
    - BC only

    TW is handled outside this module, that is why no
    code for TW is explicitly included here.
    """
    if bc_book_content_unit:
        yield bc_book_content_unit.book_intro
        for chapter in bc_book_content_unit.chapters.values():
            yield chapter.commentary
