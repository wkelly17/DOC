"""This module provides fixtures for e2e tests."""

import itertools
import os
import pathlib
import random
from collections.abc import Sequence
from typing import Any, Optional

import pydantic
import pytest
from document.config import settings
from document.domain import bible_books, model
from document.utils import file_utils

# A blessed set of language codes that can be used to randomly generate
# tests that pass, i.e., they are well supported for all their resource
# types and (hopefully) all their resource codes (i.e., books). These
# are by no means the only language codes that are supported. The more
# included the longer the tests marked 'randomized' will take to run.
PASSING_NON_ENGLISH_LANG_CODES: Sequence[str] = [
    "es-419",
    "fr",
    "gu",
    "mr",
    "pt-br",
    "sw",
    "tl",
    "zh",
]

# Every once in a while, it is good to allow tests against more language
# codes. Here we use all language codes. The system randomized fixtures
# that use PASSING_NON_ENGLISH_LANG_CODES will then have all languages
# to choose from randomly of which it will choose a subset.
if os.environ.get("ALL_LANGUAGE_CODES"):
    json_filepath = "../../language_codes.json"
    ALL_LANGUAGE_CODES = file_utils.load_json_object(pathlib.Path(json_filepath))
    PASSING_NON_ENGLISH_LANG_CODES = ALL_LANGUAGE_CODES

# No known failing languages at this time. It probably means a failing
# sample just hasn't been randomly chosen yet, but when it is we'll
# add it here to ensure it is used.
FAILING_NON_ENGLISH_LANG_CODES: Sequence[str] = [
    # "aau",
    # "abu",
    # "abz",
    # "am",
    # "guq",
    # "kbt",
    # "ndh-x-chindali",
    # "tbg-x-abuhaina",
]


@pytest.fixture()
def english_lang_code() -> str:
    return "en"


@pytest.fixture(params=PASSING_NON_ENGLISH_LANG_CODES)
# Type of request parameter is actually _pytest.fixtures.FixtureRequest
def non_english_lang_code(request: Any) -> Any:
    """Get all non-English language codes, but one per request."""
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
def resource_code(request: Any) -> Any:
    """All book names sequentially, but one at a time."""
    return request.param


@pytest.fixture()
def random_resource_code() -> str:
    """One random book name chosen at random."""
    book_ids: list[str] = list(bible_books.BOOK_NAMES.keys())
    return random.choice(book_ids)


@pytest.fixture()
def random_resource_code2() -> str:
    """One random book name chosen at random. This fixture exists so
    that we can have a separate book chosen in a two language document
    request."""
    book_ids: list[str] = list(bible_books.BOOK_NAMES.keys())
    return random.choice(book_ids)


@pytest.fixture()
def email_address() -> str:
    return str(settings.TO_EMAIL_ADDRESS)


@pytest.fixture()
def assembly_strategy_kind() -> str:
    return str(
        random.choice(
            [
                model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
            ]
        )
    )


@pytest.fixture
def assembly_layout_kind() -> Optional[str]:
    return None  # Choose none to let the system decide


@pytest.fixture
def layout_for_print() -> bool:
    return random.choice([True, False])


@pytest.fixture
def generate_pdf() -> bool:
    return random.choice([True, False])


@pytest.fixture
def generate_epub() -> bool:
    return random.choice([True, False])


@pytest.fixture
def generate_docx() -> bool:
    return random.choice([True, False])


@pytest.fixture()
def english_resource_types() -> Sequence[str]:
    """All the English resource types."""
    return ["ulb-wa", "tn-wa", "tq-wa", "tw-wa", "bc-wa"]


@pytest.fixture()
def non_english_resource_types() -> Sequence[str]:
    """All the non-English resource types."""
    return ["ulb", "reg", "tn", "tq", "tw"]


