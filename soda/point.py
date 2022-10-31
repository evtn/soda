from __future__ import annotations
from typing import Iterator, Sequence, Union, overload
from math import pi, cos, sin, hypot, acos

from soda.paths import Path, compact_path
from soda.tags import Node, Tag


PointLike = Union["Point", float, Sequence[float]]

rad_to_deg_k = 180 / pi


def radians_to_degrees(radians: float) -> float:
    return radians * rad_to_deg_k


def degrees_to_radians(degrees: float) -> float:
    return degrees / rad_to_deg_k


class Point:
    def __init__(self, x: float = 0, y: float = 0):
        self.coords = x, y
        self.x: float = x
        self.y: float = y

    @staticmethod
    def from_(value: PointLike = 0) -> Point:
        if isinstance(value, Point):
            return value
        if isinstance(value, (float, int)):
            return Point(value, value)
        return Point(*value[:2])

    def __add__(self, other: PointLike = 0) -> Point:
        other = Point.from_(other)
        return Point(self.x + other.x, self.y + other.y)

    def __radd__(self, other: PointLike = 0) -> Point:
        return self + other

    def __sub__(self, other: PointLike = 0) -> Point:
        other = Point.from_(other)
        return Point(self.x - other.x, self.y - other.y)

    def __rsub__(self, other: PointLike = 0) -> Point:
        return Point.from_(other) - self

    def __mul__(self, other: PointLike = 0) -> Point:
        other = Point.from_(other)
        return Point(self.x * other.x, self.y * other.y)

    def __rmul__(self, other: PointLike = 0) -> Point:
        return self * other

    def __truediv__(self, other: PointLike = 0) -> Point:
        other = Point.from_(other)
        return Point(self.x / other.x, self.y / other.y)

    def __rtruediv__(self, other: PointLike = 0) -> Point:
        return Point.from_(other) / self

    def __pow__(self, other: PointLike = 0) -> Point:
        other = Point.from_(other)

        # this is due to the fact that float.__pow__(float) is suddenly Any (not float, not complex | float, etc.)
        new_x: float = self.x ** other.x
        new_y: float = self.y ** other.y

        assert isinstance(new_x, (float, int))
        assert isinstance(new_y, (float, int))

        return Point(new_x, new_y)

    def __rpow__(self, other: PointLike = 0) -> Point:
        return Point.from_(other) ** self

    def __mod__(self, other: PointLike = 0) -> Point:
        other = Point.from_(other)
        return Point(self.x % other.x, self.y % other.y)

    def __rmod__(self, other: PointLike = 0) -> Point:
        return Point.from_(other) % self

    def __floordiv__(self, other: PointLike = 0) -> Point:
        other = Point.from_(other)
        return Point(self.x // other.x, self.y // other.y)

    def __rfloordiv__(self, other: PointLike = 0) -> Point:
        return Point.from_(other) // self

    def round(self, ndigits: int = 0) -> Point:
        return Point(
            round(self.x, ndigits),
            round(self.y, ndigits),
        )

    def __iter__(self) -> Iterator[float]:
        return iter(self.coords)

    @overload
    def rotate(self, center: PointLike = 0, *, degrees: float, radians: None = None) -> Point:
        ...

    @overload
    def rotate(self, center: PointLike = 0, *, degrees: None = None, radians: float) -> Point:
        ...

    def rotate(self, center: PointLike = 0, *, degrees: float | None = None, radians: float | None = None) -> Point:
        error = ValueError("Either degrees or radians should be provided, not both nor neither")
        center = Point.from_(center)

        if radians is None:
            if degrees is None:
                raise error
            radians = degrees_to_radians(degrees)
        elif degrees is not None:
            raise error

        diff = self - center

        sin_vec = sin(radians) * diff
        cos_vec = cos(radians) * diff

        x = cos_vec.x - sin_vec.y
        y = sin_vec.x + cos_vec.y

        return Point(x, y) + center

    def distance(self, other: PointLike = 0) -> float:
        return hypot(*(self - other))

    def __str__(self) -> str:
        return f"Point[{self.x}, {self.y}]"

    def as_(self, x_argname: str = "x", y_argname: str = "y") -> dict[str, float]:
        return {x_argname: self.x, y_argname: self.y}

    def angle(self, other: PointLike = (1, 0), center: PointLike = 0) -> float:
        center = Point.from_(center)
        other = Point.from_(other) - center
        self = self - center

        dot_product = sum(self * other)
        distance_product = self.distance() * other.distance()

        if distance_product == 0:
            return 0

        return acos(
            dot_product / distance_product
        )

    def normalized(self) -> Point:
        return self / self.distance()

class PointPath:
    @staticmethod
    def build(*commands: str, compact: bool = False) -> str:
        if compact:
            return compact_path(" ".join(commands).split(" "))
        return " ".join(commands)

    # M x y
    @staticmethod
    def moveto(
        point: PointLike = 0,
        *, relative: bool = False
    ) -> str:
        point = Point.from_(point)
        return Path.moveto(
            point.x,
            point.y, 
            relative=relative
        )

    @staticmethod
    def M(point: PointLike = 0) -> str:
        return PointPath.moveto(point, relative=False)

    @staticmethod
    def m(point: PointLike = 0) -> str:
        return PointPath.moveto(point, relative=True)

    # L x y
    @staticmethod
    def line(
        point: PointLike = 0, 
        *, relative: bool = False
    ) -> str:
        point = Point.from_(point)
        return Path.line(
            point.x,
            point.y,
            relative=relative
        )

    @staticmethod
    def L(point: PointLike = 0) -> str:
        return PointPath.line(point, relative=False)

    @staticmethod
    def l(point: PointLike = 0) -> str:
        return PointPath.line(point, relative=True)

    # V y
    @staticmethod
    def vertical(
        point: PointLike = 0,
        *, relative: bool = False
    ) -> str:
        point = Point.from_(point)
        return Path.vertical(
            point.y,
            relative=relative
        )

    @staticmethod
    def V(y: float) -> str:
        return PointPath.vertical(y, relative=False)

    @staticmethod
    def v(y: float) -> str:
        return PointPath.vertical(y, relative=True)

    # H x
    @staticmethod
    def horizontal(
        point: PointLike = 0,
        *, relative: bool = False
    ) -> str:
        point = Point.from_(point)
        return Path.horizontal(
            point.x,
            relative=relative
        )

    @staticmethod
    def H(point: PointLike = 0) -> str:
        return PointPath.vertical(point, relative=False)

    @staticmethod
    def h(point: PointLike = 0) -> str:
        return PointPath.vertical(point, relative=True)

    # Z
    @staticmethod
    def close(*, relative: bool = False) -> str:
        return Path.close(relative=relative)

    @staticmethod
    def Z() -> str:
        return PointPath.close(relative=False)

    @staticmethod
    def z() -> str:
        return PointPath.close(relative=True)

    # C x1 y1 x2 y2 x y
    @staticmethod
    def cubic(first_control: PointLike = 0, second_control: PointLike = 0, end: PointLike = 0, *, relative: bool = False) -> str:
        first_control = Point.from_(first_control)
        second_control = Point.from_(second_control)
        end = Point.from_(end)
        return Path.cubic(
            first_control.x,
            first_control.y,
            second_control.x,
            second_control.y,
            end.x,
            end.y,
            relative=relative
        )

    @staticmethod
    def C(first_control: PointLike = 0, second_control: PointLike = 0, end: PointLike = 0) -> str:
        return PointPath.cubic(first_control, second_control, end, relative=False)

    @staticmethod
    def c(first_control: PointLike = 0, second_control: PointLike = 0, end: PointLike = 0) -> str:
        return PointPath.cubic(first_control, second_control, end, relative=True)

    # S x2 y2, x y
    @staticmethod
    def shorthand(second_control: PointLike = 0, end: PointLike = 0, *, relative: bool = False) -> str:
        second_control = Point.from_(second_control)
        end = Point.from_(end)
        return Path.shorthand(
            second_control.x,
            second_control.y,
            end.x,
            end.y,
            relative=relative
        )

    @staticmethod
    def S(second_control: PointLike = 0, end: PointLike = 0) -> str:
        return PointPath.shorthand(second_control, end, relative=False)

    @staticmethod
    def s(second_control: PointLike = 0, end: PointLike = 0) -> str:
        return PointPath.shorthand(second_control, end, relative=True)

    # Q x1 y1 x y
    @staticmethod
    def quadratic(control: PointLike = 0, end: PointLike = 0, *, relative: bool = False) -> str:
        control = Point.from_(control)
        end = Point.from_(end)
        return Path.quadratic(
            control.x,
            control.y,
            end.x,
            end.y,
            relative=relative
        )

    @staticmethod
    def Q(control: PointLike = 0, end: PointLike = 0) -> str:
        return PointPath.quadratic(control, end, relative=False)

    @staticmethod
    def q(control: PointLike = 0, end: PointLike = 0) -> str:
        return PointPath.quadratic(control, end, relative=True)

    # T x y
    @staticmethod
    def q_shorthand(end: PointLike = 0, *, relative: bool = False) -> str:
        end = Point.from_(end)
        return Path.q_shorthand(
            end.x,
            end.y,
            relative=relative
        )

    @staticmethod
    def T(end: PointLike = 0) -> str:
        return PointPath.q_shorthand(end, relative=False)

    @staticmethod
    def t(end: PointLike = 0) -> str:
        return PointPath.q_shorthand(end, relative=True)

    # A rx ry x-axis-rotation large-arc-flag sweep-flag x y
    @staticmethod
    def arc(
        radius: PointLike = 0, 
        x_axis_rotation: float = 0, 
        large_arc_flag: bool | int = 0, 
        sweep_flag: bool | int = 0, 
        end: PointLike = 0, 
        *, relative: bool = False
    ) -> str:
        radius = Point.from_(radius)
        end = Point.from_(end)
        return Path.arc(
            radius.x,
            radius.y,
            x_axis_rotation,
            large_arc_flag, 
            sweep_flag, 
            end.x,
            end.y,
            relative=relative 
        )

    @staticmethod
    def A(
        radius: PointLike = 0, 
        x_axis_rotation: float = 0, 
        large_arc_flag: bool | int = 0, 
        sweep_flag: bool | int = 0, 
        end: PointLike = 0, 
    ) -> str:
        return PointPath.arc(radius, x_axis_rotation, large_arc_flag, sweep_flag, end, relative=False)

    @staticmethod
    def a(
        radius: PointLike = 0, 
        x_axis_rotation: float = 0, 
        large_arc_flag: bool | int = 0, 
        sweep_flag: bool | int = 0, 
        end: PointLike = 0, 
    ) -> str:
        return PointPath.arc(radius, x_axis_rotation, large_arc_flag, sweep_flag, end, relative=True)

    @staticmethod
    def polygon(*points: Point, **attributes: Node) -> Tag:
        commands = [
            PointPath.line(point) if i else PointPath.moveto(point)
            for i, point in enumerate(points)
        ]

        return Tag.path(
            d=PointPath.build(*commands, PointPath.close()),
            **attributes
        )

    @staticmethod
    def polyline(*points: Point, **attributes: Node) -> Tag:
        commands = [
            PointPath.line(point) if i else PointPath.moveto(point)
            for i, point in enumerate(points)
        ]

        return Tag.path(
            d=PointPath.build(*commands),
            **attributes
        )