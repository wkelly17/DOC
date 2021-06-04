"""This module provides fixtures for e2e tests."""

import itertools
import pathlib
import pydantic
import pytest
import random

from typing import Any, List, Tuple
from document import config
from document.domain import bible_books, model
from document.utils import file_utils

# Good enough for now. May put in config.py later.
PASSING_NON_ENGLISH_LANG_CODES = ["pt-br", "tl", "es-419", "zh"]
# PASSING_NON_ENGLISH_LANG_CODES = ["es-419", "zh"]
FAILING_NON_ENGLISH_LANG_CODES = [
    "kbt",
    "aau",
    "tbg-x-abuhaina",
    "abz",
    "abu",
    "guq",
    "am",
]
# ALL_LANGUAGE_CODES = file_utils.load_json_object(pathlib.Path("./language_codes.json"))


@pytest.fixture()
def english_lang_code() -> str:
    return "en"


@pytest.fixture(params=PASSING_NON_ENGLISH_LANG_CODES)
# type of request is actually _pytest.fixtures.FixtureRequest
def non_english_lang_code(request: Any) -> str:
    """
    Get all non-English language codes, but one per request.

    NOTE This is not currently used. Once a set of non-English
    language codes which are known to pass the test are identified,
    this can be used to test all of them one at a time.
    """
    return request.param


@pytest.fixture()
def random_non_english_lang_code() -> str:
    """
    Return a randomly chosen non-English language code that we
    want to test.
    """
    return random.choice(PASSING_NON_ENGLISH_LANG_CODES)


@pytest.fixture()
def random_non_english_lang_code2() -> str:
    """
    Return a randomly chosen non-English language code that we
    want to test. This fixture is used when we want a second random
    non-English language code for the case where we want a document
    request with more than one non-English language in it.
    """
    return random.choice(PASSING_NON_ENGLISH_LANG_CODES)


@pytest.fixture()
def random_failing_non_english_lang_code() -> str:
    """
    Return a randomly chosen non-English language code for a language
    which currently fails due to an issue with its resources' asset
    files, e.g., malformed USFM (this could be because the USFM file
    does not start with an ID element which the parser requires).
    """
    return random.choice(FAILING_NON_ENGLISH_LANG_CODES)


@pytest.fixture(params=bible_books.BOOK_NAMES.keys())
def resource_code(request: Any) -> str:
    """All book names sequentially, but one at a time."""
    return request.param


@pytest.fixture()
def random_resource_code() -> str:
    """One random book name chosen at random."""
    book_ids = list(bible_books.BOOK_NAMES.keys())
    return random.choice(book_ids)


@pytest.fixture()
def random_resource_code2() -> str:
    """One random book name chosen at random. This fixture exists so
    that we can have a separate book chosen in a two language document
    request."""
    book_ids = list(bible_books.BOOK_NAMES.keys())
    return random.choice(book_ids)


@pytest.fixture(params=[config.get_to_email_address()])
def email_address(request: Any) -> str:
    return request.param


@pytest.fixture(params=[model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER])
def assembly_strategy_kind(request: Any) -> str:
    return request.param


@pytest.fixture()
def english_resource_types() -> List[str]:
    """All the English resource types."""
    return ["ulb-wa", "tn-wa", "tq-wa", "tw-wa"]


@pytest.fixture()
def non_english_resource_types() -> List[str]:
    """All the non-English resource types."""
    return ["ulb", "tn", "tq", "tw"]


@pytest.fixture()
def english_resource_type_combos(english_resource_types: List[str]) -> List[Tuple]:
    """
    All possible combinations, in the mathematical sense, of
    English resource types. See documentation for
    itertools.combinations for the combinatoric algorithm.
    """
    resource_type_combos = []
    for idx in range(1, len(english_resource_types)):
        resource_type_combos.extend(
            list(itertools.combinations(english_resource_types, idx))
        )
    return resource_type_combos


@pytest.fixture()
def non_english_resource_type_combos(
    non_english_resource_types: List[str],
) -> List[Tuple]:
    """
    All possible combinations, in the mathematical sense, of
    non-English resource types. See documentation for
    itertools.combinations for the combinatoric algorithm.
    """
    resource_type_combos = []
    for idx in range(1, len(non_english_resource_types)):
        resource_type_combos.extend(
            list(itertools.combinations(non_english_resource_types, idx))
        )
    return resource_type_combos


