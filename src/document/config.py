"""This module provides configuration values used by the application."""


import jinja2
import logging
import os
import pydantic
from logging import config as lc
from typing import List

import yaml

from document import config
from document.domain import model

# FIXME Use pydantic Settings and types

GIT = "git"
USFM = "usfm"
ZIP = "zip"
YAML = "yaml"
JSON = "json"
TXT = "txt"
YAML_SUFFIX = ".yaml"
TXT_SUFFIX = ".txt"
JSON_SUFFIX = ".json"
REPO_URL_DICT_KEY = "../download-scripture?repo_url"
RESOURCE_TYPES_JSONPATH = "$[*].contents[*].code"
RESOURCE_CODES_JSONPATH = "$[*].contents[*].subcontents[*].code"


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
    resource URL, e.g., tn, tq, ta, obs, ulb, udb, etc., may normally
    be found.
    """
    return "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url"


def get_resource_lang_name_jsonpath() -> str:
    """
    The language's name.
    """
    return "$[?code='{}'].name"


def get_resource_url_level2_jsonpath() -> str:
    """
    The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource URL, e.g., tn, tq, ta, obs, ulb, udb, etc., may
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


# def get_markdown_resource_types() -> List[str]:
#     """ Get the resource types that can have a Markdown file. """
#     return ["tn", "tq", "tw", "ta", "tn-wa", "tq-wa", "tw-wa", "ta-wa"]


# FIXME Fix literal paths now that directory organization has changed
def get_tex_format_location() -> str:
    """
    Return the location of where the format.tex file is located
    that is used in converting the HTML to PDF using pandoc.
    """
    filepath = ""
    if os.getenv("IN_CONTAINER"):
        filepath = os.environ.get("TEX_FORMAT_FILEPATH", "tex/format.tex")
    else:
        filepath = "tex/format.tex"
    return filepath


# FIXME Fix literal paths now that directory organization has changed
def get_tex_template_location() -> str:
    """
    Return the location of where the template.tex file is located
    that is used in converting the HTML to PDF using pandoc.
    """
    filepath = ""
    if os.getenv("IN_CONTAINER"):
        filepath = os.environ.get("TEX_TEMPLATE_FILEPATH", "tex/template.tex")
    else:
        filepath = "tex/template.tex"
    return filepath


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


# Generate PDF from HTML
PANDOC_COMMAND = """pandoc \
--verbose \
--pdf-engine="xelatex" \
--template={8} \
--toc \
--toc-depth=2 \
-V documentclass="scrartcl" \
-V classoption="oneside" \
-V geometry='hmargin=2cm' \
-V geometry='vmargin=3cm' \
-V title="{0}" \
-V subtitle="Translation Notes" \
-V logo="{4}/icon-tn.png" \
-V date="{1}" \
-V revision_date="{6}" \
-V version="{2}" \
-V mainfont="Raleway" \
-V sansfont="Raleway" \
-V fontsize="13pt" \
-V urlcolor="Bittersweet" \
-V linkcolor="Bittersweet" \
-H {7} \
-o "{3}/{5}.pdf" \
"{3}/{5}.html"
"""

# Generate just LaTeX output so that we can debug LaTeX issues.
PANDOC_COMMAND2 = """pandoc -f html -t latex \
--verbose \
--template={8} \
--toc \
--toc-depth=2 \
-V documentclass="scrartcl" \
-V classoption="oneside" \
-V geometry='hmargin=2cm' \
-V geometry='vmargin=3cm' \
-V title="{0}" \
-V subtitle="Translation Notes" \
-V logo="{4}/icon-tn.png" \
-V date="{1}" \
-V revision_date="{6}" \
-V version="{2}" \
-V mainfont="Raleway" \
-V sansfont="Raleway" \
-V fontsize="13pt" \
-V urlcolor="Bittersweet" \
-V linkcolor="Bittersweet" \
-H {7} \
-o "{3}/{5}.latex" \
"{3}/{5}.html"
"""


# FIXME There is some issue with the HTML to LaTeX generation or from
# the LaTeX to PDF generation. It may be wise to tell pandoc to
# generate LaTeX from HTML also so that we can debug the LaTeX.
def get_pandoc_command() -> str:
    """Return the pandoc command format string."""
    # return PANDOC_COMMAND2
    return PANDOC_COMMAND


def get_english_repos_dict() -> dict:
    """
    This is a hack to compensate for translations.json which only
    provides URLs for PDF assets in the English language. We need USFM
    and Markdown.
    """
    return {
        "ulb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_ulb",
        "udb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_udb",
        "tn-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn",
        "tw-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tw",
        "tq-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tq",
    }


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
    }
    path = templates[key]
    # if not os.environ.get("IN_CONTAINER"):
    #     path = "src/{}".format(path)
    return path


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


def get_template(template_lookup_key: str) -> str:
    """
    Return template as string.
    """
    with open(config.get_template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    return template


def get_pdf_generation_method() -> str:
    """
    Return the current method of PDF generation. This is used by
    document_generator module to decide which method to call to
    generate the PDF.
    """
    return model.PdfGenerationMethodEnum.WEBKIT


def get_html_format_string(lookup_key: str) -> str:
    """
    Return the HTML string associated with its lookup_key. This allows
    changes to the HTML output without having to spelunk into code.
    """
    html_format_strings: dict = {
        "language": "<h1>Language: {}</h1>",
        "book": "<h2>Book: {}</h2>",
        "verse": "<h3>Verse {}:{}</h3>",
        "translation_note": "<h3>Translation note {}:{}</h3>",
        # Example: <h2 class="c-num" id="042-ch-001">Chapter 1</h2>
        "tn_only_chapter_header": '<h2 class="c-num" id="{}-ch-{}">Chapter {}</h2>',
    }
    return html_format_strings[lookup_key]
def get_logo_image_path() -> str:
    """
    Get the path to the logo image that will be used on the PDF cover,
    i.e., first, page.
    """
    return os.path.join(get_working_dir(), "icon-tn.png")
