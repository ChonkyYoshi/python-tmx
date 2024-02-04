from enum import Enum


class Pos(Enum):
    BEGIN = "begin"
    END = "end"


class Assoc(Enum):
    P = "p"
    F = "f"
    B = "b"


class text_run:
    __slots__ = ["text"]

    def __init__(self, text: str) -> None:
        self.text = text


class bpt:
    __slots__ = ["text", "i", "x", "_type"]

    def __init__(
        self,
        text: str,
        i: int,
        x: int | None = None,
        _type: str | None = None,
    ) -> None:
        self.text = text
        self.i = i
        self.x = x
        self._type = _type


class ept:
    __slots__ = ["text", "i"]

    def __init__(self, text: str, i: int) -> None:
        self.text = text
        self.i = i


class hi:
    __slots__ = ["text", "x"]

    def __init__(self, text: str, x: int) -> None:
        self.text = text
        self.x = x


class ph:
    __slots__ = ["text", "x", "_type", "assoc"]

    def __init__(
        self,
        text: str,
        x: int | None = None,
        _type: str | None = None,
        assoc: Assoc | None = None,
    ) -> None:
        self.text = text
        self.x = x
        self._type = _type
        self.assoc = assoc


class it:

    __slots__ = ["text", "pos", "x", "_type"]

    def __init__(
        self,
        text: str,
        pos: Pos,
        x: int | None = None,
        _type: str | None = None,
    ) -> None:
        self.text = text
        self.pos = pos
        self.x = x
        self._type = _type
