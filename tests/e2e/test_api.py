"""This module provides tests for the application's FastAPI API."""

# import itertools
# import json
import os

# import pathlib

from typing import Any, List

import pytest
import requests
from fastapi.testclient import TestClient

from document import config
from document.domain import model
from document.entrypoints.app import app

# from document.utils import file_utils


def test_english_fixtures(english_document_request: model.DocumentRequest) -> None:
    """
    Use the fixtures in ./conftest.py for non-English languages to generate random
    tests.
    """
    data = english_document_request.dict()
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post("/documents", json=data)
        assert response.ok


def test_non_english_fixtures(
    non_english_document_request: model.DocumentRequest,
) -> None:
    """
    Use the fixtures in ./conftest.py for non-English languages to generate random
    tests.
    """
    data = non_english_document_request.dict()
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post("/documents", json=data)
        assert response.ok


# def test_single_or_multi_language_multi_resource_documents_language_book_order(
#     helpers: Any,
# ) -> None:
#     """
#     Produce verse level interleaved documents for different
#     combinations of resources in resource_fixtures below.
#     """
#     resource_fixtures = [
#         [
#             # True indicates multi-language fixture
#             ["en", ["ulb-wa", "tn-wa", "tq-wa", "tw-wa"], "col"],
#             ["pt-br", ["ulb", "tn"], "tit"],
#         ],
#         # False indicates single language fixture
#         [False, "tl", ["ulb", "tn", "tq", "tw"], "jdg"],
#         # [
#         #     True,  # indicates multi-language fixture
#         #     # ["kbt", ["reg"], "2co"],  # This fails because the USFM does not have the expected, by books.py, 'id' element.
#         #     # ["aau", ["reg"], "heb"], # This fails because the USFM does not have the expected, by books.py, 'id' element.
#         #     # ["tbg-x-abuhaina", ["reg"], "2th"], # This fails because the USFM does not have the expected, by books.py, 'id' element.
#         #     # ["abz", ["reg"], "gal"], # This fails because the USFM does not have the expected, by books.py, 'id' element.
#         #     # ["abu", ["reg"], "3jn"], # This fails because the USFM does not have the expected, by books.py, 'id' element.
#         #     # ["guq", ["reg"], "2sa"], # This fails because the USFM does not have the expected, by books.py, 'id' element.
#         # ],
#     ]

#     def build_and_send_request(
#         lang_code: str, resource_type_list: List[str], resource_code: str
#     ) -> None:
#         """
#         Build the json data and then submit the request and check the
#         result.
#         """
#         # Build the json to send.
#         data = {}
#         data["assembly_strategy_kind"] = "language_book_order"
#         data["resource_requests"] = []  # type: ignore
#         for resource_type in resource_type_list:
#             resource_dict = {
#                 "lang_code": lang_code,
#                 "resource_type": resource_type,
#                 "resource_code": resource_code,
#             }
#             data["resource_requests"].append(resource_dict)  # type: ignore

#         with TestClient(app=app, base_url=config.get_api_test_url()) as client:
#             response: requests.Response = client.post("/documents", json=data)
#             format_values = list(
#                 zip(
#                     itertools.repeat(lang_code, len(resource_type_list)),
#                     resource_type_list,
#                     itertools.repeat(resource_code, len(resource_type_list)),
#                 )
#             )
#             format_flattened_values = "_".join(
#                 ["-".join(tuple) for tuple in format_values]  # type: ignore
#             )
#             finished_document_path = "/working/temp/{}_language_book_order.html".format(
#                 format_flattened_values
#             )
#             finished_document_path = helpers.get_document_filepath_for_testing(
#                 finished_document_path
#             )
#             assert os.path.isfile(finished_document_path)
#             assert response.json() == {"finished_document_path": finished_document_path}

#     # FIXME This logic is broken.
#     for resource_fixture in resource_fixtures:
#         breakpoint()
#         if len(resource_fixture) > 1:
#             breakpoint()
#             for lang in resource_fixture:
#                 breakpoint()
#                 for idx in range(len(resource_fixture) - 1):
#                     breakpoint()
#                     lang_code = resource_fixture[idx][0]
#                     resource_type_list = resource_fixture[idx][1]
#                     resource_code = resource_fixture[idx][2]
#                     build_and_send_request(lang_code, resource_type_list, resource_code)

#         else:
#             resource_fixture = resource_fixture[1:]
#             lang_code = resource_fixture[0]
#             resource_type_list = resource_fixture[1]
#             resource_code = resource_fixture[2]
#             build_and_send_request(lang_code, resource_type_list, resource_code)


