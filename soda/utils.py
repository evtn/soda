from typing import Callable, Iterable

from .tags import Node
from .config import config

char_range: Callable[[str, str], "map[str]"] = lambda s, e: map(
    chr, 
    range(
        ord(s), 
        ord(e) + 1
    )
)

ident_chars = {
    *char_range("a", "z"),
    *char_range("A", "Z"),
    *char_range("0", "9"),
    "-",
    "_",
    ":"
}


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")


def filter_ident_func(char: str) -> bool:
    return (
        char in ident_chars
    )


def filter_ident(text: Iterable[str]) -> str:
    return "".join(
        filter(
            filter_ident_func,
            text 
        )
    )


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
            elif not config.strip_underscores:
                yield "_"
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
        return round(value, config.decimal_length)
    return value