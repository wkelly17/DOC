"""This module provides configuration values used by the application."""
import logging
import os
from collections.abc import Mapping
from logging import config as lc
from typing import Any, Optional, Union

import icontract
import jinja2
import yaml
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, EmailStr, HttpUrl, validator
from typeguard.importhook import install_import_hook

with install_import_hook("document.domain"):
    from document.domain import model


class Settings(BaseSettings):
    """
    BaseSettings subclasses allow values of constants to be overridden
    by environment variables and env files, e.g., ../../.env
    """

    REPO_URL_DICT_KEY: str = "../download-scripture?repo_url"
    RESOURCE_TYPES_JSONPATH: str = "$[*].contents[*].code"
    RESOURCE_CODES_JSONPATH: str = "$[*].contents[*].subcontents[*].code"

    LANGUAGE_FMT_STR: str = "<h1>Language: {}</h1>"
    RESOURCE_TYPE_NAME_FMT_STR: str = "<h2>{}</h2>"
    RESOURCE_TYPE_NAME_WITH_REF_FMT_STR: str = "<h3>{} {}:{}</h3>"
    TN_RESOURCE_TYPE_NAME_WITH_ID_AND_REF_FMT_STR: str = (
        '<h3 id="{}-{}-tn-ch-{}-v-{}">{} {}:{}</h3>'
    )
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
    TRANSLATION_WORD_PREFIX_ANCHOR_LINK_FMT_STR: str = "({}: [{}](#{}-{}))"
    TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-tn-ch-{}-v-{})"
    # FIXME Tighten up the '.' usage in the following regex
    VERSE_ANCHOR_ID_FMT_STR: str = 'id="(.+?)-ch-(.+?)-v-(.+?)"'
    VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR: str = r"id='{}-\1-ch-\2-v-\3'"

    LOGGING_CONFIG_FILE_PATH: str = "src/document/logging_config.yaml"
    DOCKER_CONTAINER_PDF_OUTPUT_DIR = "/output"

    @icontract.require(lambda name: name)
    def get_logger(self, name: str) -> logging.Logger:
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

    # Get API prefix. Useful to have a prefix for versioning of the API.
    # TODO Consider using API_ROOT in router prefix
    API_ROOT: str

    API_LOCAL_PORT: int
    API_REMOTE_PORT: int

    # FIXME HTTPS shouldn't be hardcoded. fastapi will have a sane way
    # to deal with this that I've yet to research.
    def api_url(self) -> str:
        """Return the full base URL of the Fastapi server."""
        host = os.environ.get("API_HOST", "localhost")
        port = self.API_LOCAL_PORT if host == "localhost" else self.API_REMOTE_PORT
        root = self.API_ROOT
        return "https://{}:{}{}".format(host, port, root)

    # Location where resource assets will be downloaded.
    RESOURCE_ASSETS_DIR: str

    # Indicate whether running in Docker container.
    IN_CONTAINER: bool = False

    def working_dir(self) -> str:
        """
        The directory where the resources will be placed once
        acquired. RESOURCE_ASSETS_DIR is used when running in a docker
        environment. Otherwise a suitable local path.
        """
        dirname = ""
        if self.IN_CONTAINER:
            dirname = self.RESOURCE_ASSETS_DIR
        else:
            dirname = "working/temp"
        return dirname

    # Location where generated PDFs will be written to.
    DOCUMENT_OUTPUT_DIR: str

    def output_dir(self) -> str:
        """The directory where the generated documents are placed."""
        dirname = ""
        if self.IN_CONTAINER:
            dirname = self.DOCUMENT_OUTPUT_DIR
        else:
            dirname = "working/output"
        return dirname

    def resource_type_lookup_map(self) -> Mapping[str, Any]:
        """
        Return an immutable dictionary, MappingProxyType, of mappings
        between resource_type and Resource subclass instance.
        """
        # Lazy import to avoid circular import.
        from document.domain.resource import (
            # Resource,
            TAResource,
            TNResource,
            TQResource,
            TWResource,
            USFMResource,
        )

        # resource_type is key, Resource subclass is value
        return {
            "usfm": USFMResource,
            "ulb": USFMResource,
            "ulb-wa": USFMResource,
            "udb": USFMResource,
            "udb-wa": USFMResource,
            "nav": USFMResource,
            "reg": USFMResource,
            "cuv": USFMResource,
            "f10": USFMResource,
            "tn": TNResource,
            "tn-wa": TNResource,
            "tq": TQResource,
            "tq-wa": TQResource,
            "tw": TWResource,
            "tw-wa": TWResource,
            "ta": TAResource,
            "ta-wa": TAResource,
        }

    # For options see https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    WKHTMLTOPDF_OPTIONS: Mapping[str, Optional[str]] = {
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
        "header-left": "[section]",
        "header-right": "[subsection]",
        "header-line": None,  # Produce a line under the header
        "footer-center": "[page]",
        "footer-line": None,  # Produce a line above the footer
    }

    # Return the message to show to user on successful generation of
    # PDF.
    SUCCESS_MESSAGE: str = "Success! Please retrieve your generated document using a GET REST request to /pdf/{document_request_key} where document_request_key is the finished_document_request_key in this payload."

    # Return the message to show to user on failure generating PDF.
    FAILURE_MESSAGE: str = "The document request could not be fulfilled either because the resources requested are not available either currently or at all or because the system does not yet support the resources requested."

    # The location where the JSON data file that we use to lookup
    # location of resources is located.
    TRANSLATIONS_JSON_LOCATION: HttpUrl

    # The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    # individual USFM files (per bible book) may be found.
    INDIVIDUAL_USFM_URL_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='usfm'].url"

    # The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    # resource URL, e.g., tn, tq, tw, ta, obs, ulb, udb, etc., may normally
    # be found.
    RESOURCE_URL_LEVEL1_JSONPATH: str = (
        "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url"
    )

    # The json path to the language's name.
    RESOURCE_LANG_NAME_JSONPATH: str = "$[?code='{}'].name"

    #  The json path to the resource type's name.
    RESOURCE_TYPE_NAME_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].name"

    # The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    # resource URL, e.g., tn, tq, tw, ta, obs, ulb, udb, etc., may
    # additionally/alternatively be found.
    RESOURCE_URL_LEVEL2_JSONPATH: str = (
        "$[?code='{}'].contents[*].subcontents[?code='{}'].links[?format='zip'].url"
    )

    # The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    # resource git repo may be found.
    RESOURCE_DOWNLOAD_FORMAT_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='Download'].url"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200",
    # "http://localhost:8000"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Return the file names, excluding suffix, of files that do not
    # contain content but which may be in the same directory or
    # subdirectories of a resource's acquired files.
    MARKDOWN_DOC_FILE_NAMES: list[str] = ["readme", "license"]

    def document_html_header(self) -> str:
        """
        Return the enclosing HTML and body element format string used
        to enclose the document's HTML content which was aggregated from
        all the resources in the document request.
        """
        return self.template("header_enclosing")

    def document_html_footer(self) -> str:
        """
        Return the enclosing HTML and body element format string used
        to enclose the document's HTML content which was aggregated from
        all the resources in the document request.
        """
        return self.template("footer_enclosing")

    ENGLISH_GIT_REPO_MAP: Mapping[str, str] = {
        "ulb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_ulb",
        "udb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_udb",
        "tn-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn",
        "tw-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tw",
        "tq-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tq",
    }

    def english_git_repo_url(self, resource_type: str) -> str:
        """
        This is a hack to compensate for translations.json which only
        provides URLs in non-English languages.
        """
        return self.ENGLISH_GIT_REPO_MAP[resource_type]

    ENGLISH_RESOURCE_TYPE_MAP: Mapping[str, str] = {
        "ulb-wa": "Unlocked Literal Bible (ULB)",
        "udb-wa": "Unlocked Dynamic Bible (UDB)",
        "tn-wa": "ULB Translation Helps",
        "tq-wa": "ULB Translation Questions",
        "tw-wa": "ULB Translation Words",
    }

    def english_resource_type_name(self, resource_type: str) -> str:
        """
        This is a hack to compensate for translations.json which only
        provides information for non-English languages.
        """
        return self.ENGLISH_RESOURCE_TYPE_MAP[resource_type]

    TEMPLATE_PATHS_MAP: Mapping[str, str] = {
        "book_intro": "src/templates/tn/book_intro_template.md",
        "header_enclosing": "src/templates/html/header_enclosing.html",
        "footer_enclosing": "src/templates/html/footer_enclosing.html",
        "cover": "src/templates/html/cover.html",
        "email-html": "src/templates/html/email.html",
        "email": "src/templates/text/email.txt",
    }

    def template_path(self, key: str) -> str:
        """
        Return the path to the requested template give a lookup key.
        Return a different path if the code is running inside the Docker
        container.
        """
        return self.TEMPLATE_PATHS_MAP[key]

    @icontract.require(
        lambda template_lookup_key, dto: template_lookup_key and dto is not None
    )
    def instantiated_template(self, template_lookup_key: str, dto: BaseModel) -> str:
        """
        Instantiate Jinja2 template with dto BaseModel instance. Return
        instantiated template as string.
        """
        # FIXME Maybe use jinja2.PackageLoader here instead: https://github.com/tfbf/usfm/blob/master/usfm/html.py
        with open(self.template_path(template_lookup_key), "r") as filepath:
            template = filepath.read()
        # FIXME Handle exceptions
        env = jinja2.Environment().from_string(template)
        return env.render(data=dto)

    @icontract.require(lambda template_lookup_key: template_lookup_key)
    def template(self, template_lookup_key: str) -> str:
        """Return template as string."""
        with open(self.template_path(template_lookup_key), "r") as filepath:
            template = filepath.read()
        return template

    # Return boolean indicating if caching of generated document's should be
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
    DEFAULT_ASSEMBLY_SUBSTRATEGY: model.AssemblySubstrategyEnum = (
        model.AssemblySubstrategyEnum.VERSE
    )

    # Return a list of the Markdown section titles that our
    # Python-Markdown remove_section_processor extension should remove.
    MARKDOWN_SECTIONS_TO_REMOVE: list[str] = [
        "Examples from the Bible stories",
        "Links",
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
    def get_send_email(cls, v: bool) -> bool:
        return bool(v)

    SMTP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
