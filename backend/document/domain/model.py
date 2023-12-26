"""
This module provides classes that are used as data transfer objects.
In particular, many of the classes here are subclasses of
pydantic.BaseModel as FastAPI can use these classes to do automatic
validation and JSON serialization.
"""

from enum import Enum
from typing import Any, Callable, NamedTuple, Optional, Sequence, Union, final

from document.config import settings
from document.domain.bible_books import BOOK_NAMES
from document.utils.number_utils import is_even
from docx import Document  # type: ignore
from more_itertools import all_equal
from pydantic import BaseModel, EmailStr
from pydantic.functional_validators import model_validator
from toolz import itertoolz  # type: ignore

# These type aliases give us more self-documenting code, but of course
# aren't strictly necessary.
HtmlContent = str
MarkdownContent = str
VerseRef = str
ChapterNum = int


@final
class AssemblyStrategyEnum(str, Enum):
    """
    There is currently one high level assembly strategy kind to choose from:

    * LANGUAGE_BOOK_ORDER
      - This enum value signals to use the high level strategy that orders
        by language and then by book before delegating to an assembly
        sub-strategy.
    * BOOK_LANGUAGE_ORDER
      - This enum value signals to use the high level strategy that orders
        by book and then by language  before delegating to an assembly
        sub-strategy.

    NOTE
    We could later add others. As an arbitrary example,
    perhaps we'd want a high level strategy that ordered by book then
    language (as opposed to the other way around) before delegating
    the lower level assembly to a sub-strategy as signaled by
    AssemblySubstrategyEnum. The sky is the limit.
    """

    LANGUAGE_BOOK_ORDER = "lbo"
    BOOK_LANGUAGE_ORDER = "blo"


@final
class AssemblyLayoutEnum(str, Enum):
    """
    An enum used by the assembly_strategies module to know how
    to layout the content.

    We can have N such layouts and each can be completely
    arbitrary, simply based on the desires of content designers.

    Layouts:

    * ONE_COLUMN
      All content in one column

    * ONE_COLUMN_COMPACT
      This layout minimizes whitespace in a one column layout so as to
      be appropriate for printing to paper.

    * TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
      Two columns, with scripture on the left and a different
      scripture on the right. Obviously only applicable when at least
      two languages have been chosen.

    * TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT
      This layout minimizes whitespace by using
      TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT layout but with a
      different CSS styling that results in less whitespace.
    """

    ONE_COLUMN = "1c"
    ONE_COLUMN_COMPACT = "1c_c"
    # fmt: off
    # NOTE The next two layouts only make sense
    # with an AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER assembly
    # strategy and when more than one language is chosen for the same
    # book.
    TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT = "2c_sl_sr"
    TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT = "2c_sl_sr_c"
    # fmt: on


@final
class ChunkSizeEnum(str, Enum):
    """
    The length of content to burst out at a time when interleaving.
    E.g., if CHAPTER is chosen as the chunk size then the interleaving will
    do so in chapter chunks (one chapter of scripture, then one chapter of helps,
    etc.). This exists because translators want to be able to choose
    the chunk size of scripture that should be grouped together for the
    purpose of translational cohesion.

    * CHAPTER
      - This enum value signals to make each chunk of interleaved
        content be one chapter's worth in length.

    NOTE
    We could later add others.
    """

    CHAPTER = "chapter"


# https://blog.meadsteve.dev/programming/2020/02/10/types-at-the-edges-in-python/
# https://pydantic-docs.helpmanual.io/usage/models/
@final
class ResourceRequest(BaseModel):
    """
    This class is used to encode a request for a resource, e.g.,
    language 'French', fr, resource type 'ulb', book code, i.e.,
    book, 'gen'. A document request composes N of these resource
    request instances. Because this class inherits from pydantic's
    BaseModel we get validation and JSON serialization for free.
    """

    lang_code: str
    resource_type: str
    book_code: str


@final
class DocumentRequestSourceEnum(str, Enum):
    """
    This class/enum captures the concept of: where did the document
    request originate from? At present it originates from either the UI or
    tests.
    """

    UI = "ui"
    TEST = "test"
    BIEL_UI = "biel_ui"