# @pytest.mark.parametrize("lang_codes", [["en"]])
# @pytest.mark.parametrize("resource_types", [["ulb-wa", "tn-wa"]])
# @pytest.mark.parametrize("resource_codes", [["col"]])
# @pytest.mark.parametrize(
#     "document_paths", [["en-ulb-wa-col_en-tn-wa-col_language_book_order"]]
# )
# NOTE Using Any type is a mypy hack for fixture being passed in. Not
# ideal, but the way pytest builds its path is not ideal either.
@pytest.mark.skip
def test_two_resource_combos_language_book_order(helpers: Any) -> None:
    """
    Produce verse level interleaved document for English scripture and
    translation notes for the book of Colossians.
    """
    lang_codes: List[str] = ["en", "pt-br", "tl", "en", "en", "en", "en"]
    resource_types: List[List[str]] = [
        ["ulb-wa", "tn-wa"],
        ["ulb", "tn"],
        ["ulb", "tn"],
        ["ulb-wa", "tq-wa"],
        ["ulb-wa", "tw-wa"],
        ["tn-wa", "tq-wa"],
        ["tn-wa", "tw-wa"],
    ]
    resource_codes: List[str] = ["col", "tit", "jhn", "rom", "col", "2co", "jhn"]

    assert (
        len(lang_codes) == len(resource_types) == len(resource_codes)
    ), "Make sure you have your test data input correctly."

    for lang_code, resource_type, resource_code in zip(
        lang_codes, resource_types, resource_codes
    ):
        data = {
            "assembly_strategy_kind": "language_book_order",
            "resource_requests": [
                {
                    "lang_code": lang_code,
                    "resource_type": resource_type[0],
                    "resource_code": resource_code,
                },
                {
                    "lang_code": lang_code,
                    "resource_type": resource_type[1],
                    "resource_code": resource_code,
                },
            ],
        }
        with TestClient(app=app, base_url=config.get_api_test_url()) as client:
            response: requests.Response = client.post("/documents", json=data)
            finished_document_path = "/working/temp/{}-{}-{}_{}-{}-{}_language_book_order.html".format(
                lang_code,
                resource_type[0],
                resource_code,
                lang_code,
                resource_type[1],
                resource_code,
            )
            finished_document_path = helpers.get_document_filepath_for_testing(
                finished_document_path
            )
            assert os.path.isfile(finished_document_path)
            assert response.json() == {"finished_document_path": finished_document_path}


# NOTE Using Any type is a mypy hack for fixture being passed in. Not
# ideal, but the way pytest builds its path is not ideal either.
def test_verse_interleaved_en_ulb_tn_returns_ok(helpers: Any) -> None:
    """
    Produce verse level interleaved document for English scripture and
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

        finished_document_path = (
            "/working/temp/en-ulb-wa-col_en-tn-wa-col_language_book_order.html"
        )
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


# @pytest.mark.skip
def test_verse_interleaved_en_ulb_tn_tq_returns_ok(helpers: Any) -> None:
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
        finished_document_path = "/working/temp/en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_language_book_order.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_verse_interleaved_en_ulb_tn_jud_returns_ok(helpers: Any) -> None:
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
        finished_document_path = (
            "/working/temp/en-ulb-wa-jud_en-tn-wa-jud_language_book_order.html"
        )
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


# @pytest.mark.skip
def test_verse_interleaved_ar_ulb_returns_ok(helpers: Any) -> None:
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
        finished_document_path = "/working/temp/ar-nav-jud_language_book_order.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_verse_interleaved_pt_br_ulb_tn_tn_doesnt_exist_for_book_returns_ok(
    helpers: Any,
) -> None:
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
        finished_document_path = (
            "/working/temp/pt-br-ulb-gen_pt-br-tn-gen_language_book_order.html"
        )
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_verse_interleaved_en_ulb_tn_pt_br_ulb_tn_returns_ok(helpers: Any) -> None:
    """
    Produce verse level interleaved document for English and
    Brazilian Portuguese scripture and translation notes for the book
    of Luke.
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
        finished_document_path = "/working/temp/pt-br-ulb-luk_pt-br-tn-luk_en-ulb-wa-luk_en-tn-wa-luk_language_book_order.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_verse_interleaved_en_ulb_tn_pt_br_ulb_tn_sw_ulb_tn_returns_ok(
    helpers: Any,
) -> None:
    """
    Produce verse level interleaved document for English and
    Brazilian Portuguese scripture and translation notes for the book
    of Luke.
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
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {"lang_code": "sw", "resource_type": "tn", "resource_code": "col",},
                ],
            },
        )
        finished_document_path = "/working/temp/pt-br-ulb-luk_pt-br-tn-luk_en-ulb-wa-luk_en-tn-wa-luk_sw-ulb-col_sw-tn-col_language_book_order.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


# FIXME This doesn't fail any assertions but the resulting HTML is
# missing a body of content, so there is possibly an edge case here
# that needs investigation.
@pytest.mark.skip
def test_verse_interleaved_pt_br_ulb_tn_luk_returns_ok(helpers: Any) -> None:
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
        finished_document_path = (
            "/working/temp/pt-br-ulb-luk_pt-br-tn-luk_language_book_order.html"
        )
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}
