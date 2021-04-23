import bs4
import os
import re
import requests
from fastapi.testclient import TestClient
from typing import Any

from document import config
from document.entrypoints.app import app

#############################################################################
## Test at least one example of all combinations of ulb, tn, tq, tw.       ##
## These are the possible combinations of the resource types ulb, tn,      ##
## tq, tw:                                                                 ##
##                                                                         ##
##  | ulb | tn | tq | tw | combination as string | complete | unit test |  ##
##  |-----+----+----+----+-----------------------+----------+-----------|  ##
##  |   0 |  0 |  0 |  1 | tw                    | y        | y         |  ##
##  |   0 |  0 |  1 |  0 | tq                    | y        | y         |  ##
##  |   0 |  0 |  1 |  1 | tq,tw                 | y        | y         |  ##
##  |   0 |  1 |  0 |  0 | tn                    | y        | y         |  ##
##  |   0 |  1 |  0 |  1 | tn,tw                 | y        | y         |  ##
##  |   0 |  1 |  1 |  0 | tn,tq                 | y        | y         |  ##
##  |   0 |  1 |  1 |  1 | tn,tq,tw              | y        | y         |  ##
##  |   1 |  0 |  0 |  0 | ulb                   | y        | y         |  ##
##  |   1 |  0 |  0 |  1 | ulb,tw                | y        | y         |  ##
##  |   1 |  0 |  1 |  0 | ulb,tq                | y        | y         |  ##
##  |   1 |  0 |  1 |  1 | ulb,tq,tw             | y        | y         |  ##
##  |   1 |  1 |  0 |  0 | ulb,tn                | y        | y         |  ##
##  |   1 |  1 |  0 |  1 | ulb,tn,tw             | y        | y         |  ##
##  |   1 |  1 |  1 |  0 | ulb,tn,tq             | y        | y         |  ##
#############################################################################


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_sw_ulb_col_sw_tn_col_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                ],
            },
        )
        finished_document_path = "sw-ulb-col_sw-tn-col_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.isfile(finished_document_path)
        assert os.path.isfile(html_file)
        assert response.json() == {"finished_document_path": finished_document_path}
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tn")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = (
            "sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_language_book_order.pdf"
        )
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert response.json() == {"finished_document_path": finished_document_path}
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tn")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order() -> None:
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
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert response.json() == {"finished_document_path": finished_document_path}
        assert os.path.isdir("working/temp/en_ulb-wa")
        assert os.path.isdir("working/temp/en_tn-wa")
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tn")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order() -> None:
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
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_sw-ulb-col_sw-tn-col_sw-tq-col_sw-ulb-tit_sw-tn-tit_sw-tq-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert response.json() == {"finished_document_path": finished_document_path}
        assert os.path.isdir("working/temp/en_ulb-wa")
        assert os.path.isdir("working/temp/en_tn-wa")
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tn")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order() -> None:
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
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "tit",
                    },
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-ulb-wa-col_en-tq-wa-col_sw-ulb-col_sw-tq-col_sw-ulb-tit_sw-tq-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert response.json() == {"finished_document_path": finished_document_path}
        assert os.path.isdir("working/temp/en_ulb-wa")
        assert os.path.isdir("working/temp/sw_ulb")
        assert os.path.isdir("working/temp/sw_tq")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body
            verses_html: bs4.elements.ResultSet = parser.find_all(
                "span", attrs={"class": "v-num"}
            )
            assert verses_html


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-tn-wa-col_en-tq-wa-col_en-tw-wa-col_sw-tn-col_sw-tq-col_sw-tw-col_sw-tn-tit_sw-tq-tit_sw-tw-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_tn")
        assert os.path.isdir("working/temp/sw_tq")
        assert os.path.isdir("working/temp/sw_tw")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body, "Did not find body element"
        assert response.ok


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = "en-tn-wa-col_en-tw-wa-col_sw-tn-col_sw-tw-col_sw-tn-tit_sw-tw-tit_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_tn")
        assert os.path.isdir("working/temp/sw_tw")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body, "Did not find body element"
        assert response.ok


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                ],
            },
        )
        finished_document_path = (
            "en-tq-wa-col_en-tw-wa-col_sw-tq-col_sw-tw-col_language_book_order.pdf"
        )
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_tq")
        assert os.path.isdir("working/temp/sw_tw")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body, "Did not find body element"
        assert response.ok


def test_en_tw_wa_col_sw_tw_col_sw_tw_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tw", "resource_code": "col",},
                ],
            },
        )
        finished_document_path = "en-tw-wa-col_sw-tw-col_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_tw")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body, "Did not find body element"
        assert response.ok


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
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
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                ],
            },
        )
        finished_document_path = (
            "en-tn-wa-col_en-tq-wa-col_sw-tn-col_sw-tq-col_language_book_order.pdf"
        )
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_tn")
        assert os.path.isdir("working/temp/sw_tq")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body, "Did not find body element"
        assert response.ok


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tq", "resource_code": "col",},
                ],
            },
        )
        finished_document_path = "en-tq-wa-col_sw-tq-col_language_book_order.pdf"
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_tq")
        with open(html_file, "r") as fin:
            html = fin.read()
            parser = bs4.BeautifulSoup(html, "html.parser")
            body: bs4.elements.ResultSet = parser.find_all("body")
            assert body, "Did not find body element"
        assert response.ok


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_language_book_order() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "tit",},
                ],
            },
        )
        finished_document_path = (
            "en-tn-wa-col_sw-tn-col_sw-tn-tit_language_book_order.pdf"
        )
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/en_tn-wa")
        assert os.path.isdir("working/temp/sw_tn")
        with open(html_file, "r") as fin:
            html = fin.read()
            assert re.search(r"Translation note", html)
        assert response.ok


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order() -> None:
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
        finished_document_path = os.path.join(
            config.get_output_dir(), finished_document_path
        )
        html_file = "{}.html".format(finished_document_path.split(".")[0])
        assert os.path.exists(finished_document_path)
        assert os.path.exists(html_file)
        assert os.path.isdir("working/temp/sw_ulb")
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
