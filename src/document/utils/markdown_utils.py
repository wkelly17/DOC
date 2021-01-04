import icontract
import re
from document.utils import file_utils


def remove_md_section(md: str, section_name: str) -> str:
    """ Given markdown and a section name, removes the section and the text contained in the section. """
    header_regex = re.compile("^#.*$")
    section_regex = re.compile("^#+ " + section_name)
    out_md = ""
    in_section = False
    for line in md.splitlines():
        if in_section:
            if header_regex.match(line):
                # We found a header.  The section is over.
                out_md += line + "\n"
                in_section = False
        else:
            if section_regex.match(line):
                # We found the section header.
                in_section = True
            else:
                out_md += line + "\n"
    return out_md


@icontract.require(lambda text: text is not None)
def increase_headers(text: str, increase_depth: int = 1) -> str:
    if text:
        text = re.sub(
            r"^(#+) +(.+?) *#*$",
            r"\1{0} \2".format("#" * increase_depth),
            text,
            flags=re.MULTILINE,
        )
    return text


@icontract.require(lambda text: text is not None)
def decrease_headers(text: str, minimum_header: int = 1, decrease: int = 1) -> str:
    if text:
        text = re.sub(
            r"^({0}#*){1} +(.+?) *#*$".format(
                "#" * (minimum_header - decrease), "#" * decrease
            ),
            r"\1 \2",
            text,
            flags=re.MULTILINE,
        )
    return text


@icontract.require(lambda text: text is not None)
def get_first_header(text: str) -> str:
    lines = text.split("\n")
    if lines:
        for line in lines:
            if re.match(r"^ *#+ ", line):
                return re.sub(r"^ *#+ (.*?) *#*$", r"\1", line)
        return lines[0]
    return "NO TITLE"
