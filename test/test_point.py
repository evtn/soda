from math import pi
from soda import Point

class TestClass:
    def test_basic(self):
        p = Point()

        assert p.x == 0
        assert p.y == 0
        assert p.coords == (0, 0)

        p = Point(2, 1)
        assert p.x == 2
        assert p.y == 1
        assert p.coords == (2, 1)

    def test_op(self):
        a = Point(5, 8)
        b = Point(6, 10)

        assert (a +  b).coords == (a.x +  b.x, a.y +  b.y)
        assert (a -  b).coords == (a.x -  b.x, a.y -  b.y)
        assert (a *  b).coords == (a.x *  b.x, a.y *  b.y)
        assert (a /  b).coords == (a.x /  b.x, a.y /  b.y)
        assert (a ** b).coords == (a.x ** b.x, a.y ** b.y)

        assert (a +  6).coords == (a.x +  6, a.y +  6)
        assert (a -  6).coords == (a.x -  6, a.y -  6)
        assert (a *  6).coords == (a.x *  6, a.y *  6)
        assert (a /  6).coords == (a.x /  6, a.y /  6)
        assert (a ** 6).coords == (a.x ** 6, a.y ** 6)

    def test_rotation(self):
        a = Point(5, 8)
        
        assert abs(
            sum(
                a.rotate(degrees=90).rotate(degrees=-90)
            )
        ) < 1e-10

        assert abs(
            a.angle(a.rotate(radians=pi / 2)) - pi / 2
        ) < 1e-10

