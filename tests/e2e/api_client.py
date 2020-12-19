from typing import List
import json
import requests
from document import config
from document.domain import model


def get_language_codes() -> requests.Response:
    # print("Request language codes...")
    url = config.get_api_test_url()
    res = requests.get(f"{url}/language_codes")
    return res
    # assert res.ok
    # assert res.json()
    # if res.ok:
    #     print(res.json())


def get_language_codes_and_names() -> requests.Response:
    # print("Request language code, name tuples...")
    url = config.get_api_test_url()
    res = requests.get(f"{url}/language_codes_and_names")
    # res = requests.get("/language_codes_and_names")
    return res
    # assert res.ok
    # assert res.json()
    # if res.ok:
    #     print(res.json())


def get_resource_codes() -> requests.Response:
    # print("Request language codes...")
    url = config.get_api_test_url()
    res = requests.get(f"{url}/resource_codes")
    return res
    # assert res.ok
    # assert res.json()
    # if res.ok:
    #     print(res.json())


def get_resource_types() -> requests.Response:
    # print("Request language codes...")
    url = config.get_api_test_url()
    res = requests.get(f"{url}/resource_types")
    return res
    # assert res.ok
    # assert res.json()
    # if res.ok:
    #     print(res.json())


def post_document(
    document_request: model.DocumentRequest, expect_success: bool = True,
) -> requests.Response:
    # resource_requests: List[model.ResourceRequest] = []
    # resource_requests.append(model.ResourceRequest(**payload))
    # payload = {}
    # payload["resources"] = [
    #     {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
    #     {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
    #     # {"lang_code": "am", "resource_type": "ulb", "resource_code": "deu"},
    #     # {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
    #     # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
    #     # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
    #     # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
    # ]
    # payload["assembly_strategy"] = "book"  # verse, chapter, book
    # print("payload: {}".format(payload))
    # url: str = config.get_api_url()
    url: str = config.get_api_test_url()
    # res = requests.post(f"{url}/documents", json=json.dumps(payload))
    res = requests.post(f"{url}/documents", json=document_request.json())
    print(res)
    if expect_success:
        assert res.ok
    return res
    # if res.ok:
    #     # print(res)
    #     print(res.json())
