#
#  Copyright (c) 2017 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wycliffeassociates.org>

"""
XFIXME This script exports tN into HTML format from DCS and generates a PDF from the HTML
"""

from typing import Any, Dict, List, Optional, Union
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
import yaml


import markdown  # type: ignore

import bs4  # type: ignore
from usfm_tools.transform import UsfmTransform  # type: ignore

# Handle running in container or as standalone script
try:
    from file_utils import write_file, read_file, unzip, load_yaml_object, load_json_object  # type: ignore
    from bible_books import BOOK_NUMBERS, BOOK_NAMES  # type: ignore
    from resource_lookup import ResourceJsonLookup
    from config import (
        get_working_dir,
        get_output_dir,
        get_logging_config_file_path,
        get_icon_url,
        get_markdown_resource_types,
        get_tex_format_location,
        get_tex_template_location,
        get_document_html_header,
        get_document_html_footer,
        get_pandoc_command,
    )
    from resource_utils import (
        resource_has_markdown_files,
        # files_from_url,
    )
    from resource import (
        Resource,
        USFMResource,
        TNResource,
        TQResource,
        TAResource,
        TWResource,
        ResourceFactory,
    )
except:
    from .file_utils import write_file, read_file, unzip, load_yaml_object, load_json_object  # type: ignore
    from .bible_books import BOOK_NUMBERS, BOOK_NAMES  # type: ignore
    from .resource_lookup import ResourceJsonLookup
    from .config import (
        get_working_dir,
        get_output_dir,
        get_logging_config_file_path,
        get_icon_url,
        get_markdown_resource_types,
        get_tex_format_location,
        get_tex_template_location,
        get_document_html_header,
        get_document_html_footer,
        get_pandoc_command,
    )
    from .resource_utils import (
        resource_has_markdown_files,
        # files_from_url,
    )
    from .resource import (
        Resource,
        USFMResource,
        TNResource,
        TQResource,
        TAResource,
        TWResource,
        ResourceFactory,
    )


