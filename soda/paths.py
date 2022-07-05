class Path:
    @staticmethod
    def build(*commands: str, compact=False) -> str:
        if compact:
            return compact_path(" ".join(commands).split(" "))
        return " ".join(commands)

    # M x y
    @staticmethod
    def moveto(
        x: int = 0, 
        y: int = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Mm"[relative]
        return " ".join(map(str, [prefix, x, y]))

    # L x y
    @staticmethod
    def line(
        x: int = 0, 
        y: int = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Ll"[relative]
        return " ".join(map(str, [prefix, x, y]))

    # V y
    @staticmethod
    def vertical(
        y: int = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Vv"[relative]
        return " ".join(map(str, [prefix, y]))

    # H x
    @staticmethod
    def horizontal(
        x: int = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Hh"[relative]
        return " ".join(map(str, [prefix, x]))

    # Z
    @staticmethod
    def close(*, relative: bool = False) -> str:
        # there's no difference between two, but consistent API is better
        return "Zz"[relative]

    # C x1 y1 x2 y2 x y
    @staticmethod
    def cubic(x1: int = 0, y1: int = 0, x2: int = 0, y2: int = 0, x: int = 0, y: int = 0, *, relative: bool = False):
        prefix = "Cc"[relative]
        return " ".join(map(str, [prefix, x1, y1, x2, y2, x, y]))

    # S x2 y2, x y
    @staticmethod
    def shorthand(x2: int = 0, y2: int = 0, x: int = 0, y: int = 0, *, relative: bool = False):
        prefix = "Ss"[relative]
        return " ".join(map(str, [prefix, x2, y2, x, y]))

    # Q x1 y1 x y
    @staticmethod
    def quadratic(x1: int = 0, y1: int = 0, x: int = 0, y: int = 0, *, relative: bool = False):
        prefix = "Qq"[relative]
        return " ".join(map(str, [prefix, x1, y1, x, y]))

    # T x y
    @staticmethod
    def q_shorthand(x: int = 0, y: int = 0, *, relative: bool = False):
        prefix = "Tt"[relative]
        return " ".join(map(str, [prefix, x, y]))

    # A rx ry x-axis-rotation large-arc-flag sweep-flag x y
    @staticmethod
    def arc(
        radius_x: int = 0, 
        radius_y: int = 0, 
        x_axis_rotation: int = 0, 
        large_arc_flag: int = 0, 
        sweep_flag: int = 0, 
        x: int = 0, 
        y: int = 0, 
        *, relative: bool = False
    ) -> str:
        prefix = "Aa"[relative]
        return " ".join(map(str, [prefix, radius_x, radius_y, x_axis_rotation, large_arc_flag, sweep_flag, x, y]))


def compact_path(path):
    result = []
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


def make_aliases(func):
    new_annotations = func.__annotations__.copy()
    new_annotations.pop("relative")
    abs_func = lambda *args, **kwargs: func(*args, **{**kwargs, "relative": False})
    rel_func = lambda *args, **kwargs: func(*args, **{**kwargs, "relative": True})
    abs_func.__annotations__ = new_annotations
    rel_func.__annotations__ = new_annotations
    return abs_func, rel_func


Path.M, Path.m = make_aliases(Path.moveto)
Path.L, Path.l = make_aliases(Path.line)
Path.H, Path.h = make_aliases(Path.horizontal)
Path.V, Path.v = make_aliases(Path.vertical)
Path.Z, Path.z = make_aliases(Path.close)
Path.C, Path.c = make_aliases(Path.cubic)
Path.S, Path.s = make_aliases(Path.shorthand)
Path.Q, Path.q = make_aliases(Path.quadratic)
Path.T, Path.t = make_aliases(Path.q_shorthand)
Path.A, Path.a = make_aliases(Path.arc)