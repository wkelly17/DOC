"""
Assembly strategies that sort by book then language, otherwise known in the UI as 'mix' strategies.
"""


from itertools import groupby
from typing import Callable, Iterable, Mapping, Sequence

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    book_content_unit_resource_code,
)
from document.domain.assembly_strategies.assembly_strategies_book_then_lang_by_chapter import (
    assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
    assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
    assemble_tn_as_iterator_by_chapter_for_book_then_lang,
    assemble_tq_as_iterator_by_chapter_for_book_then_lang,
    assemble_tw_as_iterator_by_chapter_for_book_then_lang,
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


def assemble_content_by_book_then_lang(
    book_content_units: Iterable[BookContent],
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
    book_as_grouper_fmt_str: str = settings.BOOK_AS_GROUPER_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> Iterable[str]:
    """
    Assemble by book then by language in alphabetic order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """

    ldebug = logger.debug

    # Sort the books in canonical order.
    book_id_map = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))
    book_content_units_sorted_by_book = sorted(
        book_content_units,
        key=lambda book_content_unit: book_id_map[book_content_unit.resource_code],
    )
    for book, group_by_book in groupby(
        book_content_units_sorted_by_book,
        book_content_unit_resource_code,
    ):
        yield book_as_grouper_fmt_str.format(book_names[book])

        # Save grouper generator values in list since it will get exhausted
        # when used and exhausted generators cannot be reused.
        book_content_units_grouped_by_book = list(group_by_book)
        usfm_book_content_units = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, USFMBook)
        ]
        tn_book_content_units: Sequence[TNBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, TNBook)
        ]
        tq_book_content_units: Sequence[TQBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, TQBook)
        ]
        tw_book_content_units: Sequence[TWBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, TWBook)
        ]
        bc_book_content_units: Sequence[BCBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, BCBook)
        ]

        # We've got the resources, now we can use the layout factory
        # function to choose the right function to use from here on out.
        assembly_layout_for_book_then_lang_strategy = (
            assembly_factory_for_book_then_lang_strategy(
                usfm_book_content_units,
                tn_book_content_units,
                tq_book_content_units,
                tw_book_content_units,
                bc_book_content_units,
                assembly_layout_kind,
                chunk_size,
            )
        )

        ldebug(
            "assembly_layout_for_book_then_lang_strategy: %s",
            str(assembly_layout_for_book_then_lang_strategy),
        )

        # Now that we have the sub-strategy, let's run it and
        # generate the HTML output.
        yield from assembly_layout_for_book_then_lang_strategy(
            usfm_book_content_units,
            tn_book_content_units,
            tq_book_content_units,
            tw_book_content_units,
            bc_book_content_units,
        )


def assembly_factory_for_book_then_lang_strategy(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
) -> Callable[
    [
        Sequence[USFMBook],
        Sequence[TNBook],
        Sequence[TQBook],
        Sequence[TWBook],
        Sequence[BCBook],
    ],
    Iterable[HtmlContent],
]:
    """
    Strategy pattern. Given the existence, i.e., exists or empty, of each
    type of the possible resource instances and an
    assembly layout kind, returns the appropriate layout
    function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in an otherwise monolithic assembly algorithm
    that would be checking the existence of each resource.
    This makes adding new strategies straightforward, if a bit
    redundant. The redundancy is the cost for comprehension.
    """
    strategies: Mapping[
        tuple[
            bool,  # usfm_book_content_units is non-empty
            bool,  # tn_book_content_units is non-empty
            bool,  # tq_book_content_units is non-empty
            bool,  # tw_book_content_units is non-empty
            bool,  # bc_book_content_units is non-empty
            AssemblyLayoutEnum,  # assembly_layout_kind
            ChunkSizeEnum,  # chunk_size
        ],
        Callable[
            [
                Sequence[USFMBook],
                Sequence[TNBook],
                Sequence[TQBook],
                Sequence[TWBook],
                Sequence[BCBook],
            ],
            Iterable[HtmlContent],
        ],
    ] = {
        # -------------------------
        # By chapter
        # -------------------------
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_usfm_as_iterator_by_chapter_for_book_then_lang_1c,
        (
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tn_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tq_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_book_then_lang,
        (
            False,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
            ChunkSizeEnum.CHAPTER,
        ): assemble_tw_as_iterator_by_chapter_for_book_then_lang,
    }
    return strategies[
        # Turn existence (exists or not) into a boolean for each
        # instance, the tuple of these together are an immutable,
        # and hashable dictionary key into our function lookup table.
        (
            True if usfm_book_content_units else False,
            True if tn_book_content_units else False,
            True if tq_book_content_units else False,
            True if tw_book_content_units else False,
            True if bc_book_content_units else False,
            assembly_layout_kind,
            chunk_size,
        )
    ]
