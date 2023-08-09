"""This module provides the FastAPI API definition."""

import os
import pathlib

from typing import Any, Iterable, Sequence


import celery.states
from celery.result import AsyncResult
from document.config import settings
from document.domain import document_generator, exceptions, model, resource_lookup
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, ORJSONResponse
from pydantic import AnyHttpUrl

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
) -> ORJSONResponse:
    logger.error(f"{request}: {exc}")
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": f"{exc.message}",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return ORJSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.post("/documents")
async def generate_document(
    document_request: model.DocumentRequest,
    success_message: str = settings.SUCCESS_MESSAGE,
) -> ORJSONResponse:
    """
    Get the document request and hand it off to the document_generator
    module for processing. Return model.FinishedDocumentDetails instance
    containing URL of resulting output file, or, raise an
    InvalidDocumentRequestException if there is an exception which is
    subsequently caught in the frontend UI.
    """
    # Top level exception handler
    try:
        task = document_generator.main.apply_async(args=(document_request.json(),))
    except HTTPException as exc:
        raise exc
    except Exception as exc:  # catch any exceptions we weren't expecting, handlers handle the ones we do expect.
        logger.exception(
            "There was an error while attempting to fulfill the document "
            "request. Likely reason is the following exception:"
        )
        # Handle exceptions that aren't handled otherwise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
    else:
        logger.debug("task_id: %s", task.id)
        return ORJSONResponse({"task_id": task.id})


@app.post("/documents_docx")
async def generate_docx_document(
    document_request: model.DocumentRequest,
    success_message: str = settings.SUCCESS_MESSAGE,
) -> ORJSONResponse:
    """
    Get the document request and hand it off to the document_generator
    module for processing. Return model.FinishedDocumentDetails instance
    containing URL of resulting Docx, or, raise an
    InvalidDocumentRequestException if there is an exception which is
    subsequently caught in the frontend UI.
    """
    # Top level exception handler
    try:
        task = document_generator.alt_main.apply_async(args=(document_request.json(),))
    except HTTPException as exc:
        raise exc
    except Exception as exc:  # catch any exceptions we weren't expecting, handlers handle the ones we do expect.
        logger.exception(
            "There was an error while attempting to fulfill the document "
            "request. Likely reason is the following exception:"
        )
        # Handle exceptions that aren't handled otherwise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
    else:
        logger.debug("task_id: %s", task.id)
        return ORJSONResponse({"task_id": task.id})


@app.get("/task_status/{task_id}")
async def task_status(task_id: str) -> ORJSONResponse:
    res: AsyncResult[dict[str, str]] = AsyncResult(task_id)
    if res.state == celery.states.SUCCESS:
        return ORJSONResponse({"state": celery.states.SUCCESS, "result": res.result})
    return ORJSONResponse(
        {
            "state": res.state,
        }
    )


@app.get("/language_codes_names_and_resource_types")
async def lang_codes_names_and_resource_types() -> Iterable[model.CodeNameTypeTriplet]:
    """
    Return list of tuples of lang_code, lang_name, resource_types for
    all available language codes.
    """
    return resource_lookup.lang_codes_names_and_resource_types()


@app.get("/language_codes")
async def lang_codes() -> Iterable[str]:
    """Return list of all available language codes."""
    return resource_lookup.lang_codes()


@app.get("/language_codes_and_names")
async def lang_codes_and_names() -> Sequence[tuple[str, str]]:
    """
    Return list of all available language code, name tuples.
    """
    return resource_lookup.lang_codes_and_names()


@app.get("/language_codes_and_names_v1")
async def lang_codes_and_names_for_v1() -> Sequence[tuple[str, str]]:
    """
    Return list of available gateway language code, name tuples.
    """
    return resource_lookup.lang_codes_and_names_for_v1()


@app.get("/resource_types")
async def resource_types() -> Any:
    """Return list of all available resource types."""
    return resource_lookup.resource_types()


@app.get("/resource_types_v1")
async def resource_types_for_v1() -> Any:
    """Return list of resource types approved for v1 release."""
    return resource_lookup.resource_types_for_v1()


@app.get("/resource_types_for_lang/{lang_code}")
async def resource_types_for_lang(lang_code: str) -> Sequence[Any]:
    """Return list of available resource types for lang_code."""
    return resource_lookup.resource_types_for_lang(lang_code)


@app.get("/resource_types_and_names_for_lang/{lang_code}")
async def resource_types_and_names_for_lang(lang_code: str) -> list[tuple[str, str]]:
    """Return list of available resource types and their names for lang_code."""
    return resource_lookup.resource_types_and_names_for_lang(lang_code)


@app.get("/resource_types_and_names_for_lang_v1/{lang_code}")
async def resource_types_and_names_for_lang_for_v1_release(
    lang_code: str,
) -> Sequence[Any]:
    """Return list of available resource types and their names for lang_code."""
    return resource_lookup.resource_types_and_names_for_lang_for_v1_release(lang_code)


@app.get("/shared_resource_codes/{lang0_code}/{lang1_code}")
async def shared_resource_codes(lang0_code: str, lang1_code: str) -> Sequence[Any]:
    """
    Return list of available resource codes common to both lang0_code and lang1_code.
    """
    return resource_lookup.shared_resource_codes(lang0_code, lang1_code)


@app.get("/resource_types/{lang_code}/")
async def shared_resource_types(
    lang_code: str,
    resource_codes: Sequence[str] = Query(default=None),
) -> Iterable[tuple[str, str]]:
    """
    Return the list of available resource types tuples for lang_code
    with resource_codes.
    """
    return resource_lookup.shared_resource_types(lang_code, resource_codes)


@app.get("/resource_types_v1/{lang_code}/")
async def shared_resource_types_for_v1(
    lang_code: str,
    resource_codes: Sequence[str] = Query(default=None),
) -> Iterable[tuple[str, str]]:
    """
    Return the list of v1 release approved resource types tuples for lang_code
    with resource_codes.
    """
    return resource_lookup.shared_resource_types_for_v1(lang_code, resource_codes)


@app.get("/resource_codes_for_lang/{lang_code}")
async def resource_codes_for_lang(lang_code: str) -> Sequence[tuple[str, str]]:
    """Return list of all available resource codes."""
    return resource_lookup.resource_codes_for_lang(lang_code)


@app.get("/resource_codes")
async def resource_codes() -> Any:
    """Return list of all available resource codes."""
    return resource_lookup.resource_codes()


@app.get("/health/status")
async def health_status() -> tuple[dict[str, str], int]:
    """Ping-able server endpoint."""
    return {"status": "ok"}, 200
