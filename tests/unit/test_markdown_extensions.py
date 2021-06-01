import markdown
import os
import pytest

from document.markdown_extensions import (
    wikilink_preprocessor,
    remove_section_preprocessor,
    translation_word_link_preprocessor,
)

from typing import List

EN_TW_RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_data",
    "en_tw-wa",
    "en_tw",
)

GU_TW_RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_data",
    "gu_tw",
    "gu_tw",
)


def test_remove_section_preprocessor() -> None:
    """
    Test the remove section Markdown pre-processor extension.
    """
    source = """# apostle

## Related Ideas:

apostleship

## Links:

The "apostles" were men sent by Jesus to preach about God and his kingdom. The term "apostleship" refers to the position and authority of those who were chosen as apostles.

* The word "apostle" means "someone who is sent out for a special purpose." The apostle has the same authority as the one who sent him.
* Jesus' twelve closest disciples became the first apostles. Other men, such as Paul and James, also became apostles.
* By God's power, the apostles were able to boldly preach the gospel and heal people, and were able to force demons to come out of people."""
    expected = """<h1>apostle</h1>\n<h2>Related Ideas:</h2>\n<p>apostleship</p>"""

    md = markdown.Markdown(
        extensions=[remove_section_preprocessor.RemoveSectionExtension()]
    )
    actual = md.convert(source)
    assert expected == actual


def test_wikilink_preprocessor() -> None:
    """
    Test the remove section Markdown pre-processor extension.
    """
    source = """## Translation Suggestions:

* Also consider how this term was translated in a Bible translation in a local or national language. (See [[rc://en/ta/man/jit/translate-unknown]])"""
    expected = """<h2>Translation Suggestions:</h2>\n<ul>\n<li>Also consider how this term was translated in a Bible translation in a local or national language. (See <a href="rc://en/ta/man/jit/translate-unknown"></a>)</li>\n</ul>"""
    md = markdown.Markdown(extensions=[wikilink_preprocessor.WikiLinkExtension()])
    actual = md.convert(source)
    assert expected == actual


@pytest.mark.datafiles(EN_TW_RESOURCE_DIR)
def test_translation_word_link_preprocessor(datafiles: List) -> None:
    """
    Test the translation word link Markdown pre-processor extension.
    """
    path = str(datafiles)
    source = """## Translation Suggestions:

* It is important to translate the terms "apostle" and "disciple" in different ways.

(See also: [authority](../kt/authority.md), [disciple](../kt/disciple.md), [James (son of Zebedee)](../names/jamessonofzebedee.md), [Paul](../names/paul.md), [the twelve](../kt/thetwelve.md))"""

    expected = """<h2>Translation Suggestions:</h2>\n<ul>\n<li>It is important to translate the terms "apostle" and "disciple" in different ways.</li>\n</ul>\n<p>(See also: <a href="#en-authority">authority</a>, <a href="#en-disciple">disciple</a>, <a href="#en-jamessonofzebedee">James (son of Zebedee)</a>, <a href="#en-paul">Paul</a>, <a href="#en-thetwelve">the twelve</a>)</p>"""
    md = markdown.Markdown(
        extensions=[
            translation_word_link_preprocessor.TranslationWordLinkExtension(
                lang_code={"en": "Language code for resource"},
                tw_resource_dir={
                    path: "Base directory for paths to translation word markdown files"
                },
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual


@pytest.mark.datafiles(EN_TW_RESOURCE_DIR)
def test_translation_word_link_alt_preprocessor(datafiles: List) -> None:
    """
    Test the translation word link Markdown pre-processor extension.
    """
    path = str(datafiles)
    source = """## Translation Suggestions:

* It is important to translate the terms "apostle" and "disciple" in different ways.

(See also: [[rc://*/tw/dict/bible/kt/authority]], [[rc://*/tw/dict/bible/kt/disciple]])"""

    expected = """<h2>Translation Suggestions:</h2>\n<ul>\n<li>It is important to translate the terms "apostle" and "disciple" in different ways.</li>\n</ul>\n<p>(See also: <a href="#en-authority">authority</a>, <a href="#en-disciple">disciple</a>)</p>"""
    md = markdown.Markdown(
        extensions=[
            translation_word_link_preprocessor.TranslationWordLinkExtension(
                lang_code={"en": "Language code for resource."},
                tw_resource_dir={
                    path: "Base directory for paths to translation word markdown files"
                },
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual


@pytest.mark.datafiles(GU_TW_RESOURCE_DIR)
def test_translation_word_link_alt_gu_preprocessor(datafiles: List) -> None:
    """
    Test the translation word link Markdown pre-processor extension.
    """
    path = str(datafiles)
    source = """દ્રષ્ટાંતો એ એવીવાર્તાઓ છે જે નૈતિક પાઠો શીખવે છે. (જુઓ: [[rc://*/tw/dict/bible/kt/lawofmoses]] અને [[rc://*/tw/dict/bible/kt/disciple]] અને [[rc://*/tw/dict/bible/kt/parable]]"""
    expected = """<p>દ્રષ્ટાંતો એ એવીવાર્તાઓ છે જે નૈતિક પાઠો શીખવે છે. (જુઓ: <a href="#gu-lawofmoses">નિયમ/કાયદો/કાનૂન</a> અને <a href="#gu-disciple">શિષ્ય</a> અને <a href="#gu-parable">દ્રષ્ટાંત</a></p>"""

    md = markdown.Markdown(
        extensions=[
            translation_word_link_preprocessor.TranslationWordLinkExtension(
                lang_code={"gu": "Language code for resource."},
                tw_resource_dir={
                    path: "Base directory for paths to translation word markdown files"
                },
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual


@pytest.mark.datafiles(GU_TW_RESOURCE_DIR)
def test_translation_note_link_gu_preprocessor(datafiles: List) -> None:
    """
    Test the translation note link Markdown pre-processor extension.
    """
    path = str(datafiles)
    source = """* [ઉત્પત્તિ 4:18-19](rc://gu/tn/help/gen/04/18)
* [ઉત્પત્તિ 4:23-24](rc://gu/tn/help/gen/04/23)
* [લૂક 3:36-38](rc://gu/tn/help/luk/03/36)"""
    expected = """<ul>
<li><a href="#gu-gen-tn-ch-004-v-018">ઉત્પત્તિ 4:18-19</a></li>
<li><a href="#gu-gen-tn-ch-004-v-023">ઉત્પત્તિ 4:23-24</a></li>
<li><a href="#gu-luk-tn-ch-003-v-036">લૂક 3:36-38</a></li>
</ul>"""

    md = markdown.Markdown(
        extensions=[
            translation_word_link_preprocessor.TranslationWordLinkExtension(
                lang_code={"gu": "Language code for resource."},
                tw_resource_dir={
                    path: "Base directory for paths to translation word markdown files"
                },
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual
