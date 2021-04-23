"""This module provides tests for the application's FastAPI API."""

import bs4
import os
import pathlib
from typing import Any

import pytest
import requests
from fastapi.testclient import TestClient

from document import config
from document.utils import file_utils
from document.entrypoints.app import app

##########################################################################
## Specific targeted tests (wrt language, resource type, resource code) ##
##########################################################################


def test_en_ulb_wa_col_en_tn_wa_col_language_book_order() -> None:
    """
    Produce verse interleaved document for English scripture and
    translation notes for the book of Colossians.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        assert response.ok
        # FIXME Serving PDFs is yet to be implemented
        # assert os.path.exists(finished_document_path)
        # assert response.json() == {
        #     "finished_document_path": "{}.pdf".format(
        #         pathlib.Path(os.path.basename(finished_document_path)).stem
        #     )
        # }


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_language_book_order() -> None:
    """
    Produce verse level interleaved document for English scripture,
    translation notes, and translation questions for the book of Col.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        assert response.ok
        # FIXME Serving PDFs is yet to be implemented
        # assert os.path.exists(finished_document_path)
        # assert response.json() == {
        #     "finished_document_path": "{}.pdf".format(
        #         pathlib.Path(os.path.basename(finished_document_path)).stem
        #     )
        # }


def test_en_ulb_wa_tn_wa_jud_language_book_order() -> None:
    """
    Produce verse level interleaved document for English scripture and
    translation notes for the book of Jude.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        assert response.ok
        # FIXME Serving PDFs is yet to be implemented
        # assert os.path.exists(finished_document_path)
        # assert response.json() == {
        #     "finished_document_path": "{}.pdf".format(
        #         pathlib.Path(os.path.basename(finished_document_path)).stem
        #     )
        # }


def test_ar_nav_jud_language_book_order() -> None:
    """
    Produce verse level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        assert response.ok
        # FIXME Serving PDFs is yet to be implemented
        # assert os.path.exists(finished_document_path)
        # assert response.json() == {
        #     "finished_document_path": "{}.pdf".format(
        #         pathlib.Path(os.path.basename(finished_document_path)).stem
        #     )
        # }


def test_pt_br_ulb_tn_language_book_order() -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        assert response.ok
        # FIXME Serving PDFs is yet to be implemented
        # assert os.path.exists(finished_document_path)
        # assert response.json() == {
        #     "finished_document_path": "{}.pdf".format(
        #         pathlib.Path(os.path.basename(finished_document_path)).stem
        #     )
        # }


def test_pt_br_ulb_tn_en_ulb_wa_tn_wa_luk_language_book_order() -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese
    and English scripture and translation notes for the book of Luke.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        assert response.ok
        # FIXME Serving PDFs is yet to be implemented
        # assert response.json() == {
        # assert os.path.exists(finished_document_path)
        #     "finished_document_path": "{}.pdf".format(
        #         pathlib.Path(os.path.basename(finished_document_path)).stem
        #     )
        # }


