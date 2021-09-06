import os
import pathlib
import re

import bs4
import pytest
import requests
from document import config
from document.entrypoints.app import app
from fastapi.testclient import TestClient


def check_finished_document_with_verses_success(
    response: requests.Response, finished_document_path: str
) -> None:
    """
    Helper to keep tests DRY.

    Check that the finished_document_path exists and also check that
    the HTML file associated with it exists and includes verses_html.
    """
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert os.path.isfile(finished_document_path)
    html_file = "{}.html".format(finished_document_path.split(".")[0])
    assert os.path.isfile(html_file)
    assert response.json() == {
        "finished_document_request_key": pathlib.Path(finished_document_path).stem
    }
    with open(html_file, "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        assert verses_html
    assert response.ok


def check_finished_document_without_verses_success(
    response: requests.Response, finished_document_path: str
) -> None:
    """
    Helper to keep tests DRY.

    Check that the finished_document_path exists and also check that
    the HTML file associated with it exists and includes verses_html.
    """
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert os.path.isfile(finished_document_path)
    html_file = "{}.html".format(finished_document_path.split(".")[0])
    assert os.path.isfile(html_file)
    assert response.json() == {
        "finished_document_request_key": pathlib.Path(finished_document_path).stem
    }
    with open(html_file, "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
    assert response.ok


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-tit_en-tn-wa-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_sw_ulb_col_sw_tn_col_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "sw-ulb-col_sw-tn-col_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = (
            "sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_sw-ulb-col_sw-tn-col_sw-tq-col_sw-ulb-tit_sw-tn-tit_sw-tq-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tq-wa-col_sw-ulb-col_sw-tq-col_sw-ulb-tit_sw-tq-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_sw-tn-col_sw-tq-col_sw-tw-col_sw-tn-tit_sw-tq-tit_sw-tw-tit_language_book_order.pdf"
        check_finished_document_without_verses_success(response, finished_document_path)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-tn-wa-col_en-tw-wa-col_sw-tn-col_sw-tw-col_sw-tn-tit_sw-tw-tit_language_book_order.pdf"
        check_finished_document_without_verses_success(response, finished_document_path)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = (
            "en-tq-wa-col_en-tw-wa-col_sw-tq-col_sw-tw-col_language_book_order.pdf"
        )
        check_finished_document_without_verses_success(response, finished_document_path)


def test_en_tw_wa_col_sw_tw_col_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "en-tw-wa-col_sw-tw-col_language_book_order.pdf"
        check_finished_document_without_verses_success(response, finished_document_path)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = (
            "en-tn-wa-col_en-tq-wa-col_sw-tn-col_sw-tq-col_language_book_order.pdf"
        )
        check_finished_document_without_verses_success(response, finished_document_path)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "en-tq-wa-col_sw-tq-col_language_book_order.pdf"
        check_finished_document_without_verses_success(response, finished_document_path)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = (
            "en-tn-wa-col_sw-tn-col_sw-tn-tit_language_book_order.pdf"
        )
        check_finished_document_without_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = (
            "en-ulb-wa-col_sw-ulb-col_sw-ulb-tit_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "ulb",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tw",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        finished_document_path = "gu-ulb-mrk_gu-tn-mrk_gu-tq-mrk_gu-tw-mrk_gu-udb-mrk_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tw",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        finished_document_path = "mr-ulb-mrk_mr-tn-mrk_mr-tq-mrk_mr-tw-mrk_mr-udb-mrk_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        finished_document_path = (
            "mr-ulb-mrk_mr-tn-mrk_mr-tq-mrk_mr-udb-mrk_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tw",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        finished_document_path = (
            "mr-ulb-mrk_mr-tn-mrk_mr-tw-mrk_mr-udb-mrk_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        finished_document_path = (
            "mr-ulb-mrk_mr-tn-mrk_mr-udb-mrk_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "resource_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        finished_document_path = (
            "mr-ulb-mrk_mr-tq-mrk_mr-udb-mrk_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


@pytest.mark.skip
def test_gu_ulb_mic_gu_tn_mic_gu_tq_mic_gu_tw_mic_gu_ta_mic_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "ulb",
                        "resource_code": "mic",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "resource_code": "mic",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "resource_code": "mic",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tw",
                        "resource_code": "mic",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "ta",
                        "resource_code": "mic",
                    },
                ],
            },
        )
        finished_document_path = (
            "gu-ulb-mic_gu-tn-mic_gu-tq-mic_gu-tw-mic_gu-ta-mic_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_ulb_gen_tl_udb_gen_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "resource_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        finished_document_path = "tl-ulb-gen_tl-udb-gen_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tw",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "resource_code": "mat",
                    },
                ],
            },
        )
        finished_document_path = (
            "gu-tn-mat_gu-tq-mat_gu-tw-mat_gu-udb-mat_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "resource_code": "mat",
                    },
                ],
            },
        )
        finished_document_path = (
            "gu-tn-mat_gu-tq-mat_gu-udb-mat_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "resource_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "resource_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        finished_document_path = (
            "tl-tn-gen_tl-tw-gen_tl-udb-gen_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_tq_gen_tl_udb_gen_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "resource_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        finished_document_path = "tl-tq-gen_tl-udb-gen_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_tw_gen_tl_udb_gen_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "resource_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        finished_document_path = "tl-tw-gen_tl-udb-gen_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_udb_gen_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        finished_document_path = "tl-udb-gen_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_language_book_order() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "udb",
                        "resource_code": "rev",
                    },
                ],
            },
        )
        finished_document_path = "fr-ulb-rev_fr-tn-rev_fr-tq-rev_fr-tw-rev_fr-udb-rev_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "resource_code": "rev",
                    },
                ],
            },
        )
        finished_document_path = "fr-ulb-rev_fr-tn-rev_fr-tq-rev_fr-tw-rev_fr-f10-rev_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "resource_code": "rev",
                    },
                ],
            },
        )
        finished_document_path = (
            "fr-ulb-rev_fr-tq-rev_fr-tw-rev_fr-f10-rev_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_language_book_order() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "resource_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "resource_code": "rev",
                    },
                ],
            },
        )
        finished_document_path = (
            "fr-ulb-rev_fr-tw-rev_fr-f10-rev_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_es-419-ulb-col_es-419-tn-col_es-419-tq-col_es-419-tw-col_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)
