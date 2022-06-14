"""This module provides the FastAPI API definition."""

import os
import pathlib
from collections.abc import Iterable, Sequence
from typing import Any

from document.config import settings
from document.domain import document_generator, exceptions, model, resource_lookup
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import AnyHttpUrl


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


@app.exception_handler(exceptions.InvalidDocumentRequestException)
def invalid_document_request_exception_handler(
    request: Request, exc: exceptions.InvalidDocumentRequestException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": f"{exc.message}",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.post("/documents")
def document_endpoint(
    document_request: model.DocumentRequest,
    success_message: str = settings.SUCCESS_MESSAGE,
    failure_message: str = settings.FAILURE_MESSAGE,
) -> model.FinishedDocumentDetails:
    """
    Get the document request and hand it off to the document_generator
    module for processing. Return model.FinishedDocumentDetails instance
    containing URL of resulting PDF, or, raise an
    InvalidDocumentRequestException if there is an exception which is
    subsequently caught in the frontend UI.
    """
    # Top level exception handler
    try:
        document_request_key, finished_document_path = document_generator.main(
            document_request
        )
        assert os.path.exists(finished_document_path)
    except Exception:
        logger.exception(
            "There was a error while attempting to fulfill the document "
            "request. Likely reason is the following exception:"
        )
        # NOTE It might not always be the case that an exception here
        # is as a result of an invalid document request, but it often
        # is.
        raise exceptions.InvalidDocumentRequestException(message=failure_message)
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


@app.get("/html/{document_request_key}")
def serve_html_document(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> FileResponse:
    """Serve the requested HTML document."""
    path = "{}.html".format(os.path.join(output_dir, document_request_key))
    return FileResponse(
        path=path,
        filename=pathlib.Path(path).name,
        headers={"Content-Disposition": "inline"},
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
    """Return list of all available resource codes."""
    return resource_lookup.resource_codes_for_lang(lang_code)


@app.get("/resource_codes")
def resource_codes() -> Any:
    """Return list of all available resource codes."""
    return resource_lookup.resource_codes()


@app.get("/health/status")
def health_status() -> tuple[dict[str, str], int]:
    """Ping-able server endpoint."""
    return {"status": "ok"}, 200