def test_pt_br_ulb_tn_luk_en_ulb_wa_tn_wa_luk_sw_ulb_tn_col_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                ],
            },
        )
        finished_document_path = "pt-br-ulb-luk_pt-br-tn-luk_en-ulb-wa-luk_en-tn-wa-luk_sw-ulb-col_sw-tn-col_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        # FIXME html_file does not exist
        assert os.path.exists(html_file)
        assert response.ok
        # FIXME Serving PDFs is yet to be implemented
        assert response.json() == {"finished_document_path": finished_document_path}


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_sw-ulb-col_sw-tn-col_sw-tq-col_sw-tw-col_sw-tn-tit_sw-tq-tit_sw-tw-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        # FIXME HTML_file does not exist? Yet PDF generation
        # succeeded. Does wkhtmltopdf delete the HTML file after
        # consuming it? If I run
        # wkhtmltopdf ../../working/temp/pt-br-ulb-mal_pt-br-tq-mal_pt-br-tw-mal_tl-ulb-1ki_tl-tq-1ki_tl-tw-1ki_language_book_order.html foo.pdf
        # both foo.pdf and
        # ../../working/temp/pt-br-ulb-mal_pt-br-tq-mal_pt-br-tw-mal_tl-ulb-1ki_tl-tq-1ki_tl-tw-1ki_language_book_order.html
        # exist after the command.Therefore, wkhtmltopdf is not
        # deleting the HTML file after consuming it. Something else is
        # removing the HTML file. Perhaps it is pdf_kit.from_file.
        # I'll take a look at the source for pdf_kit.from_file.
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/en_ulb-wa")
        assert os.path.isdir("working/temp/en_tn-wa")
        assert os.path.isdir("working/temp/en_tq-wa")
        assert os.path.isdir("working/temp/en_tw-wa")
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tn")
        assert os.path.isdir("working/temp/sw_tq")
        assert os.path.isdir("working/temp/sw_tw")
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


def test_en_ulb_wa_col_en_tn_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tw-wa-col_sw-ulb-col_sw-tn-col_sw-tw-col_sw-ulb-tit_sw-tn-tit_sw-tw-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tn")
        assert os.path.isdir("working/temp/sw_tw")
        assert response.ok
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_en_ulb_wa_col_en_tw_wa_col_sw_ulb_col_sw_tw_col_sw_ulb_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tw-wa-col_sw-ulb-col_sw-tw-col_sw-ulb-tit_sw-tw-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tw")
        assert response.ok
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_en_ulb_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tq-wa-col_en-tw-wa-col_sw-ulb-col_sw-tq-col_sw-tw-col_sw-ulb-tit_sw-tq-tit_sw-tw-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/en_ulb-wa")
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tq")
        assert os.path.isdir("working/temp/sw_tw")
        assert response.ok
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


###################################################################
# Targeted tests
#
# Targeted tests that originally were randomly chosen and failed
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
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "ulb",
                        "resource_code": "jol",
                    },
                    {"lang_code": "zh", "resource_type": "tn", "resource_code": "jol",},
                ],
            },
        )
        finished_document_path = "zh-ulb-jol_zh-tn-jol_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        # This fails because zh does not have a ulb resource type and
        # thus that resource is not found. The other resources are
        # found and so the document can still be built.
        assert not os.path.isdir("working/temp/zh_ulb")
        assert os.path.isdir("working/temp/zh_tn")
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
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "resource_code": "jol",
                    },
                    {"lang_code": "zh", "resource_type": "tn", "resource_code": "jol",},
                ],
            },
        )
        finished_document_path = "zh-cuv-jol_zh-tn-jol_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/zh_cuv")
        assert os.path.isdir("working/temp/zh_tn")
        assert response.ok
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_zh_cuv_jol_zh_tn_jol_zh_tq_jol_zh_tw_jol_language_book_order() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "resource_code": "jol",
                    },
                    {"lang_code": "zh", "resource_type": "tn", "resource_code": "jol",},
                    {"lang_code": "zh", "resource_type": "tq", "resource_code": "jol",},
                    {"lang_code": "zh", "resource_type": "tw", "resource_code": "jol",},
                ],
            },
        )
        finished_document_path = (
            "zh-cuv-jol_zh-tn-jol_zh-tq-jol_zh-tw-jol_language_book_order.pdf"
        )
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/zh_cuv")
        assert os.path.isdir("working/temp/zh_tn")
        assert os.path.isdir("working/temp/zh_tq")
        assert os.path.isdir("working/temp/zh_tw")
        assert response.ok
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_pt_br_ulb_luk_pt_br_tn_luk_language_book_order() -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        # FIXME HTML file is missing when we go to read and parse
        # HTML? And yet it does exist when checked right after
        # creating the PDF in document_generator module.
        assert os.path.exists(html_file)
        assert response.json() == {"finished_document_path": finished_document_path}
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html
