import logging
import os
import time
from typing import Literal

import requests
import yaml
from document.config import settings
from document.domain import model
from document.entrypoints.app import app
from fastapi.testclient import TestClient
from tests.shared.utils import check_finished_document_with_verses_success

logger = settings.logger(__name__)


def test_stream_pdf() -> None:
    """
    Produce verse level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    # First generate the PDF
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )

    check_finished_document_with_verses_success(response, suffix="pdf")
