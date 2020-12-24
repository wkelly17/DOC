from typing import List
import pytest
from fastapi.testclient import TestClient
from document import config
from document.domain import model
from document.entrypoints.app import app


@pytest.mark.usefixtures("restart_api")
def test_get_language_codes_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/language_codes")
        # print("response.url: {}".format(response.url))
        # assert response.ok
        assert response.status_code == 200, response.text
        assert len(response.json()) > 0


@pytest.mark.usefixtures("restart_api")
def test_get_language_codes_and_names_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/language_codes_and_names")
        assert response.status_code == 200, response.text
        assert len(response.json()) > 0


@pytest.mark.usefixtures("restart_api")
def test_get_resource_codes_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/resource_codes")
        assert response.status_code == 200, response.text
        assert len(response.json()) > 0


@pytest.mark.usefixtures("restart_api")
def test_get_resource_types_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/resource_types")
        assert response.status_code == 200, response.text
        assert len(response.json()) > 0


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_ok2() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "assembly_strategy_kind": "book",
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "resource_code": "eph",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "resource_code": "eph",
                    },
                ],
            },
        )
        assert response.status_code == 200, response.text
        # assert response.json() == {
        #     "finished_document_url": "/working/temp/en-ulb-wa-gen_en-tn-wa-gen.html"
        # }


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
