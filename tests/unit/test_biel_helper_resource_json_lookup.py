from typing import Tuple

from document.domain import resource_lookup


def test_lookup_all_language_codes() -> None:
    assert resource_lookup.lang_codes()


def test_lookup_all_language_codes_and_names() -> None:
    assert resource_lookup.lang_codes_and_names()


def test_lookup_all_resource_types() -> None:
    assert resource_lookup.resource_types()


def test_lookup_all_resource_codes() -> None:
    assert resource_lookup.resource_codes()
