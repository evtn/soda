from __future__ import annotations
from typing import Iterable
import xml.etree.ElementTree as etree
from soda.tags import Literal, Tag


def xml_to_tag(xml: str) -> Tag:
    return element_to_tag(etree.fromstring(xml))


def str_to_tag(text: str | None) -> Literal | None:
    if text:
        text = text.strip()
        if text:
            return Literal(text, escape=False)
    return None


def process_children(element: etree.Element) -> Iterable[Tag]:
    text = str_to_tag(element.text)
    if text:
        yield text

    for child in element:
        yield element_to_tag(child)
        tail = str_to_tag(child.tail)
        if tail:
            yield tail


def element_to_tag(element: etree.Element) -> Tag:
    tag_name = element.tag
    attributes = element.attrib

    return Tag(tag_name)(
        *process_children(element),
        **attributes
    )