@final
class DocumentRequest(BaseModel):
    """
    This class reifies a document generation request from a client of
    the API. A document request is composed of N resource requests.
    Because this class inherits from pydantic's BaseModel we get
    validation, serialization, and special dunder functions for free.
    """

    email_address: Optional[EmailStr] = None
    assembly_strategy_kind: AssemblyStrategyEnum
    # NOTE For testing we want to exercise various layouts, thus we
    # make this attribute Optional so that we can specify it in unit
    # tests if desired. But the normal case is to set
    # assembly_layout_kind to None in a document request if we are
    # manually coding up a document request instance to send to the
    # API. If you go this latter route, say to use the API in a
    # different context than interacting with the UI then the onus is
    # on you as the developer to choose an assembly_layout_kind that
    # makes sense given the document request you have instantiated.
    # The system knows which make sense and which do not given your
    # document request and if you choose one that does not make sense
    # then you'll get an exception on purpose.
    assembly_layout_kind: Optional[AssemblyLayoutEnum] = AssemblyLayoutEnum.ONE_COLUMN
    # The user can choose whether the result should be formatted to
    # print. When the user selects yes/True to format for print
    # then we'll choose a compact layout that makes sense for their
    # document request.
    layout_for_print: bool = False
    resource_requests: Sequence[ResourceRequest]
    # Indicate whether PDF should be generated.
    generate_pdf: bool = True
    # Indicate whether ePub should be generated.
    generate_epub: bool = False
    # Indicate whether Docx should be generated.
    generate_docx: bool = False
    # Indicate the chunk size to interleave. Default to chapter. Verse
    # chunk size was deemed non-useful, but remains for now as a historical
    # option.
    chunk_size: ChunkSizeEnum = ChunkSizeEnum.CHAPTER
    # Indicate whether translation words, TW, should be limited to
    # only those that appear in the USFM requested (True), or, include all
    # the TW words available for the language requested (False).
    limit_words: bool = True
    # Indicate whether TN book intros should be included. Currently,
    # the content team does not want them included.
    include_tn_book_intros: bool = False
    # Indicate where the document request originated from. We default to
    # TEST so that tests don't have to specify and every other client, e.g.,
    # UI, should specify in order for
    # document_generator.select_assembly_layout_kind to produce
    # expected results.
    document_request_source: DocumentRequestSourceEnum = DocumentRequestSourceEnum.TEST

    @model_validator(mode="after")
    def ensure_valid_document_request(self) -> Any:
        """
        See ValueError messages below for the rules we are enforcing.
        """

        usfm_resource_types = [
            *settings.USFM_RESOURCE_TYPES,
            *settings.EN_USFM_RESOURCE_TYPES,
        ]

        non_usfm_resource_types = [
            *settings.TN_RESOURCE_TYPES,
            *settings.EN_TN_RESOURCE_TYPES,
            *settings.TQ_RESOURCE_TYPES,
            *settings.EN_TQ_RESOURCE_TYPES,
            *settings.TW_RESOURCE_TYPES,
            *settings.EN_TW_RESOURCE_TYPES,
            *settings.BC_RESOURCE_TYPES,
        ]
        all_resource_types = [*usfm_resource_types, *non_usfm_resource_types]
        for resource_request in self.resource_requests:
            # Make sure resource_type for every ResourceRequest instance
            # is a valid value
            if not resource_request.resource_type in all_resource_types:
                raise ValueError(
                    f"{resource_request.resource_type} is not a valid resource type"
                )
            # Make sure book_code is a valid value
            if not resource_request.book_code in BOOK_NAMES.keys():
                raise ValueError(
                    f"{resource_request.book_code} is not a valid book code"
                )

        # Partition USFM resource requests by language
        language_groups = itertoolz.groupby(
            lambda r: r.lang_code,
            filter(
                lambda r: r.resource_type in usfm_resource_types,
                self.resource_requests,
            ),
        )
        # Get a list of the sorted set of books for each language for later
        # comparison.
        sorted_book_set_for_each_language = [
            sorted({item.book_code for item in value})
            for key, value in language_groups.items()
        ]

        # Get the unique number of languages
        number_of_usfm_languages = len(
            # set(
            [
                resource_request.lang_code
                for resource_request in self.resource_requests
                if resource_request.resource_type in usfm_resource_types
            ]
            # )
        )

        if (
            self.assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
            and self.assembly_strategy_kind
            != AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            != AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
        ):
            raise ValueError(
                "Two column scripture left, scripture right layout is only compatible with book language order assembly strategy."
            )
        elif (
            self.assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
            and self.assembly_strategy_kind
            == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            # Because book content for different languages will be side by side for
            # the scripture left scripture right layout, we make sure there are a non-zero
            # even number of languages so that we can display them left and right in
            # pairs.
            # and not (number_of_usfm_languages > 1 and is_even(number_of_usfm_languages))
            and not is_even(number_of_usfm_languages)
        ):
            raise ValueError(
                "Two column scripture left, scripture right layout requires a non-zero even number of languages. For an uneven number of languages you'll want to use the one column layout kind."
            )
        elif (
            self.assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
            and self.assembly_strategy_kind
            == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            # Because book content for different languages will be side by side for
            # the scripture left scripture right layout, we make sure there are a non-zero
            # even number of languages so that we can display them left and right in
            # pairs.
            # and number_of_usfm_languages > 1
            and is_even(number_of_usfm_languages)
            # Each language must have the same set of books in order to
            # use the scripture left scripture right layout strategy. As an example,
            # you wouldn't want to allow the sl-sr layout if the document request
            # asked for swahili ulb for lamentations and spanish ulb for nahum -
            # the set of books in each language are not the same and so do not make
            # sense to be displayed side by side.
            and not all_equal(sorted_book_set_for_each_language)
        ):
            raise ValueError(
                "Two column scripture left, scripture right layout requires the same books for each language chosen since they are displayed side by side. If you want a different set of books for each language you'll instead need to use the one column layout."
            )

        return self


