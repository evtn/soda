from typing import Dict, Generator, List, Optional, Union, Any, overload

Node = Union["Tag", str]
Number = Union[float, int]
Value = Union[str, Number]

tab_char: str = "    "


def add_tab(text: str) -> str:
    if text:
        return tab_char + text.replace("\n", "\n" + tab_char)
    return ""


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")


def identifier(text: str) -> str:
    return "".join(filter(lambda x: x in ["-", ":"] or x.isalnum(), str(text)))


class MetaTag(type):
    def __getattr__(self, attr: str) -> "Tag":
        return Tag(attr.replace("_", "-"))


class Tag(metaclass=MetaTag):
    tag_name: str
    children: List[Node]
    attributes: Dict[str, Any]
    self_closing: bool

    def __init__(
        self,
        tag_name: str,
        *children: Node,
        self_closing: bool = True,
        **attributes: Any,
    ):
        self.tag_name = tag_name
        self.children = list(children)
        self.attributes = {k.replace("_", "-"): v for k, v in attributes.items()}
        self.self_closing = self_closing

    def copy(self) -> "Tag":
        return Tag(self.tag_name, *self.children, **self.attributes)

    def render_attributes(self):
        if self.attributes:
            result = add_tab(
                "\n".join(
                    f'{identifier(key)}="{value}"'
                    for key, value in self.attributes.items()
                )
            )
            return f"\n{result}\n"
        return ""

    @staticmethod
    def render_node(node: Node) -> str:
        if isinstance(node, str):
            return escape(node)
        return node.render(True)

    def render_children(self) -> str:
        if self.children:
            result = "\n".join(self.render_node(child) for child in self.children)
            if result:
                return add_tab(result)
        return ""

    @overload
    def set_attribute(self, attr: str, value: None) -> None:
        ...

    @overload
    def set_attribute(self, attr: str, value: Value) -> Value:
        ...

    def set_attribute(self, attr: str, value: Optional[Value]) -> Optional[Value]:
        """sets tag attribute to value. If None is passed, deletes attribute"""
        attr = attr.replace("_", "-")
        if value is None:
            if attr in self.attributes:
                self.attributes.pop(attr)
        else:
            self.attributes[attr] = value
        return value

    def get_attribute(self, attr: str) -> Optional[Value]:
        """returns tag attribute or None"""
        return self.attributes.get(attr.replace("_", "-"))

    @overload
    def __setitem__(self, item: int, value: Node) -> Node:
        ...

    @overload
    def __setitem__(self, item: slice, value: List[Node]) -> List[Node]:
        ...

    @overload
    def __setitem__(self, item: str, value: Optional[Value]) -> Optional[Value]:
        ...

    def __setitem__(self, item, value) -> Union[Node, List[Node], Optional[Value]]:
        if isinstance(item, (int, slice)):
            self.children[item] = value
            return value
        return self.set_attribute(item, value)

    @overload
    def __getitem__(self, item: int) -> Node:
        ...

    @overload
    def __getitem__(self, item: slice) -> List[Node]:
        ...

    @overload
    def __getitem__(self, item: str) -> Value:
        ...

    def __getitem__(
        self, item: Union[str, int, slice]
    ) -> Optional[Union[Node, List[Node], Value]]:
        if isinstance(item, (int, slice)):
            return self.children[item]
        return self.get_attribute(item)

    def __call__(self, *children: Node, **attributes: Any) -> "Tag":
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

    def build_child(self, child: Node) -> str:
        if isinstance(child, str):
            return escape(child)
        return "".join(child.build())

    def build(self) -> Generator[str, None, None]:
        tag_name = identifier(self.tag_name)
        yield f"<{tag_name}"

        if self.attributes:
            yield " "

        for key in self.attributes:
            yield f'{key}="{self.attributes[key]}" '

        if self.children or not self.self_closing:
            yield ">"

        for child in self.children:
            yield self.build_child(child)

        if self.children or not self.self_closing:
            yield f"</{tag_name}>"
        else:
            yield "/>"

    def render(self, pretty: bool = False) -> str:
        if not pretty:
            return "".join(self.build())

        children = self.render_children()
        attributes = self.render_attributes()
        tag_name = identifier(self.tag_name)
        open_tag = f"<{tag_name}"

        if children:
            children = "\n".join([">", children, ""])
            close_tag = f"</{tag_name}>"
        elif not self.self_closing:
            close_tag = f"></{tag_name}>"
        else:
            close_tag = f"/>"

        return f"{open_tag}{attributes}{children}{close_tag}"

    def prerender(self, pretty: bool = False) -> "Literal":
        """Renders a tag into a non-escaping literal. Could be useful for heavy tags."""
        return Literal(self.render(pretty), escape=False)


class Literal:
    def __init__(self, text: str, escape: bool = True):
        self.tag_name = ""
        self.children = [text]
        self.attributes = {}
        self.escape = escape

    def copy(self) -> "Literal":
        return Literal(self.children[0], self.escape)

    def render(self, pretty: bool = False) -> str:
        children = self.render_children()
        if self.escape:
            return escape(children)
        return children

    def render_children(self):
        return "".join(map(str, self.children))


class Fragment(Tag):
    """React-like fragment, renders just its children"""

    def __init__(self, *children: Node):
        super().__init__("soda:fragment", *children)

    def render(self, pretty: bool = False) -> str:
        result = [self.build_child(child) for child in self.children]
        if pretty:
            return "\n".join(result)
        return "".join(result)


class Root(Tag):
    def __init__(
        self, *children: Node, use_namespace: bool = False, **attributes: Value
    ):
        super().__init__("svg", *children, **attributes)
        if use_namespace:
            self(
                **{
                    "version": "2.0",
                    "xmlns": "http://www.w3.org/2000/svg",
                    "xmlns:xlink": "http://www.w3.org/1999/xlink",
                }
            )
