from typing import Iterable, Optional

from lxml.etree import Element, _Element

from PythonTmx.base import TmxElement
from PythonTmx.helpers import make_xml_string


class Sub(TmxElement): ...


class Bpt(TmxElement):
    __attributes: tuple[str, str, str] = ("i", "x", "type")
    i: Optional[int | str]
    x: Optional[int | str]
    type: Optional[str]
    content: Optional[Iterable[str | Sub]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        if XmlElement is None:
            self.i = attribs.get("i")
            self.x = attribs.get("x")
            self.type = attribs.get("type")
            self.content = attribs.get("text")
        else:
            if "type" in attribs.keys():
                self.type = attribs["type"]
            else:
                self.type = XmlElement.get("type")
            if "i" in attribs.keys():
                self.i = attribs["i"]
            else:
                self.i = XmlElement.get("i")
            if "x" in attribs.keys():
                self.x = attribs["x"]
            else:
                self.x = XmlElement.get("x")
            if "content" in attribs.keys():
                self.content = attribs["content"]
            else:
                self.content = []
                if XmlElement.text:
                    self.content.append(XmlElement.text)
                for child in XmlElement:
                    if child.tag == "sub":
                        self.content.append(Sub(XmlElement=child))
                    if child.tail:
                        self.content.append(child.tail)
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
                        "cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        bpt_elem: _Element = Element(_tag="bpt", attrib=self.xml_attrib())
        if self.content:
            for child in self.content:
                match child:
                    case str() if not bpt_elem.text:
                        bpt_elem.text = child
                    case str() if bpt_elem.text and not len(bpt_elem):
                        bpt_elem.text += child
                    case str() if not bpt_elem[-1].tail:
                        bpt_elem[-1].tail = child
                    case str() if bpt_elem[-1].tail:
                        bpt_elem[-1].tail += child
                    case Sub():
                        bpt_elem.append(child.to_element())
                    case _:
                        raise TypeError(
                            "Bpt elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return bpt_elem

    def to_string(self) -> str:
        final: str = "<bpt "
        for key, val in self.xml_attrib().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.content:
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Sub():
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "Bpt elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        final += "</bpt>"
        return final


class Ept(TmxElement):
    __attributes: tuple[str] = ("i",)
    i: Optional[int | str]
    content: Optional[Iterable[str | Sub]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        if XmlElement is None:
            self.i = attribs.get("i")
            self.content = attribs.get("text")
        else:
            if "i" in attribs.keys():
                self.i = attribs["i"]
            else:
                self.i = XmlElement.get("i")
            if "content" in attribs.keys():
                self.content = attribs["content"]
            else:
                self.content = []
                if XmlElement.text:
                    self.content.append(XmlElement.text)
                for child in XmlElement:
                    if child.tag == "sub":
                        self.content.append(Sub(XmlElement=child))
                    if child.tail:
                        self.content.append(child.tail)
        if self.i:
            try:
                self.i = int(self.i)
            except (ValueError, TypeError):
                pass

    def xml_attrib(self) -> dict[str, str]:
        if not self.i:
            raise AttributeError("Attribute 'i' is required and cannot be None")
        elif not isinstance(self.i, (str, int)):
            raise TypeError(
                "Unsupported type for attribute 'i' "
                "cannot build xml compliant attribute dict"
            )
        else:
            return {"i": str(self.i)}

    def to_element(self) -> _Element:
        ept_elem: _Element = Element(_tag="ept", attrib=self.xml_attrib())
        if self.content:
            for child in self.content:
                match child:
                    case str() if not ept_elem.text:
                        ept_elem.text = child
                    case str() if ept_elem.text and not len(ept_elem):
                        ept_elem.text += child
                    case str() if not ept_elem[-1].tail:
                        ept_elem[-1].tail = child
                    case str() if ept_elem[-1].tail:
                        ept_elem[-1].tail += child
                    case Sub():
                        ept_elem.append(child.to_element())
                    case _:
                        raise TypeError(
                            "Ept elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return ept_elem

    def to_string(self) -> str:
        final: str = "<ept "
        for key, val in self.xml_attrib().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.content:
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Sub():
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "Ept elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        final += "</ept>"
        return final
