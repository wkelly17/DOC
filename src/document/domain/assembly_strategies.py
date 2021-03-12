"""
This module provides the assembly strategies that are used to assemble
HTML documents prior to their conversion to PDF form.

Assembly strategies utilize the Strategy pattern:
https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py
"""


# Handle circular import issue with document_generator module.
from __future__ import annotations  # https://www.python.org/dev/peps/pep-0563/

import itertools
import logging  # For logdecorator
import re

from logdecorator import log_on_start
from typing import Callable, cast, List, Optional

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
                    bible_books.BOOK_NAMES[book]
                )
            )

            # Save grouper generator since it will get exhausted
            # when used and exhausted generators cannot be reused.
            resources = list(group_by_book)
            usfm_resource: Optional[USFMResource] = get_usfm_resource(resources)
            tn_resource: Optional[TNResource] = get_tn_resource(resources)
            tq_resource: Optional[TQResource] = get_tq_resource(resources)
            tw_resource: Optional[TWResource] = get_tw_resource(resources)
            ta_resource: Optional[TAResource] = get_ta_resource(resources)

            # We've got the resources, now we can use the strategy factory method to choose the right function to use
            # from here on out.
            docgen._assembly_sub_strategy = _assembly_sub_strategy_factory(
                usfm_resource,
                tn_resource,
                tq_resource,
                tw_resource,
                ta_resource,
                config.get_default_assembly_substrategy(),
                # NOTE DocumentGenerator does not accept a
                # sub-strategy at this time (and may never).
                # docgen._document_request.assembly_substrategy_kind,
            )

            sub_html: str = docgen._assembly_sub_strategy(
                usfm_resource,
                tn_resource,
                tq_resource,
                tw_resource,
                ta_resource,
                config.get_default_assembly_substrategy(),
                # NOTE DocumentGenerator does not accept a
                # sub-strategy at this time (and may never).
                # docgen._document_request.assembly_strategy_kind,
            )
            html.append(sub_html)

    return "\n".join(html)


def _assemble_usfm_tn_tq_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> str:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TN, and
    TQ exist.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    tq_resource = cast(
        TQResource, tq_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    html = []
    book_intro = tn_resource.book_payload.intro_html if tn_resource else ""
    book_intro = adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: int
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = ""
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)
        # Add in the translation notes chapter intro.
        chapter_intro = get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        # NOTE This commented out section is for use when
        # we implement a by chapter interleaving strategy.
        # Skip some useless elements and get the USFM
        # verse HTML content.
        # Chapter all at once including formatting HTML
        # elements. This would be useful for a 'by
        # chapter' interleaving strategy.
        # usfm_verses = chapter.chapter_content[3:]

        # Get TN chapter verses
        tn_verses = (
            tn_resource.book_payload.chapters[chapter_num].verses_html
            if tn_resource
            else {}
        )
        # Get TQ chapter verses
        tq_verses = (
            tq_resource.book_payload.chapters[chapter_num].verses_html
            if tq_resource
            else {}
        )
        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: int
        verse: str
        # Now let's interleave USFM verse with its
        # translation note if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            html.append(
                config.get_html_format_string("verse").format(chapter_num, verse_num)
            )
            html.append(verse)
            if tn_verses and verse_num in tn_verses:
                html.append(
                    config.get_html_format_string("translation_note").format(
                        chapter_num, verse_num
                    )
                )
                # Change H1 HTML elements to H4 HTML
                # elements in each translation note.
                tn_verse = tn_verses[verse_num]
                html.append(re.sub(r"h1", r"h4", tn_verse))
            if tq_verses and verse_num in tq_verses:
                html.append(
                    config.get_html_format_string("translation_question").format(
                        chapter_num, verse_num
                    )
                )
                # Change H1 HTML elements to H4 HTML
                # elements in each translation note.
                tq_verse = tq_verses[verse_num]
                html.append(re.sub(r"h1", r"h4", tq_verse))
    return "\n".join(html)