@pytest.fixture()
def english_resource_type_combos(
    english_resource_types: Sequence[str],
) -> Sequence[tuple[str, ...]]:
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
    non_english_resource_types: Sequence[str],
) -> Sequence[tuple[str, ...]]:
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
    english_resource_type_combos: Sequence[Sequence[str]],
) -> Sequence[str]:
    """
    A random choice of one set of all possible English resource type
    combination sets, e.g., ulb-wa, tn-wa, tw-wa; or, ulb-wa, tn-wa,
    tw-wa; or ulb-wa, tn-wa, tq-wa, tw-wa; etc..
    """
    return random.choice(english_resource_type_combos)


@pytest.fixture()
def random_non_english_resource_type_combo(
    non_english_resource_type_combos: Sequence[Sequence[str]],
) -> Sequence[str]:
    """
    A random choice of one set of all possible non-English resource type
    combination sets, e.g., ulb, tn, tw; or, ulb, tn, tw; or ulb, tn,
    tq, tw; etc..
    """
    return random.choice(non_english_resource_type_combos)


@pytest.fixture()
def english_resource_requests(
    english_lang_code: str,
    random_english_resource_type_combo: Sequence[str],
    resource_code: str,
) -> Sequence[model.ResourceRequest]:
    """
    Build a list of resource request instances for the set of English
    resource types passed in as a parameter and a resource_code. This
    will cycle through all resource_codes.
    """
    resource_requests = [
        model.ResourceRequest(
            lang_code=english_lang_code,
            resource_type=resource_type,
            resource_code=resource_code,
        )
        for resource_type in random_english_resource_type_combo
    ]
    return resource_requests


@pytest.fixture()
def random_english_resource_requests(
    english_lang_code: str,
    random_english_resource_type_combo: Sequence[str],
    random_resource_code: str,
) -> Sequence[model.ResourceRequest]:
    """
    Build a list of resource request instances for the set of English
    resource types passed in as a parameter and a randomly chosen
    resource code.
    """
    resource_requests = [
        model.ResourceRequest(
            lang_code=english_lang_code,
            resource_type=resource_type,
            resource_code=random_resource_code,
        )
        for resource_type in random_english_resource_type_combo
    ]
    return resource_requests


@pytest.fixture()
def random_non_english_resource_requests(
    random_non_english_lang_code: str,
    random_non_english_resource_type_combo: Sequence[str],
    random_resource_code2: str,
) -> Sequence[model.ResourceRequest]:
    """
    Build a list of resource request instances for a randomly chosen
    non-English lang_code, the set of non-English resource types
    passed in as a parameter, and a randomly chosen resource code.
    """
    resource_requests = [
        model.ResourceRequest(
            lang_code=random_non_english_lang_code,
            resource_type=resource_type,
            resource_code=random_resource_code2,
        )
        for resource_type in random_non_english_resource_type_combo
    ]
    return resource_requests


@pytest.fixture()
def random_failing_non_english_resource_requests(
    random_failing_non_english_lang_code: str,
    random_non_english_resource_type_combo: Sequence[str],
    random_resource_code2: str,
) -> Sequence[model.ResourceRequest]:
    """
    Build a list of resource request instances for:
    - a randomly chosen non-English lang_code that has ill-formed USFM and thus can fail
    if USFM is requested,
    - the set of non-English resource types passed in as a parameter, and
    - a randomly chosen resource code.
    """
    resource_requests = [
        model.ResourceRequest(
            lang_code=random_failing_non_english_lang_code,
            resource_type=resource_type,
            resource_code=random_resource_code2,
        )
        for resource_type in random_non_english_resource_type_combo
    ]
    return resource_requests


@pytest.fixture()
def random_non_english_resource_requests2(
    random_non_english_lang_code2: str,
    random_non_english_resource_type_combo: Sequence[str],
    random_resource_code: str,
) -> Sequence[model.ResourceRequest]:
    """
    Build a list of resource request instances for:
    - a randomly chosen non-English lang_code,
    - the set of non-English resource types
    passed in as a parameter, and,
    - a randomly chosen resource code.
    """
    resource_requests = [
        model.ResourceRequest(
            lang_code=random_non_english_lang_code2,
            resource_type=resource_type,
            resource_code=random_resource_code,
        )
        for resource_type in random_non_english_resource_type_combo
    ]
    return resource_requests


