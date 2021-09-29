import shutil
from contextlib import closing
from typing import Any, Optional
from urllib.error import URLError
from urllib.request import urlopen

from document.config import settings

logger = settings.logger(__name__)


def url(url: str) -> Any:
    """
    :param url: URL to open
    """
    try:
        with closing(urlopen(url)) as request:
            response = request.read()
            # Convert bytes to str
            if isinstance(response, bytes):
                return response.decode("utf-8")
            return response
    except URLError as err:
        logger.debug("ERROR retrieving %s", url)
        logger.debug(err)
        return None


def download_file(url: str, outfile: str) -> None:
    """Downloads a file from url and saves it to outfile."""
    try:
        with closing(urlopen(url)) as request:
            with open(outfile, "wb") as fp:
                shutil.copyfileobj(request, fp)
    except IOError as err:
        logger.debug("ERROR retrieving %s", url)
        logger.debug(err)
