from soda.paths import Path
from soda.point import PointPath

result = "A 1.1 2 3 0 1 6 7 L 8 9 V 10 H 11 Q 12 -13 14 15 T 16 17 C 17 18 19 20 21 22 S 23 24 25 26 M 27 0.5 Z"
result_compact = (
    "A1.1 2 3 0 1 6 7L8 9V10H11Q12-13 14 15T16 17C17 18 19 20 21 22S23 24 25 26M27 .5Z"
)


class TestClass:
    def test_basic(self):
        commands = [
            Path.arc(1.1, 2, 3, 4, 5, 6, 7),
            Path.line(8, 9),
            Path.vertical(10),
            Path.horizontal(11),
            Path.quadratic(12, -13, 14, 15),
            Path.q_shorthand(16, 17),
            Path.cubic(17, 18, 19, 20, 21, 22),
            Path.shorthand(23, 24, 25, 26),
            Path.moveto(27, 0.5),
            Path.close(),
        ]

        assert Path.build(*commands) == result

        assert Path.build(*commands, compact=True) == result_compact

    def test_short(self):
        commands_absolute = [
            Path.A(1.1, 2, 3, 4, 5, 6, 7),
            Path.L(8, 9),
            Path.V(10),
            Path.H(11),
            Path.Q(12, -13, 14, 15),
            Path.T(16, 17),
            Path.C(17, 18, 19, 20, 21, 22),
            Path.S(23, 24, 25, 26),
            Path.M(27, 0.5),
            Path.Z(),
        ]

        commands_relative = [
            Path.a(1.1, 2, 3, 4, 5, 6, 7),
            Path.l(8, 9),
            Path.v(10),
            Path.h(11),
            Path.q(12, -13, 14, 15),
            Path.t(16, 17),
            Path.c(17, 18, 19, 20, 21, 22),
            Path.s(23, 24, 25, 26),
            Path.m(27, 0.5),
            Path.z(),
        ]

        p_abs = Path.build(*commands_absolute)
        p_rel = Path.build(*commands_relative)

        assert p_abs == result
        assert p_abs.lower() == p_rel

    def test_pointpath_basic(self):
        commands = [
            PointPath.arc((1.1, 2), 3, 4, 5, (6, 7)),
            PointPath.line((8, 9)),
            PointPath.vertical(10),
            PointPath.horizontal(11),
            PointPath.quadratic((12, -13), (14, 15)),
            PointPath.q_shorthand((16, 17)),
            PointPath.cubic((17, 18), (19, 20), (21, 22)),
            PointPath.shorthand((23, 24), (25, 26)),
            PointPath.moveto((27, 0.5)),
            PointPath.close(),
        ]

        assert PointPath.build(*commands) == result

        assert PointPath.build(*commands, compact=True) == result_compact

    def test_pointpath_short(self):
        commands_absolute = [
            PointPath.A((1.1, 2), 3, 4, 5, (6, 7)),
            PointPath.L((8, 9)),
            PointPath.V(10),
            PointPath.H(11),
            PointPath.Q((12, -13), (14, 15)),
            PointPath.T((16, 17)),
            PointPath.C((17, 18), (19, 20), (21, 22)),
            PointPath.S((23, 24), (25, 26)),
            PointPath.M((27, 0.5)),
            PointPath.Z(),
        ]

        commands_relative = [
            PointPath.a((1.1, 2), 3, 4, 5, (6, 7)),
            PointPath.l((8, 9)),
            PointPath.v(10),
            PointPath.h(11),
            PointPath.q((12, -13), (14, 15)),
            PointPath.t((16, 17)),
            PointPath.c((17, 18), (19, 20), (21, 22)),
            PointPath.s((23, 24), (25, 26)),
            PointPath.m((27, 0.5)),
            PointPath.z(),
        ]

        p_abs = PointPath.build(*commands_absolute)
        p_rel = PointPath.build(*commands_relative)

        assert p_abs == result
        assert p_abs.lower() == p_rel

    def test_poly(self):
        points = [(1, 2), (4, 5), (6, 7)]

        polygon = PointPath.polygon(*points)
        polyline = PointPath.polyline(*points)

        assert polygon.render() == '<path d="M1 2L4 5L6 7Z"/>'
        assert polyline.render() == '<path d="M1 2L4 5L6 7"/>'
