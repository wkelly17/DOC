import icontract
import pytest
import requests
from fastapi.testclient import TestClient

from document.config import settings
from document.domain import model
from document.entrypoints.app import app

############################
## Expected failing tests ##
############################


# Some of the FAILING_NON_ENGLISH_LANG_CODES actual succeed if only
# certain resource types are requested, e.g., am, tq succeeds, but am,
# ulb fails. For these reasons, I am skipping this test for now.
@pytest.mark.skip
def test_random_failing_non_english_document_request(
    random_failing_non_english_document_request: model.DocumentRequest,
) -> None:
    """
    Test a randomly generated document request that will fail for
    reasons explained in the fixtures docstring.
    """
    data = random_failing_non_english_document_request.dict()
    with pytest.raises(icontract.errors.ViolationError):
        with TestClient(app=app, base_url=settings.api_test_url()) as client:
            response: requests.Response = client.post("/documents", json=data)
            # Will fail to find so don't expect ok code.
            assert not response.ok
