from __future__ import annotations

from typing import Iterator, Optional, Sequence, Union, overload

from wordstreamer import Context, Renderable, TokenStream
from wordstreamer.stream_utils import separated

FlatNode = Union["Renderable", str, float]
Node = Union[FlatNode, "list[Node]"]


class MetaTag(type):
    def __getattr__(self, tag_name: str) -> Tag:
        return Tag(tag_name)


class Tag(Renderable, metaclass=MetaTag):
    """

    Main class of the module, used to create tags.

    To create a simple `<tagname>` tag, use a shorthand: `Tag.tagname`.

    You can then call it to mutate its contents:

    - `Tag.tagname(child1, child2)` adds two children nodes (could be tags or text-like values: strings/numbers, or a list of nodes)
    - `Tag.tagname(child1, child2, a=1, b=2)` same as above, but sets `a` attribute to `1`, `b` to 2. Attribute types could be the same as with nodes.

    To set contents in one call and/or manage self-closing behaviour, use Tag constructor:

    `Tag(tag_name: str, *children: Node, self_closing: bool = True, **attributes: Node)`

    """

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
        return Tag(
            self.tag_name,
            *self.children,
            self_closing=self.self_closing,
            **self.attributes,
        )

    @overload
    def set_attribute(self, attr: str, value: None) -> None: ...

    @overload
    def set_attribute(self, attr: str, value: Node) -> Node: ...

    @overload
    def set_attribute(self, attr: str, value: Node | None) -> Node | None: ...

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
    def __setitem__(self, item: str | int | slice, value: Node) -> Node: ...

    @overload
    def __setitem__(self, item: str | int | slice, value: None) -> None: ...

    @overload
    def __setitem__(
        self, item: str | int | slice, value: Optional[Node]
    ) -> Optional[Node]: ...

    def __setitem__(
        self, item: str | int | slice, value: Optional[Node]
    ) -> Optional[Node]:
        # slice is basically slice[Any, Any, Any] and https://github.com/python/typeshed/issues/8647 looks dead
        # after an hour of thinking and three broken keyboards I've decided to do this:
        if isinstance(item, slice):  # type: ignore[misc]
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
    def __getitem__(self, item: int) -> Node: ...

    @overload
    def __getitem__(self, item: slice) -> list[Node]: ...

    @overload
    def __getitem__(self, item: str) -> Node: ...

    def __getitem__(
        self, item: Union[str, int, slice]
    ) -> Optional[Union[Node, list[Node], Node]]:
        # check __setitem__ for explanation of ignore
        if isinstance(item, (int, slice)):  # type: ignore[misc]
            return self.children[item]

        return self.get_attribute(item)

    def insert(self, index: int, node: Node) -> None:
        """Inserts an entry into the tag"""
        self.children.insert(index, node)

    def append(self, child: Node) -> None:
        """A more list-like way to add a node to the tag"""
        self(child)

    def extend(self, children: Sequence[Node]) -> None:
        """A more list-like way to add several nodes to the tag"""
        self(*children)

    def pop(self, index: int = -1) -> Node:
        """Pop one (by default last one) entry from the tag"""
        return self.children.pop(index)

    def __iter__(self) -> Iterator[FlatNode]:
        return iter(node_iterator(self.children))

    def iter_raw(self) -> Iterator[Node]:
        return iter(self.children)

    def __call__(self, *children: Node, **attributes: Node) -> Tag:
        self.children.extend(children)

        if attributes:
            for attr in attributes:
                self[attr] = attributes[attr]
        return self

    def __repr__(self) -> str:
        return f"Tag<{self.tag_name} attributes: {len(self.attributes)}>children: {len(self.children)}</{self.tag_name}>"

    def __str__(self) -> str:
        return self.render()

    def build_child(
        self,
        child: FlatNode,
        context: Context,
    ) -> TokenStream:
        tab_level = self.get_tab_level(context) + 1
        tab_size = self.get_tab_size(context)

        if isinstance(child, (float, int)):
            yield from self.build_child(str(trunc(child)), context)
            return

        if isinstance(child, str):
            yield " " * (tab_size * tab_level)
            yield escape(child)
            return

        yield from child.stream(
            context.derive(
                tab_size=tab_size,
            )
        )

    def compare_attrs(self, other: Tag) -> bool:
        attrs1 = self.attributes
        attrs2 = other.attributes

        if attrs1.keys() ^ attrs2.keys():
            return False

        for key in attrs1:
            if attrs1[key] != attrs2[key]:
                return False

        return True

    def compare_children(self, other: Tag) -> bool:
        iter_self = iter(self)
        iter_other = iter(other)

        # be aware that we can't compare length here because possible
        # node nesting prevents us from doing so

        for self_child in iter_self:
            other_child = next(iter_other, None)

            if other_child is None:
                return False

            if self_child != other_child:
                return False

        # remaining elements in `other`
        if next(iter_other, None) is not None:
            return False

        return True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return False

        return (
            (self.tag_name == other.tag_name)
            and self.compare_attrs(other)
            and self.compare_children(other)
        )

    def get_tab_size(self, context: Context) -> int:
        tab_size = context.tab_size

        if not isinstance(tab_size, int):
            return 0

        return tab_size

    def get_tab_level(self, context: Context) -> int:
        tab_level = context.tab_level

        if not isinstance(tab_level, int):
            return 0

        return tab_level

    def is_pretty(self, context: Context) -> bool:
        tab_size = self.get_tab_size(context)

        if not tab_size:
            return False

        return context.pretty is True

    def build(self, context: Context) -> TokenStream:
        """alias for Tag.stream for some compatibility with 1.x (not full since TokenStream != Iterable[str])"""
        return self.stream(context)

    def stream(self, context: Context) -> TokenStream:
        tab_size = self.get_tab_size(context)
        tab_level = self.get_tab_level(context)

        tag_name = self.tag_name
        pretty = self.is_pretty(context)

        tab = " " * tab_size
        tag_indent = " " * (tab_size * tab_level)
        separator = "\n" * pretty
        attr_space = "\n" if pretty else " "
        quote = '"'

        attr_separator = [attr_space, tag_indent, tab]
        newline_indented = [separator, tag_indent]

        if tab_size:
            yield tag_indent

        yield self.brackets[0]  # <
        yield tag_name

        for key in self.attributes:
            yield from attr_separator
            yield str(key)
            yield self.key_value_sep  # =
            yield quote

            value = self.attributes[key]
            if isinstance(value, Tag):
                value = value.render()
            else:
                value = str(value)

            yield value.replace(quote, "&quot;")
            yield quote

        if self.attributes:
            yield from newline_indented

        if self.children or not self.self_closing:
            yield self.brackets[2]  # >

        for child in self:
            yield separator
            yield from self.build_child(child, context)

        if self.children:
            yield from newline_indented

        if self.children or not self.self_closing:
            yield self.brackets[1]  # </
            yield tag_name
            yield self.brackets[2]  # >
        else:
            yield self.brackets[3]  # />

    def render(self, pretty: bool = False, tab_size: int = 2) -> str:
        return self.render_string(
            {
                "pretty": pretty,
                "tab_size": tab_size * pretty,
            }
        )

    def prerender(self, pretty: bool = False) -> Literal:
        """Renders a tag into a non-escaping literal. Could speed up rendering of heavy tags."""
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

    def stream(self, context: Context) -> TokenStream:
        separator = "\n" * bool(self.is_pretty(context))

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

    def build_children(self, context) -> TokenStream:
        for child in self:
            yield from self.build_child(child, context)

    def stream(self, context: Context) -> TokenStream:
        return separated(
            *[self.build_child(child, context) for child in self],
            separator="\n" * self.is_pretty(context),
        )

    def copy(self) -> Fragment:
        return Fragment(*self.children)


from .utils import escape, node_iterator, normalize_ident, trunc
from .xml_parse import xml_to_tag
