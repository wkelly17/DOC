import json
import requests
from document import config


def get_language_codes():
    # print("Request language codes...")
    url = config.get_api_url()
    res = requests.get(f"{url}/language_codes")
    return res
    # assert res.ok
    # assert res.json()
    # if res.ok:
    #     print(res.json())


def get_language_codes_and_names():
    # print("Request language code, name tuples...")
    url = config.get_api_url()
    res = requests.get("{url}/language_codes_and_names")
    return res
    # assert res.ok
    # assert res.json()
    # if res.ok:
    #     print(res.json())


# FIXME Add return type
def post_document(payload: dict, expect_success=True):
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
    url: str = config.get_api_url()
    res = requests.post(f"{url}/document", json=json.dumps(payload))
    if expect_success:
        assert res.ok
    return res
    # if res.ok:
    #     # print(res)
    #     print(res.json())
