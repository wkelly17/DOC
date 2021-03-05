import re
from typing import Any, Dict, List

import markdown
from markdown import Extension
from markdown.preprocessors import Preprocessor


class WikiLinkPreprocessor(Preprocessor):
    """Convert wiki links to Markdown links."""

    def __init__(self, config: Dict, md: markdown.Markdown) -> None:
        """Initialize."""

        # self.base_path = config.get("base_path")
        self.encoding = config.get("encoding")
        # self.check_paths = config.get("check_paths")
        # self.tab_length = md.tab_length
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

        # self.seen = set()
        return self.parse_wikilinks(lines)


class WikiLinkExtension(Extension):
    """Snippet extension."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize."""

        self.config = {
            # FIXME
            # "base_path": [".", 'Base path for snippet paths - Default: ""'],
            "encoding": ["utf-8", 'Encoding of snippets - Default: "utf-8"'],
            # "check_paths": [
            #     False,
            #     'Make the build fail if a snippet can\'t be found - Default: "false"',
            # ],
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


# import markdown
# from markdown import preprocessors
# import re
# from typing import Any, List


# class WikiLinksExtension(markdown.Extension):
#     def __init__(self, **kwargs: Any) -> None:
#         # self.config = {
#         #     'lang_prefix': ['language-', 'Prefix prepended to the language. Default: "language-"']
#         # }
#         super().__init__(**kwargs)

#     def extendMarkdown(self, md: markdown.Markdown) -> None:
#         """
#         Add OrgLinksPreprocessor to the Markdown instance.
#         """
#         md.registerExtension(self)

#         md.preprocessors.register(
#             WikiLinksPreprocessor(md, self.getConfigs()), "org_link", 25,
#         )


# class WikiLinksPreProcessor(preprocessors.Preprocessor):
#     """
#     Convert (See: [[rc://foo]]) style links to [](rc://foo) style links.
#     """

#     # FIXME Don't use type Any. Just using it for now until I look up
#     # the type of config.
#     def __init__(self, md: markdown.Markdown, config: Any):
#         super().__init__(md)
#         self.config = config

#     def run(self, lines: List[str]) -> List[str]:
#         pattern = r"\(See: \[\[(.*)\]\]\)"
#         new_lines = []
#         for line in lines:
#             # Convert [[]] style link to markdown style link []().
#             line = re.sub(pattern, "[](\1)", line)
#             new_lines.append(line)
#         return new_lines


# def makeExtension(**kwargs: Any):  # pragma: no cover
#     return WikiLinksExtension(**kwargs)
