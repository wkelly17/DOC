import os
import pathlib
import re

import bs4
import pytest
import requests
from document.config import settings
from document.entrypoints.app import app
from tests.shared.utils import (
    check_finished_document_with_verses_success,
    check_finished_document_with_body_success,
    check_finished_document_without_verses_success,
)
from fastapi.testclient import TestClient

from document.domain import model

##################################################
## Tests for assembly strategy book -hen-language


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
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
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_epub_by_chapter() -> None:
    with TestClient(app=app) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": True,
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
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="epub")


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
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
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
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
        check_finished_document_with_verses_success(response)


def test_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
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
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_tl_ulb_col_tl_tn_col_tl_tq_col_tl_tw_col_tl_udb_col_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
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
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_tl_ulb_col_tl_tn_col_tl_tq_col_tl_tw_col_tl_udb_col_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
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
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_tl_ulb_col_tl_tn_col_tl_tq_col_tl_tw_col_tl_udb_col_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_tl_ulb_col_tl_tn_col_tl_tq_col_tl_tw_col_tl_udb_col_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
                        "lang_code": "tl",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "tl",
                        "resource_type": "udb",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": None,
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


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": None,
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


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": None,
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


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": None,
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


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_en_ulb_wa_col_en_tq_wa_col_sw_ulb_col_sw_tq_col_sw_ulb_tit_sw_tq_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_tn_tit_sw_tq_tit_sw_tw_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tn_wa_col_en_tw_wa_col_sw_tn_col_sw_tw_col_sw_tn_tit_sw_tw_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tq_wa_col_en_tw_wa_col_sw_tq_col_sw_tw_col_sw_tq_tit_sw_tw_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tw_wa_col_sw_tw_col_sw_tw_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tw_wa_col_sw_tw_col_sw_tw_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
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
        check_finished_document_with_body_success(response)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tn_wa_col_en_tq_wa_col_sw_tn_col_sw_tq_col_sw_tn_tit_sw_tq_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tq_wa_col_sw_tq_col_sw_tq_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_body_success(response)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_tn_wa_col_sw_tn_col_sw_tn_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
        check_finished_document_with_body_success(response)


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_en_ulb_wa_col_sw_ulb_col_sw_ulb_tit_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_gu_ulb_mrk_gu_tn_mrk_gu_tq_mrk_gu_tw_mrk_gu_udb_mrk_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_ceb_ulb_mrk_ceb_tw_mrk_ceb_tq_mrk_ceb_tn_mrk_fr_ulb_mrk_fr_tw_mrk_fr_tq_mrk_fr_tn_mrk_fr_f10_mrk_pt_br_ulb_mrk_pt_br_tw_mrk_pt_br_tq_mrk_pt_br_tn_mrk_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "ceb",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "ceb",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "ceb",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "ceb",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_ceb_ulb_mrk_ceb_tw_mrk_ceb_tq_mrk_ceb_tn_mrk_fr_ulb_mrk_fr_tw_mrk_fr_tq_mrk_fr_tn_mrk_fr_f10_mrk_pt_br_ulb_mrk_pt_br_tw_mrk_pt_br_tq_mrk_pt_br_tn_mrk_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "ceb",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "ceb",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "ceb",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "ceb",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "mrk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "mrk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_tw_mrk_mr_udb_mrk_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tn_mrk_mr_tq_mrk_mr_udb_mrk_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tn_mrk_mr_tw_mrk_mr_udb_mrk_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tn_mrk_mr_udb_mrk_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_mr_ulb_mrk_mr_tq_mrk_mr_udb_mrk_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_ulb_gen_tl_udb_gen_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_ulb_gen_tl_udb_gen_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_gu_tn_mat_gu_tq_mat_gu_tw_mat_gu_udb_mat_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_gu_tn_mat_gu_tq_mat_gu_udb_mat_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_tn_gen_tl_tw_gen_tl_udb_gen_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_tq_gen_tl_udb_gen_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_tq_gen_tl_udb_gen_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_tw_gen_tl_udb_gen_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_tw_gen_tl_udb_gen_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_udb_gen_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_tl_udb_gen_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_book_language_order_1c_by_chapter() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_udb_rev_book_language_order_1c_c_by_chapter() -> None:
    """Demonstrate listing unfound resources, in this case fr-udb-rev"""
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_book_language_order_1c_by_chapter() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_fr_ulb_rev_fr_tn_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_book_language_order_1c_c_by_chapter() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_book_language_order_1c_by_chapter() -> None:
    """
    Demonstrate two USFM resources, French, and use of a special
    USFM resource: f10.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_fr_ulb_rev_fr_tq_rev_fr_tw_rev_fr_f10_rev_book_language_order_1c_c_by_chapter() -> None:
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
def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_book_language_order_1c_by_chapter() -> None:
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
def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_book_language_order_1c_c_by_chapter() -> None:
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


# Content team don't want udb used so now that it is configured out of
# the usfm resource types, this test fails.
@pytest.mark.skip
def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_ndh_x_chindali_reg_mat_ndh_x_chindali_tn_mat_ndh_x_chindali_tq_mat_ndh_x_chindali_tw_mat_ndh_x_chindali_udb_mat_book_language_order_1c_by_chapter() -> None:
    """
    Show that the succeeding resource request's, fr-f10-rev,
    content is rendered and the failing resource requests are reported
    on the cover page of the PDF.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "reg",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tn",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tq",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tw",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
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
def test_fr_ulb_rev_fr_tw_rev_fr_udb_rev_ndh_x_chindali_reg_mat_ndh_x_chindali_tn_mat_ndh_x_chindali_tq_mat_ndh_x_chindali_tw_mat_ndh_x_chindali_udb_mat_book_language_order_1c_c_by_chapter() -> None:
    """
    Show that the succeeding resource request's, fr-f10-rev,
    content is rendered and the failing resource requests are reported
    on the cover page of the PDF.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "reg",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tn",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tq",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tw",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
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
def test_ndh_x_chindali_reg_mat_ndh_x_chindali_tn_mat_ndh_x_chindali_tq_mat_ndh_x_chindali_tw_mat_ndh_x_chindali_udb_mat_book_language_order_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "reg",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tn",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tq",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "tw",
                        "book_code": "mat",
                    },
                    {
                        "lang_code": "ndh-x-chindali",
                        "resource_type": "udb",
                        "book_code": "mat",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
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


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
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


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
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


def test_es_ulb_col_es_tn_col_en_tq_col_es_tw_col_book_language_order_1c_by_chapter() -> None:
    """
    Ask for a combination of available and unavailable resources.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_es_ulb_col_es_tn_col_en_tq_col_es_tw_col_book_language_order_1c_c_by_chapter() -> None:
    """
    Ask for a combination of available and unavailable resources.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "es",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_llx_ulb_col_llx_tn_col_en_tq_col_llx_tw_col_book_language_order_1c_by_chapter() -> None:
    """
    Ask for an unavailable resource and assert that the verses_html is
    not generated.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "llx",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_llx_ulb_col_llx_tn_col_en_tq_col_llx_tw_col_book_language_order_1c_c_by_chapter() -> None:
    """
    Ask for an unavailable resource and assert that the verses_html is
    not generated.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "llx",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_llx_reg_col_llx_tn_col_en_tq_col_llx_tw_col_book_language_order_1c_by_chapter() -> None:
    """
    Ask for an unavailable resource and assert that the verses_html is
    not generated.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "llx",
                        "resource_type": "reg",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_llx_reg_col_llx_tn_col_en_tq_col_llx_tw_col_book_language_order_1c_c_by_chapter() -> None:
    """
    Ask for an unavailable resource and assert that the verses_html is
    not generated.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "llx",
                        "resource_type": "reg",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "llx",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_es_419_ulb_col_es_419_tn_col_es419_tq_col_es_419_tw_col_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
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
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_es_419_ulb_col_es_419_tn_col_es419_tq_col_es_419_tw_col_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
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
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_es_419_ulb_rom_es_419_tn_rom_es_419_tq_rom_es_419_tw_rom_pt_br_ulb_rom_pt_br_tn_rom_pt_br_tq_rom_pt_br_tw_rom_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_es_419_ulb_rom_es_419_tn_rom_es_419_tq_rom_es_419_tw_rom_pt_br_ulb_rom_pt_br_tn_rom_pt_br_tq_rom_pt_br_tw_rom_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order_1c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order_1c_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_rom_en_tn_wa_rom_en_tq_wa_rom_en_tw_wa_rom_zh_cuv_wa_rom_zh_cuv_tn_wa_rom_zh_cuv_tq_wa_rom_zh_cuv_tw_wa_rom_book_language_order_2c_sl_sr_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_wa_rom_en_tn_wa_rom_en_tq_wa_rom_en_tw_wa_rom_zh_cuv_wa_rom_zh_cuv_tn_wa_rom_zh_cuv_tq_wa_rom_zh_cuv_tw_wa_rom_book_language_order_2c_sl_sr_c_by_chapter() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tq",
                        "book_code": "rom",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tw",
                        "book_code": "rom",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)
