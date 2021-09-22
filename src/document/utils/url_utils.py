import shutil
from contextlib import closing
from urllib.request import urlopen

from document.config import settings

logger = settings.logger(__name__)


# FIXME Improve this legacy code
def url(url: str, catch_exception: bool = False) -> str:
    """
    :param str|unicode url: URL to open
    :param bool catch_exception: If <True> catches all exceptions and returns <False>
    """
    if catch_exception:
        try:
            with closing(urlopen(url)) as request:
                response = request.read()
        except Exception:
            response = False
    else:
        with closing(urlopen(url)) as request:
            response = request.read()

    # Convert bytes to str (
    if isinstance(response, bytes):
        return response.decode("utf-8")
    return response


def download_file(url: str, outfile: str) -> None:
    """Downloads a file and saves it."""
    try:
        with closing(urlopen(url)) as request:
            with open(outfile, "wb") as fp:
                shutil.copyfileobj(request, fp)
    except IOError as err:
        logger.debug("ERROR retrieving %s", url)
        logger.debug(err)
