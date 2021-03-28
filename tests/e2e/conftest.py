import itertools
import pytest
import random

from typing import Any, List, Tuple
from document.domain import bible_books, model


@pytest.fixture()
def english_lang_code() -> str:
    return "en"


@pytest.fixture(params=["pt-br", "tl"])
# type of request is actually _pytest.fixtures.FixtureRequest
def non_english_lang_code(request: Any) -> str:
    return request.param


@pytest.fixture(params=bible_books.BOOK_NAMES.keys())
def resource_code(request: Any) -> str:
    return request.param


@pytest.fixture(params=[model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER])
def assembly_strategy_kind(request: Any) -> str:
    return request.param


@pytest.fixture()
def english_resource_types() -> List[str]:
    return ["ulb-wa", "tn-wa", "tq-wa", "tw-wa"]


@pytest.fixture()
def non_english_resource_types() -> List[str]:
    return ["ulb", "tn", "tq", "tw"]


@pytest.fixture()
def english_resource_type_combos(english_resource_types: List[str]) -> List[Tuple]:
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
    return random.choice(english_resource_type_combos)


@pytest.fixture()
def random_non_english_resource_type_combo(
    non_english_resource_type_combos: List[List[str]],
) -> List[str]:
    return random.choice(non_english_resource_type_combos)


@pytest.fixture()
def english_resource_requests(
    english_lang_code: str,
    random_english_resource_type_combo: List[str],
    resource_code: str,
) -> List[model.ResourceRequest]:
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
def non_english_resource_requests(
    non_english_lang_code: str,
    random_non_english_resource_type_combo: List[str],
    resource_code: str,
) -> List[model.ResourceRequest]:
    resource_requests = []
    for resource_type in random_non_english_resource_type_combo:
        resource_requests.append(
            model.ResourceRequest(
                lang_code=non_english_lang_code,
                resource_type=resource_type,
                resource_code=resource_code,
            )
        )
    return resource_requests


@pytest.fixture()
def english_document_request(
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    english_resource_requests: List[model.ResourceRequest],
    resource_code: str,
) -> model.DocumentRequest:
    return model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=english_resource_requests,
    )


@pytest.fixture()
def non_english_document_request(
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    non_english_resource_requests: List[model.ResourceRequest],
    resource_code: str,
) -> model.DocumentRequest:
    return model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=non_english_resource_requests,
    )


# @pytest.fixture(params=[pytest.lazy_fixture("document_request")])