with open(get_logging_config_file_path(), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


# NOTE Not all languages have tn, tw, tq, tq, udb, ulb. Some
# have only a subset of those resources. Presumably the web UI
# will present only valid choices per language.
# NOTE resources could serve as a cache as well. Perhaps the
# cache key could be an md5 hash of the resource's key/value
# pairs or a simple concatenation of lang_code, resource_type,
# resource_code. If the key is hashed hash, subsequent lookups
# would compare a hash of an incoming resource request's
# key/value pairs and if it was already in the resources
# dictionary then the generation of the document could be
# skipped (after first checking the final document result was
# still available - container redeploys could destroy cache)
# and return the URL to the previously generated document
# right away.
# NOTE resources is the incoming resource request dictionary
# and so is per request, per instance. The cache, however,
# would need to persist beyond each request. Perhaps it should
# be maintained as a class variable?


class DocumentGenerator(object):
    def __init__(
        self,
        resources: Dict,
        working_dir: str = get_working_dir(),
        output_dir: str = get_output_dir(),
    ) -> None:
        """
        :param resources:
        :param working_dir:
        :param output_dir:
        """
        self.working_dir = working_dir
        self.output_dir = output_dir
        # The Markdown and later HTML for the document which is composed of the Markdown and later HTML for each resource.
        self.content: str = ""
        # NOTE The lookup service could be (re)-implemented as a
        # singleton (or Global Object at module level for
        # Pythonicness) if desired. For now, just passing it to each
        # Resource instance at object creation.
        lookup_svc: ResourceJsonLookup = ResourceJsonLookup(self.working_dir)

        # Show the dictionary that was passed in.
        logger.debug("resources: {}".format(resources))

        # FIXME Is this even necessary? I don't think that we will
        # design this to not provide a working_dir.
        if not self.working_dir:
            self.working_dir = tempfile.mkdtemp(prefix="tn-")
        if not self.output_dir:
            self.output_dir = self.working_dir

        logger.debug("Working dir is {}".format(self.working_dir))

        # Uniquely identifies a document request that has this order
        # of resource requests where a resource request is identified
        # by lang_code, resource_type, and resource_code. This can
        # serve as a cache lookup key also so that document requests
        # having the same self._document_request_key can skip
        # processing and simply return the end result document if it
        # still exists.
        self._document_request_key: str = ""

        # TODO To be production worthy, we need to make this resilient
        # to errors when creating Resource instances.
        self._resources: List[Resource] = []
        for resource in resources:
            # FIXME self.lookup_svc will become a local var: lookup_svc
            self._resources.append(
                ResourceFactory(self.working_dir, self.output_dir, lookup_svc, resource)
            )
            # NOTE Alternatively, could create a (md5?) hash of th
            # concatenation of lang_code, resource_type,
            # resource_code.
            self._document_request_key += "-".join(
                [
                    resource["lang_code"],
                    resource["resource_type"],
                    resource["resource_code"],
                ]
            )

        logger.debug(
            "self._document_request_key: {}".format(self._document_request_key)
        )

    def run(self) -> None:
        # FIXME icon no longer exists where it used to. I've saved the
        # icon to ./working/temp for now until we find a different
        # location for the icon that is to be used.
        # self._get_unfoldingword_icon()

        # Get the resources files
        for resource in self._resources:
            resource.find_location()
            resource.get_files()

        # Initialize the resources and generate their content
        for resource in self._resources:
            resource.initialize_properties()
            resource.get_content()

        if not os.path.isfile(
            os.path.join(self.output_dir, "{}.pdf".format(self._document_request_key))
            # os.path.join(self.output_dir, "{}.pdf".format(self.filename_base))
        ):
            self.assemble_content()
            logger.info("Generating PDF...")
            self.convert_html2pdf()

    def _get_unfoldingword_icon(self) -> None:
        """ Get Unfolding Word's icon for display in generated PDF. """

        if not os.path.isfile(os.path.join(self.working_dir, "icon-tn.png")):
            command = "curl -o {}/icon-tn.png {}".format(
                self.working_dir, get_icon_url()
            )
            subprocess.call(command, shell=True)

    def assemble_content(self) -> None:
        """ Concatenate all the content from all requested resources
        in the order they were requested and write out to a single
        HTML file excluding a wrapping HTML and BODY element.
        Precondition: each resource has already generated HTML of its
        body content (sans enclosing HTML and body elements) and
        stored it in its _content instance variable. """
        for resource in self._resources:
            self.content += "\n\n{}".format(resource._content)
        self.enclose_html_content()
        logger.debug(
            "About to write HTML to {}".format(
                os.path.join(
                    self.output_dir, "{}.html".format(self._document_request_key)
                )
            )
        )
        write_file(
            os.path.join(self.output_dir, "{}.html".format(self._document_request_key)),
            self.content,
        )

    def enclose_html_content(self):
        """ Write the enclosing HTML and body elements around the HTML
        body content for the document. """
        html = get_document_html_header()
        html += self.content
        html += get_document_html_footer()
        self.content = html

    def convert_html2pdf(self) -> None:
        """ Generate PDF from HTML contained in self.content. """
        now = datetime.datetime.now()
        revision_date = "{}-{}-{}".format(now.year, now.month, now.day)
        # FIXME This should probably be something else, but this will
        # do for now.
        title = "Resources: "
        title += ",".join(set([r._resource_code for r in self._resources]))
        command = get_pandoc_command().format(
            # First hack at a title. Used to be just self.book_title which
            # doesn't make sense anymore.
            title,
            # FIXME This should probably be today's date since not all
            # resources have a manifest file from which issued may be
            # initialized. And since we are dealing with multiple resources
            # per document, which issued date would we use? It doesn't really
            # make sense to use it anymore so I am substituting revision_date
            # instead for now.
            # resource._issued if resource._issued else "",
            revision_date,
            # FIXME Not all resources have a manifest file from which version
            # may be initialized. Further, a document request can include
            # multiple resources each of which can have a manifest file,
            # depending on what is requested, and thus a _version, which one
            # would we use? It doesn't make sense to use this anymore. For now
            # I am just going to use some meaningless literal instead of the
            # next commented out line.
            # resource._version if resource._version else ""
            "v0",
            self.output_dir,
            self.working_dir,
            # FIXME A document generation request is composed of theoretically
            # an infinite number of arbitrarily ordered resources. In this new
            # context using the file location for one resource doesn't make
            # sense as in the next commented out line of code. Instead we use
            # the filename unique to the document generation request itself.
            # resource._filename_base,
            self._document_request_key,
            # NOTE Having revision_date likely obviates _issued above.
            revision_date,
            get_tex_format_location(),
            get_tex_template_location(),
        )
        logger.debug(command)
        subprocess.call(command, shell=True)


# FIXME Old legacy code
def read_csv_as_dicts(filename: str) -> List:
    """ Returns a list of dicts, each containing the contents of a row of
        the given csv file. The CSV file is assumed to have a header row with
        the field names. """
    rows = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


# FIXME Old legacy code
def index_tw_refs_by_verse(tw_refs: List) -> dict:
    """ Returns a dictionary of books -> chapters -> verses, where each
        verse is a list of rows for that verse. """
    tw_refs_by_verse: dict = {}
    for tw_ref in tw_refs:
        book = tw_ref["Book"]
        chapter = tw_ref["Chapter"]
        verse = tw_ref["Verse"]
        if book not in tw_refs_by_verse:
            tw_refs_by_verse[book] = {}
        if chapter not in tw_refs_by_verse[book]:
            tw_refs_by_verse[book][chapter] = {}
        if verse not in tw_refs_by_verse[book][chapter]:
            tw_refs_by_verse[book][chapter][verse] = []

        # # Check for duplicates -- not sure if we need this yet
        # folder = tw_ref["Dir"]
        # reference = tw_ref["Ref"]
        # found_duplicate = False
        # for existing_tw_ref in tw_refs_by_verse[book][chapter][verse]:
        #     if existing_tw_ref["Dir"] == folder and existing_tw_ref["Ref"] == reference:
        #         logger.debug("Found duplicate: ", book, chapter, verse, folder, reference)
        #         found_duplicate = True
        #         break
        # if found_duplicate:
        #     continue

        tw_refs_by_verse[book][chapter][verse].append(tw_ref)
    return tw_refs_by_verse
