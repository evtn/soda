from soda import Tag, Literal
from soda import config


class TestClass:
    def test_basic(self):
        assert Tag.g.render() == "<g/>"
        assert Tag("g").render() == "<g/>"
        assert Tag("g", "test").render() == "<g>test</g>"

    def test_closing(self):
        assert Tag("g", self_closing=False).render() == "<g></g>"

    def test_attributes(self):
        assert Tag.g(x="1", y="2").render() == '<g x="1" y="2"/>'
        assert Tag.g(x=1, y=2).render() == '<g x="1" y="2"/>'
        assert (
            Tag.g(qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM=1).render()
            == '<g qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM="1"/>'
        )
        assert Tag.g(aაвá=1).render() == '<g a="1"/>'

    def test_escape(self):
        assert Tag.g("&").render() == "<g>&amp;</g>"
        assert Literal("&").render() == "&amp;"
        assert Literal("&", escape=False).render() == "&"

    def test_rounding(self):
        config.decimal_length = 2
        assert Tag.g(x=1 / 3).render() == '<g x="0.33"/>'

        config.decimal_length = 3
        assert Tag.g(x=1 / 3).render() == '<g x="0.333"/>'

    def test_underscores(self):
        config.replace_underscores = True
        config.strip_underscores = True
        assert Tag.g(cla_ss_="test").render() == '<g cla-ss="test"/>'

        config.replace_underscores = False
        config.strip_underscores = True
        assert Tag.g(cla_ss_="test").render() == '<g cla_ss="test"/>'

        config.replace_underscores = True
        config.strip_underscores = False
        assert Tag.g(cla_ss_="test").render() == '<g cla-ss_="test"/>'

        config.replace_underscores = False
        config.strip_underscores = False
        assert Tag.g(cla_ss_="test").render() == '<g cla_ss_="test"/>'

    def test_pretty(self):
        assert (
            Tag.g.render(pretty=True) == "<g/>"
        )  # no extra newlines/spaces, it's a simple tag
        assert Tag.g(x=1, y=2).render(pretty=True) == '<g\n  x="1"\n  y="2"\n/>'
        assert Tag.g("test", x=1).render(pretty=True) == '<g\n  x="1"\n>\n  test\n</g>'

    def test_nested_children(self):
        a = Tag.a
        assert Tag.g([a, [a, [a]]]).render(pretty=False) == "<g><a/><a/><a/></g>"
