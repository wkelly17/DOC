"""This module provides configuration values used by the application."""


import icontract
import jinja2
import logging
import os
import pydantic
from logging import config as lc
from typing import Dict, List

import yaml

from document import config
from document.domain import model


REPO_URL_DICT_KEY = "../download-scripture?repo_url"
RESOURCE_TYPES_JSONPATH = "$[*].contents[*].code"
RESOURCE_CODES_JSONPATH = "$[*].contents[*].subcontents[*].code"


@icontract.require(lambda name: name)
def get_logger(name: str) -> logging.Logger:
    """
    Return a Logger for scope named by name, e.g., module, that can be
    used for logging.
    """
    with open(config.get_logging_config_file_path(), "r") as fin:
        logging_config = yaml.safe_load(fin.read())
        lc.dictConfig(logging_config)
    return logging.getLogger(name)


def get_api_test_url() -> str:
    """Non-secure local URL for running the Fastapi server for testing."""
    return "http://localhost:{}".format(get_api_local_port())


def get_api_root() -> str:
    """
    Get API prefix. Useful to have a prefix for versioning of the
    API. TODO Fastapi probably provides a better way of specifying an
    API prefix.
    """
    return os.environ.get("API_ROOT", "/api/v1")


def get_api_local_port() -> str:
    """Get port where the Fastapi server runs locally."""
    return os.environ.get("API_LOCAL_PORT", "5005")


def get_api_remote_port() -> str:
    """Get port where the Fastapi server runs remotely in the Docker container."""
    return os.environ.get("API_REMOTE_PORT", "80")


def get_api_url() -> str:
    """Return the full base URL of the Fastapi server."""
    host = os.environ.get("API_HOST", "localhost")
    port = get_api_local_port() if host == "localhost" else get_api_remote_port()
    root = get_api_root()
    # FIXME HTTPS shouldn't be hardcoded. fastapi will have a sane way
    # to deal with this that I've yet to research.
    return "https://{}:{}{}".format(host, port, root)
    # return f"http://{host}:{port}"


# FIXME Proper setting of working_dir is currently being handled by
# convert_html2pdf method of document_generator instance.
# NOTE This should be using RESOURCE_ASSETS_DIR if it is set in the shell,
# but this presupposes that the call to python -m test_flask on the
# tools repo is being called on the same shell as Docker container is
# being run in. But until now, I've been running tools in a fish shell
# and Docker container in a zshell.
def get_working_dir() -> str:
    """
    The directory where the resources will be placed once
    acquired. RESOURCE_ASSETS_DIR is provided when running in a docker
    environment. Otherwise a suitable temporary local directory is
    generated automatically.
    """
    dirname = ""
    if os.environ.get("IN_CONTAINER"):
        dirname = os.environ.get("RESOURCE_ASSETS_DIR", "/working/temp")
    else:
        dirname = os.environ.get("RESOURCE_ASSETS_DIR", "working/temp")
    return dirname


def get_output_dir() -> str:
    """The directory where the generated documents are placed."""
    dirname = ""
    if os.environ.get("IN_CONTAINER"):
        dirname = os.environ.get("DOCUMENT_OUTPUT_DIR", "/working/temp")
    else:
        dirname = os.environ.get("DOCUMENT_OUTPUT_DIR", "working/temp")
    return dirname


def get_translations_json_location() -> str:
    """
    The location where the JSON data file that we use to lookup
    location of resources is located.
    """
    loc = os.environ.get(
        "TRANSLATIONS_JSON_LOCATION",
        "http://bibleineverylanguage.org/wp-content/themes/bb-theme-child/data/translations.json",
    )
    return loc


def get_individual_usfm_url_jsonpath() -> str:
    """
    The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    individual USFM files (per bible book) may be found.
    """
    return "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='usfm'].url"


def get_resource_url_level1_jsonpath() -> str:
    """
    The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource URL, e.g., tn, tq, tw, ta, obs, ulb, udb, etc., may normally
    be found.
    """
    return "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url"


def get_resource_lang_name_jsonpath() -> str:
    """
    The language's name.
    """
    return "$[?code='{}'].name"


def get_resource_type_name_jsonpath() -> str:
    """
    The resource type's name.
    """
    return "$[?code='{}'].contents[?code='{}'].name"


