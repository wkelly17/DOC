import os
import pathlib
import re

import bs4
import pytest
import requests
from fastapi.testclient import TestClient

from document.config import settings
from document.entrypoints.app import app

##################################################
## Tests for assembly strategy book -hen-language


def check_finished_document_with_verses_success(
    response: requests.Response, finished_document_path: str
) -> None:
    """
    Helper to keep tests DRY.

    Check that the finished_document_path exists and also check that
    the HTML file associated with it exists and includes verses_html.
    """
    finished_document_path = os.path.join(settings.output_dir(), finished_document_path)
    assert os.path.isfile(finished_document_path)
    html_file = "{}.html".format(finished_document_path.split(".")[0])
    assert os.path.isfile(html_file)
    assert response.json() == {
        "finished_document_request_key": pathlib.Path(finished_document_path).stem,
        "message": settings.SUCCESS_MESSAGE,
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


def check_finished_document_with_body_success(
    response: requests.Response, finished_document_path: str
) -> None:
    """
    Helper to keep tests DRY.

    Check that the finished_document_path exists and also check that
    the HTML file associated with it exists and includes body.
    """
    finished_document_path = os.path.join(settings.output_dir(), finished_document_path)
    assert os.path.isfile(finished_document_path)
    html_file = "{}.html".format(finished_document_path.split(".")[0])
    assert os.path.isfile(html_file)
    assert response.json() == {
        "finished_document_request_key": pathlib.Path(finished_document_path).stem,
        "message": settings.SUCCESS_MESSAGE,
    }
    with open(html_file, "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
    assert response.ok


def check_finished_document_without_verses_success(
    response: requests.Response, finished_document_path: str
) -> None:
    """
    Helper to keep tests DRY.

    Check that the finished_document_path exists and also check that
    the HTML file associated with it exists and includes body but not
    verses_html.
    """
    finished_document_path = os.path.join(settings.output_dir(), finished_document_path)
    assert os.path.exists(finished_document_path)
    html_file = "{}.html".format(finished_document_path.split(".")[0])
    assert os.path.exists(html_file)
    with open(html_file, "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        # reg is malformed and udb does not exist, thus there is
        # no html generated
        assert not verses_html
    assert response.ok


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_fr-f10-col_fr-tn-col_fr-tq-col_fr-tw-col_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_pt-br-ulb-col_pt-br-tn-col_pt-br-tq-col_pt-br-tw-col_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "pt-br-ulb-col_pt-br-tn-col_pt-br-tq-col_pt-br-tw-col_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = (
            "fr-f10-col_fr-tn-col_fr-tq-col_fr-tw-col_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_tl_ulb_col_tl_tn_col_tl_tq_col_tl_tw_col_tl_udb_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_tl-ulb-col_tl-tn-col_tl-tq-col_tl-tw-col_tl-udb-col_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_tit_en_tn_wa_tit_book_language_order() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-ulb-wa-tit_en-tn-wa-tit_book_language_order.pdf"
        finished_document_path = os.path.join(
            settings.output_dir(), finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {
            "finished_document_request_key": pathlib.Path(finished_document_path).stem,
            "message": settings.SUCCESS_MESSAGE,
        }


def test_sw_ulb_col_sw_tn_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "sw-ulb-col_sw-tn-col_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_sw-ulb-col_sw-tn-col_sw-tq-col_sw-ulb-tit_sw-tn-tit_sw-tq-tit_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-ulb-wa-col_en-tq-wa-col_sw-ulb-col_sw-tq-col_sw-ulb-tit_sw-tq-tit_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_sw-tn-col_sw-tq-col_sw-tw-col_sw-tn-tit_sw-tq-tit_sw-tw-tit_book_language_order.pdf"
        check_finished_document_with_body_success(response, finished_document_path)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-tn-wa-col_en-tw-wa-col_sw-tn-col_sw-tw-col_sw-tn-tit_sw-tw-tit_book_language_order.pdf"
        check_finished_document_with_body_success(response, finished_document_path)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "en-tq-wa-col_en-tw-wa-col_sw-tq-col_sw-tw-col_book_language_order.pdf"
        )
        check_finished_document_with_body_success(response, finished_document_path)


def test_en_tw_wa_col_sw_tw_col_sw_tw_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-tw-wa-col_sw-tw-col_book_language_order.pdf"
        check_finished_document_with_body_success(response, finished_document_path)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "en-tn-wa-col_en-tq-wa-col_sw-tn-col_sw-tq-col_book_language_order.pdf"
        )
        check_finished_document_with_body_success(response, finished_document_path)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-tq-wa-col_sw-tq-col_book_language_order.pdf"
        check_finished_document_with_body_success(response, finished_document_path)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "en-tn-wa-col_sw-tn-col_sw-tn-tit_book_language_order.pdf"
        )
        check_finished_document_with_body_success(response, finished_document_path)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "en-ulb-wa-col_sw-ulb-col_sw-ulb-tit_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "gu-ulb-mrk_gu-tn-mrk_gu-tq-mrk_gu-tw-mrk_gu-udb-mrk_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "mr-ulb-mrk_mr-tn-mrk_mr-tq-mrk_mr-tw-mrk_mr-udb-mrk_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "mr-ulb-mrk_mr-tn-mrk_mr-tq-mrk_mr-udb-mrk_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "mr-ulb-mrk_mr-tn-mrk_mr-tw-mrk_mr-udb-mrk_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "mr-ulb-mrk_mr-tn-mrk_mr-udb-mrk_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "mr-ulb-mrk_mr-tq-mrk_mr-udb-mrk_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


@pytest.mark.skip
def test_gu_ulb_mic_gu_tn_mic_gu_tq_mic_gu_tw_mic_gu_ta_mic_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "gu-ulb-mic_gu-tn-mic_gu-tq-mic_gu-tw-mic_gu-ta-mic_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_ulb_gen_tl_udb_gen_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "tl-ulb-gen_tl-udb-gen_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "gu-tn-mat_gu-tq-mat_gu-tw-mat_gu-udb-mat_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "gu-tn-mat_gu-tq-mat_gu-udb-mat_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "tl-tn-gen_tl-tw-gen_tl-udb-gen_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_tq_gen_tl_udb_gen_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "tl-tq-gen_tl-udb-gen_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_tw_gen_tl_udb_gen_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "tl-tw-gen_tl-udb-gen_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_tl_udb_gen_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        finished_document_path = "tl-udb-gen_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_book_language_order() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "fr-ulb-rev_fr-tn-rev_fr-tq-rev_fr-tw-rev_fr-udb-rev_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_book_language_order() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "fr-ulb-rev_fr-tn-rev_fr-tq-rev_fr-tw-rev_fr-f10-rev_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_book_language_order() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "fr-ulb-rev_fr-tq-rev_fr-tw-rev_fr-f10-rev_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_book_language_order() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
            "fr-ulb-rev_fr-tw-rev_fr-f10-rev_book_language_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_ndh_x_chindali_reg_mat_ndh_x_chindali_tn_mat_ndh_x_chindali_tq_mat_ndh_x_chindali_tw_mat_ndh_x_chindali_udb_mat_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "reg",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tn",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tq",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tw",
                        "resource_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "udb",
                        "resource_code": "mat",
                    },
                ],
            },
        )
        finished_document_path = "ndh-x-chindali-reg-mat_ndh-x-chindali-tn-mat_ndh-x-chindali-tq-mat_ndh-x-chindali-tw-mat_ndh-x-chindali-udb-mat_book_language_order.pdf"
        with pytest.raises(Exception):
            check_finished_document_without_verses_success(
                response, finished_document_path
            )


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
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
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_es-419-ulb-col_es-419-tn-col_es-419-tq-col_es-419-tw-col_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_es_ulb_col_es_tn_col_en_tq_col_es_tw_col_book_language_order() -> None:
    """
    Ask for a combination of available and unavailable resources.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "es",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = (
            "es-ulb-col_es-tn-col_es-tq-col_es-tw-col_book_language_order.pdf"
        )
        check_finished_document_without_verses_success(response, finished_document_path)


def test_llx_ulb_col_llx_tn_col_en_tq_col_llx_tw_col_book_language_order() -> None:
    """
    Ask for an unavailable resource and assert that the verses_html is
    not generated.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "llx",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = (
            "llx-ulb-col_llx-tn-col_llx-tq-col_llx-tw-col_book_language_order.pdf"
        )
        check_finished_document_without_verses_success(response, finished_document_path)