@pytest.fixture()
def random_english_resource_type_combo(
    english_resource_type_combos: List[List[str]],
) -> List[str]:
    """
    A random choice of one set of all possible English resource type
    combination sets, e.g., ulb-wa, tn-wa, tw-wa; or, ulb-wa, tn-wa,
    tw-wa; or ulb-wa, tn-wa, tq-wa, tw-wa; etc..
    """
    return random.choice(english_resource_type_combos)


@pytest.fixture()
def random_non_english_resource_type_combo(
    non_english_resource_type_combos: List[List[str]],
) -> List[str]:
    """
    A random choice of one set of all possible non-English resource type
    combination sets, e.g., ulb, tn, tw; or, ulb, tn, tw; or ulb, tn,
    tq, tw; etc..
    """
    return random.choice(non_english_resource_type_combos)


@pytest.fixture()
def english_resource_requests(
    english_lang_code: str,
    random_english_resource_type_combo: List[str],
    resource_code: str,
) -> List[model.ResourceRequest]:
    """
    Build a list of resource request instances for the set of English
    resource types passed in as a parameter and a resource_code. This
    will cycle through all resource_codes.
    """
    resource_requests = []
    for resource_type in random_english_resource_type_combo:
        resource_requests.append(
            model.ResourceRequest(
                lang_code=english_lang_code,
                resource_type=resource_type,
                resource_code=resource_code,
            )
        )
    return resource_requests


@pytest.fixture()
def random_english_resource_requests(
    english_lang_code: str,
    random_english_resource_type_combo: List[str],
    random_resource_code: str,
) -> List[model.ResourceRequest]:
    """
    Build a list of resource request instances for the set of English
    resource types passed in as a parameter and a randomly chosen
    resource code.
    """
    resource_requests = []
    for resource_type in random_english_resource_type_combo:
        resource_requests.append(
            model.ResourceRequest(
                lang_code=english_lang_code,
                resource_type=resource_type,
                resource_code=random_resource_code,
            )
        )
    return resource_requests


@pytest.fixture()
def random_non_english_resource_requests(
    random_non_english_lang_code: str,
    random_non_english_resource_type_combo: List[str],
    random_resource_code2: str,
) -> List[model.ResourceRequest]:
    """
    Build a list of resource request instances for a randomly chosen
    non-English lang_code, the set of non-English resource types
    passed in as a parameter, and a randomly chosen resource code.
    """
    resource_requests = []
    for resource_type in random_non_english_resource_type_combo:
        resource_requests.append(
            model.ResourceRequest(
                lang_code=random_non_english_lang_code,
                resource_type=resource_type,
                resource_code=random_resource_code2,
            )
        )
    return resource_requests


@pytest.fixture()
def random_failing_non_english_resource_requests(
    random_failing_non_english_lang_code: str,
    random_non_english_resource_type_combo: List[str],
    random_resource_code2: str,
) -> List[model.ResourceRequest]:
    """
    Build a list of resource request instances for a randomly chosen
    non-English lang_code that has ill-formed USFM and thus can fail
    if USFM is requested, the set of non-English resource types
    passed in as a parameter, and a randomly chosen resource code.
    """
    resource_requests = []
    for resource_type in random_non_english_resource_type_combo:
        resource_requests.append(
            model.ResourceRequest(
                lang_code=random_failing_non_english_lang_code,
                resource_type=resource_type,
                resource_code=random_resource_code2,
            )
        )
    return resource_requests


@pytest.fixture()
def random_non_english_resource_requests2(
    random_non_english_lang_code2: str,
    random_non_english_resource_type_combo: List[str],
    random_resource_code: str,
) -> List[model.ResourceRequest]:
    """
    Build a list of resource request instances for a randomly chosen
    non-English lang_code, the set of non-English resource types
    passed in as a parameter, and a randomly chosen resource code.
    """
    resource_requests = []
    for resource_type in random_non_english_resource_type_combo:
        resource_requests.append(
            model.ResourceRequest(
                lang_code=random_non_english_lang_code2,
                resource_type=resource_type,
                resource_code=random_resource_code,
            )
        )
    return resource_requests


