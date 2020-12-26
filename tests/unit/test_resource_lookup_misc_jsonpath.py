from document.domain import resource_lookup

## A few random tests exercising jsonpath of no real use for the API,
## but just doing some jsonpath experiments.


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
