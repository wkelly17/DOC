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