def _assemble_usfm_tn_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> str:
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
    html = []
    book_intro = tn_resource.book_payload.intro_html if tn_resource else ""
    book_intro = adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: int
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = ""
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)
        # Add in the translation notes chapter intro.
        chapter_intro = get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        # NOTE This commented out section is for use when
        # we implement a by chapter interleaving strategy.
        # Skip some useless elements and get the USFM
        # verse HTML content.
        # Chapter all at once including formatting HTML
        # elements. This would be useful for a 'by
        # chapter' interleaving strategy.
        # usfm_verses = chapter.chapter_content[3:]

        # Get TN chapter verses
        tn_verses = (
            tn_resource.book_payload.chapters[chapter_num].verses_html
            if tn_resource
            else {}
        )
        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: int
        verse: str
        # Now let's interleave USFM verse with its
        # translation note if available.
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            html.append(
                config.get_html_format_string("verse").format(chapter_num, verse_num)
            )
            html.append(verse)
            if tn_verses and verse_num in tn_verses:
                html.append(
                    config.get_html_format_string("translation_note").format(
                        chapter_num, verse_num
                    )
                )
                # Change H1 HTML elements to H4 HTML
                # elements in each translation note.
                tn_verse = tn_verses[verse_num]
                html.append(re.sub(r"h1", r"h4", tn_verse))
    return "\n".join(html)


def _assemble_usfm_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> str:
    """
    Construct the HTML for a 'by verse' strategy wherein only USFM exists.
    """
    usfm_resource = cast(
        USFMResource, usfm_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    html = []

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: int
    chapter: model.USFMChapter
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num, chapter in sorted(usfm_resource.chapters_content.items()):
        # Add in the USFM chapter heading.
        chapter_heading = ""
        chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)

        # NOTE This commented out section is for use when
        # we implement a by chapter interleaving strategy.
        # Skip some useless elements and get the USFM
        # verse HTML content.
        # Chapter all at once including formatting HTML
        # elements. This would be useful for a 'by
        # chapter' interleaving strategy.
        # usfm_verses = chapter.chapter_content[3:]

        # PEP526 disallows declaration of types in for
        # loops, but allows this.
        verse_num: int
        verse: str
        # Now append the USFM verses
        for verse_num, verse in sorted(chapter.chapter_verses.items()):
            html.append(
                config.get_html_format_string("verse").format(chapter_num, verse_num)
            )
            html.append(verse)
    return "\n".join(html)


