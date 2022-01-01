"""This module provides custom domain exceptions."""

from typing import final


@final
class InvalidDocumentRequestException(Exception):
    def __init__(self, message: str):
        self.message: str = message
