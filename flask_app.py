from flask import Flask, jsonify, request
import json
import os

# Handle running in container or as standalone script
try:
    from document_generator import DocumentGenerator
    from resource_lookup import ResourceJsonLookup
    from config import get_logging_config_file_path
except:
    from .document_generator import DocumentGenerator
    from .resource_lookup import ResourceJsonLookup
    from .config import get_logging_config_file_path

import logging
import logging.config
import yaml

# import logging
# logging.basicConfig(
#     format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s", level=logging.DEBUG
# )

app = Flask(__name__)

with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

# A particular resource is composed of: lang_code, resource_type,
# resource_code. Example: {'lang_code': 'ml', 'resource_type': 'ulb',
# 'resource_code': 'tit'}. There can be multiple resources in one request to this API
# endpoint. Example: {"resources": [{"lang_code": "ml", "resource_type": "ulb",
# "resource_code": "tit"}, {"lang_code": "ml", "resource_type": "obs-tq",
# "resource_code": ""}, {"lang_code": "mr", "resource_type": "udb",
# "resource_code": "mrk"}]}
@app.route("/api/v1/document", methods=["POST"])
def document_endpoint():
    # TODO Fix comment which is out of sync with code. Code needs to
    # change until this comment is true.
    """ Get the JSON POSTed data, create document batch job consisting
    of the requested resources and hand it off to the message bus for handling
    asynchronously. Return OK to the requesting HTTP client along with
    JSON return payload containing URL of eventually resulting PDF. """

    try:
        payload = json.loads(request.get_json())
        # app.logger.info("payload: {}".format(payload))
        logger.info("payload: {}".format(payload))
    except Exception:
        # app.logger.error("Problem reifying json")
        logger.exception("Problem reifying json")
        return "Failed to reify json", 500  # NOTE yet untested
    finally:
        app.logger.info("Successfully reified json")

    # lookup_svc = ResourceJsonLookup()

    # resource_urls = []
    for resource in payload["resources"]:
        if (
            resource["resource_code"] is not None
            and not resource["resource_code"].strip()
        ):
            resource["resource_code"] = None
        # app.logger.info("in document_endpoint, resource: {}".format(resource))
        logger.info("resource: {}".format(resource))
        # resource_urls.append(lookup_svc.lookup(resource))

    # app.logger.info("resource_urls: {}".format(resource_urls))
    # logger.info("resource_urls: {}".format(resource_urls))

    # logger.info("resources: {}".format(resources))

    # NOTE I may interject a service layer here for one layer of
    # indirection. That layer of indirection will come in handy for
    # testing and provide more flexibility to API changes.
    # Hand off resource object to domain layer
    document_generator = DocumentGenerator(payload["resources"])
    document_generator.run()  # eventually this will return path to finished PDF

    # return jsonify({"resource_urls": resource_urls}), 200
    return jsonify({"finished_document_url": "yet to be done"}), 200
    # return "OK", 201


@app.route("/api/v1/language_codes", methods=["GET"])
def lang_codes():
    """ Return list of all available language codes. """
    lookup_svc = ResourceJsonLookup()
    lang_codes: List[Optional[str]] = lookup_svc.lang_codes()
    return jsonify({"lang_codes": lang_codes}), 200


@app.route("/api/v1/language_codes_and_names", methods=["GET"])
def lang_codes_and_names():
    """ Return list of all available language code, name tuples. """
    lookup_svc = ResourceJsonLookup()
    lang_codes_and_names: List[Tuple[str, str]] = lookup_svc.lang_codes_and_names()
    return jsonify({"lang_codes_and_names": lang_codes_and_names}), 200


@app.route("/api/v1/resource_types", methods=["GET"])
def resource_types():
    """ Return list of all available resource types. """
    lookup_svc = ResourceJsonLookup()
    resource_types: List[Optional[str]] = lookup_svc.resource_types()
    return jsonify({"resource_types": resource_types}), 200


@app.route("/api/v1/resource_codes", methods=["GET"])
def resource_codes():
    """ Return list of all available resource codes. """
    lookup_svc = ResourceJsonLookup()
    resource_codes: List[Optional[str]] = lookup_svc.resource_codes()
    return jsonify({"resource_codes": resource_codes}), 200
