from typing import Callable, Iterable

from .tags import FlatNode, Fragment, Node
from .config_mod import config

char_range: Callable[[str, str], "map[str]"] = lambda s, e: map(
    chr, range(ord(s), ord(e) + 1)
)

ident_chars = {
    *char_range("a", "z"),
    *char_range("A", "Z"),
    *char_range("0", "9"),
    "-",
    "_",
    ":",
}


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")


def filter_ident_func(char: str) -> bool:
    return char in ident_chars


def filter_ident(text: Iterable[str]) -> str:
    return "".join(filter(filter_ident_func, text))


def normalize_ident(attr: str) -> str:
    return filter_ident(normalize_ident_gen(attr))


def normalize_ident_gen(attr: str) -> Iterable[str]:
    started = False
    skipped_underscores = 0
    replacement_char = "-" if config.replace_underscores else "_"

    for c in attr:
        if c == "_":
            if started:
                skipped_underscores += 1
            continue
        else:
            started = True

        yield replacement_char * skipped_underscores
        skipped_underscores = 0

        yield c

    if not config.strip_underscores:
        yield "_" * skipped_underscores


def trunc(value: Node) -> Node:
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return round(value, config.decimal_length)
    return value


def eq(v1: float, v2: float) -> bool:
    eps: float = 10 ** -(2 * config.decimal_length)

    return abs(v1 - v2) < eps


def node_iterator(iterable: Iterable[Node]) -> Iterable[FlatNode]:
    for elem in iterable:
        if isinstance(elem, list):
            yield from node_iterator(elem)
        elif isinstance(elem, Fragment):
            yield from elem
        else:
            yield elem
