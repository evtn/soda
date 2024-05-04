from __future__ import annotations
from typing import Iterable
import lxml.etree as etree
from .custom_tags import XMLComment
from .tags import Literal, Tag


def build_prefixed_name(prefix: str | None, content: str | None) -> str:
    filtered = filter(None, [prefix, content])

    return ":".join(filtered)


def xml_to_tag(xml: str) -> Tag:
    root = etree.fromstring(xml.encode())

    root_ns = root.nsmap

    namespace_attributes = {
        build_prefixed_name("xmlns", k): v for k, v in root_ns.items()
    }

    return element_to_tag(root)(**namespace_attributes)


def str_to_tag(text: str | None) -> Literal | None:
    if text:
        text = text.strip()
        if text:
            return Literal(text, escape=False)
    return None


def process_children(element: etree._Element) -> Iterable[Tag]:
    text = str_to_tag(element.text)
    if text:
        yield text

    for child in element:
        yield element_to_tag(child)
        tail = str_to_tag(child.tail)
        if tail:
            yield tail


def element_to_tag(element: etree._Element) -> Tag:
    if isinstance(element.tag, etree._Comment):
        return XMLComment(element.tag.text)

    tag_name = element.tag.split("}")[-1]
    raw_attributes = element.attrib

    reverse_nsmap = {v: k for k, v in element.nsmap.items()}

    attributes: dict[str, str] = {}

    for key, value in raw_attributes.items():
        if "{" in key:
            nsurl, attr_name = key[1:].split("}")

            ns_name = reverse_nsmap.get(nsurl)

            key = build_prefixed_name(ns_name, attr_name)

        attributes[key] = value

    return Tag(tag_name)(*process_children(element), **attributes)
