from typing import Optional, Protocol

from lxml.etree import _Element


class TmxElement(Protocol):
    """
    The base protocol all elements follow.
    """

    def __init__(self, XmlElement: Optional[_Element] = None, **attribs) -> None: ...

    def to_element(self, export_extra: bool) -> _Element: ...

    def to_string(self, export_extra: bool) -> str: ...

    def make_xml_attrib_dict(self) -> dict[str, str]: ...
