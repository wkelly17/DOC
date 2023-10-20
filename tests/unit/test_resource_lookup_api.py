import os
from document.config import settings

from document.domain import model, resource_lookup


def test_lookup_successes() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = (
        model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    )
    assembly_layout_kind: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN
    resource_requests: list[model.ResourceRequest] = [
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="gen"
        ),
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="gen"
        ),
        model.ResourceRequest(lang_code="mr", resource_type="ulb", resource_code="gen"),
        model.ResourceRequest(
            lang_code="erk-x-erakor", resource_type="reg", resource_code="eph"
        ),
    ]
    document_request = model.DocumentRequest(
        email_address=settings.FROM_EMAIL_ADDRESS,
        assembly_strategy_kind=assembly_strategy_kind,
        assembly_layout_kind=assembly_layout_kind,
        layout_for_print=True,
        generate_pdf=True,
        generate_epub=False,
        generate_docx=False,
        resource_requests=resource_requests,
    )
    for resource_request in document_request.resource_requests:
        resource_lookup_dto = resource_lookup.resource_lookup_dto(
            resource_request.lang_code,
            resource_request.resource_type,
            resource_request.resource_code,
        )
        assert resource_lookup_dto.url


# NOTE This fails because zh doesn't use ulb for its USFM resource
# type but 'cuv' instead, i.e., zh ulb is a special case.
def test_lookup_failures() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = (
        model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    )
    assembly_layout_kind: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN
    resource_requests: list[model.ResourceRequest] = [
        model.ResourceRequest(lang_code="zh", resource_type="ulb", resource_code="jol")
    ]
    document_request = model.DocumentRequest(
        email_address=settings.FROM_EMAIL_ADDRESS,
        assembly_strategy_kind=assembly_strategy_kind,
        assembly_layout_kind=assembly_layout_kind,
        layout_for_print=False,
        generate_pdf=True,
        generate_epub=False,
        generate_docx=False,
        resource_requests=resource_requests,
    )

    for resource_request in document_request.resource_requests:
        resource_lookup_dto = resource_lookup.resource_lookup_dto(
            resource_request.lang_code,
            resource_request.resource_type,
            resource_request.resource_code,
        )
        assert not resource_lookup_dto.url
