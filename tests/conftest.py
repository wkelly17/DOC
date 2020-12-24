# pylint: disable=redefined-outer-name
from pathlib import Path
import pytest
import requests
from tenacity import retry, stop_after_delay
import time

from document import config

pytest.register_assert_rewrite("tests.e2e.api_client")


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    url = config.get_api_test_url()
    return requests.get("{}/health/status".format(url))


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/document/entrypoints/app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
