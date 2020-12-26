from document.domain import resource_lookup


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
