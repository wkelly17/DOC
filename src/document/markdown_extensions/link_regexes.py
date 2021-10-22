"""Link regular expressions used by link_transformer_preprocessor module."""

import re
from typing import Pattern

# Handle TW wikilink inner text
TW_RC_LINK_RE: Pattern[str] = re.compile(
    (
        r"rc:\/\/"
        r"(?P<lang_code>[^\[\]\(\)]+?)"
        r"\/tw\/dict\/bible\/(?:kt|names|other)\/"
        r"(?P<word>[^\[\]\(\)]+?)$"
    )
)

# Handle wiki style rc links.
# e.g., [[rc://*/tw/dict/bible/kt/foo.md]]
# NOTE(id:regex_transformation_order) Ensure this doesn't interfere with
# TW_WIKI_RC_SEE_LINK_RE. Negative look-behind regex won't work because
# negative look-behinds must be of fixed length and there is no
# gaurantee of fixed-width string preceding the link regex since the
# preceding string could vary by language and by actual phrase, e.g.,
# (Veja: ...) or (See: ...) or (Blah blah blah: ...). Thus to ensure
# that we don't orphan the preceding text we need to run the
# TW_WIKI_RC_SEE_LINK_RE regex transformations first. The same is true
# for the TA and TN regexes below.
TW_WIKI_RC_LINK_RE: Pattern[
    str
] = r"\[\[rc:\/\/\*\/tw\/dict\/bible\/(?:kt|names|other)\/(?P<word>[^\]]+?)\]\]"

# TW prefixed rc wikilink regex
# (See: [[rc://en/tw/dict/bible/kt/reveal]])
TW_WIKI_PREFIXED_RC_LINK_RE: Pattern[
    str
] = r"\((?P<prefix_text>.+?):* *\[\[rc://(?P<lang_code>[^\[\]]+?)\/tw\/dict\/bible\/(?:kt|names|other)\/(?P<word>[^\[\]]+?)\]\]\)*"

# TW prefixed rc wikilink with no close parens regex
# (See: [[rc://en/tw/dict/bible/kt/reveal]])
# E.g., The first link in (See: [[rc://en/tw/dict/bible/kt/justice]] and [[rc://en/tw/dict/bible/kt/lawofmoses]])
TW_WIKI_PREFIXED_RC_LINK_NO_CLOSE_PAREN_RE: Pattern[
    str
] = r"\((?P<prefix_text>.+?):* *\[\[rc://(?P<lang_code>[^\[\]]+?)\/tw\/dict\/bible\/(?:kt|names|other)\/(?P<word>[^)\[\]]+?)\]\][^)]"

# TW markdown link regex
# e.g., [foo](../kt/foo.md) links.
# NOTE See id:regex_transformation_order above
TW_MARKDOWN_LINK_RE: Pattern[
    str
] = r"\[(?P<link_text>[^\[\]\(\)]+?)\]\(\.+\/(?:kt|names|other)\/(?P<word>[^\[\]\(\)]+?)\.md\)"


# TA rc wikilink prepended by open paren and text regex
# e.g., (See: [[rc://en/ta/man/jit/translate-names]])
TA_WIKI_PREFIXED_RC_LINK_RE: Pattern[
    str
] = r"\((?P<prefix_text>.+?):* *\[\[rc://(?P<lang_code>[^\[\]\(\)]+?)\/ta\/man\/.+?\/(?P<word>[^\[\]]+?)\]\]\)"

# There can be malformed TA wikilinks of this form. Ideally, they
# should be fixed in the source text.
# e.g., [[rc://en/ta/man/jit/figs-metaphor]] Notice the leading
# comma and space.
# NOTE See id:regex_transformation_order above
TA_WIKI_RC_LINK_RE: Pattern[
    str
] = r",* *\[\[rc://(?P<lang_code>[^\[\]\(\)]+?)\/ta\/man\/\w+?\/(?P<word>[^\[\]]+?)\]\]\)*"


# TA markdown style links
# e.g., [*](rc://lang_code/ta/man/translate/*.md)
# e.g., Found in files for ephraim.md and honey.md in pt-br_tw directory.
# e.g. (See: [synecdoche](rc://pt-br/ta/man/translate/figs_synecdoche.md))
# There can be more than one link inside parens:
# e.g., (Veja também: [simile](rc://pt-br/ta/man/translate/figs_simile.md), [metáfora](rc://pt-br/ta/man/translate/figs_metaphor.md))
# e.g., (Veja: [Simile](rc://pt-br/ta/man/translate/figs_simile.md))
# Handles the following style link also (notice there is no file
# suffix which may be malformed and may need to be fixed in markdown
# source by translators):
# e.g., (See: [synecdoche](rc://pt-br/ta/man/translate/figs-synecdoche) )
TA_PREFIXED_MARKDOWN_LINK_RE: Pattern[
    str
] = r"\(.+?:* *\[(?P<link_text>[^\[\]\(\)]*?)\] *\(rc:\/\/(?P<lang_code>[^\[\]\(\)]+?)\/ta\/man\/translate\/(?P<word>[^\[\]\(\)]+?)(.md)*\) *\),*.*"


