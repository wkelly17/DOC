"""
Assembly strategies that sort bgy language and then by book, otherwise known in the UI as 'separate' strategies.
"""


from itertools import groupby

# from re import sub
from typing import Callable, Iterable, Mapping, Optional

from document.config import settings

from document.domain.assembly_strategies.assembly_strategy_utils import (
    book_content_unit_lang_name,
    book_content_unit_book_code,
    first_usfm_book_content_unit,
    tn_book_content_unit,
    tq_book_content_unit,
    tw_book_content_unit,
    second_usfm_book_content_unit,
    bc_book_content_unit,
)
from document.domain.assembly_strategies.assembly_strategies_lang_then_book_by_chapter import (
    assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
    assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
    assemble_tq_tw_for_by_chapter_lang_then_book_1c,
    assemble_tw_as_iterator_by_chapter_for_lang_then_book,
)
from document.domain.bible_books import BOOK_NAMES
from document.domain.model import (
    AssemblyLayoutEnum,
    BCBook,
    BookContent,
    ChunkSizeEnum,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)

logger = settings.logger(__name__)

#########################################################################
# Assembly sub-strategy aka layout implementations for language then
# book strategy.
#
# Possible combinations with usfm (e.g., ulb, ulb-wa, cuv, nav, etc), tn,
# tq, tw, usfm2 (e.g., udb) expressed as a truth table to make sure no
# cases are missed:
#
#
#  | usfm | tn | tq | tw | usfm2 | combination as string | complete | test      | comment    |
#  |------+----+----+----+-------+-----------------------+----------+-----------+------------|
#  |    0 |  0 |  0 |  0 |     1 | usfm2                 | y        | y         | See note * |
#  |    0 |  0 |  0 |  1 |     0 | tw                    | y        | y         |            |
#  |    0 |  0 |  0 |  1 |     1 | tw,usfm2              | y        | y         | See note * |
#  |    0 |  0 |  1 |  0 |     0 | tq                    | y        | y         |            |
#  |    0 |  0 |  1 |  0 |     1 | tq,usfm2              | y        | y         | See note * |
#  |    0 |  0 |  1 |  1 |     0 | tq,tw                 | y        | y         |            |
#  |    0 |  0 |  1 |  1 |     1 | tq,tw,usfm2           | y        | y         | See note * |
#  |    0 |  1 |  0 |  0 |     0 | tn                    | y        | y         |            |
#  |    0 |  1 |  0 |  0 |     1 | tn,usfm2              | y        | y         | See note * |
#  |    0 |  1 |  0 |  1 |     0 | tn,tw                 | y        | y         |            |
#  |    0 |  1 |  0 |  1 |     1 | tn,tw,usfm2           | y        | y         | See note * |
#  |    0 |  1 |  1 |  0 |     0 | tn,tq                 | y        | y         |            |
#  |    0 |  1 |  1 |  0 |     1 | tn,tq,usfm2           | y        | y         | See note * |
#  |    0 |  1 |  1 |  1 |     0 | tn,tq,tw              | y        | y         |            |
#  |    0 |  1 |  1 |  1 |     1 | tn,tq,tw,usfm2        | y        | y         | See note * |
#  |    1 |  0 |  0 |  0 |     0 | usfm                  | y        | y         |            |
#  |    1 |  0 |  0 |  0 |     1 | usfm,usfm2            | y        | y         |            |
#  |    1 |  0 |  0 |  1 |     0 | usfm,tw               | y        | y         |            |
#  |    1 |  0 |  0 |  1 |     1 | usfm,tw,usfm2         | y        | y         |            |
#  |    1 |  0 |  1 |  0 |     0 | usfm,tq               | y        | y         |            |
#  |    1 |  0 |  1 |  0 |     1 | usfm,tq,usfm2         | y        | y         |            |
#  |    1 |  0 |  1 |  1 |     0 | usfm,tq,tw            | y        | y         |            |
#  |    1 |  0 |  1 |  1 |     1 | usfm,tq,tw,usfm2      | y        | y         |            |
#  |    1 |  1 |  0 |  0 |     0 | usfm,tn               | y        | y         |            |
#  |    1 |  1 |  0 |  0 |     1 | usfm,tn,usfm2         | y        | y         |            |
#  |    1 |  1 |  0 |  1 |     0 | usfm,tn,tw            | y        | y         |            |
#  |    1 |  1 |  0 |  1 |     1 | usfm,tn,tw,usfm2      | y        | y         |            |
#  |    1 |  1 |  1 |  0 |     0 | usfm,tn,tq            | y        | y         |            |
#  |    1 |  1 |  1 |  0 |     1 | usfm,tn,tq,usfm2      | y        | y         |            |
#  |    1 |  1 |  1 |  1 |     0 | usfm,tn,tq,tw         | y        | y         |            |
#  |    1 |  1 |  1 |  1 |     1 | usfm,tn,tq,tw,usfm2   | y        | y         |            |
#
# Note *:
#
# If there is only one USFM resource requested then the assembly
# strategy algo puts that USFM resource in usfm_book_content_unit
# position rather than usfm_book_content_unit2 position. If two USFM
# resources are requested then the second one in the DocumentRequest
# gets put in usfm_book_content_unit2 position. Only the first USFM
# resource in the DocumentRequest has any subsequent TN, TQ, and TW. A
# second USFMResource, e.g., udb, stands alone without referencing
# resources. This seems to work out fine in practice, but may be changed
# later by forcing usfm_book_content_unit to be of a particular
# resource_type, e.g., ulb, cuv, nav, and usfm_book_content_unit2 to be
# of another, e.g., udb.
#