@pytest.fixture()
def english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    assembly_layout_kind: model.AssemblyLayoutEnum,
    layout_for_print: bool,
    generate_pdf: bool,
    generate_epub: bool,
    generate_docx: bool,
    english_resource_requests: Sequence[model.ResourceRequest],
) -> model.DocumentRequest:
    """Build one English language document request."""
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        assembly_layout_kind=assembly_layout_kind,
        layout_for_print=layout_for_print,
        generate_pdf=generate_pdf,
        generate_epub=generate_epub,
        generate_docx=generate_docx,
        resource_requests=english_resource_requests,
    )


@pytest.fixture()
def random_non_english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    assembly_layout_kind: model.AssemblyLayoutEnum,
    layout_for_print: bool,
    generate_pdf: bool,
    generate_epub: bool,
    generate_docx: bool,
    random_non_english_resource_requests: Sequence[model.ResourceRequest],
) -> model.DocumentRequest:
    """
    Build one non-English language document request.

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
        assembly_layout_kind=assembly_layout_kind,
        layout_for_print=layout_for_print,
        generate_pdf=generate_pdf,
        generate_epub=generate_epub,
        generate_docx=generate_docx,
        resource_requests=random_non_english_resource_requests,
    )


# FIXME Not used. Consider removing.
@pytest.fixture()
def random_failing_non_english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    assembly_layout_kind: model.AssemblyLayoutEnum,
    layout_for_print: bool,
    generate_pdf: bool,
    generate_epub: bool,
    generate_docx: bool,
    random_failing_non_english_resource_requests: Sequence[model.ResourceRequest],
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
        assembly_layout_kind=assembly_layout_kind,
        layout_for_print=layout_for_print,
        generate_pdf=generate_pdf,
        generate_epub=generate_epub,
        generate_docx=generate_docx,
        resource_requests=random_failing_non_english_resource_requests,
    )


## Multi-language combination fixtures start here:


@pytest.fixture()
def random_english_and_non_english_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    assembly_layout_kind: model.AssemblyLayoutEnum,
    layout_for_print: bool,
    generate_pdf: bool,
    generate_epub: bool,
    generate_docx: bool,
    random_english_resource_requests: Sequence[model.ResourceRequest],
    random_non_english_resource_requests: Sequence[model.ResourceRequest],
) -> model.DocumentRequest:
    """
    Build one non-English language document request.

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
        assembly_layout_kind=assembly_layout_kind,
        layout_for_print=layout_for_print,
        generate_pdf=generate_pdf,
        generate_epub=generate_epub,
        generate_docx=generate_docx,
        resource_requests=[
            *random_english_resource_requests,
            *random_non_english_resource_requests,
        ],
    )


@pytest.fixture()
def random_two_non_english_languages_document_request(
    email_address: pydantic.EmailStr,
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    assembly_layout_kind: model.AssemblyLayoutEnum,
    layout_for_print: bool,
    generate_pdf: bool,
    generate_epub: bool,
    generate_docx: bool,
    random_non_english_resource_requests: Sequence[model.ResourceRequest],
    random_non_english_resource_requests2: Sequence[model.ResourceRequest],
) -> model.DocumentRequest:
    """
    Build two non-English language document requests. Each
    language has its own randomly chosen set of resource requests.
    """
    return model.DocumentRequest(
        email_address=email_address,
        assembly_strategy_kind=assembly_strategy_kind,
        assembly_layout_kind=assembly_layout_kind,
        layout_for_print=layout_for_print,
        generate_pdf=generate_pdf,
        generate_epub=generate_epub,
        generate_docx=generate_docx,
        resource_requests=[
            *random_non_english_resource_requests,
            *random_non_english_resource_requests2,
        ],
    )