def get_resource_url_level2_jsonpath() -> str:
    """
    The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource URL, e.g., tn, tq, tw, ta, obs, ulb, udb, etc., may
    additionally/alternatively be found.
    """
    return "$[?code='{}'].contents[*].subcontents[?code='{}'].links[?format='zip'].url"


def get_resource_download_format_jsonpath() -> str:
    """
    The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource git repo may be found.
    """
    return "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='Download'].url"


def get_logging_config_file_path() -> str:
    """
    The file path location where the dictConfig-style yaml
    formatted config file for logging is located.
    """
    filepath = ""
    if os.environ.get("IN_CONTAINER"):
        filepath = os.environ.get("LOGGING_CONFIG", "src/document/logging_config.yaml")
    else:
        filepath = "src/document/logging_config.yaml"
    return filepath


# FIXME Icon no longer lives at this location since they redesigned
# their website. For now I can just copy over an old version of the icon
# into ./working/temp/ or grab it from archive.org as I do here.
def get_icon_url() -> str:
    """Get the tn-icon.png from unfolding word."""
    return "https://web.archive.org/web/20160819103903if_/https://unfoldingword.org/assets/img/icon-tn.png"
    # return "https://unfoldingword.org/assets/img/icon-tn.png"
    # return "https://static1.squarespace.com/static/591e003db8a79bd6e6c9ffae/t/5e306da5898d7b14b76889dd/1600444722464/?format=1500w"


def get_markdown_doc_file_names() -> List[str]:
    """
    Return the file names, excluding suffix, of files that do not
    contain content but which may be in the same directory or
    subdirectories of a resource's acquired files.
    """
    return ["readme", "license"]


def get_document_html_header() -> str:
    """
    Return the enclosing HTML and body element format string used
    to enclose the document's HTML content which was aggregated from
    all the resources in the document request.
    """
    return get_template("header_enclosing")


def get_document_html_footer() -> str:
    """
    Return the enclosing HTML and body element format string used
    to enclose the document's HTML content which was aggregated from
    all the resources in the document request.
    """
    return get_template("footer_enclosing")


@icontract.require(lambda resource_type: resource_type)
def get_english_git_repo_url(resource_type: str) -> str:
    """
    This is a hack to compensate for translations.json which only
    provides URLs in non-English languages.
    """
    return {
        "ulb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_ulb",
        "udb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_udb",
        "tn-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn",
        "tw-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tw",
        "tq-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tq",
    }[resource_type]


@icontract.require(lambda resource_type: resource_type)
def get_english_resource_type_name(resource_type: str) -> str:
    """
    This is a hack to compensate for translations.json which only
    provides information for non-English languages.
    """
    return {
        "ulb-wa": "Unlocked Literal Bible (ULB)",
        "udb-wa": "Unlocked Dynamic Bible (UDB)",
        "tn-wa": "ULB Translation Helps",
        "tq-wa": "ULB Translation Questions",
        "tw-wa": "ULB Translation Words",
    }[resource_type]


@icontract.require(lambda key: key)
def get_template_path(key: str) -> str:
    """
    Return the path to the requested template give a lookup key.
    Return a different path if the code is running inside the Docker
    container.
    """
    templates = {
        "book_intro": "src/templates/tn/book_intro_template.md",
        "header_enclosing": "src/templates/html/header_enclosing.html",
        "footer_enclosing": "src/templates/html/footer_enclosing.html",
        "cover": "src/templates/html/cover.html",
        "email-html": "src/templates/html/email.html",
        "email": "src/templates/text/email.txt",
    }
    path = templates[key]
    # if not os.environ.get("IN_CONTAINER"):
    #     path = "src/{}".format(path)
    return path


