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