# TA markdown https style see link regex
# e.g., (Veja: [sinédoque] (https://git.door43.org/Door43/en-ta-translate-vol2/src/master/content/figs_synecdoche.md))
# in ../../../working/temp/pt-br_tw/pt-br_tw/bible/names/naphtali.md
# e.g., (Veja: [eufemismo] (https://git.door43.org/Door43/en-ta-translate-vol2/src/master/content/figs_euphemism.md))
# e.g., (Veja: [metonímia] (https://git.door43.org/Door43/en-ta-translate-vol2/src/master/content/figs_metonymy.md))
# FIXME There still exist some links that are malformed such as this
# next example. We could catch these as well, but then they would never
# get fixed in the markdown source.
# e.g.,  (Veja: [metonímia} (https://git.door43.org/Door43/en-ta-translate- vol2/src/master/content/figs_metonymy.md)).
TA_PREFIXED_MARKDOWN_HTTPS_LINK_RE: Pattern[
    str
] = r"\(.+?:* *\[(?P<link_text>.*?)\] *\(https:\/\/(?P<domain>.+?)\/.+?-ta-.*?\/(?P<work>.+?).md\)\),*.*"

# TA markdown https style link regex
# e.g., [Como Traduzir Nomes] (https://git.door43.org/Door43/en-ta-translate-vol1/src/master/content/translate_names.md)
# NOTE See id:regex_transformation_order above
TA_MARKDOWN_HTTPS_LINK_RE: Pattern[
    str
] = r"\[(?P<link_text>.*?)\] *\(https:\/\/(?P<domain>.+?)\/.+?-ta-.*?\/(?P<work>.+?).md\),*.*"

# TN markdown style scripture link regex
# e.g., [Genesis 46: 33-34](rc://gu/tn/help/gen/46/33)
# e.g.,: [Jude 01:17-19](rc://en/tn/help/jud/01/17)
# e.g., These types of links are found in the 'Bible References'
# section of a translation word definition file. For example,
# ../../../working/temp/en_tw-wa/en_tw/bible/kt/kingofthejews.md.
# NOTE See id:regex_transformation_order above
TN_MARKDOWN_SCRIPTURE_LINK_RE: Pattern[
    str
] = r"\[(?P<scripture_ref>.+?)\]\(rc:\/\/(?P<lang_code>.+?)\/tn\/help\/(?P<resource_code>(?!obs).+?)\/(?P<chapter_num>\d+?)\/(?P<verse_ref>.+?)\)"

MARKDOWN_LINK_RE: Pattern[str] = r"(?<!\\)\[(?P<link_text>.+?)\]\((?P<url>.+?)\)"

# WIKI_LINK_RE = r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]"
WIKI_LINK_RE: Pattern[str] = r"\[\[(?P<url>[^\]]+)\]\]"

# TN markdown relative file path scripture link regex
# e.g., ([Colossians 1:24](../../col/01/24.md))
# e.g., in intro to Colossians chapter 1
#
# NOTE See id:regex_transformation_order above
TN_MARKDOWN_RELATIVE_SCRIPTURE_LINK_RE: Pattern[
    str
] = r"\(\[(?P<scripture_ref>.+?)\]\((\.\.\/)+(?P<resource_code>\w+?)\/(?P<chapter_num>\d+?)\/(?P<verse_ref>.+?).md\)\)"


# FIXME Handle ([Colossians 1:7](../01/07.md)) and
# [Colossians 2:8](../02/08.md) still show up, but
# this is because technically the link is malformed as it is missing
# the resource_code, i.e., the book_id: col.
# TN_MARKDOWN_RELATIVE_TO_CURRENT_BOOK_SCRIPTURE_LINK_RE = r"\[(?P<scripture_ref>.+?)\]\((?:\.\.\/)+(?P<chapter_num>.+?)\/(?P<verse_ref>.+?).md\)"
TN_MARKDOWN_RELATIVE_TO_CURRENT_BOOK_SCRIPTURE_LINK_RE: Pattern[
    str
] = r"\(\[(?P<scripture_ref>.+?)\]\((?:\.\.\/)+(?P<chapter_num>\d+?)\/(?P<verse_ref>.+?).md\)\)"

# TN_MARKDOWN_RELATIVE_TO_CURRENT_CHAPTER_SCRIPTURE_LINK_RE = r"\(\[(?P<scripture_ref>.+?)\]\((?:\.\.\/)+(?P<chapter_num>\d+?)\/(?P<verse_ref>.+?).md\)\)"

# TN OBS markdown link regex
# NOTE Not currently used since TN bible reference and OBS bible
# reference sections are removed by remove_section_preprocessor.py
# FIXME OBS yet to be supported. We need to find out what URL(s) to
# use for TN OBS resources.
# [21:9](rc://gu/tn/help/obs/21/09)
# __[14:02](rc://en/tn/help/obs/14/02)__
TN_OBS_MARKDOWN_LINK_RE: Pattern[
    str
] = r"\[(?P<link_text>.+?)\] *\(rc:\/\/(?P<lang_code>.+?)\/tn\/help\/obs\/(?P<chapter_num>.+?)\/(?P<verse_ref>.+?)\)"

# TN_VERSE_ID_REGEX = r"id=\"(?P<lang_code>.*?)-(?P<book_num>.*?)-tn-ch-(?P<chapter_num>.*?)-v-(?P<verse_ref>.*?)\""
