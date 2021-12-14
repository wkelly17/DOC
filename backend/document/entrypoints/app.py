"""This module provides the FastAPI API definition."""

import os
import pathlib
from collections.abc import Iterable, Sequence
from typing import Any

from document.config import settings
from document.domain import document_generator, model, resource_lookup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl
from starlette.responses import HTMLResponse

# Don't serve swagger docs static assets from third party CDN.
# Source: https://github.com/tiangolo/fastapi/issues/2518#issuecomment-827513744
app = FastAPI()


logger = settings.logger(__name__)

# CORS configuration to allow frontend to talk to backend
origins: list[AnyHttpUrl] = settings.BACKEND_CORS_ORIGINS

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
    success_message: str = settings.SUCCESS_MESSAGE,
    failure_message: str = settings.FAILURE_MESSAGE,
) -> model.FinishedDocumentDetails:
    """
    Get the document request and hand it off to the document_generator
    module for processing. Return model.FinishedDocumentDetails instance
    containing URL of resulting PDF, or, None in the case of failure plus a
    message to return to the UI.
    """
    # Top level exception handler
    try:
        document_request_key, finished_document_path = document_generator.main(
            document_request
        )
        assert os.path.exists(finished_document_path)
    except Exception as exc:
        logger.exception(
            "There was a error while attempting to fulfill the document request. Likely reason is the following exception:"
        )

        # Prepare the exception to send to the front end if needed.
        # Source: https://fastapi.tiangolo.com/tutorial/handling-errors/
        # Source: https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/
        # FIXME: Still have not found a way to retrieve on the JS
        # frontend the exception message that is set below in 'detail'.
        backend_exception = HTTPException(
            status_code=404,
            detail="{}, Exception: {}".format(failure_message, exc),
        )
        raise backend_exception
        # details = model.FinishedDocumentDetails(
        #     finished_document_request_key=None,
        #     # Provide an appropriate message back to the UI that can
        #     # be shared with the user when the document request cannot
        #     # be fulfilled for some reason.
        #     message=failure_message,
        # )
    else:
        details = model.FinishedDocumentDetails(
            finished_document_request_key=document_request_key,
            message=success_message,
        )
        logger.debug("FinishedDocumentDetails: %s", details)
    return details


@app.get("/pdfs/{document_request_key}")
def serve_pdf_document(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> FileResponse:
    """Serve the requested PDF document."""
    path = "{}.pdf".format(os.path.join(output_dir, document_request_key))
    return FileResponse(
        path=path,
        filename=pathlib.Path(path).name,
        headers={"Content-Disposition": "attachment"},
    )


@app.get("/language_codes_names_and_resource_types")
def lang_codes_names_and_resource_types() -> Iterable[model.CodeNameTypeTriplet]:
    """
    Return list of tuples of lang_code, lang_name, resource_types for
    all available language codes.
    """
    return resource_lookup.lang_codes_names_and_resource_types()


@app.get("/language_codes")
def lang_codes() -> Iterable[str]:
    """Return list of all available language codes."""
    return resource_lookup.lang_codes()


@app.get("/language_codes_and_names")
def lang_codes_and_names() -> list[tuple[str, str]]:
    """Return list of all available language code, name tuples."""
    return resource_lookup.lang_codes_and_names()


@app.get("/resource_types")
def resource_types() -> Any:
    """Return list of all available resource types."""
    return resource_lookup.resource_types()


@app.get("/resource_types_for_lang/{lang_code}")
def resource_types_for_lang(lang_code: str) -> Sequence[Any]:
    """Return list of all available resource types."""
    return resource_lookup.resource_types_for_lang(lang_code)


@app.get("/resource_codes_for_lang/{lang_code}")
def resource_codes_for_lang(lang_code: str) -> Sequence[Sequence[Any]]:
    """Return list of all available resource types."""
    return resource_lookup.resource_codes_for_lang(lang_code)


@app.get("/resource_codes")
def resource_codes() -> Any:
    """Return list of all available resource codes."""
    return resource_lookup.resource_codes()


@app.get("/health/status")
def health_status() -> tuple[dict[str, str], int]:
    """Ping-able server endpoint."""
    return {"status": "ok"}, 200
