# import logging  # For logdecorator
import markdown
import os
import pathlib
import re

# from logdecorator import log_on_end
from markdown import Extension
from markdown.preprocessors import Preprocessor
from typing import cast, Dict, FrozenSet, List, Optional

from document.utils import file_utils

# logger = config.get_logger(__name__)

# See https://github.com/Python-Markdown/markdown/wiki/Tutorial-2---Altering-Markdown-Rendering
# for template to follow.


class TranslationWordLinkPreprocessor(Preprocessor):
    """Convert wiki links to Markdown links."""

    def __init__(
        self,
        md: markdown.Markdown,
        lang_code: str,
        filepaths: Optional[FrozenSet[str]],
    ) -> None:
        """Initialize."""
        self.md = md
        self.lang_code = lang_code
        self.translation_word_filepaths = (
            cast(FrozenSet[str], filepaths) if filepaths else None
        )
        self.translation_words_dict = (
            {
                pathlib.Path(os.path.basename(word_filepath)).stem: word_filepath
                for word_filepath in self.translation_word_filepaths
            }
            if self.translation_word_filepaths
            else {}
        )
        super().__init__()

    # @log_on_end(logging.DEBUG, "lines after preprocessor: {result}", logger=logger)
    def run(self, lines: List[str]) -> List[str]:
        """
        Entry point. Convert translation word relative file Markdown links into
        links pointing to the anchor for said translation words in the
        translation words section.

        FIXME: Better docs, this can be unclear to the uninitiated.
        """
        source = "\n".join(lines)
        # pattern = r"\[(.*?)\]\(\.+\/(?:kt|names|other)\/(.*?)\.md\)"
        # This next pattern catches scripture references like
        # ../col/01/03.md
        pattern = r"\[(.*?)\]\(.*?\/(.*?)\.md\)"
        if m := re.search(pattern, source):
            # FIXME Refactor into its own method. Then we'll have
            # another method for scripture links.
            # FIXME Better name? This might be a 'See:'-style
            # scripture link rather than a translation word link.
            filename_sans_suffix = m.groups()[1]
            # NOTE This extension may be instantiated with self.translation_word_paths set to None in its
            # constructor. This can be the case when called within a
            # a non-TWResource. The design will likely change.
            if filename_sans_suffix in self.translation_words_dict:
                # Only need to localize non-English languages.
                if self.lang_code != "en":
                    # Get the localized name for the translation word
                    # dirname = "{}_tw".format(self.lang_code)
                    # filename = "{}{}.md".format(
                    #     os.path.join(self.working_dir, dirname, dirname),
                    #     filename_sans_suffix,
                    # )

                    # with open(
                    #     self.translation_words_dict[filename_sans_suffix], "r"
                    # ) as fin:

                    file_content = file_utils.read_file(
                        self.translation_words_dict[filename_sans_suffix]
                    )
                    localized_translation_word = file_content.split("\n").split(" ")
                    source = re.sub(
                        pattern,
                        r"[\1](#{}-{})".format(
                            self.lang_code, localized_translation_word
                        ),
                        source,
                    )
                    breakpoint()
                else:
                    # English, no need to localize translation word,
                    # just create the link.
                    source = re.sub(
                        pattern, r"[\1](#{}-\2)".format(self.lang_code), source
                    )
            # FIXME Handle non-translation word cases, e.g., scripture links
            else:
                breakpoint()
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
            "filepaths": [
                {},
                "The filepaths to the language's translation word Markdown files.",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.preprocessors.register(
            TranslationWordLinkPreprocessor(
                md,
                lang_code=list(self.getConfig("lang_code"))[0],
                filepaths=self.getConfig("translation_word_filepaths"),
            ),
            "translationwordlink",
            32,
        )
