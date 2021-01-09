import json
import shutil
import sys
from contextlib import closing
from typing import List
from urllib.request import urlopen

from document import config

logger = config.get_logger(__name__)


def get_url(url: str, catch_exception: bool = False) -> str:
    """
    :param str|unicode url: URL to open
    :param bool catch_exception: If <True> catches all exceptions and returns <False>
    """
    return _get_url(url, catch_exception)


def _get_url(url: str, catch_exception: bool) -> str:
    if catch_exception:
        # noinspection PyBroadException
        try:
            with closing(urlopen(url)) as request:
                response = request.read()
        except:
            response = False
    else:
        with closing(urlopen(url)) as request:
            response = request.read()

    # convert bytes to str (Python 3.5)
    # if type(response) is bytes:
    if isinstance(response, bytes):
        return response.decode("utf-8")
    return response


def download_file(url: str, outfile: str) -> None:
    """Downloads a file and saves it."""
    _download_file(url, outfile)


def _download_file(url: str, outfile: str) -> None:
    try:
        with closing(urlopen(url)) as request:
            with open(outfile, "wb") as fp:
                shutil.copyfileobj(request, fp)
    except IOError as err:
        logger.debug("ERROR retrieving {}".format(url))
        logger.debug(err)
        sys.exit(1)


def get_languages() -> List:
    """
    Returns an array of over 7000 dictionaries.

    Structure:
    [
      {
        cc: ["DJ", "US", "CA"],
        pk: 2,
        lr: "Africa",
        ln: "Afaraf",
        ang: "Afar",
        gw: false,
        ld: "ltr",
        alt: ["Afaraf", "Danakil"],
        lc: aa
      },
      ...
    ]
    """
    url = "http://td.unfoldingword.org/exports/langnames.json"
    return json.loads(get_url(url))


# NOTE Currently unused.
def join_url_parts(args: List[str]) -> str:
    """
    Joins a list of segments into a URL-like string.

    :type args: List<string>
    """
    # check for edge case
    if len(args) == 1:
        return args[0]

    return_val = clean_url_segment(args[0])

    for i in range(1, len(args)):
        arg = args[i]

        if i == len(args) - 1:
            # no need to remove a trailing slash if this is the last segment
            return_val = "{}/{}".format(return_val, arg)
        else:
            # remove a trailing slash so it won't be duplicated
            return_val = "{}/{}".format(return_val, clean_url_segment(arg))

    return return_val


# NOTE Currently unused.
def clean_url_segment(segment: str) -> str:
    """Remove trailing slash if it exists."""
    if segment[-1:] == "/":
        return segment[:-1]

    return segment
