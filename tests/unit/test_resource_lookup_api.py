from document import config
from document.domain import resource_lookup
from document.domain import model
from document.domain.resource import resource_factory


## Test the API:


def test_lookup() -> None:
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.book
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

    resource_requests.append(
        model.ResourceRequest(lang_code="mr", resource_type="ulb", resource_code="gen")
    )

    resource_requests.append(
        model.ResourceRequest(
            lang_code="erk-x-erakor", resource_type="reg", resource_code="eph"
        )
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    for resource_request in document_request.resource_requests:
        r = resource_factory(
            config.get_working_dir(), config.get_output_dir(), resource_request
        )
        r.find_location()
        assert r._resource_url
