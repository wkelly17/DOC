import logging
import os
import requests
import yaml
from fastapi.testclient import TestClient

from document import config
from document.entrypoints.app import app

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


def test_send_email_with_arb_nav_jud_pdf() -> None:
    """
    Produce verse level interleaved document for language, arb, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    # First generate the PDF
    with TestClient(app=app, base_url=config.get_api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": config.get_to_email_address(),
                "assembly_strategy_kind": "language_book_order",
                "resource_requests": [
                    {
                        "lang_code": "arb",
                        "resource_type": "nav",
                        "resource_code": "jud",
                    },
                ],
            },
        )
        finished_document_request_key = response.json()["finished_document_request_key"]
        finished_document_path = os.path.join(
            config.get_output_dir(), "{}.pdf".format(finished_document_request_key)
        )
        logger.debug("finished_document_path: {}".format(finished_document_path))
        assert os.path.exists(finished_document_path)
        assert response.ok
