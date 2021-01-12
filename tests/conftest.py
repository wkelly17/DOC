import os

from typing import Type

import icontract
import pytest


# NOTE Bit of a weird hack to get helper functions into pytest load path:
# https://stackoverflow.com/questions/33508060/create-and-import-helper-functions-in-tests-without-creating-packages-in-test-di
class HelperFunctions:
    """This class is used as a namespace for test helper functions used to keep tests DRY."""

    @staticmethod
    @icontract.require(
        lambda docker_container_document_filepath: docker_container_document_filepath
    )
    def get_document_filepath_for_testing(
        docker_container_document_filepath: str,
    ) -> str:
        """
        Test utility function. If this code is running in a Docker
        container do nothing, otherwise, i.e., if running locally, then remove
        the leading forward slash.
        """
        finished_document_path = docker_container_document_filepath
        if not os.environ.get("IN_CONTAINER"):
            finished_document_path = finished_document_path[1:]
        return finished_document_path


@pytest.fixture
def helpers() -> Type[HelperFunctions]:
    """
    pytest fixture that can be pass
    """
    return HelperFunctions
