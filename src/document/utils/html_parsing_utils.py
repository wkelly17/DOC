"""
This module provides utilities for use with the BeautifulSoup HTML
scraping library.
"""

from typing import Any

import bs4


def text_elements_between(cur: Any, end: Any) -> Any:
    """
    Walk the tree between a starting and ending location and yields
    the strings along the way.

    Usage:
    >>> print ' '.join(text for text in text_elements_between(soup.find('h2', text='Heading1').next_sibling,\
    soup.find('h2', text='Heading2')))

    Another example:
    >>> chapter_content = text_elements_between(parser.find("h2", text="Chapter 1").next_sibling, parser.find("h2", text="Chapter 2"))
    >>> [verse for verse in chapter_content]
    """
    while cur and cur != end:
        if isinstance(cur, bs4.NavigableString):
            text = cur.strip()
            if text:
                yield text
        cur = cur.next_element


def tag_elements_between(cur: Any, end: Any) -> Any:
    """
    Walk the tree between a starting and ending location and yields
    the tags along the way.

    Usage:
    >>> print ' '.join(tag for tag in tag_elements_between(soup.find('h2', text='Heading1').next_sibling,\
    soup.find('h2', text='Heading2')))

    Another example:
    >>> chapter_tag_content = tag_elements_between(parser.find("h2", text="Chapter 1").next_sibling, parser.find("h2", text="Chapter 2"))
    >>> [verse for verse in chapter_tag_content]
    """
    while cur and cur != end:
        yield cur
        cur = cur.next_element
