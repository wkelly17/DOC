from typing import List

import os

from document import config
from document.domain import model
from document.domain import document_generator


def test_document_generator_for_english() -> None:
    filename = "en-ulb-wa-gen_en-tn-wa-gen.html"
    filepath = os.path.join(config.get_output_dir(), filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.BOOK
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="gen"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="gen"
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
    assert os.path.isfile(
        os.path.join(config.get_working_dir(), "en-ulb-wa-gen_en-tn-wa-gen.html")
    )
