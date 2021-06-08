# import logging  # For logdecorator
import markdown
import re

# from logdecorator import log_on_end
from markdown import Extension
from markdown.preprocessors import Preprocessor
from typing import Any, Dict, List

from document import config

# logger = config.get_logger(__name__)


class RemoveSectionPreprocessor(Preprocessor):
    """Remove arbitrary Markdown sections."""

    def __init__(self, config: Dict, md: markdown.Markdown) -> None:
        """Initialize."""
        # Example use of config. See __init__ for RemoveSectionExtension
        # below for initialization.
        # self.encoding = config.get("encoding")
        super(RemoveSectionPreprocessor, self).__init__()

    # @log_on_end(logging.DEBUG, "lines after preprocessor: {result}", logger=logger)
    def remove_sections(self, md: str) -> List[str]:
        """
        Remove various markdown sections.
        """
        for section in config.get_markdown_sections_to_remove():
            md = self.remove_md_section(md, section)
        return md.split("\n")

    def remove_md_section(self, md: str, section_name: str) -> str:
        """
        Given markdown and a section name, removes the section header and the
        text contained in the section.
        """
        header_regex = re.compile("^#.*$")
        section_regex = re.compile("^#+ {}".format(section_name))
        out_md = ""
        in_section = False
        for line in md.splitlines():
            if in_section:
                if header_regex.match(line):
                    # We found a header.  The section is over.
                    out_md += line + "\n"
                    in_section = False
            else:
                if section_regex.match(line):
                    # We found the section header.
                    in_section = True
                else:
                    out_md = "{}{}\n".format(out_md, line)
        return out_md

    def run(self, lines: List[str]) -> List[str]:
        """Entrypoint."""
        source = "\n".join(lines)
        return self.remove_sections(source)


class RemoveSectionExtension(Extension):
    """Wikilink to Markdown link conversion extension."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize."""
        self.config = {
            # Example config entry from the snippets extension that
            # ships with Python-Markdown library.
            # "encoding": ["utf-8", 'Encoding of snippets - Default: "utf-8"'],
        }
        super(RemoveSectionExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        """Register the extension."""
        self.md = md
        md.registerExtension(self)
        config = self.getConfigs()
        removesection = RemoveSectionPreprocessor(config, md)
        md.preprocessors.register(removesection, "remove_section", 32)


def makeExtension(*args: Any, **kwargs: Any) -> RemoveSectionExtension:
    """Return extension."""
    return RemoveSectionExtension(*args, **kwargs)
