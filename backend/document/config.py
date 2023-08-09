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
    LTR_DIRECTION_HTML: str = "<div style='direction: ltr;'>"
    RTL_DIRECTION_HTML: str = "<div style='direction: rtl;'>"

    END_OF_CHAPTER_HTML: str = '<div class="end-of-chapter"></div>'
    LANGUAGE_FMT_STR: str = "<h1 style='text-align: center'>Language: {}</h1>"
    RESOURCE_TYPE_NAME_FMT_STR: str = "<h1>{}</h1>"
    TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR: str = "<div style='column-count: 2;'>{}</div>"
    TQ_HEADING_FMT_STR: str = "<h3>{}</h3>"
    TQ_HEADING_AND_QUESTIONS_FMT_STR: str = (
        "<h3>{}</h3>\n<div style='column-count: 2;'>{}</div>"
    )
    HTML_ROW_BEGIN: str = model.HtmlContent("<div class='row'>")
    HTML_ROW_END: str = model.HtmlContent("</div>")
    HTML_COLUMN_BEGIN: str = model.HtmlContent("<div class='column'>")
    HTML_COLUMN_END: str = model.HtmlContent("</div>")
    HTML_COLUMN_LEFT_BEGIN: str = model.HtmlContent("<div class='column-left'>")
    HTML_COLUMN_RIGHT_BEGIN: str = model.HtmlContent("<div class='column-right'>")
    BOOK_NAME_FMT_STR: str = "<h2 style='text-align: center;'>{}</h2>"
    BOOK_FMT_STR: str = "<h2 style='text-align: center;'>Book: {}</h2>"
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
    FOOTNOTES_HEADING: model.HtmlContent = model.HtmlContent("<h4>Footnotes</h4>")
    OPENING_H3_FMT_STR: str = "<h3>{}"
    OPENING_H3_WITH_ID_FMT_STR: str = '<h3 id="{}-{}">{}'
    TRANSLATION_WORD_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{})"
    TRANSLATION_WORD_FMT_STR: str = "{}"
    TRANSLATION_WORD_PREFIX_ANCHOR_LINK_FMT_STR: str = "({}: [{}](#{}-{}))"
    TRANSLATION_WORD_PREFIX_FMT_STR: str = "({}: {})"
    # TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-tn-ch-{}-v-{})"
    TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-ch-{}-v-{})"
    VERSE_ANCHOR_ID_FMT_STR: str = 'id="(.+?)-ch-(.+?)-v-(.+?)"'
    VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR: str = r"id='{}-\1-ch-\2-v-\3'"

    USFM_RESOURCE_TYPES: Sequence[str] = [
        "ayt",
        "cuv",
        "f10",
        "nav",
        "reg",
        # "udb", # 2023-06-20 Content team doesn't want this used.
        # "udb-wa", # 2022-05-12 - Content team doesn't want this used.
        "ugnt",
        # "uhb", # parser blows on: AttributeError: 'SingleHTMLRenderer' object has no attribute 'renderCAS'
        "ulb",
        "usfm",
    ]
    # f10 for fr, and udb for many other languages are secondary USFM types,
    # meaning: for those languages that have them those same languages have
    # a primary USFM type such as ulb (there can be other primary USFM types
    # besides ulb such as cuv, reg, nav, etc.). For v1, we only allow use of
    # a primary USFM type since v1 has a requirement that the user is not to
    # choose resource types in the UI, so we use this next list to manage
    # that when we automatically choose the reesource types (from the USFM
    # and TN resource types that translations.json lists as available) for
    # the GL languages and books chosen.
    USFM_RESOURCE_TYPES_MINUS_SECONDARY: Sequence[str] = [
        usfm_resource_type
        for usfm_resource_type in USFM_RESOURCE_TYPES
        if usfm_resource_type
        not in [
            "f10"
        ]  # Used to include udb too, but content team requested no use of udb
    ]
    EN_USFM_RESOURCE_TYPES: Sequence[str] = ["ulb-wa"]
    TN_RESOURCE_TYPES: Sequence[str] = ["tn"]
    EN_TN_RESOURCE_TYPES: Sequence[str] = ["tn-wa"]
    TQ_RESOURCE_TYPES: Sequence[str] = ["tq"]
    EN_TQ_RESOURCE_TYPES: Sequence[str] = ["tq-wa"]
    TW_RESOURCE_TYPES: Sequence[str] = ["tw"]
    EN_TW_RESOURCE_TYPES: Sequence[str] = ["tw-wa"]
    BC_RESOURCE_TYPES: Sequence[str] = ["bc-wa"]
    V1_APPROVED_RESOURCE_TYPES: Sequence[str] = [
        *EN_USFM_RESOURCE_TYPES,
        *USFM_RESOURCE_TYPES_MINUS_SECONDARY,
        *TN_RESOURCE_TYPES,
        *EN_TN_RESOURCE_TYPES,
    ]
    # List of language codes for which there is a content issue
    # such that a complete document request cannot
    # be formed. E.g., hu doesn't have any resource types or resource
    # codes in translations.json. E.g., abz's content has unresolved
    # git merge markers in source that were accidentally committed.
    # TODO Test to see which of these languages can be added back now
    # that several content defect handling features have been added.
    LANG_CODE_FILTER_LIST: Sequence[str] = [
        "acq",
        "gaj-x-ymnk",
        "fa",
        "hr",
        "hu",
        # "id",  # Currently doesn't provide USFM, but might soon
        "kbt",
        "kip",
        "lus",
        "mor",
        "mve",
        "pmy",  # Currently doesn't provide USFM, but might soon
        "sr-Latn",
        "tig",
        "tem",
    ]
    GATEWAY_LANGUAGES: Sequence[str] = [
        "am",
        "arb",
        "as",
        "bn",
        "pt-br",
        "my",
        "ceb",
        "zh",
        "en",
        "fr",
        "gu",
        "ha",
        "hi",
        "ilo",
        "id",
        "kn",
        "km",
        "lo",
        "es-419",
        "plt",
        "ml",
        "mr",
        "ne",
        "or",
        "pmy",
        "fa",
        "pa",
        "ru",
        "sw",
        "tl",
        "ta",
        "te",
        "th",
        "tpi",
        "ur",
        "ur-deva",
        "vi",
    ]

    # fmt: off
    BC_ARTICLE_URL_FMT_STR: str = "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc/src/branch/master/{}"
    # fmt: on

    OXML_LANGUAGE_LIST: list[str] = [
        "ar-SA",
        "bg-BG",
        "zh-CN",
        "zh-TW",
        "hr-HR",
        "cs-CZ",
        "da-DK",
        "nl-NL",
        "en-US",
        "et-EE",
        "fi-FI",
        "fr-FR",
        "de-DE",
        "el-GR",
        "he-IL",
        "hi-IN",
        "hu-HU",
        "id-ID",
        "it-IT",
        "ja-JP",
        "kk-KZ",
        "ko-KR",
        "lv-LV",
        "lt-LT",
        "ms-MY",
        "nb-NO",
        "pl-PL",
        "pt-BR",
        "pt-PT",
        "ro-RO",
        "ru-RU",
        "sr-latn-RS",
        "sk-SK",
        "sl-SI",
        "es-ES",
        "sv-SE",
        "th-TH",
        "tr-TR",
        "uk-UA",
        "vi-VN",
    ]
    OXML_LANGUAGE_LIST_LOWERCASE: list[str] = [
        language.lower() for language in OXML_LANGUAGE_LIST
    ]
    OXML_LANGUAGE_LIST_LOWERCASE_SPLIT: list[str] = [
        language for language in OXML_LANGUAGE_LIST_LOWERCASE if "-" in language
    ]

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
        return "http://{}:{}".format(self.API_TEST_BASE_URL, self.API_LOCAL_PORT)

    API_TEST_BASE_URL: str = "http://localhost"

    API_LOCAL_PORT: int

    USE_GIT_CLI: bool = False

    LOGGING_CONFIG_FILE_PATH: str = "backend/document/logging_config.yaml"

    # Location where resource assets will be downloaded.
    RESOURCE_ASSETS_DIR: str = "working/temp"

    # Location where generated PDFs will be written to.
    DOCUMENT_OUTPUT_DIR: str = "working/output"

    # Location where generated PDFs will be written to.
    DOCUMENT_SERVE_DIR: str = "document_output"

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
        raise ValueError("Malformed JSON for BACKEND_CORS_ORIGINS value.")

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
    ID_GIT_REPO_MAP: Mapping[str, str] = {
        "ayt": "https://content.bibletranslationtools.org/WA-Catalog/id_ayt",
        "tn": "https://content.bibletranslationtools.org/WA-Catalog/id_tn",
        "tq": "https://content.bibletranslationtools.org/WA-Catalog/id_tq",
        "tw": "https://content.bibletranslationtools.org/WA-Catalog/id_tw",
    }

    ENGLISH_RESOURCE_TYPE_MAP: Mapping[str, str] = {
        "ulb-wa": "Unlocked Literal Bible (ULB)",
        # "udb-wa": "Unlocked Dynamic Bible (UDB)",
        "tn-wa": "ULB Translation Notes",
        "tq-wa": "ULB Translation Questions",
        "tw-wa": "ULB Translation Words",
        "bc-wa": "Bible Commentary",
    }

    ID_LANGUAGE_NAME = "Bahasa Indonesian"
    ID_RESOURCE_TYPE_MAP: Mapping[str, str] = {
        "ayt": "Bahasa Indonesian Bible (ayt)",
        "tn": "Translation Helps (tn)",
        "tq": "Translation Questions (tq)",
        "tw": "Translation Words (tw)",
    }
    ENGLISH_RESOURCE_TYPE_MAP_USFM_AND_TN_ONLY: Mapping[str, str] = {
        "ulb-wa": "Unlocked Literal Bible (ULB)",
        # "udb-wa": "Unlocked Dynamic Bible (UDB)",
        "tn-wa": "ULB Translation Notes",
    }
    ID_RESOURCE_TYPE_MAP_USFM_AND_TN_ONLY: Mapping[str, str] = {
        "ayt": "Bahasa Indonesian Bible (ayt)",
        "tn": "Translation Helps",
    }

    TEMPLATE_PATHS_MAP: Mapping[str, str] = {
        "book_intro": "backend/templates/tn/book_intro_template.md",
        "header_enclosing": "backend/templates/html/header_enclosing.html",
        "header_no_css_enclosing": "backend/templates/html/header_no_css_enclosing.html",
        "header_compact_enclosing": "backend/templates/html/header_compact_enclosing.html",
        "footer_enclosing": "backend/templates/html/footer_enclosing.html",
        "cover": "backend/templates/html/cover.html",
        "email-html": "backend/templates/html/email.html",
        "email": "backend/templates/text/email.txt",
    }

    DOCX_TEMPLATE_PATH: str = "/app/template.docx"
    DOCX_COMPACT_TEMPLATE_PATH: str = "/app/template_compact.docx"

    # Return boolean indicating if caching of generated documents should be
    # cached.
    ASSET_CACHING_ENABLED: bool = True
    # Caching window of time in which asset
    # files on disk are considered fresh rather than re-acquiring (in
    # the case of resource asset files) or re-generating them (in the
    # case of the final PDF). In hours.
    ASSET_CACHING_PERIOD: int

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

    # Used in assembly_strategy_utils modeule when zero-filling various strings
    NUM_ZEROS = 3

    # Pydantic uses this inner class convention to configure the
    # Settings class.
    class Config:
        env_file = ".env"
        case_sensitive = True


settings: Settings = Settings()
