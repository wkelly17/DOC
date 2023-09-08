from typing import Tuple

from document.domain import resource_lookup


def test_lookup_all_language_codes_and_names() -> None:
    assert resource_lookup.lang_codes_and_names()




