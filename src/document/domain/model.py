"""
This module provides classes that are used as data transfer objects.
In particular, many of the classes here are subclasses of
pydantic.BaseModel as FastAPI can use these classes to do automatic
validation and JSON serialization.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


# https://blog.meadsteve.dev/programming/2020/02/10/types-at-the-edges-in-python/
# https://pydantic-docs.helpmanual.io/usage/models/
class ResourceRequest(BaseModel):
    """
    This class is used to encode a request for a resource, e.g.,
    language 'English', resource type 'ulb', resource code, i.e.,
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
    There are three assembly strategy kinds to choose from:

    * verse
      - verse strategy will cause a verse's worth of each resource's
      content to be interleaved.
    * chapter
      - chapter strategy will cause a chapter's worth of each resource's
      content to be interleaved.
    * book
      - book strategy will cause a book's worth of each resource's
      content to be interleaved.
    """

    VERSE = "verse"
    # NOTE Chapter and book interleaving assembly strategies may be
    # supported in the future.
    # chapter = "chapter"
    # book = "book"


class DocumentRequest(BaseModel):
    """
    This class is used to send in a document generation request from
    the front end client. A document request is composed of n resource
    requests. Because this class inherits from pydantic's BaseModel we
    get validation, serialization, and special dunder functions for
    free.
    """

    assembly_strategy_kind: AssemblyStrategyEnum
    resource_requests: List[ResourceRequest]


class ResourceLookupDto(BaseModel):
    """
    'Data transfer object' that we use to send lookup related info to
    the resource.
    """

    url: Optional[str]
    source: str
    jsonpath: Optional[str]
    lang_name: str


class BookIntroTemplateDto(BaseModel):
    """
    'Data transfer object' that we use to hold data for use with Jinja2
    template for book intro.
    """

    book_id: str
    content: str
    id_tag: str
    anchor_id: str


class ChapterIntroTemplateDto(BookIntroTemplateDto):
    """
    'Data transfer object' that we use to hold data for use with Jinja2
    template for book intro.
    """


class FinishedDocumentDetails(BaseModel):
    """
    Pydanctic model that we use as a return value to send back via
    Fastapi to the client. For now it just contains the finished
    dcocument filepath on disk.
    """

    finished_document_path: Optional[str]


class TemplateDto(BaseModel):
    """Pydantic model that we use as HTML template data holder."""

    data: Dict


class TNChapterPayload(BaseModel):
    """
    A class to hold a chapter's intro translation notes and a list
    of its verses HTML content.
    """

    intro_html: str
    verses_html: Dict[int, str]


class TNBookPayload(BaseModel):
    """
    A class to hold a book's intro translation notes and a list
    of its chapters translation notes HTML content.
    """

    intro_html: str
    chapters: Dict[int, TNChapterPayload]


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

    chapter_content: List[str]
    chapter_verses: Dict[int, str]


class CoverPayload(BaseModel):
    """
    A class to hold a PDF cover sheet, i.e., first page, HTML template
    variable values.
    """

    title: str
    revision_date: str

