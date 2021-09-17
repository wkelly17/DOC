"""This module provides tests for the application's FastAPI API."""

import os
import pathlib

import bs4
import pytest
import requests
from fastapi.testclient import TestClient

from document.config import settings
from document.entrypoints.app import app


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


##########################################################################
## Specific targeted tests (wrt language, resource type, resource code) ##
##########################################################################


def test_en_ulb_wa_col_en_tn_wa_col_language_book_order_with_no_email() -> None:
    """
    Produce verse interleaved document for English scripture and
    translation notes for the book of Colossians.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                # "email_address": settings.TO_EMAIL_ADDRESS,
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
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_language_book_order() -> None:
    """
    Produce verse level interleaved document for English scripture,
    translation notes, and translation questions for the book of Col.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
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
                ],
            },
        )
        finished_document_path = (
            "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_tn_wa_jud_language_book_order() -> None:
    """
    Produce verse level interleaved document for English scripture and
    translation notes for the book of Jude.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "jud",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "jud",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-jud_en-tn-wa-jud_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_ar_nav_jud_language_book_order() -> None:
    """
    Produce verse level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "ar",
                        "resource_type": "nav",
                        "resource_code": "jud",
                    },
                ],
            },
        )
        finished_document_path = "ar-nav-jud_language_book_order.pdf"
        with pytest.raises(Exception):
            check_finished_document_with_verses_success(
                response, finished_document_path
            )


def test_pt_br_ulb_tn_language_book_order() -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "resource_code": "gen",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "resource_code": "gen",
                    },
                ],
            },
        )
        finished_document_path = "pt-br-ulb-gen_pt-br-tn-gen_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_pt_br_ulb_tn_en_ulb_wa_tn_wa_luk_language_book_order() -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese
    and English scripture and translation notes for the book of Luke.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "resource_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "resource_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "luk",
                    },
                ],
            },
        )
        finished_document_path = "pt-br-ulb-luk_pt-br-tn-luk_en-ulb-wa-luk_en-tn-wa-luk_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_pt_br_ulb_tn_luk_en_ulb_wa_tn_wa_luk_sw_ulb_tn_col_language_book_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "resource_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "resource_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "luk",
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
                ],
            },
        )
        finished_document_path = "pt-br-ulb-luk_pt-br-tn-luk_en-ulb-wa-luk_en-tn-wa-luk_sw-ulb-col_sw-tn-col_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
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
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_sw-ulb-col_sw-tn-col_sw-tq-col_sw-tw-col_sw-tn-tit_sw-tq-tit_sw-tw-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tn_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
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
                        "resource_type": "tw-wa",
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
                        "resource_type": "tw",
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
                        "resource_type": "tw",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tw-wa-col_sw-ulb-col_sw-tn-col_sw-tw-col_sw-ulb-tit_sw-tn-tit_sw-tw-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tw_wa_col_sw_ulb_col_sw_tw_col_sw_ulb_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
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
        finished_document_path = "en-ulb-wa-col_en-tw-wa-col_sw-ulb-col_sw-tw-col_sw-ulb-tit_sw-tw-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
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
                        "lang_code": "en",
                        "resource_type": "tw-wa",
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
                        "resource_type": "tw",
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
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "resource_code": "tit",
                    },
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tq-wa-col_en-tw-wa-col_sw-ulb-col_sw-tq-col_sw-tw-col_sw-ulb-tit_sw-tq-tit_sw-tw-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_en_ulb_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tq_col_sw_tw_col_zh_cuv_tit_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    """
    This test demonstrates the quirk of combining resources for
    the same books but from different languages.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
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
                        "lang_code": "en",
                        "resource_type": "tw-wa",
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
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
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
        finished_document_path = "en-ulb-wa-col_en-tq-wa-col_en-tw-wa-col_sw-ulb-col_sw-tq-col_sw-tw-col_zh-cuv-tit_sw-tq-tit_sw-tw-tit_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


###################################################################
# Tests that originally were randomly chosen and failed
# using our random combinatoric tests.
###################################################################


def test_zh_ulb_doesnt_exist_jol_zh_tn_jol_language_book_order() -> None:
    """
    This shows that resource request for resource type ULB fails for
    lang_code zh because such a resource type does not exist for zh.
    Instead, cuv should have been requested. The other resources are
    found and thus a PDF document is still created, but it lacks the
    scripture verses.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "ulb",
                        "resource_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "resource_code": "jol",
                    },
                ],
            },
        )
        finished_document_path = "zh-ulb-jol_zh-tn-jol_language_book_order.pdf"
        finished_document_path = os.path.join(
            settings.output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        # This fails because zh does not have a ulb resource type and
        # thus that resource is not found. The other resources are
        # found and so the document can still be built.
        # assert not os.path.isdir("working/temp/zh_ulb")
        # assert os.path.isdir("working/temp/zh_tn")
        # NOTE Still signals ok because ulb itself makes that
        # resource request an ignored resource, but the overall
        # document request succeeds.
        assert response.ok
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            # Since ulb doesn't exist as a resource_type for zh, there
            # are no verses available in the document.
            assert not verses_html


def test_zh_cuv_jol_zh_tn_jol_language_book_order() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "resource_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "resource_code": "jol",
                    },
                ],
            },
        )
        finished_document_path = "zh-cuv-jol_zh-tn-jol_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)


def test_zh_cuv_jol_zh_tn_jol_zh_tq_jol_zh_tw_jol_language_book_order() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "resource_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "resource_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tq",
                        "resource_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tw",
                        "resource_code": "jol",
                    },
                ],
            },
        )
        finished_document_path = (
            "zh-cuv-jol_zh-tn-jol_zh-tq-jol_zh-tw-jol_language_book_order.pdf"
        )
        check_finished_document_with_verses_success(response, finished_document_path)


def test_pt_br_ulb_luk_pt_br_tn_luk_language_book_order() -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "resource_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "resource_code": "luk",
                    },
                ],
            },
        )
        finished_document_path = "pt-br-ulb-luk_pt-br-tn-luk_language_book_order.pdf"
        check_finished_document_with_verses_success(response, finished_document_path)
