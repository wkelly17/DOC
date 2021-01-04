from typing import List, Optional

from enum import Enum
from enum import unique
from pydantic import BaseModel

# https://blog.meadsteve.dev/programming/2020/02/10/types-at-the-edges-in-python/
# https://pydantic-docs.helpmanual.io/usage/models/
class ResourceRequest(BaseModel):
    """
    This class is used to encode a request for a resource, e.g.,
    language 'English', resource type 'ulb', resource code, i.e.,
    book, 'gen'. A document request composes n of these resource
    request instances. Because this class inherits from pydantic's
    BaseModel we get validation and serialization for free.
    """

    lang_code: str
    resource_type: str
    resource_code: str


# See
# https://pydantic-docs.helpmanual.io/usage/types/#enums-and-choices
# for where this pattern of combining Enum and BaseModel comes from in
# pydantic.
@unique
class AssemblyStrategyEnum(Enum):
    """
    There are three assembly strategy kinds to choose from:

    * BOOK
    * CHAPTER
    * VERSE

    - BOOK strategy will cause a book's worth of each resource's
    content to be interleaved.
    - CHAPTER strategy will cause a chapter's worth of each resource's
    content to be interleaved.
    - VERSE strategy will cause a verse's worth of each resource's
    content to be interleaved.
    """

    BOOK = "book"
    CHAPTER = "chapter"
    VERSE = "verse"


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
    the resource that it needs.
    """

    url: Optional[str]
    source: str
    jsonpath: Optional[str]


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

    pass
