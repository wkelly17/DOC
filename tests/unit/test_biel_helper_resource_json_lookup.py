from typing import Tuple

from document.domain import resource_lookup

## Test BIELHelperResourceJsonLookup service


def test_lookup_all_language_codes() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    assert lookup_svc.lang_codes()


def test_lookup_all_language_codes_and_names() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    assert lookup_svc.lang_codes_and_names()


def test_lookup_all_resource_types() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    assert lookup_svc.resource_types()


def test_lookup_all_resource_codes() -> None:
    lookup_svc = resource_lookup.BIELHelperResourceJsonLookup()
    assert lookup_svc.resource_codes()
