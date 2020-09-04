import json
import requests


payload = {}
payload["resources"] = [
    {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
    {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
    {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
]


print("payload: {}".format(payload))
res = requests.post(
    "http://localhost:5000/api/v1/generate_document", json=json.dumps(payload)
)
if res.ok:
    # print(res)
    print(res.json())
