from math import pi
from soda import Point
from soda.utils import eq
import pytest


class TestClass:
    def test_basic(self):
        p = Point()

        assert p.x == 0
        assert p.y == 0
        assert p == (0, 0)

        p = Point(2, 1)
        assert p.x == 2
        assert p.y == 1
        assert p == (2, 1)

    def test_eq(self):
        a = Point(5, 8)

        assert a == (5, 8)
        assert a != 5
        assert a != 8
        assert a != object()

        b = Point.from_(12)
        assert b == 12

    def test_op(self):
        a = Point(5, 8)
        b = Point(6, 10)

        assert (a + b) == (a.x + b.x, a.y + b.y)
        assert (a - b) == (a.x - b.x, a.y - b.y)
        assert (a * b) == (a.x * b.x, a.y * b.y)
        assert (a / b) == (a.x / b.x, a.y / b.y)
        assert (a**b) == (a.x**b.x, a.y**b.y)
        assert (a % b) == (a.x % b.x, a.y % b.y)
        assert (a // b) == (a.x // b.x, a.y // b.y)

        assert (a + 6) == (a.x + 6, a.y + 6)
        assert (a - 6) == (a.x - 6, a.y - 6)
        assert (a * 6) == (a.x * 6, a.y * 6)
        assert (a / 6) == (a.x / 6, a.y / 6)
        assert (a**6) == (a.x**6, a.y**6)

        assert (6 + a) == (6 + a.x, 6 + a.y)
        assert (6 - a) == (6 - a.x, 6 - a.y)
        assert (6 * a) == (6 * a.x, 6 * a.y)
        assert (6 / a) == (6 / a.x, 6 / a.y)
        assert (6**a) == (6**a.x, 6**a.y)
        assert (6 % a) == (6 % a.x, 6 % a.y)
        assert (6 // a) == (6 // a.x, 6 // a.y)

    def test_round(self):
        for i in range(20):
            a = Point(i / 10, 1 + i / 10) + 4

            assert a.round() == (round(a.x), round(a.y))

    def test_rotation(self):
        a = Point(5, 8)

        assert a.rotate(degrees=90).rotate(degrees=-90) == a
        assert a.rotate(degrees=75).rotate(degrees=165).rotate(degrees=120) == a
        assert eq(a.angle(a.rotate(radians=pi / 2)), pi / 2)
        assert a.rotate(degrees=90) == (-8, 5)

        with pytest.raises(ValueError):
            a.rotate()  # type: ignore

        with pytest.raises(ValueError):
            a.rotate(degrees=90, radians=90)  # type: ignore

    def test_repr(self):
        a = Point(1, 2)
        assert repr(a) == "Point[1, 2]"

    def test_as(self):
        a = Point(55, 3)

        assert a.as_("mmm", "ooo") == {"mmm": 55, "ooo": 3}
