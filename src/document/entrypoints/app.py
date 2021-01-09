"""This module provides the FastAPI API definition."""

import logging
import logging.config
import os
from typing import Dict, List, Optional, Tuple

import yaml
from fastapi import FastAPI

from document import config
from document.domain import model, resource_lookup
from document.domain.document_generator import DocumentGenerator

# import json


app = FastAPI()

with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


# FIXME This could be async def, see
# ~/.ghq/github.com/hogeline/sample_fastapi/code/main.py, instead of synchronous.
# @app.post(f"{config.get_api_root()}/document")
@app.post("/documents", response_model=model.FinishedDocumentDetails)
def document_endpoint(
    document_request: model.DocumentRequest,
) -> model.FinishedDocumentDetails:
    """
    Get the document request hand it off to the document_generator
    module for processing. Return FinishedDocumentDetails instance
    containing URL of resulting PDF.
    """
    document_generator = DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    document_generator.run()

    # HACK for now
    details = model.FinishedDocumentDetails(
        finished_document_url="{}.html".format(
            os.path.join(
                document_generator.working_dir, document_generator._document_request_key
            )
        )
    )

    logger.debug("details: {}".format(details))
    return details


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/language_codes")
@app.get("/language_codes")
def lang_codes() -> List[str]:
    """Return list of all available language codes."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    lang_codes: List[str] = lookup_svc.lang_codes()
    # return jsonify({"lang_codes": lang_codes}), 200
    return lang_codes


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/language_codes_and_names")
@app.get("/language_codes_and_names")
def lang_codes_and_names() -> List[Tuple[str, str]]:
    """Return list of all available language code, name tuples."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    lang_codes_and_names = lookup_svc.lang_codes_and_names()
    # return jsonify({"lang_codes_and_names": lang_codes_and_names}), 200
    return lang_codes_and_names


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/resource_types")
@app.get("/resource_types")
def resource_types() -> List[str]:
    """Return list of all available resource types."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    resource_types: List[str] = lookup_svc.resource_types()
    # return jsonify({"resource_types": resource_types}), 200
    return resource_types


# FIXME Add return type info
# @app.get(f"{config.get_api_root()}/resource_codes")
@app.get("/resource_codes")
def resource_codes() -> List[str]:
    """Return list of all available resource codes."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    resource_codes: List[str] = lookup_svc.resource_codes()
    # return jsonify({"resource_codes": resource_codes}), 200
    return resource_codes


@app.get("/health/status")
def health_status() -> Tuple[Dict, int]:
    """Ping-able server endpoint."""
    return {"status": "ok"}, 200