@pytest.fixture()
def english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    english_resource_requests: List[model.ResourceRequest],
) -> model.DocumentRequest:
    """Build one English language document request."""
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=english_resource_requests,
    )


@pytest.fixture()
def random_english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    english_resource_requests: List[model.ResourceRequest],
) -> model.DocumentRequest:
    """
    Build one randomly chosen English language document request. This
    fixture does not iterate through all resource codes like
    english_document_request does because it depends on
    random_english_resource_requests rather than
    english_resource_requests which in turn depends on
    random_resource_code rather than resource_code.
    """
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=random_english_resource_requests,
    )


@pytest.fixture()
def random_non_english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    random_non_english_resource_requests: List[model.ResourceRequest],
    random_resource_code: str,
) -> model.DocumentRequest:
    """
    Build one non-English language document request for each
    assembly_strategy_kind, one randomly chosen set of resource
    requests, and one randomly chosen resource code.

    NOTE Many such randomly generated non-English tests will fail
    since non-English language support is not complete with respect to
    resource types or books. Thus we can use this test to find tests
    that we expect to fail and possibly use such tests to identify
    language-resource_type-resource_code combos that should be
    precluded from the front end so as not to waste user's time
    requesting a document that cannot be successfully fulfilled. Or,
    short of that, to help guide us to implementing the graceful
    raising of exceptions and their handlers for such failures.
    """
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=random_non_english_resource_requests,
    )


@pytest.fixture()
def random_failing_non_english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    random_failing_non_english_resource_requests: List[model.ResourceRequest],
    random_resource_code: str,
) -> model.DocumentRequest:
    """
    Build one non-English language document request for each
    assembly_strategy_kind, one randomly chosen set of resource
    requests, and one randomly chosen resource code. This fixture will
    use language codes that are known to have, at this time, non-valid
    (from the perspective of USFM-Tools USFM parser) USFM. Thus if the
    resource requests randomly generated include ULB (or another USFM
    resource type) then they will fail. They may also fail for other
    reasons.

    NOTE We can use this test to find individual tests
    that we expect to fail and possibly use such tests to identify
    lang_code,resource_type,resource_code combos that should be
    precluded from the front end so as not to waste user's time
    requesting a document that cannot be successfully fulfilled. Or,
    short of that, to help guide us to implementing the graceful
    handling of such failures.
    """
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=random_failing_non_english_resource_requests,
    )


# @pytest.fixture(params=[pytest.lazy_fixture("document_request")])

## Multi-language combination fixtures start here:


@pytest.fixture()
def random_english_and_non_english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    random_english_resource_requests: List[model.ResourceRequest],
    random_non_english_resource_requests: List[model.ResourceRequest],
) -> model.DocumentRequest:
    """
    Build one non-English language document request for each
    assembly_strategy_kind, one randomly chosen set of resource
    requests, and one randomly chosen resource code.

    NOTE Many such randomly generated non-English tests will fail
    since non-English language support is not complete with respect to
    resource types or books. Thus we can use this test to find tests
    that we expect to fail and possibly use such tests to identify
    language-resource_type-resource_code combos that should be
    precluded from the front end so as not to waste user's time
    requesting a document that cannot be successfully fulfilled. Or,
    short of that, to help guide us to implementing the graceful
    raising of exceptions and their handlers for such failures.
    """
    random_english_resource_requests.extend(random_non_english_resource_requests)
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=random_english_resource_requests,
    )


@pytest.fixture()
def random_two_non_english_languages_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    random_non_english_resource_requests: List[model.ResourceRequest],
    random_non_english_resource_requests2: List[model.ResourceRequest],
) -> model.DocumentRequest:
    """
    Build one non-English language document request with two
    non-English languages for each assembly_strategy_kind. Each
    language has its own randomly chosen set of resource requests.
    """
    random_non_english_resource_requests.extend(random_non_english_resource_requests2)
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=random_non_english_resource_requests,
    )
