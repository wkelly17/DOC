from document import config
from document.domain import resource_lookup
from document.domain import model
from document.domain.resource import resource_factory


## Test the API:


def test_lookup() -> None:
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


## Test BIELHelperResourceJsonLookup service


def test_lookup_all_language_codes() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    values = lookup_svc.lang_codes()
    assert len(values) > 0


def test_lookup_all_language_codes_and_names() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    values: List[Tuple[str, str]] = lookup_svc.lang_codes_and_names()
    assert len(values) > 0


def test_lookup_all_resource_types() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    values: List[str] = lookup_svc.resource_types()
    assert len(values) > 0


def test_lookup_all_resource_codes() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    values: List[str] = lookup_svc.resource_codes()
    assert len(values) > 0


## A few random tests exercising jsonpath


def test_lookup_downloads_at_reg() -> None:
    lookup_svc = resource_lookup.USFMResourceJsonLookup()
    jsonpath_str = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)
    assert len(values) > 0


def test_lookup_usfm_downloads() -> None:
    """ Find all the git repos to determine all the locations they can
    be found in translations.json. """
    lookup_svc = resource_lookup.USFMResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)
    assert len(values) > 0


def test_lookup_tresource_downloads() -> None:
    """ Find all the git repos to determine all the locations they can
    be found in translations.json. """
    lookup_svc = resource_lookup.TResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)
    assert len(values) > 0


def test_lookup_usfm_downloads_not_at_reg() -> None:
    lookup_svc = resource_lookup.USFMResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))

    assert len(values2) > 0
    # assert len(result) > 0


def test_lookup_tresource_downloads_not_at_reg() -> None:
    lookup_svc = resource_lookup.TResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))

    assert len(values2) > 0
    # assert len(result) > 0


def test_lookup_usfm_downloads_not_at_reg2() -> None:
    lookup_svc = resource_lookup.USFMResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))

    assert len(values2) > 0
    # assert len(result) > 0


def test_lookup_tresource_downloads_not_at_reg2() -> None:
    lookup_svc = resource_lookup.TResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    result = list(filter(lambda x: x not in values, values2))

    assert len(values2) > 0
    # assert len(result) > 0


def test_lookup_usfm_downloads_not_at_reg3() -> None:
    lookup_svc = resource_lookup.USFMResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    jsonpath_str3 = (
        "$[*].contents[?code='ulb'].subcontents[*].links[?format='Download'].url"
    )
    values3: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str3)

    jsonpath_str4 = (
        "$[*].contents[?code='udb'].subcontents[*].links[?format='Download'].url"
    )
    values4: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str4)

    assert len(values) > 0
    assert len(values2) > 0
    assert len(values3) > 0
    assert len(values4) > 0


def test_lookup_tresource_downloads_not_at_reg3() -> None:
    lookup_svc = resource_lookup.TResourceJsonLookup()
    jsonpath_str = "$[*].contents[*].subcontents[*].links[?format='Download'].url"
    values: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str)

    jsonpath_str2 = (
        "$[*].contents[?code='reg'].subcontents[*].links[?format='Download'].url"
    )
    values2: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str2)

    jsonpath_str3 = (
        "$[*].contents[?code='ulb'].subcontents[*].links[?format='Download'].url"
    )
    values3: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str3)

    jsonpath_str4 = (
        "$[*].contents[?code='udb'].subcontents[*].links[?format='Download'].url"
    )
    values4: List[str] = lookup_svc.resource_json_lookup._lookup(jsonpath_str4)

    assert len(values) > 0
    assert len(values2) > 0
    assert len(values3) > 0
    assert len(values4) > 0


def test_all_tn_zip_urls_lookup() -> None:
    # For all languages
    lookup_svc = resource_lookup.TResourceJsonLookup()
    download_urls: List[str] = lookup_svc.resource_json_lookup._lookup(
        "$[*].contents[?code='tn'].links[?format='zip'].url",
    )
    assert len(download_urls) > 0
