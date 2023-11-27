import os
import pathlib
import re

import bs4
import pytest
import requests
from document.config import settings
from document.entrypoints.app import app
from fastapi.testclient import TestClient
from tests.shared.utils import (
    check_finished_document_with_verses_success,
    check_finished_document_without_verses_success,
)
from document.domain import model


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order_1c_by_chapter() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_tit_en_tn_wa_tit_language_book_order_1c_c_by_chapter() -> None:
    "English ulb-wa and tn-wa for book of Timothy."
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tw_wa_col_sw_tw_col_sw_tw_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "mr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "mr",
                        "resource_type": "udb",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_ulb_gen_tl_udb_gen_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_ulb_gen_tl_udb_gen_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tw",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "book_code": "mat",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tw",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "book_code": "mat",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "book_code": "mat",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "gu",
                        "resource_type": "tn",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "tq",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "gu",
                        "resource_type": "udb",
                        "book_code": "mat",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_tq_gen_tl_udb_gen_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_tq_gen_tl_udb_gen_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_tw_gen_tl_udb_gen_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_tw_gen_tl_udb_gen_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_udb_gen_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_tl_udb_gen_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c_by_chapter() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "udb",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c_c_by_chapter() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "udb",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c_by_chapter() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c_c_by_chapter() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c_by_chapter() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_language_book_order_1c_c_by_chapter() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c_by_chapter() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_language_book_order_1c_c_by_chapter() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "rev",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "rev",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
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
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
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
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# NOTE This test succeeds in that it throws an expected exception
# (oxymoron I know). The problem is that celery can't pickle it because
# the exception's type differs from what celery's pickling subsystem was
# expecting. This can be and was diagnosed by consulting the celery flower
# dashboard for the task generated by this test.
@pytest.mark.skip
def test_kbt_reg_2co_ajg_reg_2co_pmm_reg_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "ajg",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        # kbt has a malformed asset URL in translations.json so we
        # expect to fail obtaining it through git cloning.
        with pytest.raises(Exception):
            check_finished_document_with_verses_success(response)


# NOTE This test succeeds in that it throws an expected exception
# (oxymoron I know). The problem is that celery can't pickle it because
# the exception's type differs from what celery's pickling subsystem was
# expecting. This can be and was diagnosed by consulting the celery flower
# dashboard for the task generated by this test.
@pytest.mark.skip
def test_kbt_reg_2co_ajg_reg_2co_pmm_reg_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "ajg",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        # kbt has a malformed asset URL in translations.json so we
        # expect to fail obtaining it through git cloning.
        with pytest.raises(Exception):
            check_finished_document_with_verses_success(response)


# NOTE This test succeeds in that it throws an expected exception
# (oxymoron I know). The problem is that celery can't pickle it because
# the exception's type differs from what celery's pickling subsystem was
# expecting. This can be and was diagnosed by consulting the celery flower
# dashboard for the task generated by this test.
@pytest.mark.skip
def test_kbt_reg_2co_ajg_x_adjtalagbe_reg_2co_pmm_reg_mrk_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "ajg-x-adjtalagbe",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        # kbt has a malformed asset URL in translations.json so we
        # expect to fail obtaining it through git cloning.
        with pytest.raises(Exception):
            check_finished_document_with_verses_success(response)


# NOTE This test succeeds in that it throws an expected exception
# (oxymoron I know). The problem is that celery can't pickle it because
# the exception's type differs from what celery's pickling subsystem was
# expecting. This can be and was diagnosed by consulting the celery flower
# dashboard for the task generated by this test.
@pytest.mark.skip
def test_kbt_reg_2co_ajg_x_adjtalagbe_reg_2co_pmm_reg_mrk_language_book_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "kbt",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "ajg-x-adjtalagbe",
                        "resource_type": "reg",
                        "book_code": "2co",
                    },
                    {
                        "lang_code": "pmm",
                        "resource_type": "reg",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        # kbt has a malformed asset URL in translations.json so we
        # expect to fail obtaining it through git cloning.
        with pytest.raises(Exception):
            check_finished_document_with_verses_success(response)


def test_id_ayt_tit_id_tn_tit_language_book_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "id",
                        "resource_type": "ayt",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "id",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_mat_en_bc_wa_mat_language_book_order_1c_by_chapter() -> None:
    """Test bug wherein ulb with commentary bombs whereas ulb with tn and commentary is fine."""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "bc-wa",
                        "book_code": "mat",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)
