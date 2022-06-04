import re
from typing import Any, final

import markdown
from markdown import Extension
from markdown.preprocessors import Preprocessor

from document.config import settings

logger = settings.logger(__name__)


@final
class RemoveSectionPreprocessor(Preprocessor):
    """Remove arbitrary Markdown sections."""

    def __init__(self, md: markdown.Markdown, sections_to_remove: list[str]) -> None:
        self._md: markdown.Markdown = md
        self._sections_to_remove: list[str] = sections_to_remove
        logger.debug("sections_to_remove: %s", sections_to_remove)
        super().__init__()

    def remove_sections(
        self,
        md: str,
    ) -> list[str]:
        """Remove various markdown sections."""
        for section in self._sections_to_remove:
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

    def run(self, lines: list[str]) -> list[str]:
        """Entrypoint."""
        source = "\n".join(lines)
        return self.remove_sections(source)


@final
class RemoveSectionExtension(Extension):
    """Wikilink to Markdown link conversion extension."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Entrypoint."""
        self.config = kwargs

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        """Automatically called by superclass."""
        self.md = md
        md.registerExtension(self)
        remove_section_transformer = RemoveSectionPreprocessor(
            md, self.getConfig("sections_to_remove")
        )
        md.preprocessors.register(
            remove_section_transformer, "remove_section_transformer", 32
        )
