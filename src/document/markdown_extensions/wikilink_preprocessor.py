import markdown
import re

from markdown import Extension
from markdown.preprocessors import Preprocessor
from typing import Any, Dict, List


class WikiLinkPreprocessor(Preprocessor):
    """Convert wiki links to Markdown links."""

    def __init__(self, config: Dict, md: markdown.Markdown) -> None:
        """Initialize."""
        self.encoding = config.get("encoding")
        super(WikiLinkPreprocessor, self).__init__()

    def parse_wikilinks(self, lines: List[str]) -> List[str]:
        """Parse wikilinks and convert to Markdown links."""
        pattern = r"\(See: \[\[(.*)\]\]\)"
        new_lines = []
        for line in lines:
            # Convert [[]] style link to markdown style link []().
            line = re.sub(pattern, r"[](\1)", line)
            new_lines.append(line)
        return new_lines

    def run(self, lines: List[str]) -> List[str]:
        """Process wikilinks."""
        return self.parse_wikilinks(lines)


class WikiLinkExtension(Extension):
    """Wikilink to Markdown link conversion extension."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize."""
        self.config = {
            "encoding": ["utf-8", 'Encoding of snippets - Default: "utf-8"'],
        }
        super(WikiLinkExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        """Register the extension."""
        self.md = md
        md.registerExtension(self)
        config = self.getConfigs()
        wikilink = WikiLinkPreprocessor(config, md)
        md.preprocessors.register(wikilink, "snippet", 32)


def makeExtension(*args: Any, **kwargs: Any) -> WikiLinkExtension:
    """Return extension."""
    return WikiLinkExtension(*args, **kwargs)
