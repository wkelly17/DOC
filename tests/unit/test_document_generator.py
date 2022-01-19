import re

from document.config import settings
from document.domain import model, document_generator


def test_coalesce_english_tn_requests() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = (
        model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    )
    resource_requests: list[model.ResourceRequest] = []
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
    resource_requests.append(
        model.ResourceRequest(lang_code="en", resource_type="tn", resource_code="gen")
    )
    resource_requests.append(
        model.ResourceRequest(lang_code="mr", resource_type="ulb", resource_code="gen")
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="erk-x-erakor", resource_type="reg", resource_code="eph"
        )
    )
    document_request = model.DocumentRequest(
        email_address=settings.FROM_EMAIL_ADDRESS,
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )
    assert len(document_request.resource_requests) == 5
    resource_requests_ = document_generator.coalesce_english_tn_requests(
        document_request.resource_requests
    )
    # Extra tn resource request is filtered out, leaving 4 instead of
    # 5 resource requests.
    assert len(resource_requests_) == 4


def test_document_request_key_too_long_for_semantic_result() -> None:
    """
    Use enough resource requests that a semantic name built from them
    will be too long which will cause the document request key algorithm
    to use a timestamp-based, non-semantic, name.
    """
    components = [
        (
            "bdf",
            "reg",
            "mat",
        ),
        (
            "bdf",
            "reg",
            "mrk",
        ),
        (
            "pt-br",
            "ulb",
            "mat",
        ),
        (
            "pt-br",
            "tw",
            "mat",
        ),
        (
            "pt-br",
            "tq",
            "mat",
        ),
        (
            "pt-br",
            "tn",
            "mat",
        ),
        (
            "pt-br",
            "ulb",
            "mrk",
        ),
        (
            "pt-br",
            "tw",
            "mrk",
        ),
        (
            "pt-br",
            "tq",
            "mrk",
        ),
        (
            "pt-br",
            "tn",
            "mrk",
        ),
        ("fr", "ulb", "mat"),
        ("fr", "tw", "mat"),
        ("fr", "tq", "mat"),
        ("fr", "tn", "mat"),
        ("fr", "f10", "mat"),
        ("fr", "ulb", "mrk"),
        ("fr", "tw", "mrk"),
        ("fr", "tq", "mrk"),
        ("fr", "tn", "mrk"),
        ("fr", "f10", "mrk"),
    ]
    resource_requests = [
        model.ResourceRequest(
            lang_code=component[0],
            resource_type=component[1],
            resource_code=component[2],
        )
        for component in components
    ]
    assembly_strategy_kind = model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
    key = document_generator.document_request_key(
        resource_requests, assembly_strategy_kind
    )
    assert re.search(r"[0-9]+_[0-9]+", key)
