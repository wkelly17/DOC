from typing import Any, Dict, List, Optional, Union
import abc
import yaml

# import document_generator

try:
    from config import get_logging_config_file_path

    # from document_generator import DocumentGenerator
except:
    from .config import get_logging_config_file_path

    # from .document_generator import DocumentGenerator


import logging
import logging.config

with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


class AssemblyStrategy(abc.ABC):
    """ Strategy pattern superclass. Subclasses implement different
    algorithms (strategies) for assembling a document. """

    @abc.abstractmethod
    # def assemble_content(self, docgen: DocumentGenerator) -> None:
    def assemble_content(self, docgen) -> None:
        pass


class VerseAssemblyStrategy(AssemblyStrategy):
    """ Subclass which implements an assemble_content method which
    interleaves USFM, TN, etc. at the verse level. """

    # def assemble_content(self, docgen: DocumentGenerator) -> None:
    def assemble_content(self, docgen) -> None:
        """ Assemble the collection of resources' content according to
        the 'by verse' strategy."""
        logger.info("Assembling document by interleaving at the verse level.")
        pass


class ChapterAssemblyStrategy(AssemblyStrategy):
    """ Subclass which implements an assemble_content method which
    interleaves USFM, TN, etc. at the chapter level. """

    # def assemble_content(self, docgen: DocumentGenerator) -> None:
    def assemble_content(self, docgen) -> None:
        """ Assemble the collection of resources' content according to
        the 'by chapter' strategy. """
        logger.info("Assembling document by interleaving at the chapter level.")
        pass


class BookAssemblyStrategy(AssemblyStrategy):
    """ Subclass which implements an assemble_content method which
    interleaves USFM, TN, etc. at the book level. """

    # def assemble_content(self, docgen: DocumentGenerator) -> None:
    def assemble_content(self, docgen) -> None:
        """ Assemble the collection of resources content according to
        the 'by book' strategy. """
        logger.info("Assembling document by interleaving at the book level.")
        for resource in docgen.found_resources:
            docgen.content += "\n\n{}".format(resource._content)
