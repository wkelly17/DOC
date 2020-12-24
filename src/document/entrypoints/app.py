from typing import List, Optional, Tuple
from fastapi import FastAPI
import os
from pydantic import BaseModel

# import json


from document.domain.document_generator import DocumentGenerator
from document.domain import resource_lookup
from document.domain import model
from document import config

import logging
import logging.config
import yaml


app = FastAPI()

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


class FinishedDocumentDetails(BaseModel):
    finished_document_url: Optional[str]


# FIXME This could be async def, see
# ~/.ghq/github.com/hogeline/sample_fastapi/code/main.py, instead of synchronous.
# @app.post(f"{config.get_api_root()}/document")
@app.post("/documents")
def document_endpoint(
    document_request: model.DocumentRequest, response_model=FinishedDocumentDetails
):
    # FIXME Fix comment which is out of sync with code. Code needs to
    # change until this comment is true.
    """
    Get the JSON POSTed data, create document batch job consisting
    of the requested resources and hand it off to the message bus for handling
    asynchronously. Return OK to the requesting HTTP client along with
    JSON return payload containing URL of eventually resulting PDF.

    Params:

    - assembly_strategy_kind Either BOOK - "book", CHAPTER -
    "chapter", or VERSE - "verse"

    - document_request The DocumentRequest instance that contains the
    resource requests for one document generation request.

    """

    # NOTE I may interject a service layer here for one layer of
    # indirection. That layer of indirection will come in handy for
    # testing and provide more flexibility to API changes.
    # Hand off resource object to domain layer
    document_generator = DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    document_generator.run()  # eventually this will return path to finished PDF

    details = FinishedDocumentDetails(
        finished_document_url="{}.html".format(
            os.path.join(
                document_generator.working_dir, document_generator._document_request_key
            )
        )
    )

    logger.debug("details: {}".format(details))
    print("details: {}".format(details))
    return details, 200
    # FIXME Ask document_generator for URL where finished document can
    # be downloaded. A subsequent HTTP GET of that URL should yield
    # the document.
    # return jsonify({"finished_document_url": "yet to be done"}), 200
    # return "OK", 201


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/language_codes")
@app.get("/language_codes")
def lang_codes():
    """ Return list of all available language codes. """
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    lang_codes: List[str] = lookup_svc.lang_codes()
    # return jsonify({"lang_codes": lang_codes}), 200
    return lang_codes


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/language_codes_and_names")
@app.get("/language_codes_and_names")
def lang_codes_and_names():
    """ Return list of all available language code, name tuples. """
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    lang_codes_and_names: List[Tuple[str, str]] = lookup_svc.lang_codes_and_names()
    # return jsonify({"lang_codes_and_names": lang_codes_and_names}), 200
    return lang_codes_and_names


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/resource_types")
@app.get("/resource_types")
def resource_types():
    """ Return list of all available resource types. """
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    resource_types: List[str] = lookup_svc.resource_types()
    # return jsonify({"resource_types": resource_types}), 200
    return resource_types


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/resource_codes")
@app.get("/resource_codes")
def resource_codes():
    """ Return list of all available resource codes. """
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    resource_codes: List[str] = lookup_svc.resource_codes()
    # return jsonify({"resource_codes": resource_codes}), 200
    return resource_codes


@app.get("/health/status")
def health_status():
    """ Ping-able server endpoint. """
    return {"status": "ok"}, 200
