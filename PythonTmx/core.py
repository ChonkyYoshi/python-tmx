from typing import Optional, Protocol

from lxml.etree import _Element


class TmxElement(Protocol):
    """
    The base protocol all elements follow.
    """

    def __init__(
        self,
        XmlElement: Optional[_Element] = None,
        keep_unknown_attributes: bool = False,
        keep_unknown_children: bool = False,
        **attribs,
    ) -> None: ...

    def to_element(self, keep_unknown_attributes: bool = False) -> _Element: ...

    def to_string(self, keep_unknown_attributes: bool = False) -> str: ...

    @property
    def tmx_attributes(self) -> dict[str, str]: ...
