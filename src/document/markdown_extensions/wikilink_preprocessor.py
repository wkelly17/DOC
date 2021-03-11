# import logging  # For logdecorator
import markdown
import re

# from logdecorator import log_on_end
from markdown import Extension
from markdown.preprocessors import Preprocessor
from typing import Any, Dict, List

from document import config

# logger = config.get_logger(__name__)

# An experiment to see if we can make processing of links in the
# interleaved document assets' Markdown content pluggable into the
# Markdown library. Answer: yes. This has the potential to clean up and
# better engineer the way links are converted from wikilink to Markdown
# style, from rc:// to https://, etc.. Plugins or extensions as they are
# called in Python-Markdown library can be assigned priorities which
# control their execution/loading order and you can have preprocessors
# or block processors (and other types too) depending on what superclass
# you inherit from so you can choose where in the conversion from
# Markdown to HTNL you want your extension to operate. See
# https://python-markdown.github.io/extensions/api/ for more details.
class WikiLinkPreprocessor(Preprocessor):
    """Convert wiki links to Markdown links."""

    def __init__(self, config: Dict, md: markdown.Markdown) -> None:
        """Initialize."""
        # Example use of config. See __init__ for WikiLinkExtension
        # below for initialization.
        # self.encoding = config.get("encoding")
        super(WikiLinkPreprocessor, self).__init__()

    # @log_on_end(logging.DEBUG, "lines after preprocessor: {result}", logger=logger)
    def parse_wikilinks(self, lines: List[str]) -> List[str]:
        """Parse wikilinks and convert to Markdown links."""
        source = "\n".join(lines)
        pattern = r"\[\[(.*?)\]\]"
        # if m := re.search(pattern, source):
        #     # Inspect source and m here in debug repl
        #     breakpoint()
        source = re.sub(pattern, r"[](\1)", source)
        return source.split("\n")

    def run(self, lines: List[str]) -> List[str]:
        """Process wikilinks."""
        return self.parse_wikilinks(lines)


class WikiLinkExtension(Extension):
    """Wikilink to Markdown link conversion extension."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize."""
        self.config = {
            # Example config entry from the snippets extension that
            # ships with Python-Markdown library.
            # "encoding": ["utf-8", 'Encoding of snippets - Default: "utf-8"'],
        }
        super(WikiLinkExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        """Register the extension."""
        self.md = md
        md.registerExtension(self)
        config = self.getConfigs()
        wikilink = WikiLinkPreprocessor(config, md)
        md.preprocessors.register(wikilink, "wikilink", 32)


def makeExtension(*args: Any, **kwargs: Any) -> WikiLinkExtension:
    """Return extension."""
    return WikiLinkExtension(*args, **kwargs)
