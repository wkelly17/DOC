"""This module provides configuration values used by the application."""
import logging
from collections.abc import Mapping, Sequence
from logging import config as lc
from typing import Optional, final

import yaml
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, validator

from document.domain import model


@final
class Settings(BaseSettings):
    """
    BaseSettings subclasses like this one allow values of constants to
    be overridden by environment variables like those defined in env
    files, e.g., ../../.env
    """

    REPO_URL_DICT_KEY: str = "../download-scripture?repo_url"
    ALT_REPO_URL_DICT_KEY: str = "/download-scripture?repo_url"

    # The location where the JSON data file that we use to lookup
    # location of resources is located.
    TRANSLATIONS_JSON_LOCATION: HttpUrl
    # The jsonpath format string for the resource's git repo for a given language, resource type, and book.
    RESOURCE_DOWNLOAD_FORMAT_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='Download'].url"
    # All resource types.
    RESOURCE_TYPES_JSONPATH: str = "$[*].contents[*].code"
    # The jsonpath format string for resource types for a given language.
    RESOURCE_TYPES_FOR_LANG_JSONPATH: str = "$[?code='{}'].contents[*].code"
    # jsonpath for all resource codes.
    RESOURCE_CODES_JSONPATH: str = "$[*].contents[*].subcontents[*].code"
    # jsonpath format string for all resource codes for a given language.
    RESOURCE_CODES_FOR_LANG_JSONPATH: str = (
        "$[?code='{}'].contents[*].subcontents[*].code"
    )
    # The jsonpath format string for individual USFM files (per bible book) for a given language, resource type, and book.
    INDIVIDUAL_USFM_URL_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='usfm'].url"
    # The jsonpath format string for resource URL for a given lanaguage and resource type.
    RESOURCE_URL_LEVEL1_JSONPATH: str = (
        "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url"
    )
    # The jsonpath format string for a given language's name.
    RESOURCE_LANG_NAME_JSONPATH: str = "$[?code='{}'].name"
    # The jsonpath format string to the resource type's name for a given language and resource type.
    RESOURCE_TYPE_NAME_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].name"
    # The jsonpath format string for a zip URL for a given language and resource code.
    RESOURCE_URL_LEVEL2_JSONPATH: str = (
        "$[?code='{}'].contents[*].subcontents[?code='{}'].links[?format='zip'].url"
    )

    LANGUAGE_FMT_STR: str = "<h1>Language: {}</h1>"
    RESOURCE_TYPE_NAME_FMT_STR: str = "<h1>{}</h1>"
    HTML_ROW_BEGIN: str = model.HtmlContent("<div class='row'>")
    HTML_ROW_END: str = model.HtmlContent("</div>")
    HTML_COLUMN_BEGIN: str = model.HtmlContent("<div class='column'>")
    HTML_COLUMN_END: str = model.HtmlContent("</div>")
    HTML_COLUMN_LEFT_BEGIN: str = model.HtmlContent("<div class='column-left'>")
    HTML_COLUMN_RIGHT_BEGIN: str = model.HtmlContent("<div class='column-right'>")
    BOOK_FMT_STR: str = "<h2>Book: {}</h2>"
    BOOK_AS_GROUPER_FMT_STR: str = "<h1>Book: {}</h1>"
    VERSE_FMT_STR: str = "<h3>Verse {}:{}</h3>"
    TRANSLATION_NOTE_FMT_STR: str = "<h3>Translation note {}:{}</h3>"
    CHAPTER_HEADER_FMT_STR: str = '<h2 class="c-num" id="{}-{}-ch-{}">Chapter {}</h2>'
    TRANSLATION_QUESTION_FMT_STR: str = "<h3>Translation question {}:{}</h3>"
    TRANSLATION_ACADEMY_FMT_STR: str = "<h3>Translation academy {}:{}</h3>"
    UNORDERED_LIST_BEGIN_STR: model.HtmlContent = model.HtmlContent("<ul>")
    UNORDERED_LIST_END_STR: model.HtmlContent = model.HtmlContent("</ul>")
    TRANSLATION_WORD_LIST_ITEM_FMT_STR: model.HtmlContent = model.HtmlContent(
        '<li><a href="#{}-{}">{}</a></li>'
    )
    TRANSLATION_WORDS_FMT_STR: str = "<h3>Translation words {}:{}</h3>"
    TRANSLATION_WORDS_SECTION_STR: str = "<h2>Translation words</h2>"
    TRANSLATION_WORD_VERSE_SECTION_HEADER_STR: model.HtmlContent = model.HtmlContent(
        "<h4>Uses:</h4>"
    )
    TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR: str = (
        '<li><a href="#{}-{}-ch-{}-v-{}">{} {}:{}</a></li>'
    )
    FOOTNOTES_HEADING: model.HtmlContent = model.HtmlContent("<h3>Footnotes</h3>")
    OPENING_H3_FMT_STR: str = "<h3>{}"
    OPENING_H3_WITH_ID_FMT_STR: str = '<h3 id="{}-{}">{}'
    TRANSLATION_WORD_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{})"
    TRANSLATION_WORD_FMT_STR: str = "{}"
    TRANSLATION_WORD_PREFIX_ANCHOR_LINK_FMT_STR: str = "({}: [{}](#{}-{}))"
    TRANSLATION_WORD_PREFIX_FMT_STR: str = "({}: {})"
    TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-tn-ch-{}-v-{})"
    # FIXME Tighten up the '.' usage in the following regex
    VERSE_ANCHOR_ID_FMT_STR: str = 'id="(.+?)-ch-(.+?)-v-(.+?)"'
    VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR: str = r"id='{}-\1-ch-\2-v-\3'"

    LOGGING_CONFIG_FILE_PATH: str = "backend/document/logging_config.yaml"
    DOCKER_CONTAINER_DOCUMENT_OUTPUT_DIR: str = "/document_output"
    USFM_RESOURCE_TYPES: Sequence[str] = [
        "cuv",
        "f10",
        "nav",
        "reg",
        "udb",
        # "udb-wa", # 2022-05-12 - Content team doesn't want this used.
        "ugnt",
        # "uhb", # parser blows on: AttributeError: 'SingleHTMLRenderer' object has no attribute 'renderCAS'
        "ulb",
        "ulb-wa",
        "usfm",
    ]
    TN_RESOURCE_TYPES: Sequence[str] = ["tn"]
    EN_TN_RESOURCE_TYPES: Sequence[str] = ["tn-wa"]
    TQ_RESOURCE_TYPES: Sequence[str] = ["tq", "tq-wa"]
    TW_RESOURCE_TYPES: Sequence[str] = ["tw", "tw-wa"]
    BC_RESOURCE_TYPES: Sequence[str] = ["bc-wa"]
    # List of language codes for which there is an issue in
    # translations.json such that a complete document request cannot
    # be formed for these languages due to some issue with respect to
    # their resource types or resource codes. E.g., hu doesn't have
    # any resource types or resource codes in translations.json.
    LANG_CODE_FILTER_LIST: Sequence[str] = [
        "acq",
        "gaj-x-ymnk",
        "fa",
        "hr",
        "hu",
        "id",
        "kbt",
        "kip",
        "lus",
        "mor",
        "mve",
        "pmy",
        "sr-Latn",
        "tig",
        "tem",
    ]

    # fmt: off
    BC_ARTICLE_URL_FMT_STR: str = "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc/src/branch/master/{}"
    # fmt: on

    def logger(self, name: str) -> logging.Logger:
        """
        Return a Logger for scope named by name, e.g., module, that can be
        used for logging.
        """
        with open(self.LOGGING_CONFIG_FILE_PATH, "r") as fin:
            logging_config = yaml.safe_load(fin.read())
            lc.dictConfig(logging_config)
        return logging.getLogger(name)

    def api_test_url(self) -> str:
        """Non-secure local URL for running the Fastapi server for testing."""
        return "http://localhost:{}".format(self.API_LOCAL_PORT)

    API_LOCAL_PORT: int

    # Location where resource assets will be downloaded.
    RESOURCE_ASSETS_DIR: str = "/working/temp"

    # Indicate whether running in Docker container.
    IN_CONTAINER: bool = False

    USE_GIT_CLI: bool = False

    def working_dir(self) -> str:
        """
        The directory where the resources will be placed once
        acquired.
        """
        if self.IN_CONTAINER:
            return self.RESOURCE_ASSETS_DIR
        else:
            return self.RESOURCE_ASSETS_DIR[1:]

    # Location where generated PDFs will be written to.
    DOCUMENT_OUTPUT_DIR: str = "/working/output"

    def output_dir(self) -> str:
        """The directory where the generated documents are placed."""
        dirname = ""
        if self.IN_CONTAINER:
            dirname = self.DOCUMENT_OUTPUT_DIR
        else:
            dirname = self.DOCUMENT_OUTPUT_DIR[1:]
        return dirname

    # For options see https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    WKHTMLTOPDF_OPTIONS: dict[str, Optional[str]] = {
        "page-size": "Letter",
        # 'margin-top': '0.75in',
        # 'margin-right': '0.75in',
        # 'margin-bottom': '0.75in',
        # 'margin-left': '0.75in',
        "encoding": "UTF-8",
        "load-error-handling": "ignore",
        "outline": None,  # Produce an outline
        "outline-depth": "3",  # Only go depth of 3 on the outline
        "enable-internal-links": None,  # enable internal links
        "header-font-size": "10",
        "header-left": "[section]",
        "header-right": "[subsection]",
        "header-line": None,  # Produce a line under the header
        "footer-font-size": "10",
        "footer-center": "[page]",
        "footer-right": "generated on [isodate] at [time]",
        "footer-line": None,  # Produce a line above the footer
    }
    PANDOC_OPTIONS: str = "--quiet"

    # Return the message to show to user on successful generation of
    # PDF.
    SUCCESS_MESSAGE: str = "Success! Please retrieve your generated document using a GET REST request to /pdf/{document_request_key} or /epub/{document_request_key} or /docx/{document_request_key} (depending on whether you requested PDF, ePub, or Docx result) where document_request_key is the finished_document_request_key in this payload."

    # Return the message to show to user on failure generating PDF.
    FAILURE_MESSAGE: str = "The document request could not be fulfilled either because the resources requested are not available either currently or at all or because the system does not yet support the resources requested."

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200",
    # "http://localhost:8000"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Return the file names, excluding suffix, of files that do not
    # contain content but which may be in the same directory or
    # subdirectories of a resource's acquired files.
    MARKDOWN_DOC_FILE_NAMES: list[str] = ["readme", "license"]

    ENGLISH_GIT_REPO_MAP: Mapping[str, str] = {
        "ulb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_ulb",
        "udb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_udb",
        "tn-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn",
        "tw-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tw",
        "tq-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tq",
        "bc-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc",
    }

    ENGLISH_RESOURCE_TYPE_MAP: Mapping[str, str] = {
        "ulb-wa": "Unlocked Literal Bible (ULB)",
        "udb-wa": "Unlocked Dynamic Bible (UDB)",
        "tn-wa": "ULB Translation Helps",
        "tq-wa": "ULB Translation Questions",
        "tw-wa": "ULB Translation Words",
        "bc-wa": "Bible Commentary",
    }

    TEMPLATE_PATHS_MAP: Mapping[str, str] = {
        "book_intro": "backend/templates/tn/book_intro_template.md",
        "header_enclosing": "backend/templates/html/header_enclosing.html",
        "header_compact_enclosing": "backend/templates/html/header_compact_enclosing.html",
        "footer_enclosing": "backend/templates/html/footer_enclosing.html",
        "cover": "backend/templates/html/cover.html",
        "email-html": "backend/templates/html/email.html",
        "email": "backend/templates/text/email.txt",
    }

    # Return boolean indicating if caching of generated documents should be
    # cached.
    ASSET_CACHING_ENABLED: bool = True
    # Caching window of time in which asset
    # files on disk are considered fresh rather than re-acquiring (in
    # the case of resource asset files) or re-generating them (in the
    # case of the final PDF). In hours.
    ASSET_CACHING_PERIOD: int

    # Get the path to the logo image that will be used on the PDF cover,
    # i.e., first, page.
    LOGO_IMAGE_PATH: str = "icon-tn.png"

    # It doesn't yet make sense to offer the (high level)
    # assembly strategy _and_ the assembly sub-strategy to the end user
    # as a document request parameter so we'll just choose an arbitrary
    # sub-strategy here. This means that we can write code for multiple
    # sub-strategies and choose one to put in play at a time here.

    # Return a list of the Markdown section titles that our
    # Python-Markdown remove_section_processor extension should remove.
    MARKDOWN_SECTIONS_TO_REMOVE: list[str] = [
        "Examples from the Bible stories",
        "Links",
        "Picture of",
        "Pictures",
    ]

    #  Return the from email to use for sending email with generated PDF
    #  attachment to document request recipient. Look for the value to
    #  use in FROM_EMAIL environment variable, use default if it doesn't
    #  exist.
    FROM_EMAIL_ADDRESS: EmailStr

    # The to-email address to use for sending email with generated
    # PDF attachment to document request recipient during testing - in
    # production the to-email address is supplied by the user.
    TO_EMAIL_ADDRESS: EmailStr
    EMAIL_SEND_SUBJECT: str

    # Return boolean representing if the system should execute the
    # action of sending an email when appropriate to do so.
    SEND_EMAIL: bool

    @validator("SEND_EMAIL")
    def send_email(cls, v: bool) -> bool:
        return bool(v)

    SMTP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int

    # Example fake user agent value required by domain host to allow serving
    # files. Other values could possibly work. This value definitely
    # works.
    USER_AGENT: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"

    # Pydantic uses this inner class convention to configure the
    # Settings class.
    class Config:
        env_file = ".env"
        case_sensitive = True


settings: Settings = Settings()