@final
class AssetSourceEnum(str, Enum):
    """
    This class/enum captures the concept of: where did the resource's
    asset files come from? At present they come from either a GIT
    repository, an individual USFM file download, or a ZIP file
    download.
    """

    GIT = "git"
    USFM = "usfm"
    ZIP = "zip"


@final
class LangDirEnum(str, Enum):
    """
    This class/enum enumerates the possible language display
    directions: LTR or RTL.
    """

    LTR = "ltr"
    RTL = "rtl"


@final
class ResourceLookupDto(NamedTuple):
    """
    'Data transfer object' that we use to send resource lookup related
    info around in the system.
    """

    lang_code: str
    lang_name: str
    resource_type: str
    resource_type_name: str
    book_code: str
    url: Optional[str]
    source: AssetSourceEnum
    jsonpath: Optional[str]


@final
class TNChapter(NamedTuple):
    """
    A class to hold a chapter's intro translation notes and a mapping
    of its verse references to translation notes HTML content.
    """

    intro_html: HtmlContent
    verses: dict[VerseRef, HtmlContent]


@final
class TNBook(NamedTuple):
    """
    A class to hold a book's intro translation notes and a mapping
    of chapter numbers to translation notes HTML content.
    """

    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    intro_html: HtmlContent
    chapters: dict[ChapterNum, TNChapter]
    lang_direction: LangDirEnum


@final
class TQChapter(NamedTuple):
    """
    A class to hold a mapping of verse references to translation
    questions HTML content.
    """

    verses: dict[VerseRef, HtmlContent]


@final
class TQBook(NamedTuple):
    """
    A class to hold a mapping of chapter numbers to translation questions
    HTML content.
    """

    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, TQChapter]
    lang_direction: LangDirEnum


@final
class TWUse(NamedTuple):
    """
    A class to reify a reference to a translation word occurring
    in a USFM verse.
    """

    lang_code: str
    book_id: str
    book_name: str
    chapter_num: ChapterNum
    verse_num: VerseRef
    localized_word: str


# `content' gets mutated after instantiation therefore we can't subclass NamedTuple
@final
class TWNameContentPair:
    """
    A class to hold the localized translation word and its associated
    HTML content (which was converted from its Markdown).
    """

    def __init__(self, localized_word: str, content: HtmlContent):
        self.localized_word = localized_word
        self.content = content


@final
class TWBook(NamedTuple):
    """
    A class to hold a list of TWNameContentPair instances and a list
    of TWUse instances.
    """

    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    lang_direction: LangDirEnum
    name_content_pairs: list[TWNameContentPair] = []
    uses: dict[str, list[TWUse]] = {}


@final
class BCChapter(NamedTuple):
    """
    A class to hold a mapping of verse references to bible
    commentary HTML content.
    """

    commentary: HtmlContent


@final
class BCBook(NamedTuple):
    """
    A class to hold a mapping of chapter numbers to translation questions
    HTML content.
    """

    book_intro: str
    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, BCChapter]


@final
class USFMChapter(NamedTuple):
    """
    A class to hold the USFM converted to HTML content for a chapter
    in total (including things like 'chunk breaks' and other verse
    formatting HTML elements), content, and by verse per chapter (missing
    the 'chunk breaks' and other inter-verse HTML formatting elements),
    verses. The purpose of 'content' is so that you can display a whole
    chapter at a time when desired. The purpose of 'verses' is so that you
    can display verses in a particular chapter one at a time or a range of
    them at a time.
    """

    content: list[HtmlContent]
    verses: dict[VerseRef, HtmlContent]
    footnotes: HtmlContent


@final
class USFMBook(NamedTuple):
    """A class to hold a book's USFMChapter instances."""

    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, USFMChapter]
    lang_direction: LangDirEnum


BookContent = Union[USFMBook, TNBook, TQBook, TWBook, BCBook]


@final
class WikiLink(NamedTuple):
    """
    Reify a wiki link for use in link_transformer_preprocessor
    module.
    """

    url: str


@final
class Attachment(NamedTuple):
    """
    An email attachment.
    """

    filepath: str
    mime_type: tuple[str, str]
