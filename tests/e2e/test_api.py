"""This module provides tests for the FastAPI API."""

import os

from fastapi.testclient import TestClient

from document import config
from document.entrypoints.app import app


def test_book_interleaved_en_ulb_tn_returns_ok() -> None:
    """
    Produce book level interleaved document for English scripture and
    translation notes for the book of Jude.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "book",
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
        finished_document_path = "/working/temp/en-ulb-wa-jud_en-tn-wa-jud_book.html"
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_url": finished_document_path}


def test_book_interleaved_en_ulb_tn_tq_returns_ok() -> None:
    """
    Produce book level interleaved document for English scripture,
    translation notes, and translation questions for the book of Jude.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "book",
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
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "resource_code": "jud",
                    },
                ],
            },
        )
        finished_document_path = (
            "/working/temp/en-ulb-wa-jud_en-tn-wa-jud_en-tq-wa-jud_book.html"
        )
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_url": finished_document_path}


def test_verse_interleaved_en_ulb_tn_returns_ok() -> None:
    """
    Produce verse level interleaved document for English scripture and
    translation notes for the book of Jude.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
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
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_url": finished_document_path}


def test_book_interleaved_ar_ulb_returns_ok() -> None:
    """
    Produce book level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "book",
                "resource_requests": [
                    {
                        "lang_code": "ar",
                        "resource_type": "nav",
                        "resource_code": "jud",
                    },
                ],
            },
        )
        finished_document_path = "/working/temp/ar-nav-jud_book.html"
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_url": finished_document_path}


def test_book_interleaved_pt_br_ulb_tn_tn_doesnt_exist_for_book_returns_ok() -> None:
    """
    Produce book level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "book",
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
        finished_document_path = "/working/temp/pt-br-ulb-gen_pt-br-tn-gen_book.html"
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_url": finished_document_path}


def test_book_interleaved_pt_br_ulb_tn_returns_ok() -> None:
    """
    Produce book level interleaved document for Brazilian Portuguese scripture and
    request translation notes, which do not exist for this book at
    this time - so fail gracefully, for the book of Genesis.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "book",
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
        finished_document_path = "/working/temp/pt-br-ulb-luk_pt-br-tn-luk_book.html"
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        assert os.path.isfile(finished_document_path)
        assert response.json() == {"finished_document_url": finished_document_path}


# FIXME This doesn't fail any assertions but the resulting HTML is
# missing a body of content, so something is possibly edge case here.
def test_verse_interleaved_pt_br_ulb_tn_returns_ok() -> None:
    """
    Produce verse level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
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
        assert response.json() == {"finished_document_url": finished_document_path}


# TODO
# @pytest.mark.usefixtures("restart_api")
# def test_unhappy_path_returns_400_and_error_message():
#     payload = {}
#     payload["resources"] = [
#         # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
#         # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
#         # {"lang_code": "am", "resource_type": "ulb", "resource_code": "deu"},
#         {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
#         # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
#         # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
#         # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
#     ]
#     payload["assembly_strategy"] = "book"  # verse, chapter, book
#     # unknown_sku, orderid = random_sku(), random_orderid()
#     r = api_client.post_to_allocate(payload, expect_success=False)
#     assert r.status_code == 400
#     # assert r.json()["message"] == f"Invalid sku {unknown_sku}"

#     # r = api_client.get_allocation(orderid)
#     # assert r.status_code == 404
