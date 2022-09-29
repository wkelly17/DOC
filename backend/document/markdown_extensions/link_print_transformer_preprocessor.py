import re

import markdown
from typing import Any, final

from document.config import settings
from document.domain import model
from document.markdown_extensions import link_regexes
from document.utils import file_utils, tw_utils

logger = settings.logger(__name__)

TN = "tn"
TW = "tw"


@final
class LinkPrintTransformerPreprocessor(markdown.preprocessors.Preprocessor):
    """
    Convert various link types to text of the link description instead
    of a live link since this is used for producing content suitable for
    printing.
    """

    def __init__(
        self,
        md: markdown.Markdown,
        lang_code: str,
        resource_requests: list[model.ResourceRequest],
        translation_words_dict: dict[str, str],
    ) -> None:
        """Initialize."""
        self._md: markdown.Markdown = md
        self._lang_code: str = lang_code
        self._resource_requests: list[model.ResourceRequest] = resource_requests
        self._translation_words_dict: dict[str, str] = translation_words_dict
        super().__init__()

    def run(self, lines: list[str]) -> list[str]:
        """This is automatically called in super class."""
        source = "\n".join(lines)

        # Transform the '...PREFIXED...' version of regexes in each
        # resource_type group first before its non-'...PREFIXED...' version
        # of regex otherwise we could orphan the prefix portion of the
        # phrase, e.g., you could be left with (Veja: ) or (See: ) or
        # (Blah blah blah: ).

        for wiki_link in wiki_link_parser(source):
            source = self.transform_tw_rc_link(wiki_link, source)

        # Handle links pointing at TW resource assets
        source = self.transform_tw_wiki_prefixed_rc_links(source)
        source = self.transform_tw_wiki_rc_links(source)
        source = self.transform_tw_markdown_links(source)

        # Handle links pointing at TA resource assets
        source = self.transform_ta_prefixed_wiki_rc_links(source)
        source = self.transform_ta_wiki_rc_links(source)
        source = self.transform_ta_prefixed_markdown_https_links(source)
        source = self.transform_ta_markdown_links(source)
        source = self.transform_ta_markdown_https_links(source)

        # Handle links pointing at TN resource assets
        source = self.transform_tn_prefixed_markdown_links(source)
        source = self.transform_tn_markdown_links(source)
        # NOTE Haven't decided yet if we should use this next method or instead
        # have human translators use more explicit scripture reference that
        # includes the resource_code, e.g., col, rather than leave it out. If
        # they did provide the resource_code then this case would be picked up
        # by self.transform_tn_markdown_links.
        source = self.transform_tn_missing_resource_code_markdown_links(source)
        source = self.transform_tn_obs_markdown_links(source)
        source = self.transform_bc_markdown_links(source)
        return source.split("\n")

    def transform_tw_rc_link(self, wikilink: model.WikiLink, source: str) -> str:
        """
        Transform the translation word rc wikilink into a Markdown
        source anchor link pointing to a destination anchor link for
        the translation word definition if it exists or replace the
        link with the non-localized word if it doesn't.
        """
        match = re.search(link_regexes.TW_RC_LINK_RE, wikilink.url)
        if match:
            # Determine if resource_type TW was one of the requested
            # resources.
            url = wikilink.url
            tw_resources_requests = [
                resource_request
                for resource_request in self._resource_requests
                if TW in resource_request.resource_type
            ]
            filename_sans_suffix = match.group("word")
            # Check that there are translation word asset files available for this
            # resource _and_ that the document request included a request for them.
            # The check is necessary because TW resource asset files might be
            # available on disk, in the cache, from a previous document request but
            # the current document request may not have requested them
            # - if it hasn't requested the TW resource in this document request then
            # we should not make links to TW word definitions. Hence the need to
            # also check tw_resources_requests.
            if (
                filename_sans_suffix in self._translation_words_dict
                and tw_resources_requests
            ):
                # Localize the translation word.
                file_content = model.MarkdownContent(
                    file_utils.read_file(
                        self._translation_words_dict[filename_sans_suffix]
                    )
                )
                # Get the localized name for the translation word.
                localized_translation_word = tw_utils.localized_translation_word(
                    file_content
                )
                # Build the anchor link.
                url = url.replace(
                    match.group(0),  # The whole match
                    settings.TRANSLATION_WORD_FMT_STR.format(
                        localized_translation_word
                    ),
                )
            else:
                url = url.replace(match.group(0), filename_sans_suffix)

            for match2 in re.finditer(r"\[\[{}\]\]".format(wikilink.url), source):
                source = source.replace(match2.group(0), url)
        return source

    def transform_tw_markdown_links(self, source: str) -> str:
        """
        Transform the translation word relative file link into a
        source anchor link pointing to a destination anchor link for
        the translation word definition.
        """
        # Determine if resource_type TW was one of the requested
        # resources.
        tw_resources_requests = [
            resource_request
            for resource_request in self._resource_requests
            if TW in resource_request.resource_type
        ]
        for match in re.finditer(link_regexes.TW_MARKDOWN_LINK_RE, source):
            match_text = match.group(0)
            filename_sans_suffix = match.group("word")
            if (
                filename_sans_suffix in self._translation_words_dict
                and tw_resources_requests
            ):
                # Localize non-English languages.
                file_content = model.MarkdownContent(
                    file_utils.read_file(
                        self._translation_words_dict[filename_sans_suffix]
                    )
                )
                # Get the localized name for the translation word
                localized_translation_word = tw_utils.localized_translation_word(
                    file_content
                )
                # Build the anchor links
                source = source.replace(
                    match_text,
                    settings.TRANSLATION_WORD_FMT_STR.format(
                        localized_translation_word,
                    ),
                )
            else:
                logger.debug(
                    "TW file for filename_sans_suffix: %s not found for lang_code: %s",
                    filename_sans_suffix,
                    self._lang_code,
                )
                # Search for translation word relative link
                # and remove it along with any trailing comma from
                # the source text.
                # NOTE Theoretically, this will leave a trailing comma after the link
                # if the link is not the last link in a list of links. I haven't
                # yet seen such a case in practice though.
                match_text_plus_preceding_dot_utf8_char = "· {}".format(match_text)
                source = source.replace(match_text_plus_preceding_dot_utf8_char, "")

        return source

    def transform_tw_wiki_rc_links(self, source: str) -> str:
        """
        Transform the translation word rc link into source anchor link
        pointing to a destination anchor link for the translation word
        definition.
        """
        # Determine if resource_type TW was one of the requested
        # resources.
        tw_resources_requests = [
            resource_request
            for resource_request in self._resource_requests
            if TW in resource_request.resource_type
        ]
        for match in re.finditer(link_regexes.TW_WIKI_RC_LINK_RE, source):
            filename_sans_suffix = match.group("word")
            if (
                filename_sans_suffix in self._translation_words_dict
                and tw_resources_requests
            ):
                # Localize non-English languages.
                file_content = model.MarkdownContent(
                    file_utils.read_file(
                        self._translation_words_dict[filename_sans_suffix]
                    )
                )
                # Get the localized name for the translation word
                localized_translation_word = tw_utils.localized_translation_word(
                    file_content
                )
                # Build the anchor links
                source = source.replace(
                    match.group(0),  # The whole match
                    settings.TRANSLATION_WORD_FMT_STR.format(
                        localized_translation_word,
                    ),
                )
            else:
                logger.debug(
                    "TW file for filename_sans_suffix: %s not found for lang_code: %s",
                    filename_sans_suffix,
                    self._lang_code,
                )
                # Search for translation word relative link
                # and remove it along with any trailing comma from
                # the source text.
                # FIXME Theoretically, this will leave a trailing comma after the link
                # if the link is not the last link in a list of links. I haven't
                # actually seen this case though in practice.
                source = source.replace(match.group(0), "")

        return source

    def transform_tw_wiki_prefixed_rc_links(self, source: str) -> str:
        """
        Transform the translation word rc TW wikilink into source anchor link
        pointing to a destination anchor link for the translation word
        definition.
        """
        # Determine if resource_type TW was one of the requested
        # resources.
        tw_resources_requests = [
            resource_request
            for resource_request in self._resource_requests
            if TW in resource_request.resource_type
        ]
        for match in re.finditer(link_regexes.TW_WIKI_PREFIXED_RC_LINK_RE, source):
            filename_sans_suffix = match.group("word")
            if (
                filename_sans_suffix in self._translation_words_dict
                and tw_resources_requests
            ):
                # Need to localize non-English languages.
                file_content = model.MarkdownContent(
                    file_utils.read_file(
                        self._translation_words_dict[filename_sans_suffix]
                    )
                )
                # Get the localized name for the translation word
                localized_translation_word = tw_utils.localized_translation_word(
                    file_content
                )
                # Build the anchor links
                source = source.replace(
                    match.group(0),  # The whole match
                    settings.TRANSLATION_WORD_PREFIX_FMT_STR.format(
                        match.group("prefix_text"),
                        localized_translation_word,
                    ),
                )
            else:
                logger.debug(
                    "TW file for filename_sans_suffix: %s not found for lang_code: %s",
                    filename_sans_suffix,
                    self._lang_code,
                )
                # Search for translation word relative link and remove it along with any
                # trailing comma from the source text.
                source = source.replace(match.group(0), "")

        return source

    def transform_ta_prefixed_wiki_rc_links(self, source: str) -> str:
        """
        Transform the translation academy rc wikilink into source anchor link
        pointing to a destination anchor link for the translation academy
        reference.
        """
        # FIXME When TA gets implemented we'll need to actually build
        # the anchor link.
        for match in re.finditer(link_regexes.TA_WIKI_PREFIXED_RC_LINK_RE, source):
            # For now, remove match text the source text.
            source = source.replace(match.group(0), "")
        return source

    def transform_ta_wiki_rc_links(self, source: str) -> str:
        """
        Transform the translation academy rc wikilink into source anchor link
        pointing to a destination anchor link for the translation academy
        reference.
        """
        # FIXME When TA gets implemented we'll need to actually build
        # the anchor link.
        for match in re.finditer(link_regexes.TA_WIKI_RC_LINK_RE, source):
            # For now, remove match text the source text.
            source = source.replace(match.group(0), "")
        return source

    def transform_ta_markdown_links(self, source: str) -> str:
        """
        Transform the translation academy markdown link into source anchor link
        pointing to a destination anchor link for the translation
        academy reference.
        """
        # FIXME When TA gets implemented we'll need to actually build
        # the anchor link.
        for match in re.finditer(link_regexes.TA_PREFIXED_MARKDOWN_LINK_RE, source):
            # For now, remove match text the source text.
            source = source.replace(match.group(0), "")
        return source

    def transform_ta_prefixed_markdown_https_links(self, source: str) -> str:
        """
        Transform the translation academy markdown link into source anchor link
        pointing to a destination anchor link for the translation
        academy reference.
        """
        # FIXME When TA gets implemented we'll need to actually build
        # the anchor link.
        for match in re.finditer(
            link_regexes.TA_PREFIXED_MARKDOWN_HTTPS_LINK_RE, source
        ):
            # For now, remove match text the source text.
            source = source.replace(match.group(0), "")
        return source

    def transform_ta_markdown_https_links(self, source: str) -> str:
        """
        Transform the translation academy markdown link into source anchor link
        pointing to a destination anchor link for the translation
        academy reference.
        """
        # FIXME When TA gets implemented we'll need to actually build
        # the anchor link.
        for match in re.finditer(link_regexes.TA_MARKDOWN_HTTPS_LINK_RE, source):
            # For now, remove match text the source text.
            source = source.replace(match.group(0), "")
        return source

    def transform_tn_prefixed_markdown_links(
        self, source: str, working_dir: str = settings.working_dir()
    ) -> str:
        """
        Transform the translation note rc link into a link pointing to
        the anchor link for the translation note for chapter verse
        reference.
        """
        for match in re.finditer(link_regexes.TN_MARKDOWN_SCRIPTURE_LINK_RE, source):
            scripture_ref = match.group("scripture_ref")
            # lang_code = match.group("lang_code")
            # resource_code = match.group("resource_code")
            # chapter_num = match.group("chapter_num")
            # verse_ref = match.group("verse_ref")

            # # NOTE(id:check_for_resource_request) To bother getting the TN resource
            # # asset file referenced in the matched link we must know that said TN
            # # resource identified by the lang_code/resource_type/resource_code combo
            # # in the link has been requested by the user in the DocumentRequest.
            # tn_resource_requests: list[model.ResourceRequest] = [
            #     resource_request
            #     for resource_request in self._resource_requests
            #     if resource_request.lang_code == lang_code
            #     and TN in resource_request.resource_type
            #     and resource_request.resource_code == resource_code
            # ]
            # if tn_resource_requests:
            #     tn_resource_request: model.ResourceRequest = tn_resource_requests[0]
            #     # Build a file path to the TN note being requested.
            #     first_resource_path_segment = "{}_{}".format(
            #         tn_resource_request.lang_code,
            #         tn_resource_request.resource_type,
            #     )
            #     second_resource_path_segment = "{}_tn".format(
            #         tn_resource_request.lang_code
            #     )
            #     path = "{}.md".format(
            #         os.path.join(
            #             working_dir,
            #             first_resource_path_segment,
            #             second_resource_path_segment,
            #             resource_code,
            #             chapter_num,
            #             verse_ref,
            #         )
            #     )
            #     if os.path.exists(path):  # file path to TN note exists
            #         # Create anchor link to translation note
            #         new_link = settings.TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR.format(
            #             scripture_ref,
            #             tn_resource_request.lang_code,
            #             bible_books.BOOK_NUMBERS[
            #                 tn_resource_request.resource_code
            #             ].zfill(3),
            #             chapter_num.zfill(3),
            #             verse_ref.zfill(3),
            #         )
            #         # Replace the match text with the new anchor link
            #         source = source.replace(
            #             match.group(0),  # The whole match
            #             "({})".format(new_link),
            #         )
            #     else:  # TN note file does not exist.
            #         # Replace link with link text only.
            #         source = source.replace(match.group(0), scripture_ref)
            # else:  # TN resource that link requested was not included as part of the DocumentRequest
            # Replace link with link text only.
            source = source.replace(match.group(0), scripture_ref)

        return source

    def transform_tn_markdown_links(self, source: str) -> str:
        """
        Transform the translation note rc link into a link pointing to
        the anchor link for the translation note for chapter verse
        reference.
        """
        for match in re.finditer(
            link_regexes.TN_MARKDOWN_RELATIVE_SCRIPTURE_LINK_RE, source
        ):
            scripture_ref = match.group("scripture_ref")
            # resource_code = match.group("resource_code")
            # chapter_num = match.group("chapter_num")
            # verse_ref = match.group("verse_ref")

            # NOTE See id:check_for_resource_request above
            # matching_resource_requests: list[model.ResourceRequest] = [
            #     resource_request
            #     for resource_request in self._resource_requests
            #     if resource_request.lang_code == self._lang_code
            #     and TN in resource_request.resource_type
            #     and resource_request.resource_code == resource_code
            # ]
            # if matching_resource_requests:
            #     matching_resource_request: model.ResourceRequest = (
            #         matching_resource_requests[0]
            #     )
            #     # Build a file path to the TN note being requested.
            #     first_resource_path_segment = "{}_{}".format(
            #         matching_resource_request.lang_code,
            #         matching_resource_request.resource_type,
            #     )
            #     second_resource_path_segment = "{}_tn".format(
            #         matching_resource_request.lang_code
            #     )
            #     path = "{}.md".format(
            #         os.path.join(
            #             settings.working_dir(),
            #             first_resource_path_segment,
            #             second_resource_path_segment,
            #             resource_code,
            #             chapter_num,
            #             verse_ref,
            #         )
            #     )
            #     if os.path.exists(path):  # file path to TN note exists
            #         # Create anchor link to translation note
            #         new_link = settings.TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR.format(
            #             scripture_ref,
            #             self._lang_code,
            #             bible_books.BOOK_NUMBERS[resource_code].zfill(3),
            #             chapter_num.zfill(3),
            #             verse_ref.zfill(3),
            #         )
            #         # Replace the match text with the new anchor link
            #         source = source.replace(
            #             match.group(0),  # The whole match
            #             "({})".format(new_link),
            #         )
            #     else:  # TN note file does not exist.
            #         # Replace match text from the source text with the
            #         # link text only so that is not clickable.
            #         # The whole match plus surrounding parenthesis
            #         source = source.replace(
            #             "({})".format(match.group(0)), scripture_ref
            #         )
            # else:  # TN resource that link requested was not included as part of the
            # DocumentRequest Replace match text from the source text with the link
            # text only so that is not clickable.
            # The whole match plus surrounding parenthesis
            source = source.replace("({})".format(match.group(0)), scripture_ref)

        return source

    def transform_tn_missing_resource_code_markdown_links(self, source: str) -> str:
        """
        Transform the translation note rc link into a link pointing to
        the anchor link for the translation note for chapter verse
        reference.
        """
        for match in re.finditer(
            link_regexes.TN_MARKDOWN_RELATIVE_TO_CURRENT_BOOK_SCRIPTURE_LINK_RE, source
        ):
            scripture_ref = match.group("scripture_ref")
            chapter_num = match.group("chapter_num")
            verse_ref = match.group("verse_ref")

            # matching_resource_requests: list[model.ResourceRequest] = [
            #     resource_request
            #     for resource_request in self._resource_requests
            #     if resource_request.lang_code == self._lang_code
            #     and TN in resource_request.resource_type
            # ]
            # resource_code = ""
            # if matching_resource_requests:
            #     matching_resource_request: model.ResourceRequest = (
            #         matching_resource_requests[0]
            #     )
            #     resource_code = matching_resource_request.resource_code
            #     # Build a file path to the TN note being requested.
            #     first_resource_path_segment = "{}_{}".format(
            #         matching_resource_request.lang_code,
            #         matching_resource_request.resource_type,
            #     )
            #     second_resource_path_segment = "{}_tn".format(
            #         matching_resource_request.lang_code
            #     )
            #     path = "{}.md".format(
            #         os.path.join(
            #             settings.working_dir(),
            #             first_resource_path_segment,
            #             second_resource_path_segment,
            #             resource_code,
            #             chapter_num,
            #             verse_ref,
            #         )
            #     )
            #     if os.path.exists(path):  # file path to TN note exists
            #         # Create anchor link to translation note
            #         new_link = settings.TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR.format(
            #             scripture_ref,
            #             self._lang_code,
            #             bible_books.BOOK_NUMBERS[resource_code].zfill(3),
            #             chapter_num.zfill(3),
            #             verse_ref.zfill(3),
            #         )
            #         # Replace the match text with the new anchor link
            #         source = source.replace(
            #             match.group(0),  # The whole match
            #             "({})".format(new_link),
            #         )
            #     else:  # TN note file does not exist.
            #         # Replace match text from the source text with the
            #         # link text only so that is not clickable.
            #         # The whole match plus surrounding parenthesis
            #         source = source.replace(
            #             "({})".format(match.group(0)), scripture_ref
            #         )
            # else:  # TN resource that link requested was not included as part of the
            # DocumentRequest Replace match text from the source text with the link
            # text only so that is not clickable.
            # The whole match plus surrounding parenthesis
            source = source.replace("({})".format(match.group(0)), scripture_ref)

        return source

    def transform_tn_obs_markdown_links(self, source: str) -> str:
        """
        Until OBS is supported, replace OBS TN link with just its link
        text.
        """
        for match in re.finditer(link_regexes.TN_OBS_MARKDOWN_LINK_RE, source):
            # Build the anchor links
            # TODO Actually create a meaningful link rather than just
            # link text
            source = source.replace(match.group(0), match.group("link_text"))
        return source

    def transform_bc_markdown_links(
        self,
        source: str,
    ) -> str:
        """
        Replace bible commentary relative link with link text.
        """
        for match in re.finditer(link_regexes.BC_MARKDOWN_LINK_RE, source):
            # Build the anchor links to referenced bible commentary
            # articles.
            source = source.replace(match.group(0), match.group("link_text"))
        return source


