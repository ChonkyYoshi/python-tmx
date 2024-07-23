from __future__ import annotations

from typing import Generator, Literal, Optional, Protocol

from lxml.etree import _Element


class BaseElement(Protocol):
    _source_element: Optional[_Element]

    def validate(self) -> None: ...

    def to_element(self) -> _Element: ...


class IterableElement(Protocol):
    def __len__(self) -> int: ...

    def __iter__(self) -> Generator[str | IterableElement, None, None]: ...

    def iter_text(self) -> Generator[str, None, None]: ...

    def iter(
        self,
        mask: Literal[
            "header",
            "map",
            "note",
            "prop",
            "seg",
            "tu",
            "tuv",
            "ude",
            "bpt",
            "ept",
            "hi",
            "it",
            "ph",
            "sub",
            "ut",
        ],
    ) -> Generator[IterableElement | BaseElement, None, None]: ...
