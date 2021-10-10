"""This module provides the FastAPI API definition."""

import os
import pathlib
from typing import Any, Generator

from document.config import settings
from document.domain import document_generator, model, resource_lookup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

logger = settings.logger(__name__)

# CORS configuration to allow frontend to talk to backend
origins = settings.BACKEND_CORS_ORIGINS

logger.debug("CORS origins: %s", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.post("/documents", response_model=model.FinishedDocumentDetails)
def document_endpoint(
    document_request: model.DocumentRequest,
) -> model.FinishedDocumentDetails:
    """
    Get the document request and hand it off to the document_generator
    module for processing. Return model.FinishedDocumentDetails instance
    containing URL of resulting PDF, or, None in the case of failure plus a
    message to return to the UI.
    """
    # Top level exception handler
    try:
        document_request_key, finished_document_path = document_generator.run(
            document_request
        )
        assert os.path.exists(finished_document_path)
        details = model.FinishedDocumentDetails(
            finished_document_request_key=document_request_key,
            message=settings.SUCCESS_MESSAGE,
        )
    except Exception:
        logger.exception(
            "The document request could not be fulfilled. Likely reason is the following exception:"
        )
        details = model.FinishedDocumentDetails(
            finished_document_request_key=None,
            # Provide an appropriate message back to the UI that can
            # be shared with the user when the document request cannot
            # be fulfilled for some reason.
            message=settings.FAILURE_MESSAGE,
        )

    logger.debug("FinishedDocumentDetails: %s", details)
    return details


@app.get("/pdfs/{document_request_key}")
def serve_pdf_document(
    document_request_key: str,
) -> FileResponse:
    """Serve the requested PDF document."""
    path = "{}.pdf".format(os.path.join(settings.output_dir(), document_request_key))
    return FileResponse(
        path=path,
        filename=pathlib.Path(path).name,
        headers={"Content-Disposition": "attachment"},
    )


# @app.get(f"{settings.API_ROOT}/language_codes_names_and_resource_types")
@app.get("/language_codes_names_and_resource_types")
def lang_codes_names_and_resource_types() -> list[model.CodeNameTypeTriplet]:
    """
    Return list of tuples of lang_code, lang_name, resource_types for
    all available language codes.
    """
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    return lookup_svc.lang_codes_names_and_resource_types()


# @app.get(f"{settings.API_ROOT}/language_codes")
@app.get("/language_codes")
def lang_codes() -> Generator[str, None, None]:
    """Return list of all available language codes."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    return lookup_svc.lang_codes()


# @app.get(f"{settings.API_ROOT}/language_codes_and_names")
@app.get("/language_codes_and_names")
def lang_codes_and_names() -> Generator[tuple[str, str], None, None]:
    """Return list of all available language code, name tuples."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    return lookup_svc.lang_codes_and_names()


# @app.get(f"{settings.API_ROOT}/resource_types")
@app.get("/resource_types")
def resource_types() -> Any:
    """Return list of all available resource types."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    return lookup_svc.resource_types()


# @app.get(f"{settings.API_ROOT}/resource_codes")
@app.get("/resource_codes")
def resource_codes() -> Any:
    """Return list of all available resource codes."""
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    return lookup_svc.resource_codes()


@app.get("/health/status")
def health_status() -> tuple[dict[str, str], int]:
    """Ping-able server endpoint."""
    return {"status": "ok"}, 200
