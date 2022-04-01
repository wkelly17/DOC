import os
import pathlib
import re

import bs4
import pytest
import requests
from fastapi.testclient import TestClient

from document.config import settings
from document.domain import model
from document.entrypoints.app import app


def check_finished_document_with_verses_success(response: requests.Response) -> None:
    """
    Helper to keep tests DRY.

    Check that the finished_document_path exists and also check that
    the HTML file associated with it exists and includes verses_html.
    """
    assert response.ok
    content = response.json()
    assert "finished_document_request_key" in content
    assert "message" in content
    finished_document_path = os.path.join(
        settings.output_dir(), "{}.pdf".format(content["finished_document_request_key"])
    )
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
        body = parser.find_all("body")
        assert body
        verses_html = parser.find_all("span", attrs={"class": "v-num"})
        assert verses_html


def check_finished_document_without_verses_success(response: requests.Response) -> None:
    """
    Helper to keep tests DRY.

    Check that the finished_document_path exists and also check that
    the HTML file associated with it exists and includes verses_html.
    """
    assert response.ok
    content = response.json()
    assert "finished_document_request_key" in content
    assert "message" in content
    finished_document_path = os.path.join(
        settings.output_dir(), "{}.pdf".format(content["finished_document_request_key"])
    )
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
        body = parser.find_all("body")
        assert body
    assert response.ok


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order_2c_sl_hr() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order_2c_sl_hr_c() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order_1c() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order_1c_c() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_without_verses_success(response)


def test_en_tw_wa_col_sw_tw_col_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_without_verses_success(response)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_tl_ulb_gen_tl_udb_gen_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_ulb_gen_tl_udb_gen_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_tl_tq_gen_tl_udb_gen_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_tq_gen_tl_udb_gen_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_tq_gen_tl_udb_gen_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_tq_gen_tl_udb_gen_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_tl_tw_gen_tl_udb_gen_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_tw_gen_tl_udb_gen_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_tl_tw_gen_tl_udb_gen_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_tl_tw_gen_tl_udb_gen_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_tl_udb_gen_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_tl_udb_gen_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_language_book_order_2c_sl_hr() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_language_book_order_2c_sl_hr_c() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c_c() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_2c_sl_hr() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_2c_sl_hr_c() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c_c() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_2c_sl_hr() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_2c_sl_hr_c() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c_c() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_language_book_order_2c_sl_hr() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_language_book_order_2c_sl_hr_c() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c_c() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_reg_2co_pmm_reg_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_reg_2co_pmm_reg_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_reg_2co_pmm_reg_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_reg_2co_pmm_reg_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_x_adjtalagbe_reg_2co_pmm_reg_mrk_language_book_order_2c_sl_hr() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT,
                "layout_for_print": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg-x-adjtalagbe",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_x_adjtalagbe_reg_2co_pmm_reg_mrk_language_book_order_2c_sl_hr_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_HELPS_RIGHT_COMPACT,
                "layout_for_print": True,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg-x-adjtalagbe",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_x_adjtalagbe_reg_2co_pmm_reg_mrk_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg-x-adjtalagbe",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_kbt_reg_2co_ajg_x_adjtalagbe_reg_2co_pmm_reg_mrk_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "ajg-x-adjtalagbe",
                        "resource_type": "reg",
                        "resource_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "resource_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)
