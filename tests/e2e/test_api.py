import pytest

from . import api_client

@pytest.mark.usefixtures("restart_api")
# def test_happy_path_returns_202_and_batch_is_allocated():
def test_happy_path_returns_ok():
    payload = {}
    payload["resources"] = [
        {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
        {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
        # {"lang_code": "am", "resource_type": "ulb", "resource_code": "deu"},
        # {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
        # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
        # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
        # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
    ]
    payload["assembly_strategy"] = "book"  # verse, chapter, book
    r = api_client.post_document(payload)
    assert r.ok

    # r = api_client.get_allocation(orderid)
    # assert r.ok
    # assert r.json() == [
    #     {"sku": sku, "batchref": earlybatch},
    # ]


# @pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    payload = {}
    payload["resources"] = [
        # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
        # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
        # {"lang_code": "am", "resource_type": "ulb", "resource_code": "deu"},
        {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
        # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
        # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
        # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
    ]
    payload["assembly_strategy"] = "book"  # verse, chapter, book
    # unknown_sku, orderid = random_sku(), random_orderid()
    r = api_client.post_to_allocate(payload, expect_success=False)
    assert r.status_code == 400
    # assert r.json()["message"] == f"Invalid sku {unknown_sku}"

    # r = api_client.get_allocation(orderid)
    # assert r.status_code == 404
