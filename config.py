import typing
import os


def get_working_dir() -> str:
    """ The directory where the resources are downloaded to. """
    dir = os.environ.get("IRG_WORKING_DIR", "/working/tn-temp")
    return dir


def get_output_dir() -> str:
    """ The directory where the generated documents are placed. """
    dir = os.environ.get("IRG_OUTPUT_DIR", get_working_dir())
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
    return "$[?code='{}'].contents[?code='{}'].subcontents[?code={}].links[?format='Download'].url"


def get_logging_config_file_path() -> str:
    """ The file path location where the dictConfig-style yaml
    formatted config file for logging is located. """
    return "./logging_config.yaml"
