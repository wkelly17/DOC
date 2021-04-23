import os
import pytest
import requests
from fastapi.testclient import TestClient
from typing import Any, List

from document import config
from document.entrypoints.app import app

#######################################################################################
## Non-random combinatoric tests (wrt language code, resource types, resource codes) ##
#######################################################################################


# @pytest.mark.skip
def test_two_resource_combos_language_book_order(helpers: Any) -> None:
    """
    Produce verse level interleaved document for English scripture and
    translation notes for the book of Colossians.
    """
    lang_codes: List[str] = ["en", "pt-br", "tl", "en", "en", "en", "en"]
    resource_types: List[List[str]] = [
        ["ulb-wa", "tn-wa"],
        ["ulb", "tn"],
        ["ulb", "tn"],
        ["ulb-wa", "tq-wa"],
        ["ulb-wa", "tw-wa"],
        ["tn-wa", "tq-wa"],
        ["tn-wa", "tw-wa"],
    ]
    resource_codes: List[str] = ["col", "tit", "jhn", "rom", "col", "2co", "jhn"]
    assert (
        len(lang_codes) == len(resource_types) == len(resource_codes)
    ), "Make sure you have your test data input correctly."
    for lang_code, resource_type, resource_code in zip(
        lang_codes, resource_types, resource_codes
    ):
        data = {
            "assembly_strategy_kind": "language_book_order",
            "resource_requests": [
                {
                    "lang_code": lang_code,
                    "resource_type": resource_type[0],
                    "resource_code": resource_code,
                },
                {
                    "lang_code": lang_code,
                    "resource_type": resource_type[1],
                    "resource_code": resource_code,
                },
            ],
        }
        with TestClient(app=app, base_url=config.get_api_test_url()) as client:
            response: requests.Response = client.post("/documents", json=data)
            finished_document_path = "/working/temp/{}-{}-{}_{}-{}-{}_language_book_order.pdf".format(
                lang_code,
                resource_type[0],
                resource_code,
                lang_code,
                resource_type[1],
                resource_code,
            )
            finished_document_path = os.path.join(
                config.get_output_dir(), finished_document_path
            )
            assert os.path.isfile(finished_document_path)
            assert response.json() == {"finished_document_path": finished_document_path}
