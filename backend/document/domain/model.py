"""
This module provides classes that are used as data transfer objects.
In particular, many of the classes here are subclasses of
pydantic.BaseModel as FastAPI can use these classes to do automatic
validation and JSON serialization.
"""

from enum import Enum
from collections.abc import Sequence
from typing import NewType, Optional, Union

from pydantic import AnyUrl, BaseModel, EmailStr

# These Type Aliases give us more self-documenting code, but of course
# aren't strictly necessary.
HtmlContent = str
# MarkdownContent = str
MarkdownContent = NewType("MarkdownContent", str)
VerseRef = str
ChapterNum = int


# https://blog.meadsteve.dev/programming/2020/02/10/types-at-the-edges-in-python/
# https://pydantic-docs.helpmanual.io/usage/models/
class ResourceRequest(BaseModel):
    """
    This class is used to encode a request for a resource, e.g.,
    language 'English', en, resource type 'ulb', resource code, i.e.,
    book, 'gen'. A document request composes n of these resource
    request instances. Because this class inherits from pydantic's
    BaseModel we get validation and JSON serialization for free.
    """

    lang_code: str
    resource_type: str
    resource_code: str


# See
# https://pydantic-docs.helpmanual.io/usage/types/#enums-and-choices
# for where this pattern of combining Enum and BaseModel comes from in
# pydantic.
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
    Perhaps we'd want a high level strategy that ordered by book then
    language (as opposed to the other way around) before delegating
    the lower level assembly to a sub-strategy as signaled by
    AssemblySubstrategyEnum. The sky is the limit.
    """

    LANGUAGE_BOOK_ORDER = "language_book_order"
    BOOK_LANGUAGE_ORDER = "book_language_order"


class DocumentRequest(BaseModel):
    """
    This class is used to send in a document generation request from
    the front end client. A document request is composed of n resource
    requests. Because this class inherits from pydantic's BaseModel we
    get validation, serialization, and special dunder functions for
    free.
    """

    email_address: Optional[EmailStr]
    assembly_strategy_kind: AssemblyStrategyEnum
    resource_requests: Sequence[ResourceRequest]


class AssemblySubstrategyEnum(str, Enum):
    """
    A sub-strategy enum signals which interleaving sub-strategy
    to use.
    E.g., If the high level interleaving strategy LANGUAGE_BOOK_ORDER
    has been chosen then inside the language and book interleaving
    loop the sub-strategy will be signaled by a value from this
    AssemblySubstrategyEnum.

    We can have N such sub-strategies and each can be completely
    arbitrary, simply based on the desires of content designers.

    Said another way: the enum is just a name that is arbitrarily
    chosen to be compact but adequate to express the type of interleaving
    that is to be accomplished in the HTML document (prior to conversion
    to PDf).

    There is currently one assembly sub-strategy kind to choose from:

    * VERSE
      - cause a verse's worth of each resource's content to be interleaved.

    NOTE
    We could later add others. As an arbitrary example, perhaps we'd
    want a sub-strategy that did verse-level interleaving for USFM and
    TN, but chapter level interleaving for TQ or if not chapter then
    some totally arbitrary interleaving or organization. Basically,
    the enum values are just used to select a particular assembly
    sub-strategy, whatever it is.
    """

    VERSE = "VERSE"


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


class ResourceLookupDto(BaseModel):
    """
    'Data transfer object' that we use to send lookup related info to
    the resource.
    """

    lang_code: str
    resource_type: str
    resource_code: str
    url: Optional[AnyUrl]
    source: AssetSourceEnum
    jsonpath: Optional[str]
    lang_name: str
    resource_type_name: str


class FinishedDocumentDetails(BaseModel):
    """
    Pydanctic model that we use as a return value to send back via
    Fastapi to the client. For now it just contains the finished
    dcocument filepath on disk.
    """

    finished_document_request_key: Optional[str]
    message: str


class TNChapter(BaseModel):
    """
    A class to hold a chapter's intro translation notes and a mapping
    of its verse references to translation notes HTML content.
    """

    intro_html: HtmlContent
    verses_html: dict[VerseRef, HtmlContent]


class TNBook(BaseModel):
    """
    A class to hold a book's intro translation notes and a mapping
    of chapter numbers to translation notes HTML content.
    """

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    intro_html: HtmlContent
    chapters: dict[ChapterNum, TNChapter]


class TQChapter(BaseModel):
    """
    A class to hold a mapping of verse references to translation
    questions HTML content.
    """

    verses_html: dict[VerseRef, HtmlContent]


class TQBook(BaseModel):
    """
    A class to hold a mapping of chapter numbers to translation questions
    HTML content.
    """

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, TQChapter]


class TWUse(BaseModel):
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


class TWNameContentPair(BaseModel):
    """
    A class to hold the localized translation word and its associated
    HTML content (which was converted from its Markdown).
    """

    localized_word: str
    content: HtmlContent


class TWBook(BaseModel):
    """
    A class to hold a list of TWNameContentPair instances and a list
    of TWUses instances.
    """

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    name_content_pairs: list[TWNameContentPair] = []
    uses: dict[str, list[TWUse]] = {}


class USFMChapter(BaseModel):
    """
    A class to hold the USFM converted to HTML content for a chapter
    in total (including things like 'chunk breaks' and other verse
    formatting HTML elements), chapter_content, and by verse per
    chapter (missing the 'chunk breaks' and other inter-verse HTML
    formatting elements), chapter_verses. The purpose of
    'chapter_content' is so that you can display a whole chapter at a
    time should the system wish to do so. The purpose of
    'chapter_verses' is so that you can display verses in a particular
    chapter one at a time or a range of them at a time should the
    system desire to do so.
    """

    chapter_content: list[HtmlContent]
    chapter_verses: dict[VerseRef, HtmlContent]
    chapter_footnotes: HtmlContent


class USFMBook(BaseModel):
    """A class to hold a book's USFMChapter instances."""

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, USFMChapter]


BookContent = Union[USFMBook, TNBook, TQBook, TWBook]


class CoverPayload(BaseModel):
    """
    A class to hold a PDF cover sheet, i.e., first page, HTML template
    variable values.
    """

    title: str
    unfound: str
    unloaded: str
    revision_date: str
    images: dict[str, Union[str, bytes]]


class EmailPayload(BaseModel):
    """A class to hold an HTML email body."""

    document_request_key: str


class CodeNameTypeTriplet(BaseModel):
    """A utility class to provide validation in resource_lookup module."""

    lang_code: str
    lang_name: str
    resource_types: list[str]


class MarkdownLink(BaseModel):
    """
    Reify a markdown link for use in link_transformer_preprocessor
    module.
    """

    url: str
    link_text: str


class WikiLink(BaseModel):
    """
    Reify a wiki link for use in link_transformer_preprocessor
    module.
    """

    url: str
