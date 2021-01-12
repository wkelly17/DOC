import os
from typing import List

from document import config
from document.domain import document_generator, model


def test_document_generator_for_english_with_interleaving_by_book() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.book
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

    finished_document_path = "en-ulb-wa-jud_en-tn-wa-jud_book.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())


def test_document_generator_for_english_with_interleaving_by_verse() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.verse
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
    finished_document_path = "en-ulb-wa-jud_en-tn-wa-jud_verse.html"
    finished_document_path = os.path.join(
        config.get_output_dir(), finished_document_path
    )
    assert finished_document_path == doc_gen.get_finished_document_filepath()
    assert os.path.isfile(doc_gen.get_finished_document_filepath())
