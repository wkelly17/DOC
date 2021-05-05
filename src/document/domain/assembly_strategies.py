"""
This module provides the assembly strategies and sub-strategies that
are used to assemble HTML documents prior to their conversion to PDF
form.

Assembly strategies utilize the Strategy pattern:
https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py
"""


# Handle circular import issue with document_generator module.
from __future__ import annotations  # https://www.python.org/dev/peps/pep-0563/

import itertools
import logging  # For logdecorator
import re

from logdecorator import log_on_start
from typing import Callable, cast, Dict, List, Optional, Tuple

from document import config
from document.domain import bible_books, document_generator, model
from document.domain.resource import (
    Resource,
    USFMResource,
    TNResource,
    TWResource,
    TQResource,
    TAResource,
)


logger = config.get_logger(__name__)

########################################################################
## Asseembly strategy and sub-strategy factories
##
## Currently, there are two levels of assembly strategies: one higher,
## chosen by _assembly_strategy_factory, and one lower, chosen by
## _assembly_sub_strategy_factory. These two levels of assembly
## strategies work together in the following way: the higher level
## constrains the assembly algorithm by some criteria, e.g., by
## language, and then the lower level further organizes the assembly
## within those constraints, .e.g., by superimposing an order to when
## resource's are interleaved. It is possible to have both multiple
## higher level, so-called 'assembly strategies' and lower level,
## so-called 'sub strategies', assembly strategies.


def _assembly_strategy_factory(
    assembly_strategy_kind: model.AssemblyStrategyEnum,
) -> Callable[[document_generator.DocumentGenerator], str]:
    """
    Strategy pattern. Given an assembly_strategy_kind, returns the
    appropriate strategy function to run.
    """
    strategies = {
        model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER: _assemble_content_by_lang_then_book
    }
    return strategies[assembly_strategy_kind]


