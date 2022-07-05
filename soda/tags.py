from typing import Dict, Generator, List, Optional, TypedDict, Union, Any, overload

Node = Union["Tag", str]
Number = Union[float, int]
Value = Union[str, Number]

tab_char: str = "    "


class TagTree(TypedDict):
    tag_name: str
    children: List[Union["TagTree", str]]
    attributes: Dict[str, Any]
    self_closing: bool


def node_to_tree(node: Node):
    if isinstance(node, str):
        return str_to_tree(node)
    return node.to_tree()


def str_to_tree(node: str) -> TagTree:
    return TagTree(tag_name="#literal", children=[node], attributes={}, self_closing=True)


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
    attributes: Dict[str, Value]
    self_closing: bool

    def __init__(
        self,
        tag_name: str,
        *children: Node,
        self_closing: bool = True,
        **attributes: Value,
    ):
        self.tag_name = tag_name
        self.children = list(children)
        self.attributes = {k.replace("_", "-"): v for k, v in attributes.items()}
        self.self_closing = self_closing

    def copy(self) -> "Tag":
        return Tag(self.tag_name, *self.children, self_closing=self.self_closing, **self.attributes)

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

    def build_child(self, child: Node, tab_size: int = 0, tab_level: int = 0) -> str:
        if isinstance(child, str):
            yield " " * (tab_size * tab_level)
            yield escape(child)
        else:
            yield from child.build(tab_size, tab_level)

    def build(self, tab_size: int = 0, tab_level: int = 0) -> Generator[str, None, None]:
        tag_name = identifier(self.tag_name)
        pretty = bool(tab_size)

        tab = " " * tab_size
        tag_indent = " " * (tab_size * tab_level)
        separator = "\n" * pretty
        attr_space = "\n" if pretty else " "

        attr_separator = [attr_space, tag_indent, tab]


        if tab_size:
            yield tag_indent

        yield f"<{tag_name}"

        for key in self.attributes:
            yield from attr_separator
            yield f'{key}="{self.attributes[key]}"'
        
        if self.children or not self.self_closing:
            if self.attributes:
                yield separator
                yield tag_indent
            yield ">"

        for child in self.children:
            yield separator
            yield from self.build_child(child, tab_size, tab_level + 1)

        yield separator
        yield tag_indent

        if self.children or not self.self_closing:
            yield f"</{tag_name}>"
        else:
            yield "/>"

    def render(self, pretty: bool = False, tab_size: int = 2) -> str:
        return "".join(self.build(tab_size * pretty))

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

    def to_tree(self) -> TagTree:
        return TagTree(
            tag_name=self.tag_name,
            children=list(map(node_to_tree, self.children)),
            attributes=self.attributes.copy(),
            self_closing=self.self_closing
        )

    def to_dict(self) -> TagTree:
        return self.to_tree()

    @staticmethod
    def from_tree(tree: TagTree):
        if tree["tag_name"] == "#literal":
            return Literal(str(tree["children"][0] if tree["children"] else ""))
        elif tree["tag_name"] == "#fragment":
            return Fragment(*map(Tag.from_tree, tree["children"]))
        else:
            return Tag(
                tree["tag_name"],
                *map(Tag.from_tree, tree.get("children", "")),
                **tree.get("attributes", {}),
                self_closing=tree.get("self_closing", True)
            )

    @staticmethod
    def render_tree(tree: TagTree, pretty=False):
        return Tag.from_tree(tree).render(pretty)


class Literal:
    def __init__(self, text: str, escape: bool = True):
        self.tag_name = ""
        self.children = [text]
        self.attributes: Dict[str, Value] = {}
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

    def to_tree(self) -> TagTree:
        return TagTree(
            tag_name="#literal", 
            children=list(map(node_to_tree, self.children)), 
            attributes={}, 
            self_closing=True
        )


class Fragment(Tag):
    """React-like fragment, renders just its children"""

    def __init__(self, *children: Node):
        super().__init__("soda:fragment", *children)

    def build(self, *args):
        for child in self.children:
            yield from self.build_child(child, *args)

    def render(self, pretty: bool = False) -> str:
        raise TypeError("Can't render fragment as a root Tag")

    def to_tree(self) -> TagTree:
        return TagTree(
            tag_name="#fragment", 
            children=list(map(node_to_tree, self.children)), 
            attributes={}, 
            self_closing=True
        )


class Root(Tag):
    def __init__(
        self, *children: Node, use_namespace: bool = False, **attributes: Value
    ):
        super().__init__("svg", *children, self_closing=False, **attributes)
        if use_namespace:
            self(
                **{
                    "version": "2.0",
                    "xmlns": "http://www.w3.org/2000/svg",
                    "xmlns:xlink": "http://www.w3.org/1999/xlink",
                }
            )
