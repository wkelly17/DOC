"""
This module provides various file utilities.
"""

import codecs
import json
import os
import pathlib
import zipfile
from typing import Any, Dict, List, Optional

import icontract
import yaml


@icontract.require(lambda source_file, destination_dir: source_file and destination_dir)
def unzip(source_file: str, destination_dir: str) -> None:
    """
    Unzips <source_file> into <destination_dir>.

    :param str|unicode source_file: The name of the file to read
    :param str|unicode destination_dir: The name of the directory to write the unzipped files
    """
    with zipfile.ZipFile(source_file) as zf:
        zf.extractall(destination_dir)


@icontract.require(lambda dir_name: dir_name)
@icontract.snapshot(lambda dir_name: dir_name)
@icontract.ensure(lambda OLD: os.path.exists(OLD.dir_name))
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


@icontract.require(
    lambda file_name: file_name is not None and os.path.exists(file_name)
)
def load_json_object(file_name: pathlib.Path) -> List:
    """
    Deserialized JSON file <file_name> into a Python dict.
    :param file_name: The name of the file to read
    """
    return json.loads(read_file(str(file_name.resolve())))


@icontract.require(
    lambda file_name: file_name is not None and os.path.exists(file_name)
)
def load_yaml_object(file_name: str) -> Dict:
    """
    Deserialized YAML file <file_name> into a Python dict.
    :param file_name: The name of the file to read
    """
    return yaml.safe_load(read_file(file_name))


# KEEP
@icontract.require(lambda file_name: os.path.exists(file_name))
def read_file(file_name: str, encoding: str = "utf-8-sig") -> str:
    r"""Read file into content. Change line endings from \r\n to \n."""
    with codecs.open(file_name, "r", encoding=encoding) as fin:
        content = fin.read()
    # convert Windows line endings to Linux line endings
    return content.replace("\r\n", "\n")


@icontract.require(
    lambda file_name, file_contents: file_name and file_contents is not None
)
def write_file(
    file_name: str, file_contents: Any, indent: Optional[int] = None
) -> None:
    """
    Writes the <file_contents> to <file_name>.

    If <file_contents> is not a string, it is serialized as JSON.

    :param file_name: The name of the file to write
    :param file_contents: The string to write or the object to serialize
    :param indent: Specify a value if you want the output formatted to be more easily readable
    """
    # make sure the directory exists
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


# NOTE Might want this later
# def remove(file_path, ignore_errors=True):
#     if ignore_errors:
#         try:
#             os.remove(file_path)
#         except OSError:
#             pass
#     else:
#         os.remove(file_path)
