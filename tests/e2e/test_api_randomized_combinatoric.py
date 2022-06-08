import pytest
import requests
from fastapi.testclient import TestClient

from document.config import settings
from document.domain import model
from document.entrypoints.app import app

#######################################################################################
## Randomized combinatoric (wrt languags, resource types, and resource codes  tests) ##
#######################################################################################

# Useful to unearth combinations that (possibly) do not work (because
# no test has been run on them until now). Such failing tests can then
# be added as permanent non-random tests so that regressions are
# avoided.


def test_random_non_english_document_request(
    random_non_english_document_request: model.DocumentRequest,
) -> None:
    """
    Use the fixtures in ./conftest.py for non-English languages to
    generate a random document request each time this is run.
    """
    data = random_non_english_document_request.dict()
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post("/documents", json=data)
        assert response.ok


def test_random_english_and_non_english_combo_document_request(
    random_english_and_non_english_document_request: model.DocumentRequest,
) -> None:
    """
    Use the fixtures in ./conftest.py for English and non-English languages to
    generate a random multi-language document request each time this is run.
    """
    data = random_english_and_non_english_document_request.dict()
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post("/documents", json=data)
        assert response.ok


def test_random_two_non_english_languages_combo_document_request(
    random_two_non_english_languages_document_request: model.DocumentRequest,
) -> None:
    """
    Use the fixtures in ./conftest.py for two non-English languages to
    generate a random multi-language document request each time this is run.
    """
    data = random_two_non_english_languages_document_request.dict()
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post("/documents", json=data)
        assert response.ok
