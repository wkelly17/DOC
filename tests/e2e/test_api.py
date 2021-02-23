"""This module provides tests for the application's FastAPI API."""

import os

from typing import Any

import pytest
import requests
from fastapi.testclient import TestClient

from document import config
from document.entrypoints.app import app


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
                "assembly_strategy_kind": "verse",
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

        finished_document_path = "/working/temp/en-ulb-wa-col_en-tn-wa-col_verse.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_verse_interleaved_en_ulb_tn_tq_returns_ok(helpers: Any) -> None:
    """
    Produce verse level interleaved document for English scripture,
    translation notes, and translation questions for the book of Col.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "verse",
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
            "/working/temp/en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_verse.html"
        )
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_verse_interleaved_en_ulb_tn_returns_ok(helpers: Any) -> None:
    """
    Produce verse level interleaved document for English scripture and
    translation notes for the book of Jude.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "verse",
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
        finished_document_path = "/working/temp/en-ulb-wa-jud_en-tn-wa-jud_verse.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


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
                "assembly_strategy_kind": "verse",
                "resource_requests": [
                    {
                        "lang_code": "ar",
                        "resource_type": "nav",
                        "resource_code": "jud",
                    },
                ],
            },
        )
        finished_document_path = "/working/temp/ar-nav-jud_verse.html"
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
                "assembly_strategy_kind": "verse",
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
        finished_document_path = "/working/temp/pt-br-ulb-gen_pt-br-tn-gen_verse.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


def test_verse_interleaved_pt_br_ulb_tn_returns_ok(helpers: Any) -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese scripture and
    request translation notes, which do not exist for this book at
    this time - so fail gracefully, for the book of Luke.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "verse",
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
        finished_document_path = "/working/temp/pt-br-ulb-luk_pt-br-tn-luk_verse.html"
        finished_document_path = helpers.get_document_filepath_for_testing(
            finished_document_path
        )
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}


# FIXME This doesn't fail any assertions but the resulting HTML is
# missing a body of content, so there is possibly an edge case here
# that needs investigation.
@pytest.mark.skip
def test_verse_interleaved_pt_br_ulb_tn_returns_ok(helpers: Any) -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "verse",
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
        finished_document_path = "/working/temp/pt-br-ulb-luk_pt-br-tn-luk_verse.html"
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_path": finished_document_path}
