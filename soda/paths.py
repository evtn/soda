from __future__ import annotations
from soda.utils import trunc

def value_to_str(value: object) -> str:
    if isinstance(value, float):
        return str(trunc(value))
    return str(value)

class Path:
    @staticmethod
    def build(*commands: str, compact: bool = False) -> str:
        if compact:
            return compact_path(" ".join(commands).split(" "))
        return " ".join(commands)

    # M x y
    @staticmethod
    def moveto(
        x: float = 0, 
        y: float = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Mm"[relative]
        return " ".join(map(value_to_str, [prefix, x, y]))

    @staticmethod
    def M(x: float, y: float) -> str:
        return Path.moveto(x, y, relative=False)

    @staticmethod
    def m(x: float, y: float) -> str:
        return Path.moveto(x, y, relative=True)

    # L x y
    @staticmethod
    def line(
        x: float = 0, 
        y: float = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Ll"[relative]
        return " ".join(map(value_to_str, [prefix, x, y]))

    @staticmethod
    def L(x: float, y: float) -> str:
        return Path.line(x, y, relative=False)

    @staticmethod
    def l(x: float, y: float) -> str:
        return Path.line(x, y, relative=True)

    # V y
    @staticmethod
    def vertical(
        y: float = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Vv"[relative]
        return " ".join(map(value_to_str, [prefix, y]))

    @staticmethod
    def V(y: float) -> str:
        return Path.vertical(y, relative=False)

    @staticmethod
    def v(y: float) -> str:
        return Path.vertical(y, relative=True)

    # H x
    @staticmethod
    def horizontal(
        x: float = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Hh"[relative]
        return " ".join(map(value_to_str, [prefix, x]))

    @staticmethod
    def H(x: float) -> str:
        return Path.vertical(x, relative=False)

    @staticmethod
    def h(x: float) -> str:
        return Path.vertical(x, relative=True)

    # Z
    @staticmethod
    def close(*, relative: bool = False) -> str:
        # there's no difference between two, but consistent API is better
        return "Zz"[relative]

    @staticmethod
    def Z() -> str:
        return Path.close(relative=False)

    @staticmethod
    def z() -> str:
        return Path.close(relative=True)

    # C x1 y1 x2 y2 x y
    @staticmethod
    def cubic(x1: float = 0, y1: float = 0, x2: float = 0, y2: float = 0, x: float = 0, y: float = 0, *, relative: bool = False) -> str:
        prefix = "Cc"[relative]
        return " ".join(map(value_to_str, [prefix, x1, y1, x2, y2, x, y]))

    @staticmethod
    def C(x1: float = 0, y1: float = 0, x2: float = 0, y2: float = 0, x: float = 0, y: float = 0) -> str:
        return Path.cubic(x1, y1, x2, y2, x, y, relative=False)

    @staticmethod
    def c(x1: float = 0, y1: float = 0, x2: float = 0, y2: float = 0, x: float = 0, y: float = 0) -> str:
        return Path.cubic(x1, y1, x2, y2, x, y, relative=True)

    # S x2 y2, x y
    @staticmethod
    def shorthand(x2: float = 0, y2: float = 0, x: float = 0, y: float = 0, *, relative: bool = False) -> str:
        prefix = "Ss"[relative]
        return " ".join(map(value_to_str, [prefix, x2, y2, x, y]))

    @staticmethod
    def S(x2: float = 0, y2: float = 0, x: float = 0, y: float = 0) -> str:
        return Path.shorthand(x2, y2, x, y, relative=False)

    @staticmethod
    def s(x2: float = 0, y2: float = 0, x: float = 0, y: float = 0) -> str:
        return Path.shorthand(x2, y2, x, y, relative=True)

    # Q x1 y1 x y
    @staticmethod
    def quadratic(x1: float = 0, y1: float = 0, x: float = 0, y: float = 0, *, relative: bool = False) -> str:
        prefix = "Qq"[relative]
        return " ".join(map(value_to_str, [prefix, x1, y1, x, y]))

    @staticmethod
    def Q(x1: float = 0, y1: float = 0, x: float = 0, y: float = 0) -> str:
        return Path.quadratic(x1, y1, x, y, relative=False)

    @staticmethod
    def q(x1: float = 0, y1: float = 0, x: float = 0, y: float = 0) -> str:
        return Path.quadratic(x1, y1, x, y, relative=True)

    # T x y
    @staticmethod
    def q_shorthand(x: float = 0, y: float = 0, *, relative: bool = False) -> str:
        prefix = "Tt"[relative]
        return " ".join(map(value_to_str, [prefix, x, y]))

    @staticmethod
    def T(x: float = 0, y: float = 0) -> str:
        return Path.q_shorthand(x, y, relative=False)

    @staticmethod
    def t(x: float = 0, y: float = 0) -> str:
        return Path.q_shorthand(x, y, relative=True)

    # A rx ry x-axis-rotation large-arc-flag sweep-flag x y
    @staticmethod
    def arc(
        radius_x: float = 0, 
        radius_y: float = 0, 
        x_axis_rotation: float = 0, 
        large_arc_flag: bool | int = 0, 
        sweep_flag: bool | int = 0, 
        x: float = 0, 
        y: float = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Aa"[relative] 
        return " ".join(map(value_to_str, [prefix, radius_x, radius_y, x_axis_rotation, int(large_arc_flag) & 1, int(sweep_flag) & 1, x, y]))

    @staticmethod
    def A(
        radius_x: float = 0, 
        radius_y: float = 0, 
        x_axis_rotation: float = 0, 
        large_arc_flag: bool | int = 0, 
        sweep_flag: bool | int = 0, 
        x: float = 0, 
        y: float = 0, 
    ) -> str:
        return Path.arc(radius_x, radius_y, x_axis_rotation, large_arc_flag, sweep_flag, x, y, relative=False)

    @staticmethod
    def a(
        radius_x: float = 0, 
        radius_y: float = 0, 
        x_axis_rotation: float = 0, 
        large_arc_flag: bool | int = 0, 
        sweep_flag: bool | int = 0, 
        x: float = 0, 
        y: float = 0, 
    ) -> str:
        return Path.arc(radius_x, radius_y, x_axis_rotation, large_arc_flag, sweep_flag, x, y, relative=True)


def compact_path(path: list[str]) -> str:
    result: list[str] = []
    digits = set("0123456789")
    
    for part in path:
        if not result:
            result.append(part)
            continue

        if part.isalpha():
            result.append(part)
            continue

        is_negative = part[0] == "-"

        part = part.lstrip("-").lstrip("0")
        
        if not part:
            is_negative = False
            part = "0"

        if is_negative:
            result.append("-")
            result.append(part)
            continue

        is_dot = part[0] == "."

        if is_dot:
            if "." not in result[-1]:
                result.append(" ")
        elif result[-1][-1] in digits:
            result.append(" ")

        result.append(part)

    return "".join(result)