def assemble_content_by_lang_then_book(
    book_content_units: Iterable[BookContent],
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
    language_fmt_str: str = settings.LANGUAGE_FMT_STR,
    book_fmt_str: str = settings.BOOK_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> Iterable[str]:
    """
    Assemble by language then by book in lexicographical order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """

    ldebug = logger.debug

    book_units_sorted_by_language = sorted(
        book_content_units,
        key=lambda book_content_unit: book_content_unit.lang_name,
    )

    book_id_map = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))

    for language, group_by_lang in groupby(
        book_units_sorted_by_language,
        book_content_unit_lang_name,
    ):
        yield language_fmt_str.format(language)

        # Sort the books in canonical order for groupby's sake.
        book_content_units_sorted_by_book = sorted(
            group_by_lang,
            key=lambda book_content_unit: book_id_map[book_content_unit.book_code],
        )
        for book, book_content_units_grouped_by_book in groupby(
            book_content_units_sorted_by_book,
            book_content_unit_book_code,
        ):
            yield book_fmt_str.format(book_names[book])

            # Save grouper generator values in list since it will get exhausted
            # when first used and exhausted generators cannot be reused.
            book_content_units_ = list(book_content_units_grouped_by_book)
            usfm_book_content_unit = first_usfm_book_content_unit(book_content_units_)
            tn_book_content_unit_ = tn_book_content_unit(book_content_units_)
            tq_book_content_unit_ = tq_book_content_unit(book_content_units_)
            tw_book_content_unit_ = tw_book_content_unit(book_content_units_)
            usfm_book_content_unit2 = second_usfm_book_content_unit(book_content_units_)
            bc_book_content_unit_ = bc_book_content_unit(book_content_units_)

            # We've got the resources, now we can use the sub-strategy factory
            # method to choose the right function to use from here on out.
            assembly_layout_strategy = assembly_factory_for_lang_then_book_strategy(
                usfm_book_content_unit,
                tn_book_content_unit_,
                tq_book_content_unit_,
                tw_book_content_unit_,
                usfm_book_content_unit2,
                bc_book_content_unit_,
                assembly_layout_kind,
                chunk_size,
            )

            ldebug("assembly_layout_strategy: %s", str(assembly_layout_strategy))

            # Now that we have the sub-strategy, let's run it and
            # generate the HTML output.
            yield from assembly_layout_strategy(
                usfm_book_content_unit,
                tn_book_content_unit_,
                tq_book_content_unit_,
                tw_book_content_unit_,
                usfm_book_content_unit2,
                bc_book_content_unit_,
            )


def assembly_factory_for_lang_then_book_strategy(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
) -> Callable[
    [
        Optional[USFMBook],
        Optional[TNBook],
        Optional[TQBook],
        Optional[TWBook],
        Optional[USFMBook],
        Optional[BCBook],
    ],
    Iterable[HtmlContent],
]:
    """
    Strategy pattern. Given the existence, i.e., exists or None, of each
    type of the possible resource instances (i.e., the resource parameters
    above) and an assembly layout kind, returns the appropriate
    layout/assembly function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in an otherwise monolithic assembly algorithm
    that would be checking the existence of each resource.
    This makes adding new strategies straightforward, if a bit
    redundant. The redundancy is the cost for comprehension.
    """
    strategies: Mapping[
        tuple[
            bool,  # usfm_book_content_unit_exists
            bool,  # tn_book_content_unit_exists
            bool,  # tq_book_content_unit_exists
            bool,  # tw_book_content_unit_exists
            bool,  # usfm_book_content_unit2_exists
            bool,  # bc_book_content_unit_exists
            AssemblyLayoutEnum,  # assembly_layout_kind
            ChunkSizeEnum,  # chunk_size
        ],
        Callable[
            [
                Optional[USFMBook],
                Optional[TNBook],
                Optional[TQBook],
                Optional[TWBook],
                Optional[USFMBook],
                Optional[BCBook],
            ],
            Iterable[HtmlContent],
        ],
    ] = {  # This is a big truth/dispatch table that ensures every case is handled explicitly.
        # ----------------------------------
        # By chapter:
        # ----------------------------------
        (
            True,
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_tw_for_by_chapter_lang_then_book_1c,
        (
            False,
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_tw_for_by_chapter_lang_then_book_1c,
        (
            False,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_tw_for_by_chapter_lang_then_book_1c,
        (
            False,
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_tw_for_by_chapter_lang_then_book_1c,
        (
            False,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_lang_then_book,
        (
            False,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_lang_then_book,
        (
            False,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_tw_for_by_chapter_lang_then_book_1c,
        (
            False,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_tw_for_by_chapter_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_lang_then_book_1c,
    }
    return strategies[
        (
            # Turn existence (exists or not) into a boolean for each instance, the
            # tuple of these together are immutable, and thus an hashable
            # dictionary key into our function lookup/dispatch table.
            usfm_book_content_unit is not None,
            tn_book_content_unit is not None,
            tq_book_content_unit is not None,
            tw_book_content_unit is not None,
            usfm_book_content_unit2 is not None,
            bc_book_content_unit is not None,
            assembly_layout_kind,
            chunk_size,
        )
    ]
