from typing import List
import os


def get_working_dir() -> str:
    """ The directory where the resources will be placed once
    acquired. IRG_WORKING_DIR is provided when running in a docker
    environment. Otherwise a suitable temporary local directory is
    generated automatically. """
    dir = os.environ.get("IRG_WORKING_DIR", "./working/temp")
    return dir


def get_output_dir() -> str:
    """ The directory where the generated documents are placed. """
    dir = os.environ.get("IRG_OUTPUT_DIR")
    return dir


def get_translations_json_location() -> str:
    """ The location where the JSON data file that we use to lookup
    location of resources is located. """
    loc = os.environ.get(
        "TRANSLATIONS_JSON_LOCATION",
        "http://bibleineverylanguage.org/wp-content/themes/bb-theme-child/data/translations.json",
    )
    return loc


def get_individual_usfm_url_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    individual USFM files (per bible book) may be found. """
    return "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='usfm'].url"


def get_resource_url_level_1_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource URL, e.g., tn, tq, ta, obs, ulb, udb, etc., may normally be found. """
    return "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url"


def get_resource_url_level_2_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource URL, e.g., tn, tq, ta, obs, ulb, udb, etc., may
    additionally/alternatively be found. """
    return "$[?code='{}'].contents[*].subcontents[?code='{}'].links[?format='zip'].url"


def get_resource_download_format_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource git repo may be found. """
    return "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='Download'].url"


def get_logging_config_file_path() -> str:
    """ The file path location where the dictConfig-style yaml
    formatted config file for logging is located. """
    if os.environ.get("IN_CONTAINER"):
        return "/tools/logging_config.yaml"
    else:
        return "logging_config.yaml"


def get_icon_url() -> str:
    """ Get the tn-icon.png from unfolding word. """
    return "https://unfoldingword.org/assets/img/icon-tn.png"
    # return "https://static1.squarespace.com/static/591e003db8a79bd6e6c9ffae/t/5e306da5898d7b14b76889dd/1600444722464/?format=1500w"


def get_markdown_resource_types() -> List[str]:
    """ Get the resource types that can have a Markdown file. """
    return ["tn", "tq", "tw", "ta", "tn-wa", "tq-wa", "tw-wa", "ta-wa"]


def get_tex_format_location() -> str:
    """ Return the location of where the format.tex file is located
    that is used in converting the HTML to PDF using pandoc. """
    return "tools/tex/format.tex" if os.getenv("IN_CONTAINER") else "./tex/format.tex"
    # return "tools/tex/format.tex"


def get_tex_template_location() -> str:
    """ Return the location of where the template.tex file is located
    that is used in converting the HTML to PDF using pandoc. """
    return (
        "tools/tex/template.tex" if os.getenv("IN_CONTAINER") else "./tex/template.tex"
    )
    # return "tools/tex/format.tex"
