from __future__ import annotations

import typing

import lxml.etree as et


class TmxElement(typing.Protocol):
    source_element: typing.Optional[et._Element]
    _content: typing.Optional[list[str | TmxElement]]
    _required_attributes: tuple[str, ...]
    _optional_attributes: tuple[str, ...]

    def __init__(
        self, lxml_element: typing.Optional[et._Element] = None, **kwargs
    ) -> None: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> typing.Generator[str | TmxElement, None, None]: ...

    def validate_attributes(self) -> dict[str, str]: ...

    def to_element(self) -> et._Element: ...

    def iter_text(self) -> typing.Generator[str, None, None]: ...

    def iter(
        self,
        mask: typing.Literal[
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
    ) -> typing.Generator[TmxElement, None, None]: ...