class LinkPrintTransformerExtension(markdown.Extension):
    """A Markdown link conversion extension."""

    def __init__(self, *args: str, **kwargs: Any) -> None:
        """Entry point."""
        self.config = kwargs
        # Don't call super.__init__(**kwargs) here as it will clobber the
        # types on kwargs and isn't necessary anyway.

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        """Automatically called by superclass."""
        link_print_transformer = LinkPrintTransformerPreprocessor(
            md,
            self.getConfig("lang_code"),
            self.getConfig("resource_requests"),
            self.getConfig("translation_words_dict"),
        )
        md.preprocessors.register(
            link_print_transformer,
            "link_print_transformer",
            32,
        )


def markdown_link_parser(source: str) -> list[model.MarkdownLink]:
    """Return a list of all Markdown links in source."""
    links: list[model.MarkdownLink] = []
    for link in re.finditer(link_regexes.MARKDOWN_LINK_RE, source):
        links.append(
            model.MarkdownLink(
                link_text=link.group("link_text"),
                url=link.group("url"),
            )
        )
    return links


def wiki_link_parser(source: str) -> list[model.WikiLink]:
    """Return a list of all Wiki links in source."""
    links: list[model.WikiLink] = []
    for link in re.finditer(link_regexes.WIKI_LINK_RE, source):
        links.append(
            model.WikiLink(
                url=link.group("url"),
            )
        )
    return links
