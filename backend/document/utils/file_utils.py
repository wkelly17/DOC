"""This module provides various file utilities."""

from contextlib import closing
import codecs
import json
import os
import pathlib
import urllib
import zipfile
import shutil
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from urllib.request import urlopen

import yaml
from document.config import settings

logger = settings.logger(__name__)


def delete_tree(dir: str) -> None:
    try:
        shutil.rmtree(dir)
    except OSError:
        logger.debug(
            "Directory %s was not removed due to an error.",
            dir,
        )
        logger.exception("Caught exception: ")


def download_file(
    url: str, outfile: str, user_agent: str = settings.USER_AGENT
) -> None:
    """Downloads a file from url and saves it to outfile."""
    # Host requires at least the User-Agent header.
    headers: dict[str, str] = {"User-Agent": user_agent}
    req = urllib.request.Request(url, None, headers)
    with closing(urlopen(req)) as request:
        with open(outfile, "wb") as fp:
            shutil.copyfileobj(request, fp)


def unzip(source_file: str, destination_dir: str) -> None:
    """
    Unzips <source_file> into <destination_dir>.

    :param str source_file: The path of the file to read
    :param str destination_dir: The path of the directory to write the unzipped files
    """
    with zipfile.ZipFile(source_file) as zf:
        zf.extractall(destination_dir)


def make_dir(
    dir_name: str, linux_mode: int = 0o755, error_if_not_writable: bool = False
) -> None:
    """
    Creates a directory, if it doesn't exist already.

    If the directory does exist, and <error_if_not_writable> is True,
    the directory will be checked for write-ability.

    :param dir_name: The name of the directory to create
    :param linux_mode: The mode/permissions to set for the new directory expressed as an octal integer (ex. 0o755)
    :param error_if_not_writable: Boolean saying whether to raise an exception if the file is not writable.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, linux_mode)
    elif error_if_not_writable:
        if not os.access(dir_name, os.R_OK | os.W_OK | os.X_OK):
            raise IOError("Directory {0} is not writable.".format(dir_name))


def load_json_object(file_name: pathlib.Path) -> Any:
    """
    Deserialized JSON file <file_name> into a Python dict.
    :param file_name: The path of the file to read
    """
    return json.loads(read_file(str(file_name.resolve())))


def read_file(file_name: str, encoding: str = "utf-8") -> str:
    r"""
    Read file into content and return content. If file doesn't exist
    return an empty string. Change line endings from \r\n to \n.
    """
    content = ""
    with codecs.open(file_name, "r", encoding=encoding) as fin:
        content = fin.read()
        # convert Windows line endings to Linux line endings
        content.replace("\r\n", "\n")
    return content


def write_file(
    file_name: str, file_contents: Any, indent: Optional[int] = None
) -> None:
    """
    Writes the <file_contents> to <file_name>.

    If <file_contents> is not a string, it is serialized as JSON.

    :param file_name: The path of the file to write
    :param file_contents: The string to write or the object to serialize
    :param indent: Specify a value if you want the output formatted to be more easily readable
    """
    # Make sure the directory exists
    make_dir(os.path.dirname(file_name))

    if isinstance(file_contents, str):
        text_to_write = file_contents
    else:
        if os.path.splitext(file_name)[1] == ".yaml":
            text_to_write = yaml.safe_dump(file_contents)
        else:
            text_to_write = json.dumps(file_contents, sort_keys=True, indent=indent)

    with codecs.open(file_name, "w", encoding="utf-8") as out_file:
        out_file.write(text_to_write)


def source_file_needs_update(file_path: Union[str, pathlib.Path]) -> bool:
    """See docstring in __file_needs_update."""
    return __file_needs_update(file_path)


def asset_file_needs_update(file_path: Union[str, pathlib.Path]) -> bool:
    """See docstring in __file_needs_update."""
    if not settings.ASSET_CACHING_ENABLED:
        return True
    return __file_needs_update(file_path)


def __file_needs_update(file_path: Union[str, pathlib.Path]) -> bool:
    """
    Return True if settings.ASSET_CACHING_ENABLED is False or if
    file_path either does not exist or does exist and has not been
    updated within settings.ASSET_CACHING_PERIOD hours.
    """
    if not os.path.exists(file_path):
        logger.debug("Cache miss for %s", file_path)
        return True
    file_mod_time: datetime = datetime.fromtimestamp(os.stat(file_path).st_mtime)
    now: datetime = datetime.today()
    max_delay: timedelta = timedelta(minutes=60 * settings.ASSET_CACHING_PERIOD)
    # Has it been more than settings.ASSET_CACHING_PERIOD hours since last modification time?
    return now - file_mod_time > max_delay
