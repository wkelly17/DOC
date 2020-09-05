# from datetime import datetime
from flask import Flask, jsonify, request
import json

# Handle running in container or as standalone script
try:
    from .resource_lookup import ResourceJsonLookup
except:
    from resource_lookup import ResourceJsonLookup


app = Flask(__name__)


# A particular resource is composed of: lang_code, resource_type,
# resource_code. Example: {'lang_code': 'ml', 'resource_type': 'ulb',
# 'resource_code': 'tit'}. There can be multiple resources in one request to this API
# endpoint. Example: {"resources": [{"lang_code": "ml", "resource_type": "ulb",
# "resource_code": "tit"}, {"lang_code": "ml", "resource_type": "obs-tq",
# "resource_code": ""}, {"lang_code": "mr", "resource_type": "udb",
# "resource_code": "mrk"}]}
@app.route("/api/v1/document", methods=["POST"])
def document_endpoint():
    """ Get the JSON POSTed data, create document batch job consisting
    of the requested resources and hand it off to the message bus for handling
    asynchronously. Return OK to the requesting HTTP client along with
    JSON return payload containing URL of eventually resulting PDF. """

    try:
        payload = json.loads(request.get_json())
        print(payload)
    except:
        print("Problem reifying json")
        return "Failed to reify json", 500  # NOTE yet untested
    finally:
        print("Successfully reified json")

    lookup_svc = ResourceJsonLookup()

    resources = payload["resources"]
    resource_urls = []
    for resource in resources:
        print("lang_code: {}".format(resource["lang_code"]))
        print("resource_type: {}".format(resource["resource_type"]))
        print("resource_code: {}".format(resource["resource_code"]))
        resource_code = (
            None if not resource["resource_code"] else resource["resource_code"]
        )
        resource_urls += lookup_svc.lookup(
            resource["lang_code"], resource["resource_type"], resource_code,
        )

    print("resource_urls: {}".format(resource_urls))

    return jsonify({"resources": resources})
    # return "OK", 201
