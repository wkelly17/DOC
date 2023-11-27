import os

import markdown
import pytest

from document.domain import model
from document.markdown_extensions import (
    link_transformer_preprocessor,
    remove_section_preprocessor,
)
from document.utils import tw_utils

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
    source = """# blah

## Flub:

Nullam eu ante vel est convallis dignissim.  Fusce suscipit, wisi nec facilisis facilisis, est dui fermentum leo, quis tempor ligula erat quis odio.  Nunc porta vulputate tellus.  Nunc rutrum turpis sed pede.  Sed bibendum.  Aliquam posuere.  Nunc aliquet, augue nec adipiscing interdum, lacus tellus malesuada massa, quis varius mi purus non odio.  Pellentesque condimentum, magna ut suscipit hendrerit, ipsum augue ornare nulla, non luctus diam neque sit amet urna.  Curabitur vulputate vestibulum lorem.  Fusce sagittis, libero non molestie mollis, magna orci ultrices dolor, at vulputate neque nulla lacinia eros.  Sed id ligula quis est convallis tempor.  Curabitur lacinia pulvinar nibh.  Nam a sapien.


## Picture of blah:

<a href="http://example.com"><img src="http://example.com/foo.png" ></a>

## Links:

Lorem ipsum dolor sit amet, consectetuer adipiscing elit.  Donec hendrerit tempor tellus.  Donec pretium posuere tellus.  Proin quam nisl, tincidunt et, mattis eget, convallis nec, purus.  Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.  Nulla posuere.  Donec vitae dolor.  Nullam tristique diam non turpis.  Cras placerat accumsan nulla.  Nullam rutrum.  Nam vestibulum accumsan nisl.


## Delete me:

* foo
* bar

## Keep me:

* Blatz

Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus."""

    source_expected = """# blah

## Flub:

Nullam eu ante vel est convallis dignissim.  Fusce suscipit, wisi nec facilisis facilisis, est dui fermentum leo, quis tempor ligula erat quis odio.  Nunc porta vulputate tellus.  Nunc rutrum turpis sed pede.  Sed bibendum.  Aliquam posuere.  Nunc aliquet, augue nec adipiscing interdum, lacus tellus malesuada massa, quis varius mi purus non odio.  Pellentesque condimentum, magna ut suscipit hendrerit, ipsum augue ornare nulla, non luctus diam neque sit amet urna.  Curabitur vulputate vestibulum lorem.  Fusce sagittis, libero non molestie mollis, magna orci ultrices dolor, at vulputate neque nulla lacinia eros.  Sed id ligula quis est convallis tempor.  Curabitur lacinia pulvinar nibh.  Nam a sapien.


## Keep me:

* Blatz

Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus."""

    md_source = markdown.Markdown()
    expected = md_source.convert(source_expected)

    md = markdown.Markdown(
        extensions=[
            remove_section_preprocessor.RemoveSectionExtension(
                sections_to_remove=[
                    ["Picture", "Links", "Delete me"],
                    "Sections to remove",
                ]
            )
        ]
    )
    actual = md.convert(source)
    assert expected == actual


@pytest.mark.datafiles(EN_TW_RESOURCE_DIR)
def test_translation_word_link_alt_preprocessor(datafiles: list[str]) -> None:
    """
    Test the translation word link Markdown pre-processor extension.
    """
    tw_resource_dir = str(datafiles)
    source = """## Translation Suggestions:

* It is important to translate the terms "apostle" and "disciple" in different ways.

(See also: [[rc://*/tw/dict/bible/kt/authority]], [[rc://*/tw/dict/bible/kt/disciple]])"""

    expected = """<h2>Translation Suggestions:</h2>\n<ul>\n<li>It is important to translate the terms "apostle" and "disciple" in different ways.</li>\n</ul>\n<p>, )</p>"""
    resource_requests = [
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", book_code="gen"
        )
    ]
    translation_words_dict = tw_utils.translation_words_dict(tw_resource_dir)
    md = markdown.Markdown(
        extensions=[
            remove_section_preprocessor.RemoveSectionExtension(),
            link_transformer_preprocessor.LinkTransformerExtension(
                lang_code=["en", "Language code for resource."],
                resource_requests=[
                    resource_requests,
                    "The list of resource requests contained in the document request.",
                ],
                translation_words_dict=[
                    translation_words_dict,
                    "Dictionary mapping translation word asset file name sans suffix to translation word asset file path.",
                ],
            ),
        ],
    )
    actual = md.convert(source)
    assert expected == actual


@pytest.mark.datafiles(GU_TW_RESOURCE_DIR)
def test_translation_word_link_alt_gu_preprocessor(datafiles: list[str]) -> None:
    """
    Test the translation word link Markdown pre-processor extension.
    """
    tw_resource_dir = str(datafiles)
    source = """દ્રષ્ટાંતો એ એવીવાર્તાઓ છે જે નૈતિક પાઠો શીખવે છે. (જુઓ: [[rc://*/tw/dict/bible/kt/lawofmoses]] અને [[rc://*/tw/dict/bible/kt/disciple]] અને [[rc://*/tw/dict/bible/kt/parable]]"""
    expected = (
        """<p>દ્રષ્ટાંતો એ એવીવાર્તાઓ છે જે નૈતિક પાઠો શીખવે છે.  અને  અને </p>"""
    )
    resource_requests = [
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", book_code="gen"
        )
    ]
    translation_words_dict = tw_utils.translation_words_dict(tw_resource_dir)
    md = markdown.Markdown(
        extensions=[
            remove_section_preprocessor.RemoveSectionExtension(),
            link_transformer_preprocessor.LinkTransformerExtension(
                lang_code=["gu", "Language code for resource."],
                resource_requests=[
                    resource_requests,
                    "The list of resource requests contained in the document request.",
                ],
                translation_words_dict=[
                    translation_words_dict,
                    "Dictionary mapping translation word asset file name sans suffix to translation word asset file path.",
                ],
            ),
        ],
    )
    actual = md.convert(source)
    assert expected == actual


@pytest.mark.datafiles(GU_TW_RESOURCE_DIR)
def test_translation_note_link_gu_preprocessor(datafiles: list[str]) -> None:
    """
    Test the translation note link Markdown pre-processor extension.
    """
    tw_resource_dir = str(datafiles)
    source = """* [ઉત્પત્તિ 4:18-19](rc://gu/tn/help/gen/04/18)
* [ઉત્પત્તિ 4:23-24](rc://gu/tn/help/gen/04/23)
* [લૂક 3:36-38](rc://gu/tn/help/luk/03/36)"""
    expected = """<ul>
<li>ઉત્પત્તિ 4:18-19</li>
<li>ઉત્પત્તિ 4:23-24</li>
<li>લૂક 3:36-38</li>
</ul>"""

    resource_requests = [
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", book_code="gen"
        )
    ]
    translation_words_dict = tw_utils.translation_words_dict(tw_resource_dir)
    md = markdown.Markdown(
        extensions=[
            remove_section_preprocessor.RemoveSectionExtension(),
            link_transformer_preprocessor.LinkTransformerExtension(
                lang_code=["gu", "Language code for resource."],
                resource_requests=[
                    resource_requests,
                    "The list of resource requests contained in the document request.",
                ],
                translation_words_dict=[
                    translation_words_dict,
                    "Dictionary mapping translation word asset file name sans suffix to translation word asset file path.",
                ],
            ),
        ],
    )
    actual = md.convert(source)
    assert expected == actual
