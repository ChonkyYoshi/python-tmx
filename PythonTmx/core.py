from typing import MutableSequence, Optional, Protocol

from lxml.etree import _Element


class TmxElement(Protocol):
    """
    The base protocol all elements follow.
    """

    __attributes: tuple[str, ...]
    unknown_attributes: Optional[dict]
    content: Optional[MutableSequence]

    def __init__(
        self,
        lxml_element: Optional[_Element] = None,
        strict: bool = False,
        **attribs,
    ) -> None:
        def set_attributes(attributes: dict, strict: bool) -> None: ...
        def parse_element(lxml_element: _Element, strict: bool) -> None: ...

    def to_element(self, export_unknown_attributes: bool = False) -> _Element: ...

    def to_string(self, export_unknown_attributes: bool = False) -> str: ...

    def serialize_attributes(self, strict: bool) -> dict[str, str]: ...
