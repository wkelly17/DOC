# import logging  # For logdecorator
import markdown
import os
import pathlib
import re

# from logdecorator import log_on_end
from markdown import Extension
from markdown.preprocessors import Preprocessor
from typing import cast, Dict, List, Optional

from document import config
from document.utils import file_utils

logger = config.get_logger(__name__)

# See https://github.com/Python-Markdown/markdown/wiki/Tutorial-2---Altering-Markdown-Rendering
# for template to follow.


class TranslationWordLinkPreprocessor(Preprocessor):
    """Convert wiki links to Markdown links."""

    def __init__(
        self, md: markdown.Markdown, lang_code: str, tw_resource_dir: Optional[str],
    ) -> None:
        """Initialize."""
        # Avoid circular reference by importing here instead of the
        # top of the file.
        from document.domain.resource import TWResource

        logger.debug("lang_code: {}".format(lang_code))
        logger.debug("tw_resource_dir: {}".format(tw_resource_dir))
        self.md = md
        self.lang_code = lang_code
        self.tw_resource_dir = tw_resource_dir
        self.translation_word_filepaths = (
            TWResource.get_translation_word_filepaths(cast(str, self.tw_resource_dir))
            if tw_resource_dir
            else None
        )
        # logger.debug(
        #     "self.translation_word_filepaths: {}".format(
        #         self.translation_word_filepaths
        #     )
        # )
        self.translation_words_dict = (
            {
                pathlib.Path(os.path.basename(word_filepath)).stem: word_filepath
                for word_filepath in self.translation_word_filepaths
            }
            if self.translation_word_filepaths
            else {}
        )
        # logger.debug(
        #     "self.translation_words_dict: {}".format(self.translation_words_dict)
        # )
        super().__init__()

    # @log_on_end(logging.DEBUG, "lines after preprocessor: {result}", logger=logger)
    def run(self, lines: List[str]) -> List[str]:
        """
        Entry point. Convert translation word relative file Markdown links into
        links pointing to the anchor for translation words in the
        translation words section.
        """
        source = "\n".join(lines)
        # FIXME Some languages do not follow this pattern, so we need
        # to handle those
        pattern = r"\[(.*?)\]\(\.+\/(?:kt|names|other)\/(.*?)\.md\)"
        # This next pattern catches scripture references like
        # ../col/01/03.md
        # pattern = r"\[(.*?)\]\(.*?\/(.*?)\.md\)"
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
                # Need to localize non-English languages.
                if self.lang_code != "en":
                    file_content = file_utils.read_file(
                        self.translation_words_dict[filename_sans_suffix]
                    )
                    # Get the localized name for the translation word
                    # FIXME Doing the same logic as in TWResource,
                    # perhaps there is a way to keep things DRY
                    localized_translation_word = file_content.split("\n")[0].split(
                        "# "
                    )[1]
                    source = re.sub(
                        pattern,
                        r"[\1](#{}-{})".format(
                            self.lang_code, localized_translation_word
                        ),
                        source,
                    )
                else:
                    # English, no need to localize translation word,
                    # just create the link.
                    source = re.sub(
                        pattern, r"[\1](#{}-\2)".format(self.lang_code), source
                    )
            # FIXME Handle non-translation word cases, e.g., scripture links
            else:
                pass
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
            "tw_resource_dir": [
                "",
                "The base directory for the translation word Markdown filepaths.",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        # logger.debug(
        #     "self.getConfig('translation_word_filepaths'): {}".format(
        #         self.getConfig("translation_word_filepaths")
        #     )
        # )
        md.preprocessors.register(
            TranslationWordLinkPreprocessor(
                md,
                lang_code=list(self.getConfig("lang_code"))[0],
                tw_resource_dir=list(self.getConfig("tw_resource_dir"))[0],
            ),
            "translationwordlink",
            32,
        )
