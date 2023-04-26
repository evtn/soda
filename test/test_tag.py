from soda.tags import Fragment, Literal, Tag


class TestClass:
    def test_compare(self):
        tags = [
            Tag.g(a=1, b=2),
            Tag.g(a=1, b=3),
            Tag.h(a=1, b=2),
            Tag.g(a=1, b=2)("8"),
            Tag.g(a=1, b=2, c=3),
            Tag.g(a=1),
            Tag.g("8"),
            Tag.g("9", "8"),
            Tag.g("9"),
            5,
        ]

        for i in range(len(tags)):
            for j in range(i, len(tags)):
                if i == j:
                    assert tags[i] == tags[j]
                else:
                    assert tags[i] != tags[j]

    def test_compare_nesting(self):
        t1 = Tag.g(1, 2)
        t2 = Tag.g([1, 2])
        t3 = Tag.g(Fragment(1, 2))

        assert t1 == t2
        assert t1 == t3
        assert t2 == t3

    def test_data(self):
        tag = Tag.g

        tag["x"] = 1

        assert tag["x"] == 1

        tag["x"] = None

        assert "x" not in tag.attributes

        tag.append(1)

        assert tag.children[0] == 1

        tag.extend([2, 3])

        assert tag.children[1] == 2
        assert tag.children[2] == 3

        tag.pop()

        assert len(tag.children) == 2

        tag.insert(0, 48)

        assert tag.children[0] == 48

        assert tag.pop(0) == 48

        assert tag.children[0] == 1

        tag[1] = 10

        assert tag.children == [1, 10]

        tag[1] = None

        assert tag.children == [1]

        tag[:2] = [4, 5]  # type: ignore

        assert tag.children == [4, 5]

        assert tag[:2] == [4, 5]
        assert tag[1] == 5

        tag[:1] = 6

        assert tag.children == [6, 5]

        tag[:] = None

        assert not tag.children

    def test_iter_raw(self):
        t1 = Tag.g([1, 2], 3, [[8]])

        t1_iter = t1.iter_raw()

        assert next(t1_iter) == [1, 2]
        assert next(t1_iter) == 3
        assert next(t1_iter) == [[8]]
        assert next(t1_iter, None) is None

    def test_repr(self):
        tag = Tag.a(b=1)("c", "d")
        assert repr(tag) == "Tag<a attributes: 1>children: 2</a>"

        literal = Literal("abcd")

        assert repr(literal) == "Literal<'abcd'>"
