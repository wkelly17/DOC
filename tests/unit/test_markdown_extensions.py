import markdown
import pytest

from document.markdown_extensions import (
    wikilink_preprocessor,
    remove_section_preprocessor,
    translation_word_link_preprocessor,
    # substitution_preprocessor,
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


def test_translation_word_link_preprocessor() -> None:
    """
    Test the translation word link Markdown pre-processor extension.
    """
    source = """## Translation Suggestions:

* It is important to translate the terms "apostle" and "disciple" in different ways.

(See also: [authority](../kt/authority.md), [disciple](../kt/disciple.md), [James (son of Zebedee)](../names/jamessonofzebedee.md), [Paul](../names/paul.md), [the twelve](../kt/thetwelve.md))"""

    expected = """<h2>Translation Suggestions:</h2>\n<ul>\n<li>It is important to translate the terms "apostle" and "disciple" in different ways.</li>\n</ul>\n<p>(See also: <a href="#en-authority">authority</a>, <a href="#en-disciple">disciple</a>, <a href="#en-jamessonofzebedee">James (son of Zebedee)</a>, <a href="#en-paul">Paul</a>, <a href="#en-thetwelve">the twelve</a>)</p>"""
    md = markdown.Markdown(
        extensions=[
            translation_word_link_preprocessor.TranslationWordLinkExtension(
                # FIXME More parameters are required now
                lang_code={"en": "Language code for resource."}
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual
