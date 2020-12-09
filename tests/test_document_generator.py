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

from document import config
from document.domain import document_generator


with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


def main():
    payload = {}
    payload["resources"] = [
        # {"lang_code": "am", "resource_type": "ulb", "resource_code": ""},
        # {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
        # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "eph"},
        # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "lev"},
        # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "lev"},
        # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
        # FIXME ml, tn, tit doesn't exist, but tn for all books does
        {"lang_code": "ml", "resource_type": "tn", "resource_code": "tit"},
        # Next two:
        # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
        # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
        # {"lang_code": "as", "resource_type": "tn", "resource_code": "rev"},
        # # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
        # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
    ]

    payload["assembly_strategy"] = "book"  # verse, chapter, book

    doc_gen = document_generator.DocumentGenerator(
        payload["assembly_strategy"], payload["resources"]
    )
    doc_gen.run()


if __name__ == "__main__":
    main()
