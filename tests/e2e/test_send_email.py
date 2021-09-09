import logging
import os
import requests
import yaml
from fastapi.testclient import TestClient

from document.config import settings
from document.entrypoints.app import app

logger = settings.get_logger(__name__)


def test_send_email_with_ar_nav_jud_pdf() -> None:
    """
    Produce verse level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    # First generate the PDF
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
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
        finished_document_request_key = response.json()["finished_document_request_key"]
        finished_document_path = os.path.join(
            settings.output_dir(), "{}.pdf".format(finished_document_request_key)
        )
        logger.debug("finished_document_path: {}".format(finished_document_path))
        assert os.path.exists(finished_document_path)
        assert response.ok
