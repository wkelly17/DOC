import os
import re
import time
from typing import Literal, Union

import bs4
import httpx
import requests
from document.config import settings
from document.entrypoints.app import app
from fastapi.testclient import TestClient

logger = settings.logger(__name__)

AcceptedSuffixes = Union[
    Literal["html"], Literal["pdf"], Literal["epub"], Literal["docx"]
]


def check_result(
    response: httpx._models.Response,
    /,
    suffix: AcceptedSuffixes,
    poll_duration: int = 4,
    status_url_fmt_str: str = "/task_status/{}",
    success_state: str = "SUCCESS",
    failure_state: str = "FAILURE",
) -> str:
    logger.debug("response.json(): {}".format(response.json()))
    task_id = response.json()["task_id"]
    assert task_id
    logger.debug("task_id: %s", task_id)
    finished_document_request_key: str
    while True:
        with TestClient(app=app, base_url=settings.api_test_url()) as client:
            response2 = client.get(
                status_url_fmt_str.format(task_id),
            )
            json_data = response2.json()
            logger.debug("json task status data: {}".format(json_data))
            if json_data["state"] == success_state:
                finished_document_request_key = json_data["result"]
                finished_document_path = os.path.join(
                    settings.DOCUMENT_SERVE_DIR,
                    "{}.{}".format(finished_document_request_key, suffix),
                )
                logger.debug(
                    "finished_document_path: {}".format(finished_document_path)
                )
                assert os.path.exists(finished_document_path)
                assert response2.status_code == 200
                break
            elif json_data["state"] == failure_state:
                logger.info(
                    "Test failed likely due to celery task failure, check the celery flower dashboard"
                )
                raise Exception(
                    "Received celery FAILURE state therefore e2e test failed"
                )
            time.sleep(poll_duration)
    return finished_document_request_key


def check_finished_document_with_verses_success(
    response: httpx._models.Response,
    suffix: AcceptedSuffixes = "html",
    poll_duration: int = 4,
) -> None:
    """
    Helper to keep tests DRY.
    """
    finished_document_request_key = check_result(response, suffix, poll_duration)
    html_filepath = os.path.join(
        settings.DOCUMENT_SERVE_DIR,
        "{}.html".format(finished_document_request_key),
    )
    with open(html_filepath, "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body = parser.find_all("body")
        assert body
        verses_html = parser.find_all("span", attrs={"class": "v-num"})
        assert verses_html
        assert len("".join([str(verse) for verse in verses_html])) >= 300
        # Test defect that can occur in USFM file parsing of
        # non-standalone USFM files, e.g., aba, reg, tit.
        repeating_verse_num_defect = re.search(
            "<sup><b>1</b></sup></span><sup><b>1</b></sup><b>1</b>1<b>1</b>11",
            html,
        )
        assert not repeating_verse_num_defect


def check_finished_document_without_verses_success(
    response: httpx._models.Response,
    suffix: AcceptedSuffixes = "html",
    poll_duration: int = 4,
) -> None:
    """
    Helper to keep tests DRY.
    """
    finished_document_request_key = check_result(response, suffix, poll_duration)
    html_filepath = os.path.join(
        settings.DOCUMENT_SERVE_DIR,
        "{}.html".format(finished_document_request_key),
    )
    with open(html_filepath, "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body = parser.find_all("body")
        assert body
        verses_html = parser.find_all("span", attrs={"class": "v-num"})
        assert not verses_html


def check_finished_document_with_body_success(
    response: httpx._models.Response,
    suffix: AcceptedSuffixes = "html",
    poll_duration: int = 4,
) -> None:
    """
    Helper to keep tests DRY.
    """
    finished_document_request_key = check_result(response, suffix, poll_duration)
    html_filepath = os.path.join(
        settings.DOCUMENT_SERVE_DIR,
        "{}.html".format(finished_document_request_key),
    )
    with open(html_filepath, "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body = parser.find_all("body")
        assert body
