#
#  Copyright (c) 2017 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wycliffeassociates.org>

"""
XFIXME This script exports tN into HTML format from DCS and generates a PDF from the HTML
"""

from typing import Any, Dict, List, Optional, Union
import logging
import logging.config
import os
import pprint
import re
import yaml
import pathlib


# Handle running in container or as standalone script
try:
    from url_utils import download_file  # type: ignore
    from file_utils import unzip  # type: ignore
    from config import get_markdown_resource_types
    from config import get_logging_config_file_path
except:
    from .url_utils import download_file  # type: ignore
    from .file_utils import unzip  # type: ignore
    from .config import get_markdown_resource_types
    from .config import get_logging_config_file_path


with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


# TODO Perhaps this should be moved to its own module since I need
# it in document_generator module and in resource_lookup module.
# Perhaps it would go in a resource_utils.py module and then if we
# later reify the resource dictionary to an actual class it would
# become an instance method on the instance.
def resource_has_markdown_files(resource) -> bool:
    """ Return True if the resource has files in Markdown format. """
    logger.debug("resource._resource_type: {}".format(resource._resource_type))
    return resource._resource_type in get_markdown_resource_types()