@icontract.require(
    lambda template_lookup_key, dto: template_lookup_key and dto is not None
)
def get_instantiated_template(template_lookup_key: str, dto: pydantic.BaseModel) -> str:
    """
    Instantiate Jinja2 template with dto BaseModel instance. Return
    instantiated template as string.
    """
    # FIXME Maybe use jinja2.PackageLoader here instead: https://github.com/tfbf/usfm/blob/master/usfm/html.py
    with open(config.get_template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    # FIXME Handle exceptions
    env = jinja2.Environment().from_string(template)
    return env.render(data=dto)


@icontract.require(lambda template_lookup_key: template_lookup_key)
def get_template(template_lookup_key: str) -> str:
    """
    Return template as string.
    """
    with open(config.get_template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    return template


@icontract.require(lambda lookup_key: lookup_key)
def get_html_format_string(lookup_key: str) -> model.HtmlContent:
    """
    Return the HTML string associated with its lookup_key. This allows
    changes to the HTML output without having to spelunk into code.
    """
    html_format_strings: Dict[str, str] = {
        "language": "<h1>Language: {}</h1>",
        "resource_type_name": "<h2>{}</h2>",
        "resource_type_name_with_ref": "<h3>{} {}:{}</h3>",
        "tn_resource_type_name_with_id_and_ref": '<h3 id="{}-{}-tn-ch-{}-v-{}">{} {}:{}</h3>',
        "book": "<h2>Book: {}</h2>",
        "book_as_grouper": "<h1>Book: {}</h1>",
        "verse": "<h3>Verse {}:{}</h3>",
        "translation_note": "<h3>Translation note {}:{}</h3>",
        # Example: <h2 class="c-num" id="en-042-ch-001">Chapter 1</h2>
        # FIXME Should rename key since it is used in more cases than
        # just TN
        "tn_only_chapter_header": '<h2 class="c-num" id="{}-{}-ch-{}">Chapter {}</h2>',
        "translation_question": "<h3>Translation question {}:{}</h3>",
        "translation_academy": "<h3>Translation academy {}:{}</h3>",
        "unordered_list_begin": "<ul>",
        "unordered_list_end": "</ul>",
        "translation_word_list_item": '<li><a href="#{}-{}">{}</a></li>',
        "translation_words": "<h3>Translation words {}:{}</h3>",
        "translation_words_section": "<h2>Translation words</h2>",
        "translation_word_verse_section_header": "<h4>Uses:</h4>",
        "translation_word_verse_ref_item": '<li><a href="#{}-{}-ch-{}-v-{}">{} {}:{}</a></li>',
        "footnotes": "<h3>Footnotes</h3>",
    }
    return model.HtmlContent(html_format_strings[lookup_key])


def asset_caching_enabled() -> bool:
    """
    Return boolean indicating if caching of generated document's
    should be cached. The default is to not cache, but can be enabled
    by setting the environment variable ENABLE_ASSET_CACHING=1 in
    the shell (Docker or otherwise) environment where Python is
    executing.
    """
    if int(os.environ.get("ENABLE_ASSET_CACHING", "0")) == 1:
        return True
    else:
        return False


def get_logo_image_path() -> str:
    """
    Get the path to the logo image that will be used on the PDF cover,
    i.e., first, page.
    """
    return os.path.join(get_working_dir(), "icon-tn.png")


def get_default_assembly_substrategy() -> model.AssemblySubstrategyEnum:
    """
    It doesn't yet make sense to offer the (high level)
    assembly strategy _and_ the assembly sub-strategy to the end user
    as a document request parameter so we'll just choose an arbitrary
    sub-strategy here. This means that we can write code for multiple
    sub-strategies and choose one to put in play at a time here.
    """
    return model.AssemblySubstrategyEnum.VERSE


def get_markdown_sections_to_remove() -> List[str]:
    """
    Return a list of the Markdown section titles that our
    Python-Markdown remove_section_processor extension should remove.
    """
    return ["Bible References", "Examples from the Bible stories", "Links"]


def get_from_email_address() -> str:
    """
    Return the from email to use for sending email with generated PDF
    attachment to document request recipient. Look for the value to
    use in FROM_EMAIL environment variable, use default if it doesn't
    exist.
    """
    return os.environ.get("FROM_EMAIL", "no email provided")


def get_to_email_address() -> str:
    """
    Return the to email address to use for sending email with
    generated PDF attachment to document request recipient during
    testing. Look for the value to use in TO_EMAIL environment
    variable, use default if it doesn't exist.
    """
    return os.environ.get("TO_EMAIL", "no email provided")


def get_sendgrid_api_key() -> str:
    """
    Return the sendgrid.com API key to use for sending emails.
    """
    return os.environ.get("SENDGRID_API_KEY", "no api key provided")


def should_send_email() -> bool:
    """
    Return boolean representing if the system should execute the
    action of sending an email when appropriate to do so.
    """
    # FIXME Later, add this env var to .env file so that email in Docker runs
    # is configurable. Left out of .env on purpose for now since if
    # someone accidentally turns this on it will quickly send nearly
    # 100 emails if all tests are run.
    if int(os.environ.get("SEND_EMAIL", "0")) == 1:
        return True
    else:
        return False
