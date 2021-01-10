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
        finished_document_path = "/working/temp/en-ulb-wa-jud_en-tn-wa-jud.html"
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
            "/working/temp/en-ulb-wa-jud_en-tn-wa-jud_en-tq-wa-jud.html"
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
        finished_document_path = "/working/temp/en-ulb-wa-jud_en-tn-wa-jud.html"
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
