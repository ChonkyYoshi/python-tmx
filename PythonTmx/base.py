from enum import StrEnum, auto
from typing import Iterable, Iterator, Protocol, Self


class _XmlElement(Protocol):
    tag: str
    attrib: dict[str, str]
    text: str | None
    tail: str | None
    _children: Iterable[Self]

    def get(self, item: str) -> str | None:
        raise NotImplementedError

    def iter(self) -> Iterator[Self]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Self]:
        pass


class Segtype(StrEnum):
    block = auto()
    paragraph = auto()
    sentence = auto()
    phrase = auto()
