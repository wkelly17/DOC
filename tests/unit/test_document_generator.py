import bs4
import os
import pytest
import re
from typing import List

from document import config
from document.domain import document_generator, model


def test_document_generator_for_english_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="jud"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="jud"
        )
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()
    assert doc_gen._document_request_key

    finished_document_path = "en-ulb-wa-jud_en-tn-wa-jud_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())


def test_document_generator_for_english_multichapter_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="tit"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="tit"
        )
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = "en-ulb-wa-tit_en-tn-wa-tit_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())


def test_document_generator_for_swahili_with_ulb_tn_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="col")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = "sw-ulb-col_sw-tn-col_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_ulb")
    assert os.path.isdir("working/temp/sw_tn")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        assert verses_html


def test_document_generator_for_swahili_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="tit")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="tit")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = (
        "sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_language_book_order.html"
    )
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_ulb")
    assert os.path.isdir("working/temp/sw_tn")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        assert verses_html


def test_document_generator_for_english_and_swahili_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="tit")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="tit")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = "en-ulb-wa-col_en-tn-wa-col_sw-ulb-col_sw-tn-col_sw-ulb-tit_sw-tn-tit_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_ulb")
    assert os.path.isdir("working/temp/sw_tn")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        assert verses_html


def test_document_generator_for_english_and_swahili_usfm_tn_tq_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tq-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tq", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="tit")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="tit")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tq", resource_code="tit")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = "en-ulb-wa-col_en-tn-wa-col_en-tq-wa-col_sw-ulb-col_sw-tn-col_sw-tq-col_sw-ulb-tit_sw-tn-tit_sw-tq-tit_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_ulb")
    assert os.path.isdir("working/temp/sw_tn")
    assert os.path.isdir("working/temp/sw_tq")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        assert verses_html


def test_document_generator_for_english_and_swahili_tn_only_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tn", resource_code="tit")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = "en-tn-wa-col_sw-tn-col_sw-tn-tit_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_tn")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        assert re.search(r"Translation note", html)


def test_document_generator_for_english_and_swahili_usfm_only_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="ulb", resource_code="tit")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = (
        "en-ulb-wa-col_sw-ulb-col_sw-ulb-tit_language_book_order.html"
    )
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_ulb")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        parser = bs4.BeautifulSoup(html, "html.parser")
        body: bs4.elements.ResultSet = parser.find_all("body")
        assert body
        verses_html: bs4.elements.ResultSet = parser.find_all(
            "span", attrs={"class": "v-num"}
        )
        assert verses_html


@pytest.mark.skip
def test_document_generator_for_english_and_swahili_tq_only_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tq-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tq", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tq", resource_code="tit")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = "en-tq-wa-col_sw-tq-col_sw-tq-tit_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_tq")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        assert re.search(r"Translation note", html)


@pytest.mark.skip
def test_document_generator_for_english_and_swahili_tw_only_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tw-wa", resource_code="col"
        )
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tw", resource_code="col")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="sw", resource_type="tw", resource_code="tit")
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()

    assert doc_gen._document_request_key
    finished_document_path = "en-tw-wa-col_sw-tw-col_sw-tw-tit_language_book_order.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
    assert os.path.isdir("working/temp/sw_tw")
    with open(doc_gen.get_finished_document_filepath(), "r") as fin:
        html = fin.read()
        assert re.search(r"Translation note", html)
