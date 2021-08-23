"""
Useful functions that are not class or instance specific for TW
resources that we use in multiple places.
"""

import icontract
import os
import pathlib

from glob import glob
from typing import Dict, List

from document import config
from document.domain import model

logger = config.get_logger(__name__)

TW = "tw"


@icontract.require(lambda resource_dir: resource_dir)
@icontract.ensure(lambda result: result)
def get_translation_word_filepaths(resource_dir: str) -> List[str]:
    """
    Get the file paths to the translation word files for the
    TWResource instance.
    """
    filepaths = glob("{}/bible/kt/*.md".format(resource_dir))
    filepaths.extend(glob("{}/bible/names/*.md".format(resource_dir)))
    filepaths.extend(glob("{}/bible/other/*.md".format(resource_dir)))
    return filepaths


@icontract.require(lambda translation_word_content: translation_word_content)
@icontract.ensure(lambda result: result)
def get_localized_translation_word(
    translation_word_content: model.MarkdownContent,
) -> model.LocalizedWord:
    """
    Get the localized translation word from the
    translation_word_content. Sometimes a translation word file has as its
    first header a list of various forms of the word. If that is the case
    we use the first form of the word in the list.
    """
    localized_translation_word = translation_word_content.split("\n")[0].split("# ")[1]
    if "," in localized_translation_word:
        # logger.debug(
        #     "localized_translation_word: %s", localized_translation_word
        # )
        # The localized word is actually multiple forms of the word separated by
        # commas, use the first form of the word.
        localized_translation_word = localized_translation_word.split(",")[0]
        # logger.debug(
        #     "Updated localized_translation_word: %s", localized_translation_word
        # )
    localized_translation_word = str.strip(localized_translation_word)
    return model.LocalizedWord(localized_translation_word)


@icontract.require(lambda lang_code: lang_code)
# @icontract.ensure(lambda result: result)
def get_tw_resource_dir(lang_code: str) -> str:
    """
    Return the location of the TW resource asset directory given the
    lang_code of the language under consideration. The location is based on
    an established convention for the directory structure that the
    system either retains or manipulates (in the case of git repo
    clones) to be consistent across lang_code, resource_type, and
    resource_code combinations.
    """
    # This is a bit hacky to "know" the actual directory path file
    # pattern/convention to expect and use it literally, albeit with some
    # globbing fuzziness. However, if we don't do this then we passing the
    # TWResource instance's resource_dir property value to them so that they
    # can pass it to the markdown extension. That end up causing design
    # issues which couple TWResource to other Resource subclass instances.
    tw_resource_dir_candidates = glob(
        "{}/{}_{}*/{}_{}*".format(
            config.get_working_dir(), lang_code, TW, lang_code, TW
        )
    )
    # If tw_resource_dir_candidates is empty it is because the user
    # did not request a TW resource as part of their document request
    # which is a valid state of affairs of course.
    return tw_resource_dir_candidates[0] if tw_resource_dir_candidates else ""


# Some document requests don't include a resource request for
# translation words. In such cases there wouldn't be a
# tw_resource_dir.
# @icontract.require(lambda tw_resource_dir: tw_resource_dir)
# @icontract.ensure(lambda result: result)
def get_translation_words_dict(tw_resource_dir: str) -> Dict[str, str]:
    """
    Given the path to the TW resource asset files, return a dictionary
    of translation word to translation word filepath mappings.
    """
    if tw_resource_dir:
        # FIXME For style, to avoid the preceding conditional, it would be nicer
        # if get_translation_word_filepaths would make tw_resource_dir Optional.
        # Really the fact that get_translation_word_filepaths globs for its
        # results means that if tw_resource_dir is the empty string we just back
        # back an empty list for translation_word_filepaths. If we go
        # that route, i.e., empty tw_resource_dir param ok, then we'll
        # want to comment out the icontract contracts on
        # get_translation_word_filepaths.
        translation_word_filepaths = get_translation_word_filepaths(tw_resource_dir)
        return {
            pathlib.Path(os.path.basename(word_filepath)).stem: word_filepath
            for word_filepath in translation_word_filepaths
        }
    else:
        return {}


# NOTE There is nothing about this function that is specific to
# translation words. If we start to accrue other utility functions
# with which this would be better grouped, then we'll later move them
# along with this function into their own module.
@icontract.require(lambda sequence: sequence)
@icontract.ensure(lambda result: result)
def uniq(sequence):  # type: ignore
    """
    Given a sequence, return a generator populated only with its
    unique elements. Works for non-hashable elements too.
    """
    import itertools, operator

    return map(operator.itemgetter(0), itertools.groupby(sequence))
