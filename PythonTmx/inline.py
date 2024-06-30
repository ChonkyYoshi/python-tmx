from typing import Optional, Sequence

from lxml.etree import Element, _Element

from PythonTmx.base import TmxElement
from PythonTmx.helpers import make_xml_string


class Sub(TmxElement): ...


class Bpt(TmxElement):
    __attributes: tuple[str, ...] = ("i", "x", "type")
    i: Optional[int | str]
    x: Optional[int | str]
    type: Optional[str]
    text: Optional[str | Sequence[str | Sub]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        if XmlElement is None:
            self.i = attribs.get("i")
            self.x = attribs.get("x")
            self.type = attribs.get("type")
            self.text = attribs.get("text")
        else:
            if "type" in attribs.keys():
                self.type = attribs["type"]
            else:
                self.type = XmlElement.get("type")
            if "i" in attribs.keys():
                self.i = attribs["i"]
            else:
                self.x = XmlElement.get("x")
            if "text" in attribs.keys():
                self.text = attribs["text"]
            else:
                self.text = XmlElement.text
        if self.i:
            try:
                self.i = int(self.i)
            except (ValueError, TypeError):
                pass
        if self.x:
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass

    def xml_attrib(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val: Optional[str | int] = getattr(self, key, None)
            match key, val:
                case "i", None:
                    raise AttributeError(
                        "Attribute 'i' is required and cannot" "have a value of None"
                    )
                case "type", str():
                    attrs[key] = val
                case "i" | "x", str() | int():
                    attrs[key] = str(val)
                case _:
                    raise TypeError(
                        f"Unsupported type for attribute '{key}' "
                        "Cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        bpt_elem: _Element = Element(_tag="bpt", attrib=self.xml_attrib())
        if isinstance(self.text, str):
            bpt_elem.text = self.text
        return bpt_elem

    def to_string(self) -> str:
        final: str = "<bpt "
        for key, val in self.xml_attrib().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if isinstance(self.text, str):
            final += self.text
        final += "</bpt>"
        return final
