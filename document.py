from typing import Any, Dict, List, NewType, Optional, Union
import abc
import os
import sys
import re
import pprint
import logging
import argparse
import tempfile
import shutil
import datetime
import subprocess
import csv
from glob import glob

import markdown  # type: ignore

import bs4  # type: ignore
from usfm_tools.transform import UsfmTransform  # type: ignore

# Handle running in container or as standalone script
try:
    from .file_utils import write_file, read_file, unzip, load_yaml_object  # type: ignore
    from .url_utils import download_file  # type: ignore
    from .bible_books import BOOK_NUMBERS  # type: ignore
    from .resource_lookup import ResourceJsonLookup
except:
    from file_utils import write_file, read_file, unzip, load_yaml_object  # type: ignore
    from url_utils import download_file  # type: ignore
    from bible_books import BOOK_NUMBERS  # type: ignore
    from resource_lookup import ResourceJsonLookup

## Document API:
## .config() # DocumentConfiguration, Document composes a DocumentConfiguration
## .lookup_resource() # This could be part of DocumentConfiguration
## .resource_acquisition() # Actually download and unzip etc. the resources.
## .typeset() # Generate the PDF


## NOTE Not sure if I'll keep these abstraction/indirection yet, we'll
## see. Perhaps this is where the web service will hand off its set of
## incoming resources that were requested and be used by the Document
## object to compose and typeset itself.
class DocumentConfiguration(abc.ABC):
    """ Abstract base class that formalizes the collection of inputs/resources that are
    folded into the document and the target format once "typeset",
    e.g., PDF. """

    # self.document_target_type: str  # For now this is just PDF

    def configure(self):
        """ Generate a configuration (whatever that means - yet to be
        determined). """
        raise NotImplementedError


FinalDocumentURL = NewType("FinalDocumentURL", str)


class DocumentTypesetter(abc.ABC):
    """ Abstract base class that formalizes the notion of how a
    document that is fully configured actually gets typeset/generated
    into the final target file type result. """

    @abc.abstractmethod
    def typeset() -> FinalDocumentURL:
        """ Do the work of producing the end result target object
        given all the inputs. """
        raise NotImplementedError


class DocumentPDFTypesetter(DocumentTypesetter):
    def typeset() -> FinalDocumentURL:
        """ Generate the PDF document. """
        ## TODO Relocate the Pandoc PDF generation invocation here.
        pass
        # TODO Do typesetting of HTML using Pandoc.
        # TODO Return URL of finally typeset (by Pandoc) document.


class Document(abc.ABC):
    """ Abstract base class that formalizes a document. Currently, we
    want to create PDF, but later we may generate other document types
    such as DOCX, etc.."""

    def __init__(
        self,
        configuration: DocumentConfiguration,
        lookup_svc: ResourceLookup,
        typesetter: DocumentTypesetter,
    ) -> None:
        self.configuration = configuration
        self.lookup_svc = lookup_svc
        self.typesetter = typesetter

    # self.configuration: DocumentConfiguration
    # self.typesetter: DocumentTypesetter
    # self.final_document_url: Optional[FinalDocumentURL] = None

    def configure(self, config: DocumentConfiguration) -> None:
        self.configuration = config.configure()

    def find_resources(self) -> None:
        # TODO
        pass

    def typeset(self, typesetter: DocumentTypesetter) -> None:
        self.configuration.final_document_url = self.typesetter.typeset()


class PDFDocument(Document):
    """ Reification of the notion of a document. """

    def __init__(self) -> None:
        # TODO
        pass

    def configure(self, configuration: DocumentConfiguration) -> None:
        self.configuration = configuration.configure()

    def typeset(self, typesetter: DocumentPDFTypesetter) -> None:
        self.configuration.final_document_url = self.typesetter.typeset()
