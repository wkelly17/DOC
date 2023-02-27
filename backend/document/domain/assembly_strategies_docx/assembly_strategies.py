"""
This module provides the assembly strategies and sub-strategies,
otherwise known as layouts, that are used to assemble Docx documents.

Currently, there are two levels of assembly strategies: one higher,
chosen by assembly strategy, and one lower, chosen by assembly layout.
These two levels of assembly strategies work together in the following
way: the higher level constrains the assembly algorithm by some
criteria, e.g., group content by language and then by book, and then
the lower level further organizes the assembly within those
constraints, e.g., by superimposing an order to when resource's are
interleaved thus affecting the structural layout of the content. It is
possible to have both multiple higher level, so-called 'assembly
strategies' and lower level, so-called 'layout', assembly strategies.

Architecturally, assembly strategies utilize the Strategy pattern:
https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py
"""

from typing import Any

from document.config import settings
from document.domain.assembly_strategies_docx.assembly_strategies_book_then_lang import (
    assemble_content_by_book_then_lang,
)
from document.domain.assembly_strategies_docx.assembly_strategies_lang_then_book import (
    assemble_content_by_lang_then_book,
)

from document.domain.model import (
    AssemblyStrategyEnum,
)

logger = settings.logger(__name__)


def assembly_strategy_factory(
    assembly_strategy_kind: AssemblyStrategyEnum,
) -> Any:
    """
    Strategy pattern. Given an assembly_strategy_kind, returns the
    appropriate strategy function to run.
    """
    strategies = {
        AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER: assemble_content_by_lang_then_book,
        AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER: assemble_content_by_book_then_lang,
    }
    return strategies[assembly_strategy_kind]
