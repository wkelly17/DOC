from fastapi.testclient import TestClient

from document import config
from document.entrypoints.app import app


def test_get_language_codes_names_and_resource_types_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/language_codes_names_and_resource_types")
        # print("response.url: {}".format(response.url))
        # assert response.ok
        assert response.status_code == 200, response.text
        assert response.json()


def test_get_language_codes_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/language_codes")
        # print("response.url: {}".format(response.url))
        # assert response.ok
        assert response.status_code == 200, response.text
        assert response.json()


def test_get_language_codes_and_names_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/language_codes_and_names")
        assert response.status_code == 200, response.text
        assert response.json()


def test_get_resource_codes_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/resource_codes")
        assert response.status_code == 200, response.text
        assert response.json()


def test_get_resource_types_returns_ok() -> None:
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response = client.get("/resource_types")
        assert response.status_code == 200, response.text
        assert response.json()
