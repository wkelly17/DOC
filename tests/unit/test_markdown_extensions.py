import markdown
import os
import pytest

from document.markdown_extensions import (
    remove_section_preprocessor,
    link_transformer_preprocessor,
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


# FIXME Temporarily commented out due to syntax issues that would
# preclude mypy from accepting it.
# FIXME Update test to new interface
# @pytest.mark.skip
# @pytest.mark.datafiles(EN_TW_RESOURCE_DIR)
# def test_link_transformer_preprocessor(datafiles: List) -> None:
#     """
#     Test the translation word link Markdown pre-processor extension.
#     """
#     path = str(datafiles)

#     assembly_strategy_kind: model.AssemblyStrategyEnum = (
#         model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
#     )
#     resource_requests: List[model.ResourceRequest] = []
#     resource_requests.append(
#         model.ResourceRequest(
#             lang_code="en", resource_type="ulb-wa", resource_code="col"
#         )
#     )
#     resource_requests.append(
#         model.ResourceRequest(
#             lang_code="en", resource_type="tn-wa", resource_code="col"
#         )
#     )

#     tw_resource_dir = tw_utils.get_tw_resource_dir("en")
#     translation_words_dict: Dict[str, str] = tw_utils.get_translation_words_dict(
#         tw_resource_dir
#     )

#     source = """## Translation Suggestions:

# * It is important to translate the terms "apostle" and "disciple" in different ways.

# (See also: [authority](../kt/authority.md), [disciple](../kt/disciple.md), [James (son of Zebedee)](../names/jamessonofzebedee.md), [Paul](../names/paul.md), [the twelve](../kt/thetwelve.md))"""

#     expected = """<h2>Translation Suggestions:</h2>
# <ul>
# <li>It is important to translate the terms "apostle" and "disciple" in different ways.</li>
# </ul>
# <p>(See also: <a href="#en-authority">authority</a>, <a href="#en-disciple">disciple</a>, <a href="#en-James son of Zebedee">James son of Zebedee</a>, <a href="#en-Paul">Paul</a>, <a href="#en-the twelve">the twelve</a>)</p>"""
#     md = markdown.Markdown(
#         extensions=[
#             link_transformer_preprocessor.LinkTransformerExtension(
#                 lang_code=["en": "Language code for resource"],
#                 resource_requests=[
#                     resource_requests: "The list of resource requests contained in the document request."
# ],
#                 translation_words_dict=[
#                     translation_words_dict,
#                     "Dictionary mapping translation word asset file name sans suffix to translation word asset file path.",
#                 ],
#             )
#         ],
#     )
#     actual = md.convert(source)
#     assert expected == actual


# FIXME Update test to new interface
@pytest.mark.skip
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
            link_transformer_preprocessor.LinkTransformerExtension(
                lang_code={"en": "Language code for resource."},
                tw_resource_dir={
                    path: "Base directory for paths to translation word markdown files"
                },
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual


# FIXME markdown extension has changed and uses localized values for
# the anchor link id too, update to new expected value
@pytest.mark.skip
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
            link_transformer_preprocessor.LinkTransformerExtension(
                lang_code={"gu": "Language code for resource."},
                tw_resource_dir={
                    path: "Base directory for paths to translation word markdown files"
                },
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual


# FIXME markdown extension has changed and uses localized values for
# the anchor link id too, update to new expected value
@pytest.mark.skip
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
            link_transformer_preprocessor.LinkTransformerExtension(
                lang_code={"gu": "Language code for resource."},
                tw_resource_dir={
                    path: "Base directory for paths to translation word markdown files"
                },
            )
        ],
    )
    actual = md.convert(source)
    assert expected == actual
