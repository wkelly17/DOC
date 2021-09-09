import shutil
from contextlib import closing
from urllib.request import urlopen

from document.config import settings

logger = settings.get_logger(__name__)


def get_url(url: str, catch_exception: bool = False) -> str:
    """
    :param str|unicode url: URL to open
    :param bool catch_exception: If <True> catches all exceptions and returns <False>
    """
    return _get_url(url, catch_exception)


# FIXME Improve this legacy code
def _get_url(url: str, catch_exception: bool) -> str:
    if catch_exception:
        # noinspection PyBroadException
        try:
            with closing(urlopen(url)) as request:
                response = request.read()
        except Exception:
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
        logger.debug("ERROR retrieving %s", url)
        logger.debug(err)
