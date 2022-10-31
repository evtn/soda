from __future__ import annotations
from typing import Iterable, Optional, Type, Union, cast, overload


Node = Union["Tag", str, float, "list[Node]"]


from .utils import escape, normalize_ident, trunc


class MetaTag(type):
    def __getattr__(self, tag_name: str) -> Tag:
        return Tag(tag_name)


class Tag(metaclass=MetaTag):
    tag_name: str
    children: list[Node]
    attributes: dict[str, Node]
    self_closing: bool
    brackets: list[str] = ["<", "</", ">", "/>"]
    key_value_sep: str = "="

    def __init__(
        self,
        tag_name: str,
        *children: Node,
        self_closing: bool = True,
        **attributes: Node,
    ):
        self.tag_name = normalize_ident(tag_name)
        self.children = list(children)
        self.attributes = {}
        for k in attributes:
            self[k] = attributes[k]
        self.self_closing = self_closing

    def copy(self) -> Tag:
        return Tag(self.tag_name, *self.children, self_closing=self.self_closing, **self.attributes)

    @overload
    def set_attribute(self, attr: str, value: None) -> None:
        ...
    @overload
    def set_attribute(self, attr: str, value: Node) -> Node:
        ...
    @overload
    def set_attribute(self, attr: str, value: Node | None) -> Node | None:
        ...
    def set_attribute(self, attr: str, value: Optional[Node]) -> Optional[Node]:
        """sets tag attribute to value. If None is passed, deletes attribute"""
        attr = normalize_ident(attr)
        if value is None:
            if attr in self.attributes:
                self.attributes.pop(attr)
        else:
            self.attributes[attr] = trunc(value)
        return value

    def get_attribute(self, attr: str) -> Optional[Node]:
        """returns tag attribute or None"""
        return self.attributes.get(normalize_ident(attr))

    @overload
    def __setitem__(self, item: str | int | slice, value: Node) -> Node:
        ...
    @overload
    def __setitem__(self, item: str | int | slice, value: None) -> None:
        ...
    @overload
    def __setitem__(self, item: str | int | slice, value: Optional[Node]) -> Optional[Node]:
        ...
    def __setitem__(self, item: str | int | slice, value: Optional[Node]) -> Optional[Node]:
        # slice is basically slice[Any, Any, Any] and https://github.com/python/typeshed/issues/8647 looks dead
        # after an hour of thinking and three broken keyboards I've decided to do this:
        if isinstance(item, slice): # type: ignore[misc]
            if value is None:
                value = []
            elif not isinstance(value, list):
                value = [value]
            self.children[item] = value
            return value
        elif isinstance(item, int):
            if value is None:
                return self.children.pop(item)
            self.children[item] = value
            return value

        return self.set_attribute(item, value)

    @overload
    def __getitem__(self, item: int) -> Node:
        ...
    @overload
    def __getitem__(self, item: slice) -> list[Node]:
        ...
    @overload
    def __getitem__(self, item: str) -> Node:
        ...
    def __getitem__(
        self, item: Union[str, int, slice]
    ) -> Optional[Union[Node, list[Node], Node]]:
        # check __setitem__ for explanation of ignore
        if isinstance(item, (int, slice)): # type: ignore[misc]
            return self.children[item]

        return self.get_attribute(item)

    def __call__(self, *children: Node, **attributes: Node) -> Tag:
        if children:
            self.children.extend(children)
        if attributes:
            for attr in attributes:
                self[attr] = attributes[attr]
        return self

    def __repr__(self) -> str:
        return f"Tag<{self.tag_name} attributes: {len(self.attributes)}>children: {len(self.children)}</{self.tag_name}>"

    def __str__(self) -> str:
        return self.render()

    def build_child(self, child: Node, tab_size: int = 0, tab_level: int = 0) -> Iterable[str]:
        if isinstance(child, (float, int)):
            return self.build_child(str(trunc(child)), tab_size, tab_level)
        
        if isinstance(child, str):
            yield " " * (tab_size * tab_level)
            yield escape(child)
        elif isinstance(child, list):
            for subchild in child:
                yield from self.build_child(subchild, tab_size, tab_level)
        else:
            yield from child.build(tab_size, tab_level)

    def build(self, tab_size: int = 0, tab_level: int = 0) -> Iterable[str]:
        tag_name = self.tag_name
        pretty = bool(tab_size)

        tab = " " * tab_size
        tag_indent = " " * (tab_size * tab_level)
        separator = "\n" * pretty
        attr_space = "\n" if pretty else " "
        quote = '"'

        attr_separator = [attr_space, tag_indent, tab]
        newline_indented = [separator, tag_indent]

        if tab_size:
            yield tag_indent

        yield self.brackets[0] # <
        yield tag_name

        for key in self.attributes:
            yield from attr_separator
            yield str(key)
            yield self.key_value_sep
            yield quote

            value = self.attributes[key]
            if isinstance(value, Tag):
                value = value.render()
            else:
                value = str(value)

            yield value.replace(quote, '&quot;')
            yield quote
        
        if self.attributes:
            yield from newline_indented

        if self.children or not self.self_closing:
            yield self.brackets[2]

        for child in self.children:
            yield separator
            yield from self.build_child(child, tab_size, tab_level + 1)

        if self.children:
            yield from newline_indented

        if self.children or not self.self_closing:
            yield self.brackets[1] # </
            yield tag_name
            yield self.brackets[2] # >
        else:
            yield self.brackets[3] # />

    def render(self, pretty: bool = False, tab_size: int = 2) -> str:
        return "".join(self.build(tab_size * pretty))

    def prerender(self, pretty: bool = False) -> Literal:
        """Renders a tag into a non-escaping literal. Could be useful for heavy tags."""
        return Literal(self.render(pretty), escape=False)

    @staticmethod
    def from_str(text: str) -> Tag:
        return xml_to_tag(text)


class Literal(Tag):
    def __init__(self, text: str, escape: bool = True):
        self.tag_name = ""
        self.children = [text.strip()]
        self.attributes = {}
        self.escape = escape

    def copy(self) -> Literal:
        assert isinstance(self.children[0], str)
        return Literal(self.children[0], self.escape)

    def build(self, tab_size: int = 0, tab_level: int = 0) -> Iterable[str]:
        separator = "\n" * bool(tab_size)

        for child in self.children:
            yield separator

            contents = str(child)

            if self.escape:
                yield escape(contents)
            else:
                yield contents

    def __repr__(self) -> str:
        return f"Literal<{repr(self.children[0])}>"

    def __str__(self) -> str:
        return self.render()


class Fragment(Tag):
    """React-like fragment, renders just its children"""

    def __init__(self, *children: Node):
        super().__init__("soda:fragment", *children)

    def build(self, tab_size: int = 0, tab_level: int = 0) -> Iterable[str]:
        for child in self.children:
            yield from self.build_child(child, tab_size, tab_level)

    def render(self, pretty: bool = False, tab_size: int = 2) -> str:
        sep = "\n" * pretty
        return sep.join(self.build(tab_size * pretty))

    def copy(self) -> Fragment:
        return Fragment(*self.children)


from soda.xml_parse import xml_to_tag