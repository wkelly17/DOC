import pytest
import requests
from fastapi.testclient import TestClient

from document import config
from document.domain import model
from document.entrypoints.app import app

########################
## Long running tests ##
########################


# This will build a PDF for every book of the bible, thus it takes a
# long time. This makes it unpleasant to run all tests via the 'make
# all' Makefile target. For this reason, skip this when you want to run
# all the tests, excepting these. Note that English tests exist in
# additional places so you aren't not testing English resources by
# skipping this. This is just additional coverage.
@pytest.mark.skip
def test_english_variable_resource_type_combos_for_all_books(
    english_document_request: model.DocumentRequest,
) -> None:
    """
    Use the fixtures in ./conftest.py for English language to generate random
    tests that test all books of the bible, but with variable
    combinations of resource type, e.g., ulb, tn, tq, tw; ulb, tq, tw;
    etc.. Because all books of the bible are tested, it takes a while
    to run. There were no errors when it ran to completion.
    """
    data = english_document_request.dict()
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post("/documents", json=data)
        assert response.ok