def test_llx_reg_col_llx_tn_col_en_tq_col_llx_tw_col_book_language_order() -> None:
    """
    Ask for an unavailable resource and assert that the verses_html is
    not generated.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "llx",
                        "resource_type": "reg",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        finished_document_path = (
            "llx-reg-col_llx-tn-col_llx-tq-col_llx-tw-col_book_language_order.pdf"
        )
        finished_document_path = os.path.join(
            settings.output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert response.ok
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            # Resource requested doesn't exist or isn't available so
            # we assert that the verses_html was not generated and
            # thus not present in the document.
            assert not verses_html


def test_es_419_ulb_col_es_419_tn_col_en_tq_col_es_419_tw_col_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
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
        finished_document_path = "es-419-ulb-col_es-419-tn-col_es-419-tq-col_es-419-tw-col_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "resource_code": "rom",
                    },
                ],
            },
        )
        finished_document_path = "es-419-ulb-rom_es-419-tn-rom_es-419-tq-rom_es-419-tw-rom_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_rom_en_tn_wa_rom_en_tq_wa_rom_en_tw_wa_rom_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "rom",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-rom_en-tn-wa-rom_en-tq-wa-rom_en-tw-wa-rom_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


# BUG See output in ~/.ghq/bitbucket.org/foobar77/timesheets/worklog3.org [[id:6F839365-1C34-4F36-B056-A91B8E5E92B5][Logs]]
# @pytest.mark.skip
def test_en_ulb_wa_rom_en_tn_wa_rom_en_tq_wa_rom_en_tw_wa_rom_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "resource_code": "rom",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-rom_en-tn-wa-rom_en-tq-wa-rom_en-tw-wa-rom_es-419-ulb-rom_es-419-tn-rom_es-419-tq-rom_es-419-tw-rom_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_jon_en_tn_wa_jon_en_tq_wa_jon_en_tw_wa_jon_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "book_language_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "jon",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "jon",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "jon",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "jon",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "resource_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "resource_code": "rom",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-jon_en-tn-wa-jon_en-tq-wa-jon_en-tw-wa-jon_es-419-ulb-rom_es-419-tn-rom_es-419-tq-rom_es-419-tw-rom_book_language_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_invalid_document_request() -> None:
    with pytest.raises(Exception):
        with TestClient(app=app, base_url=settings.api_test_url()) as client:
            response: requests.Response = client.post(
                "/documents",
                json={
                    "email_address": settings.TO_EMAIL_ADDRESS,
                    "assembly_strategy_kind": "book_language_order",
                    "resource_requests": [
                        {
                            "lang_code": "",
                            "resource_type": "xxx",
                            "resource_code": "blah",
                        },
                    ],
                },
            )
            finished_document_path = "invalid_file_that_doesnt_exist.pdf"
            check_finished_document_with_verses_success(
                response, finished_document_path
            )
