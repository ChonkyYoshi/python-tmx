from typing import Optional

from lxml.etree import _Element


class TmxElement:
    def __init__(self, XmlElement: Optional[_Element] = None, **attribs) -> None:
        raise NotImplementedError

    def to_element(self) -> _Element:
        raise NotImplementedError

    def to_string(self) -> str:
        raise NotImplementedError

    def make_xml_attrib_dict(self) -> dict[str, str]:
        raise NotImplementedError