def _assemble_tn_content_by_verse(
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> str:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN exists.
    """
    tn_resource = cast(
        TNResource, tn_resource
    )  # Make mypy happy. We know, due to how we got here, that usfm_resource object is not None.
    html = []
    book_intro = tn_resource.book_payload.intro_html if tn_resource else ""
    book_intro = adjust_book_intro_headings(book_intro)
    html.append(book_intro)

    # PEP526 disallows declaration of types in for loops, but allows this.
    chapter_num: int
    # Dict keys need to be sorted as their order is not guaranteed.
    for chapter_num in sorted(tn_resource.book_payload.chapters):
        # FIXME How to get chapter heading for Translation notes when there is
        # not USFM requested. For now we'll use non-localized chapter heading.
        # Add in the USFM chapter heading.
        chapter_heading = config.get_html_format_string(
            "tn_only_chapter_header"
        ).format(
            bible_books.BOOK_NUMBERS[tn_resource.resource_code].zfill(3),
            str(chapter_num).zfill(3),
            chapter_num,
        )
        # chapter_heading = chapter.chapter_content[0]
        html.append(chapter_heading)

        # Add in the translation notes chapter intro.
        chapter_intro = get_chapter_intro(tn_resource, chapter_num)
        html.append(chapter_intro)

        # Get TN chapter verses
        tn_verses = tn_resource.book_payload.chapters[chapter_num].verses_html

        # PEP526 disallows declaration of types in for loops, but allows this.
        verse_num: int
        verse: str
        # Now let's get all the verse translation notes available.
        for verse_num, verse in sorted(tn_verses.items()):
            html.append(
                config.get_html_format_string("translation_note").format(
                    chapter_num, verse_num
                )
            )
            # Change H1 HTML elements to H4 HTML elements in each translation note.
            html.append(re.sub(r"h1", r"h4", verse))
    return "\n".join(html)


# Utility function to clean things up.
def get_usfm_resource(resources: List[Resource]) -> Optional[USFMResource]:
    """
    Return the USFMResource instance, if any, contained in resources,
    else return None.
    """
    usfm_resources = [
        resource for resource in resources if isinstance(resource, USFMResource)
    ]
    return usfm_resources[0] if usfm_resources else None


def get_tn_resource(resources: List[Resource]) -> Optional[TNResource]:
    """
    Return the TNResource instance, if any, contained in resources,
    else return None.
    """
    tn_resources = [
        resource for resource in resources if isinstance(resource, TNResource)
    ]
    return tn_resources[0] if tn_resources else None


def get_tw_resource(resources: List[Resource]) -> Optional[TWResource]:
    """
    Return the TWResource instance, if any, contained in resources,
    else return None.
    """
    tw_resources = [
        resource for resource in resources if isinstance(resource, TWResource)
    ]
    return tw_resources[0] if tw_resources else None


def get_tq_resource(resources: List[Resource]) -> Optional[TQResource]:
    """
    Return the TQResource instance, if any, contained in resources,
    else return None.
    """
    tq_resources = [
        resource for resource in resources if isinstance(resource, TQResource)
    ]
    return tq_resources[0] if tq_resources else None


def get_ta_resource(resources: List[Resource]) -> Optional[TAResource]:
    """
    Return the TAResource instance, if any, contained in resources,
    else return None.
    """
    ta_resources = [
        resource for resource in resources if isinstance(resource, TAResource)
    ]
    return ta_resources[0] if ta_resources else None


def adjust_book_intro_headings(book_intro: str) -> str:
    """Change levels on headings."""
    # Move the H2 out of the way, we'll deal with it last.
    book_intro = re.sub(r"h2", r"h6", book_intro)
    book_intro = re.sub(r"h1", r"h2", book_intro)
    book_intro = re.sub(r"h3", r"h4", book_intro)
    # Now adjust the temporary H6s.
    return re.sub(r"h6", r"h3", book_intro)


def adjust_chapter_intro_headings(chapter_intro: str) -> str:
    """Change levels on headings."""
    # Move the H4 out of the way, we'll deal with it last.
    chapter_intro = re.sub(r"h4", r"h6", chapter_intro)
    chapter_intro = re.sub(r"h3", r"h4", chapter_intro)
    chapter_intro = re.sub(r"h1", r"h3", chapter_intro)
    chapter_intro = re.sub(r"h2", r"h4", chapter_intro)
    # Now adjust the temporary H6s.
    return re.sub(r"h6", r"h5", chapter_intro)


def get_chapter_intro(tn_resource: TNResource, chapter_num: int) -> str:
    """Get the chapter intro."""
    chapter_intro = (
        tn_resource.book_payload.chapters[chapter_num].intro_html if tn_resource else ""
    )
    # NOTE I am not sure that the 'Links:' section of chapter
    # intro makes sense anymore with the way documents
    # are interleaved.
    # Remove the Links: section of the markdown.
    # chapter_intro = markdown_utils.remove_md_section(chapter_intro, "Links:")
    return adjust_chapter_intro_headings(chapter_intro)


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
    usfm_resource: Optional[USFMResource],
    tn_resource: Optional[TNResource],
    tq_resource: Optional[TQResource],
    tw_resource: Optional[TWResource],
    ta_resource: Optional[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Callable[
    [
        Optional[USFMResource],
        Optional[TNResource],
        Optional[TQResource],
        Optional[TWResource],
        Optional[TAResource],
        model.AssemblySubstrategyEnum,
    ],
    str,
]:
    """
    Strategy pattern. Given the existence, i.e., exists or None, of each
    type of the five possible resource instances and an
    assembly_strategy_kind, returns the appropriate sub-strategy
    function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in the assembly algorithm that would otherwise
    be checking the existence of each resource. This makes adding new
    strategies straightforward.
    """
    strategies = {
        # Params: usfm_resource_exists, tn_resource_exists, tq_resource_exists, tw_resource_exists, ta_resource_exists, assembly_strategy_kind
        (
            True,
            True,
            True,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tn_tq_content_by_verse,
        (
            True,
            True,
            False,
            False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_usfm_tn_content_by_verse,
        (
            True,
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
            model.AssemblySubstrategyEnum.VERSE,
        ): _assemble_tn_content_by_verse,
    }
    return strategies[
        (
            usfm_resource is not None,
            tn_resource is not None,
            tq_resource is not None,
            tw_resource is not None,
            ta_resource is not None,
            assembly_substrategy_kind,
        )
    ]
