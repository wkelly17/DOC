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
import os
import pprint
import yaml
import logging
import logging.config
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
def resource_has_markdown_files(resource: Dict) -> bool:
    """ Return True if the resource has files in Markdown format. """
    logger.debug("resource['resource_type']: {}".format(resource["resource_type"]))
    return resource["resource_type"] in get_markdown_resource_types()


def prepare_resource_directory(resource: Dict) -> None:
    """ If it doesn't exist yet, create the directory for the
    resource where it will be downloaded to. """

    logger.debug("os.getcwd(): {}".format(os.getcwd()))
    if not os.path.exists(resource["resource_dir"]):
        logger.debug("About to create directory {}".format(resource["resource_dir"]))
        try:
            os.mkdir(resource["resource_dir"])
            logger.debug("Created directory {}".format(resource["resource_dir"]))
        except:
            logger.exception(
                "Failed to create directory {}".format(resource["resource_dir"])
            )
            # raise  # reraise the error


def resource_file_format(url: str, resource: Dict) -> None:
    """ Determine the type of file being acquired. If a type is
    not apparent then we are update resource as pointing to a git
    repo. """

    filename: Optional[str] = url.rpartition(os.path.sep)[2]
    logger.debug("filename: {}".format(filename))
    if filename:
        resource.update({"resource_filename": pathlib.Path(filename).stem})
        logger.debug(
            "resource['resource_filename']: {}".format(resource["resource_filename"])
        )
        suffix: Optional[str] = pathlib.Path(filename).suffix
        if suffix:
            resource.update({"resource_file_format": suffix.lower().split(".")[1]})
        else:
            resource.update({"resource_file_format": "git"})
    else:
        resource.update({"resource_file_format": "git"})
        # Git repo has an extra layer of depth directory
        resource.update(
            {"resource_dir": os.path.join(resource["resource_dir"], filename)}
        )
    logger.debug("resource_file_format: {}".format(resource["resource_file_format"]))


def acquire_resource(url: str, resource: Dict) -> None:
    """ Download or git clone resource and unzip resulting file if it
    is a zip file. """

    logger.debug("url: {}".format(url))

    # TODO To ensure consistent directory naming for later
    # discovery, let's not use the url.rpartition(os.path.sep)[2].
    # Instead let's use a directory built from the parameters of
    # the (updated) resource:
    # os.path.join(resource["resource_dir"], resource["resource_type"])
    logger.debug(
        "os.path.join(resource['resource_dir'], resource['resource_type']): {}".format(
            os.path.join(resource["resource_dir"], resource["resource_type"])
        )
    )
    filepath = os.path.join(resource["resource_dir"], url.rpartition(os.path.sep)[2])
    resource.update({"resource_filepath": filepath})
    logger.debug("Using file location: {}".format(resource["resource_filepath"]))

    if resource["resource_file_format"] == "git":
        try:
            # os.chdir(resource["resource_dir"])
            # os.chdir(filepath)
            command: str = "git clone --depth=1 '{}' '{}'".format(url, filepath)
            logger.debug("os.getcwd(): {}".format(os.getcwd()))
            logger.debug("git command: {}".format(command))
            subprocess.call(command, shell=True)
            logger.debug("git clone succeeded.")
            # Git repos get stored on directory deeper
            resource.update({"resource_dir": filepath})
        except:
            logger.debug("os.getcwd(): {}".format(os.getcwd()))
            logger.debug("git command: {}".format(command))
            logger.debug("git clone failed!")
    else:
        try:
            logger.debug(
                "Downloading {} into {}".format(url, resource["resource_filepath"])
            )
            download_file(url, filepath)
        finally:
            logger.debug("downloading finished.")

    if resource["resource_file_format"] == "zip":
        try:
            logger.debug(
                "Unzipping {} into {}".format(filepath, resource["resource_dir"])
            )
            unzip(filepath, resource["resource_dir"])
        finally:
            logger.debug("unzipping finished.")


def files_from_url(url: str, resource: Dict) -> None:
    """ Download and unzip the zip file (if the file is a zipped
    resource) pointed to by url to a directory located at
    resource['resource_dir']. """

    prepare_resource_directory(resource)
    resource_file_format(url, resource)
    acquire_resource(url, resource)
