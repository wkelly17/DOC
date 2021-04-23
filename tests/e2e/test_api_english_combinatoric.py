import requests
from fastapi.testclient import TestClient

from document import config
from document.domain import model
from document.entrypoints.app import app

########################
## Long running tests ##
########################

# These are set to skip for the default case as
# they really take a long time to run since they are testing many
# different combinations of languages, resource types, and resource
# codes. We run them to ensure combinations work, obviously, but also
# to unearth combinations that do not work and then add them to a
# scheme for testing known failure combos together. Such a scheme
# currently is the use of PASSING_NON_ENGLISH_LANG_CODES and
# FAILING_NON_ENGLISH_LANG_CODES for example.


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
