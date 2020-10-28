from typing import Any, Dict, List, Optional, Union
import os
import sys
import re
import pprint
import logging
import argparse
import tempfile
import shutil
import datetime
import subprocess
import csv
from glob import glob
import yaml
import pathlib


import markdown  # type: ignore

import bs4  # type: ignore
from usfm_tools.transform import UsfmTransform  # type: ignore

# Handle running in container or as standalone script
try:
    from file_utils import write_file, read_file, unzip, load_yaml_object  # type: ignore
    from url_utils import download_file  # type: ignore
    from bible_books import BOOK_NUMBERS  # type: ignore
    from resource_lookup import ResourceJsonLookup
    from config import (
        get_working_dir,
        get_output_dir,
        get_logging_config_file_path,
    )
    from document_generator import DocumentGenerator
except:
    from .file_utils import write_file, read_file, unzip, load_yaml_object  # type: ignore
    from .url_utils import download_file  # type: ignore
    from .bible_books import BOOK_NUMBERS  # type: ignore
    from .resource_lookup import ResourceJsonLookup
    from .config import (
        get_working_dir,
        get_output_dir,
        get_logging_config_file_path,
    )
    from .document_generator import DocumentGenerator


with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def main():
    payload = {}
    payload["resources"] = [
        # {"lang_code": "am", "resource_type": "ulb", "resource_code": ""},
        # {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
        # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "eph"},
        # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "lev"},
        # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "lev"},
        {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
        # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
        # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
        # {"lang_code": "ml", "resource_type": "tn", "resource_code": "tit"},
        {"lang_code": "as", "resource_type": "tn", "resource_code": "rev"},
        # # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
        # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
    ]

    document_generator = DocumentGenerator(payload["resources"])
    document_generator.run()


if __name__ == "__main__":
    main()
