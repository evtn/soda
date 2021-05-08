from typing import List, Any
from .tags import Number


class Curve:
    def __init__(self, letter: str, *data: Any):
        self.letter = letter
        self.data = data

    def render(self, is_relative: bool = False) -> str:
        return " ".join([
            self.get_letter(self.letter, is_relative),
            " ".join(map(str, self.data))
        ])

    @staticmethod
    def get_letter(letter: str, is_relative: bool = False) -> str:
        if is_relative:
            return letter.lower()
        return letter.upper()


class Arc():
    pass


class Start:
    letter = "M"

class Line:
    letter = "L"

    def render(self, is_relative: bool = False) -> str:
        if not self.data[1]: # horizontal line:
            return Curve("H", self.data[0]).render(is_relative)
        if not self.data[0]: # vertical line:
            return Curve("V", self.data[1]).render(is_relative)
        return super().render(is_relative)