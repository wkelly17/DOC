# import logging  # For logdecorator
import markdown
import re

# from logdecorator import log_on_end
from markdown import Extension
from markdown.preprocessors import Preprocessor
from typing import Any, Dict, List

# from document import config

# logger = config.get_logger(__name__)

# See https://github.com/Python-Markdown/markdown/wiki/Tutorial-2---Altering-Markdown-Rendering
# for template to follow.


class TranslationWordLinkPreprocessor(Preprocessor):
    """Convert wiki links to Markdown links."""

    def __init__(self, md: markdown.Markdown, lang_code: str) -> None:
        """Initialize."""
        self.md = md
        self.lang_code = lang_code
        super().__init__()

    # @log_on_end(logging.DEBUG, "lines after preprocessor: {result}", logger=logger)
    def run(self, lines: List[str]) -> List[str]:
        """
        Entrypoint. Convert translation word relative file Markdown links into
        links pointing to the anchor for said translation words in the
        translation words section.
        """
        source = "\n".join(lines)
        pattern = r"\[(.*?)\]\(\.\.\/(?:kt|names|other)\/(.*?)\.md\)"
        # if m := re.search(pattern, source):
        #     # Inspect source and m here in debug repl
        #     breakpoint()
        source = re.sub(pattern, r"[\1](#{}-\2)".format(self.lang_code), source)
        return source.split("\n")


class TranslationWordLinkExtension(Extension):
    """A Markdown link conversion extension."""

    def __init__(self, **kwargs: Dict) -> None:
        """Initialize."""
        self.config = {
            "lang_code": [
                "en",
                "The language code for the resource whose asset files are currently being processed.",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.preprocessors.register(
            TranslationWordLinkPreprocessor(
                md, lang_code=list(self.getConfig("lang_code"))[0]
            ),
            "translationwordlink",
            32,
        )