def _assembly_sub_strategy_factory(
    usfm_resource: Optional[USFMResource],  # ulb, nav, cuv, etc.
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],  # udb
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Callable[
    [
        Optional[USFMResource],
        Optional[TNResource],
        Optional[TQResource],
        Optional[TWResource],
        Optional[TAResource],
        Optional[USFMResource],
        model.AssemblySubstrategyEnum,
    ],
    model.HtmlContent,
]:
    """
    Strategy pattern. Given the existence, i.e., exists or None, of each
    type of the possible resource instances and an
    assembly sub-strategy kind, returns the appropriate sub-strategy
    function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in an otherwise monolithic assembly algorithm
    that would be checking the existence of each resource.
    This makes adding new strategies straightforward, if a bit
    redundant. The redundancy is the cost of comprehension.
    """
    strategies: Dict[
        Tuple[
            # Params: usfm_resource_exists, tn_resource_exists, tq_resource_exists, tw_resource_exists, ta_resource_exists, usfm_resource2_exists, assembly_strategy_kind
            bool,
            bool,
            bool,
            bool,
            bool,
            bool,
            model.AssemblySubstrategyEnum,
        ],
        Callable[
            [
                Optional[USFMResource],
                Optional[TNResource],
                Optional[TQResource],
                Optional[TWResource],
                Optional[TAResource],
                Optional[USFMResource],
                model.AssemblySubstrategyEnum,
            ],
            model.HtmlContent,
        ],
    ] = {
        (
            True,
            True,
            True,
            True,
            True,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tn_tq_tw_ta_content_by_verse,
        (
            True,
            True,
            True,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tn_tq_tw_content_by_verse,
        (
            True,
            True,
            False,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tn_tw_content_by_verse,
        (
            True,
            False,
            True,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tq_tw_content_by_verse,
        (
            True,
            False,
            False,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tw_content_by_verse,
        (
            True,
            True,
            True,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tn_tq_content_by_verse,
        (
            True,
            False,
            True,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tq_content_by_verse,
        (
            False,
            True,
            True,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tn_tq_tw_content_by_verse,
        (
            False,
            True,
            False,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tn_tw_content_by_verse,
        (
            False,
            True,
            True,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tn_tq_content_by_verse,
        (
            False,
            False,
            True,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tq_tw_content_by_verse,
        (
            False,
            False,
            False,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tw_content_by_verse,
        (
            True,
            True,
            False,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tn_content_by_verse,
        (
            False,
            False,
            True,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tq_content_by_verse,
        (
            True,
            False,
            False,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_content_by_verse,
        (
            False,
            True,
            False,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tn_content_by_verse,
    }
    return strategies[
        (
            # Turn existence (exists or not) into a boolean for each
            # instance, the tuple of these together are an immutable,
            # and thus hashable, dictionary key into our function lookup table.
            usfm_resource is not None,
            tn_resource is not None,
            tq_resource is not None,
            tw_resource is not None,
            ta_resource is not None,
            usfm_resource2 is not None,
            assembly_substrategy_kind,
        )
    ]


#######################################
## Assembly strategy implementations


@log_on_start(
    logging.INFO,
    "Assembling document by interleaving at the verse level using 'verse' strategy.",
    logger=logger,
)
def _assemble_content_by_lang_then_book(
    docgen: document_generator.DocumentGenerator,
) -> str:
    """
    Assemble by language then by book in lexicographical order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """
    # NOTE: For now we are ignoring links that may be presented. I
    # hope to handle their transformations with a Markdown extension
    # plugin rather than the legacy way of doing regexp search and
    # replace on markdown content that has been concatenated. So we'll
    # transform them at the time the markdown is converted to HTML.

    # NOTE Each strategy can interleave resource material the way it
    # wants. A user could choose a strategy they want at the front
    # end. Presumably, we could offer the user such strategies from a
    # dropdown that would be intelligent enough to only present
    # choices that make sense for the number of languages and
    # resources they have selected, e.g., we wouldn't bother them with
    # the choice of interleaving strategy if for instance all they
    # wanted was TN for Swahili and nothing else.

    resources_sorted_by_language = sorted(
        docgen._found_resources, key=lambda resource: resource.lang_name,
    )
    html = []
    language: str
    # group_by_lang: itertools._grouper
    for language, group_by_lang in itertools.groupby(
        resources_sorted_by_language, lambda resource: resource.lang_name,
    ):
        html.append(config.get_html_format_string("language").format(language))

        # For groupby's sake, we need to first sort
        # group_by_lang before doing a groupby operation on it so that
        # resources will be clumped together by resource code, i.e.,
        # by language, otherwise a new group will be created every time a new
        # resource_code is sequentially encountered.
        resources_sorted_by_book = sorted(
            group_by_lang, key=lambda resource: resource.resource_code
        )
        for book, group_by_book in itertools.groupby(
            resources_sorted_by_book, lambda resource: resource.resource_code
        ):
            html.append(
                config.get_html_format_string("book").format(
                    # FIXME Use localized book name
                    bible_books.BOOK_NAMES[book]
                )
            )

            # Save grouper generator since it will get exhausted
            # when used and exhausted generators cannot be reused.
            resources = list(group_by_book)
            usfm_resource: Optional[USFMResource] = _get_first_usfm_resource(resources)
            tn_resource: Optional[TNResource] = _get_tn_resource(resources)
            tq_resource: Optional[TQResource] = _get_tq_resource(resources)
            tw_resource: Optional[TWResource] = _get_tw_resource(resources)
            ta_resource: Optional[TAResource] = _get_ta_resource(resources)
            usfm_resource2: Optional[USFMResource] = _get_second_usfm_resource(
                resources
            )

            # We've got the resources, now we can use the sub-strategy factory
            # method to choose the right function to use from here on out.
            docgen._assembly_sub_strategy = _assembly_sub_strategy_factory(
                usfm_resource,
                tn_resource,
                tq_resource,
                tw_resource,
                ta_resource,
                usfm_resource2,
                config.get_default_assembly_substrategy(),
            )

            sub_html: model.HtmlContent = docgen._assembly_sub_strategy(
                usfm_resource,
                tn_resource,
                tq_resource,
                tw_resource,
                ta_resource,
                usfm_resource2,
                config.get_default_assembly_substrategy(),
            )
            html.append(sub_html)

    return "\n".join(html)


########################################################################
## Assembly sub-strategy implementations
##
## Possible combinations with usfm, tn, tq, tw:
##
## | ulb | tn | tq | tw | combination as string | complete | unit test |
## |-----+----+----+----+-----------------------+----------+-----------|
## |   0 |  0 |  0 |  1 | tw                    | y        | y         |
## |   0 |  0 |  1 |  0 | tq                    | y        | y         |
## |   0 |  0 |  1 |  1 | tq,tw                 | y        | y         |
## |   0 |  1 |  0 |  0 | tn                    | y        | y         |
## |   0 |  1 |  0 |  1 | tn,tw                 | y        | y         |
## |   0 |  1 |  1 |  0 | tn,tq                 | y        | y         |
## |   0 |  1 |  1 |  1 | tn,tq,tw              | y        | y         |
## |   1 |  0 |  0 |  0 | ulb                   | y        | y         |
## |   1 |  0 |  0 |  1 | ulb,tw                | y        | y         |
## |   1 |  0 |  1 |  0 | ulb,tq                | y        | y         |
## |   1 |  0 |  1 |  1 | ulb,tq,tw             | y        | y         |
## |   1 |  1 |  0 |  0 | ulb,tn                | y        | y         |
## |   1 |  1 |  0 |  1 | ulb,tn,tw             | y        | y         |
## |   1 |  1 |  1 |  0 | ulb,tn,tq             | y        | y         |
## |   1 |  1 |  1 |  1 | ulb,tn,tq,tw          | y        | y         |


def _assemble_usfm_tn_tq_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TN, TQ,
    and TW exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that tn_resource object is not None.
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(model.HtmlContent(book_intro))

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is otherwise not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)
        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)
        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's interleave USFM verse with its translation note, translation
        # questions, and translation words if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add header
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add scripture verse
            html.append(verse)
            # Add TN verse content, if any
            if tn_verses and verse_num in tn_verses:
                tn_verse_content = _format_tn_verse(
                    chapter_num, verse_num, tn_verses[verse_num]
                )
                html.extend(tn_verse_content)
            # Add TQ verse content, if any
            if tq_verses and verse_num in tq_verses:
                tq_verse_content = _format_tq_verse(
                    chapter_num, verse_num, tq_verses[verse_num]
                )
                html.extend(tq_verse_content)
            # Add the translation words links section.
            translation_word_links_html = tw_resource.get_translation_word_links(
                chapter_num, verse_num, verse,
            )
            html.extend(translation_word_links_html)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section()
    html.extend(linked_translation_words)
    return model.HtmlContent("\n".join(html))


def _assemble_usfm_tn_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TN, and
    TW exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that tn_resource object is not None.
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(model.HtmlContent(book_intro))

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is otherwise not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)
        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)
        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's interleave USFM verse with its translation note, translation
        # questions, and translation words if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add header
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add verse
            html.append(verse)
            # Add TN verse content, if any
            if tn_verses and verse_num in tn_verses:
                tn_verse_content = _format_tn_verse(
                    chapter_num, verse_num, tn_verses[verse_num]
                )
                html.extend(tn_verse_content)
            # Add the translation words links section
            translation_word_links_html = tw_resource.get_translation_word_links(
                chapter_num, verse_num, verse,
            )
            html.extend(translation_word_links_html)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section()
    html.extend(linked_translation_words)
    return model.HtmlContent("\n".join(html))


def _assemble_usfm_tq_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TQ,
    and TW exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is otherwise not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)

        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's interleave USFM verse with its translation note, translation
        # questions, and translation words if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add header
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add scripture verse
            html.append(verse)
            # Add TN verse content, if any
            if tq_verses and verse_num in tq_verses:
                tq_verse_content = _format_tq_verse(
                    chapter_num, verse_num, tq_verses[verse_num]
                )
                html.extend(tq_verse_content)
            # Add the translation words links section
            translation_word_links_html = tw_resource.get_translation_word_links(
                chapter_num, verse_num, verse,
            )
            html.extend(translation_word_links_html)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section()
    html.extend(linked_translation_words)
    return model.HtmlContent("\n".join(html))


def _assemble_usfm_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM and TW
    exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is otherwise not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's interleave USFM verse with its translation note, translation
        # questions, and translation words if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add scripture verse header
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add scripture verse
            html.append(verse)
            # Add the translation words links section
            translation_word_links_html = tw_resource.get_translation_word_links(
                chapter_num, verse_num, verse,
            )
            html.extend(translation_word_links_html)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section()
    html.extend(linked_translation_words)
    return model.HtmlContent("\n".join(html))


def _assemble_usfm_tn_tq_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TN, and
    TQ exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that tn_resource object is not None.
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)
        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)
        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's interleave USFM verse with its
        # translation note if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add scripture verse header
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add scripture verse
            html.append(verse)
            # Add TN verse content, if any
            if tn_verses and verse_num in tn_verses:
                tn_verse_content = _format_tn_verse(
                    chapter_num, verse_num, tn_verses[verse_num]
                )
                html.extend(tn_verse_content)
            # Add TQ verse content, if any
            if tq_verses and verse_num in tq_verses:
                tq_verse_content = _format_tq_verse(
                    chapter_num, verse_num, tq_verses[verse_num]
                )
                html.extend(tq_verse_content)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    return model.HtmlContent("\n".join(html))


def _assemble_usfm_tq_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only USFM and TQ exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)

        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's interleave USFM verse with its
        # translation note if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add scripture verse heading
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add scripture verse
            html.append(verse)
            # Add TQ verse content, if any
            if tq_verses and verse_num in tq_verses:
                tq_verse_content = _format_tq_verse(
                    chapter_num, verse_num, tq_verses[verse_num]
                )
                html.extend(tq_verse_content)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    return model.HtmlContent("\n".join(html))


def _assemble_usfm_tn_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only USFM and
    TN exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)
        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's interleave USFM verse with its
        # translation note if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add scripture verse header
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add scripture verse
            html.append(verse)
            # Add TN verse content, if any
            if tn_verses and verse_num in tn_verses:
                tn_verse_content = _format_tn_verse(
                    chapter_num, verse_num, tn_verses[verse_num]
                )
                html.extend(tn_verse_content)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    return model.HtmlContent("\n".join(html))


def _assemble_usfm_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only USFM exists.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    html: List[model.HtmlContent] = []

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now append the USFM verses
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            # Add scripture verse header
            html.append(
                model.HtmlContent(
                    config.get_html_format_string("verse").format(
                        chapter_num, verse_num
                    )
                )
            )
            # Add scripture verse
            html.append(verse)
        # Add scripture footnotes if available
        if chapter.chapter_footnotes:
            html.append(config.get_html_format_string("footnotes"))
            html.append(chapter.chapter_footnotes)
    return model.HtmlContent("\n".join(html))


def _assemble_tn_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN exists.
    """
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that tn_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num in sorted(tn_resource.book_payload.chapters):
        # How to get chapter heading for Translation notes when there is
        # not USFM requested? For now we'll use non-localized chapter heading.
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent(
            config.get_html_format_string("tn_only_chapter_header").format(
                tn_resource.lang_code,
                bible_books.BOOK_NUMBERS[tn_resource.resource_code].zfill(3),
                str(chapter_num).zfill(3),
                chapter_num,
            )
        )
        html.append(chapter_heading)

        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        # Get TN chapter verses
        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's get all the verse translation notes available.
        if tn_verses:
            for verse_num, verse in sorted(tn_verses.items()):
                tn_verse_content = _format_tn_verse(chapter_num, verse_num, verse)
                html.extend(tn_verse_content)
    return model.HtmlContent("\n".join(html))


def _assemble_tn_tq_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN, TQ,
    and TW exists.
    """
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that tn_resource object is not None.
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num in sorted(tn_resource.book_payload.chapters):
        # How to get chapter heading for Translation notes when USFM is not
        # requested? For now we'll use non-localized chapter heading. Add in the
        # USFM chapter heading.
        chapter_heading = model.HtmlContent(
            config.get_html_format_string("tn_only_chapter_header").format(
                tn_resource.lang_code,
                bible_books.BOOK_NUMBERS[tn_resource.resource_code].zfill(3),
                str(chapter_num).zfill(3),
                chapter_num,
            )
        )
        html.append(chapter_heading)

        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)
        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's get all the verse level content.
        iterator = tn_verses or tq_verses
        if iterator:
            for verse_num, verse in sorted(iterator.items()):
                # Add TN verse content, if any
                if tn_verses and verse_num in tn_verses:
                    tn_verse_content = _format_tn_verse(
                        chapter_num, verse_num, tn_verses[verse_num]
                    )
                    html.extend(tn_verse_content)

                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    tq_verse_content = _format_tq_verse(
                        chapter_num, verse_num, tq_verses[verse_num]
                    )
                    html.extend(tq_verse_content)
                # Add the translation words links section.
                translation_word_links_html = tw_resource.get_translation_word_links(
                    chapter_num, verse_num, verse,
                )
                html.extend(translation_word_links_html)
    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section(
        include_uses_section=False
    )
    html.extend(linked_translation_words)

    return model.HtmlContent("\n".join(html))


def _assemble_tn_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN and
    TW exists.
    """
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that tn_resource object is not None.
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    # Dict keys need to be sorted since their order is otherwise not guaranteed.
    for chapter_num in sorted(tn_resource.book_payload.chapters):
        # How to get chapter heading for Translation notes when USFM is not
        # requested? For now we'll use non-localized chapter heading. Add in the
        # USFM chapter heading.
        chapter_heading = model.HtmlContent(
            config.get_html_format_string("tn_only_chapter_header").format(
                tn_resource.lang_code,
                bible_books.BOOK_NUMBERS[tn_resource.resource_code].zfill(3),
                str(chapter_num).zfill(3),
                chapter_num,
            )
        )
        html.append(chapter_heading)

        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        # Get TN chapter verses
        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's get all the verse translation notes available.
        if tn_verses:
            for verse_num, verse in sorted(tn_verses.items()):
                # FIXME See if you can move function to resource module.
                # Add TN verse content, if any
                tn_verse_content = _format_tn_verse(chapter_num, verse_num, verse)
                html.extend(tn_verse_content)

                # Add the translation words links section.
                translation_word_links_html = tw_resource.get_translation_word_links(
                    chapter_num, verse_num, verse,
                )
                html.extend(translation_word_links_html)
    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section(
        include_uses_section=False
    )
    html.extend(linked_translation_words)
    return model.HtmlContent("\n".join(html))


def _assemble_tn_tq_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN and
    TQ exists.
    """
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that tn_resource object is not None.
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []
    book_intro = tn_resource.book_payload.intro_html
    book_intro = _adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num in sorted(tn_resource.book_payload.chapters):
        # How to get chapter heading for Translation notes when USFM is not
        # requested? For now we'll use non-localized chapter heading. Add in the
        # USFM chapter heading.
        chapter_heading = model.HtmlContent(
            config.get_html_format_string("tn_only_chapter_header").format(
                tn_resource.lang_code,
                bible_books.BOOK_NUMBERS[tn_resource.resource_code].zfill(3),
                str(chapter_num).zfill(3),
                chapter_num,
            )
        )
        html.append(chapter_heading)

        # Add the translation notes chapter intro.
        chapter_intro = _get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        # Get TN chapter verses
        tn_verses = tn_resource.get_verses_for_chapter(chapter_num)
        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's get all the verse translation notes available.
        iterator = tn_verses or tq_verses
        if iterator:
            for verse_num, verse in sorted(iterator.items()):
                # FIXME See if you can move function to resource module.
                # Add TN verse content, if any
                if tn_verses and verse_num in tn_verses:
                    tn_verse_content = _format_tn_verse(
                        chapter_num, verse_num, tn_verses[verse_num]
                    )
                    html.extend(tn_verse_content)

                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    tq_verse_content = _format_tq_verse(
                        chapter_num, verse_num, tq_verses[verse_num]
                    )
                    html.extend(tq_verse_content)
    return model.HtmlContent("\n".join(html))


def _assemble_tq_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ exists.
    """
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num in sorted(tq_resource.book_payload.chapters):
        # How to get chapter heading for Translation questions when there is
        # not USFM requested? For now we'll use non-localized chapter heading.
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent(
            config.get_html_format_string("tn_only_chapter_header").format(
                tq_resource.lang_code,
                bible_books.BOOK_NUMBERS[tq_resource.resource_code].zfill(3),
                str(chapter_num).zfill(3),
                chapter_num,
            )
        )
        html.append(chapter_heading)

        # Get TQ chapter verses
        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's get all the verse translation notes available.
        if tq_verses:
            for verse_num, verse in sorted(tq_verses.items()):
                tq_verse_content = _format_tq_verse(chapter_num, verse_num, verse)
                html.extend(tq_verse_content)
    return model.HtmlContent("\n".join(html))


def _assemble_tq_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ and
    TW exists.
    """
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: model.ChapterNum
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num in sorted(tq_resource.book_payload.chapters):
        # How to get chapter heading for Translation questions when there is
        # not USFM requested? For now we'll use non-localized chapter heading.
        # Add in the USFM chapter heading.
        chapter_heading = model.HtmlContent(
            config.get_html_format_string("tn_only_chapter_header").format(
                tq_resource.lang_code,
                bible_books.BOOK_NUMBERS[tq_resource.resource_code].zfill(3),
                str(chapter_num).zfill(3),
                chapter_num,
            )
        )
        html.append(chapter_heading)

        # Get TQ chapter verses
        tq_verses = tq_resource.get_verses_for_chapter(chapter_num)

        # PEP526 disallows declaration of types in for loops, but allows this.
        verse_num: model.VerseNum
        verse: model.HtmlContent
        # Now let's get all the verse translation notes available.
        if tq_verses:
            for verse_num, verse in sorted(tq_verses.items()):
                tq_verse_content = _format_tq_verse(chapter_num, verse_num, verse)
                html.extend(tq_verse_content)

                # Add the translation words links section.
                translation_word_links_html = tw_resource.get_translation_word_links(
                    chapter_num, verse_num, verse,
                )
                html.extend(translation_word_links_html)
    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section(
        include_uses_section=False
    )
    html.extend(linked_translation_words)
    return model.HtmlContent("\n".join(html))


def _assemble_tw_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    usfm_resource2: Optional[USFMResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> model.HtmlContent:
    """
    Construct the HTML for a 'by verse' strategy wherein only TW exists.
    """
    tw_resource = cast(
        TWResource, tw_resource
    )  # Make mypy happy. We know, due to how we got here, that tq_resource object is not None.

    _initialize_resources_html(tn_resource, tq_resource, tw_resource, ta_resource)

    html: List[model.HtmlContent] = []

    # Add the translation words definition section.
    linked_translation_words = tw_resource.get_translation_words_section(
        include_uses_section=False
    )
    html.extend(linked_translation_words)
    return model.HtmlContent("\n".join(html))


######################
## Utility functions


def _initialize_resources_html(
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
) -> None:
    """
    Call initialize_verses_html for each non-USFM resource that is not null.
    """
    tw_resource_dir = None
    if tw_resource:
        # Pass the tw_resource's resource_dir to other resources which
        # in turn will pass it on to the TranslationWordLinkExtension
        # which will handle transformating links for translation
        # words.
        tw_resource_dir = tw_resource.resource_dir
        tw_resource.initialize_verses_html(tw_resource_dir)
    if tn_resource:
        tn_resource.initialize_verses_html(tw_resource_dir)
    if tq_resource:
        tq_resource.initialize_verses_html(tw_resource_dir)


def _format_tn_verse(
    chapter_num: model.ChapterNum, verse_num: model.VerseNum, verse: model.HtmlContent
) -> List[model.HtmlContent]:
    """
    This is a slightly different form of TNResource.get_tn_verse that is used
    when no USFM has been requested.
    """
    html: List[model.HtmlContent] = []
    html.append(
        model.HtmlContent(
            config.get_html_format_string("translation_note").format(
                chapter_num, verse_num
            )
        )
    )
    # Change H1 HTML elements to H4 HTML elements in each translation note.
    html.append(model.HtmlContent(re.sub(r"h1", r"h4", verse)))
    return html


def _format_tq_verse(
    chapter_num: model.ChapterNum, verse_num: model.VerseNum, verse: model.HtmlContent
) -> List[model.HtmlContent]:
    """
    This is a slightly different form of TQResource.get_tq_verse that is used
    when no USFM or TN has been requested.
    """
    html: List[model.HtmlContent] = []
    html.append(
        model.HtmlContent(
            config.get_html_format_string("translation_question").format(
                chapter_num, verse_num
            )
        )
    )
    # Change H1 HTML elements to H4 HTML elements in each translation
    # question.
    html.append(model.HtmlContent(re.sub(r"h1", r"h4", verse)))
    return html


def _get_usfm_resource(resources: List[Resource]) -> Optional[USFMResource]:
def _get_first_usfm_resource(resources: List[Resource]) -> Optional[USFMResource]:
    """
    Return the first USFMResource instance, if any, contained in resources,
    else return None.
    """
    usfm_resources = [
        resource for resource in resources if isinstance(resource, USFMResource)
    ]
    return usfm_resources[0] if usfm_resources else None


def _get_second_usfm_resource(resources: List[Resource]) -> Optional[USFMResource]:
    """
    Return the second USFMResource instance, if any, contained in resources,
    else return None.
    """
    usfm_resources = [
        resource for resource in resources if isinstance(resource, USFMResource)
    ]
    return usfm_resources[1] if usfm_resources and 1 in usfm_resources else None


def _get_tn_resource(resources: List[Resource]) -> Optional[TNResource]:
    """
    Return the TNResource instance, if any, contained in resources,
    else return None.
    """
    tn_resources = [
        resource for resource in resources if isinstance(resource, TNResource)
    ]
    return tn_resources[0] if tn_resources else None


def _get_tw_resource(resources: List[Resource]) -> Optional[TWResource]:
    """
    Return the TWResource instance, if any, contained in resources,
    else return None.
    """
    tw_resources = [
        resource for resource in resources if isinstance(resource, TWResource)
    ]
    return tw_resources[0] if tw_resources else None


def _get_tq_resource(resources: List[Resource]) -> Optional[TQResource]:
    """
    Return the TQResource instance, if any, contained in resources,
    else return None.
    """
    tq_resources = [
        resource for resource in resources if isinstance(resource, TQResource)
    ]
    return tq_resources[0] if tq_resources else None


def _get_ta_resource(resources: List[Resource]) -> Optional[TAResource]:
    """
    Return the TAResource instance, if any, contained in resources,
    else return None.
    """
    ta_resources = [
        resource for resource in resources if isinstance(resource, TAResource)
    ]
    return ta_resources[0] if ta_resources else None


def _adjust_book_intro_headings(book_intro: str) -> model.HtmlContent:
    """Change levels on headings."""
    # Move the H2 out of the way, we'll deal with it last.
    book_intro = re.sub(r"h2", r"h6", book_intro)
    book_intro = re.sub(r"h1", r"h2", book_intro)
    book_intro = re.sub(r"h3", r"h4", book_intro)
    # Now adjust the temporary H6s.
    return model.HtmlContent(re.sub(r"h6", r"h3", book_intro))


def _adjust_chapter_intro_headings(chapter_intro: str) -> model.HtmlContent:
    """Change levels on headings."""
    # Move the H4 out of the way, we'll deal with it last.
    chapter_intro = re.sub(r"h4", r"h6", chapter_intro)
    chapter_intro = re.sub(r"h3", r"h4", chapter_intro)
    chapter_intro = re.sub(r"h1", r"h3", chapter_intro)
    chapter_intro = re.sub(r"h2", r"h4", chapter_intro)
    # Now adjust the temporary H6s.
    return model.HtmlContent(re.sub(r"h6", r"h5", chapter_intro))


def _get_chapter_intro(
    tn_resource: TNResource, chapter_num: model.ChapterNum
) -> model.HtmlContent:
    """Get the chapter intro."""
    if tn_resource and chapter_num in tn_resource.book_payload.chapters:
        chapter_intro = tn_resource.book_payload.chapters[chapter_num].intro_html
    else:
        chapter_intro = model.HtmlContent("")
    # NOTE I am not sure that the 'Links:' section of chapter
    # intro makes sense anymore with the way documents
    # are interleaved.
    # Remove the Links: section of the markdown.
    # chapter_intro = markdown_utils.remove_md_section(chapter_intro, "Links:")
    return _adjust_chapter_intro_headings(chapter_intro)
