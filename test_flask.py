import json
import requests


payload = {}
payload["resources"] = [
    {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
    # {"lang_code": "am", "resource_type": "ulb", "resource_code": "deu"},
    # {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
    # {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
    # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
    # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
]


print("Request language codes...")
res = requests.get("http://localhost:5005/api/v1/language_codes")
if res.ok:
    print(res.json())

print("Request language code, name tuples...")
res = requests.get("http://localhost:5005/api/v1/language_codes_and_names")
if res.ok:
    print(res.json())

print("payload: {}".format(payload))
res = requests.post("http://localhost:5005/api/v1/document", json=json.dumps(payload))
if res.ok:
    # print(res)
    print(res.json())
