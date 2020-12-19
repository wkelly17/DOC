from typing import List
import pytest

from document.domain import model
from . import api_client


# At the repl:
# from typing import List
# from tests.e2e import api_client
# from document.domain import model

# resource_requests: List[model.ResourceRequest] = []
# resource_requests.append(
#     model.ResourceRequest(lang_code="en", resource_type="ulb-wa", resource_code="gen")
# )
# resource_requests.append(
#     model.ResourceRequest(lang_code="en", resource_type="tn-wa", resource_code="gen")
# )
# docreq = model.DocumentRequest(resource_requests=resource_requests)
# r = api_client.post_document("book", docreq)
# assert r.ok


@pytest.mark.usefixtures("restart_api")
def test_get_language_codes_returns_ok() -> None:
    r = api_client.get_language_codes()
    assert r.ok
    # Example test approach:
    # assert r.json()  # == [
    #     {"sku": sku, "batchref": earlybatch},
    # ]


@pytest.mark.usefixtures("restart_api")
def test_get_language_codes_and_names_returns_ok() -> None:
    r = api_client.get_language_codes_and_names()
    assert r.ok
    assert len(r.json()) > 0


@pytest.mark.usefixtures("restart_api")
def test_get_resource_codes_returns_ok() -> None:
    r = api_client.get_resource_codes()
    assert r.ok
    assert len(r.json()) > 0


@pytest.mark.usefixtures("restart_api")
def test_get_resource_types_returns_ok() -> None:
    r = api_client.get_resource_types()
    assert r.ok
    assert len(r.json()) > 0


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_ok() -> None:
    # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
    # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
    # {"lang_code": "am", "resource_type": "ulb", "resource_code": "deu"},
    # {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
    # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
    # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
    # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
    assembly_strategy_kind = model.AssemblyStrategyEnum.BOOK
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="gen"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="gen"
        )
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )
    print("document_request: {}".format(document_request))
    r = api_client.post_document(document_request)
    print("r: {}".format(r))
    assert r.ok

    # Example HTTP GET test to see if HTTP POST was successful.
    # r = api_client.get_allocation(orderid)
    # assert r.ok
    # assert r.json() == [
    #     {"sku": sku, "batchref": earlybatch},
    # ]


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
