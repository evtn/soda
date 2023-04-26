from soda import Tag
from soda.tags import Literal
from soda.xml_parse import str_to_tag


class TestClass:
    def test_parse(self):
        tag = Tag.from_str('<a c="12">asdf<x>8</x>123</a>')

        assert tag["c"] == "12"
        assert not ({"c", "xmlns"} ^ tag.attributes.keys())

        content = tag.children

        assert len(content) == 3

        assert isinstance(content[0], Literal)
        assert content[0].children[0] == "asdf"

        assert isinstance(content[1], Tag)
        assert len(content[1].children) == 1

        x_child = content[1].children[0]

        assert isinstance(x_child, Literal)
        assert x_child.children[0] == "8"

        assert isinstance(content[2], Literal)
        assert content[2].children[0] == "123"

        assert str_to_tag(None) is None
