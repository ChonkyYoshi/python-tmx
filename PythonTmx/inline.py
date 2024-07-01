from typing import Literal, MutableSequence, Optional

from lxml.etree import Element, _Element

from PythonTmx.base import TmxElement
from PythonTmx.helpers import make_xml_string


class Sub(TmxElement):
    __attributes: tuple[str, str] = ("type", "datatype")
    type: Optional[int | str]
    datatype: Optional[str]
    content: Optional[MutableSequence[str | "Bpt" | "Ept" | "It" | "Ph" | "Hi"]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
                ToAssign.pop("content")
            else:
                self.content = []
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "bpt":
                                self.content.append(Bpt(XmlElement=child))
                            case "ept":
                                self.content.append(Ept(XmlElement=child))
                            case "it":
                                self.content.append(It(XmlElement=child))
                            case "hi":
                                self.content.append(Hi(XmlElement=child))
                            case "ph":
                                self.content.append(Ph(XmlElement=child))
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in self.__attributes:
            if Attribute in ToAssign.keys():
                setattr(self, Attribute, ToAssign.get(Attribute))

    def make_xml_attrib_dict(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if self.type and isinstance(self.type, str):
            attrs["type"] = self.type
        else:
            raise TypeError(
                "Unsupported type for attribute 'type' "
                "cannot build xml compliant attribute dict"
            )
        if self.datatype and isinstance(self.datatype, str):
            attrs["datatype"] = str(self.datatype)
        else:
            raise TypeError(
                "Unsupported type for attribute 'datatype' "
                "cannot build xml compliant attribute dict"
            )
        return attrs

    def to_element(self) -> _Element:
        sub_elem: _Element = Element(_tag="sub", attrib=self.make_xml_attrib_dict())
        if self.content:
            for child in self.content:
                match child:
                    case str() if not sub_elem.text:
                        sub_elem.text = child
                    case str() if sub_elem.text and not len(sub_elem):
                        sub_elem.text += child
                    case str() if not sub_elem[-1].tail:
                        sub_elem[-1].tail = child
                    case str() if sub_elem[-1].tail:
                        sub_elem[-1].tail += child
                    case Bpt() | Ept() | It() | Ph() | Hi():
                        sub_elem.append(child.to_element())
                    case _:
                        raise TypeError(
                            "Sub elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return sub_elem

    def to_string(self) -> str:
        final: str = "<sub "
        for key, val in self.make_xml_attrib_dict().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.content:
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Bpt() | Ept() | It() | Ph() | Hi():
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "Sub elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        final += "</sub>"
        return final


class It(TmxElement):
    __attributes: tuple[str, str, str] = ("x", "type", "pos")
    x: Optional[int | str]
    type: Optional[str]
    pos: Optional[Literal["begin", "end"]]
    content: Optional[MutableSequence[str | Sub]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
                ToAssign.pop("content")
            else:
                self.content = []
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "sub":
                                self.content.append(Sub(XmlElement=child))
                            case _:
                                raise ValueError
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in self.__attributes:
            if Attribute in ToAssign.keys():
                setattr(self, Attribute, ToAssign.get(Attribute))
        if self.x:
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass

    def make_xml_attrib_dict(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val: Optional[str | int] = getattr(self, key, None)
            match key, val:
                case "pos", str():
                    if val not in ("being" "end"):
                        raise ValueError(
                            f"'pos' must be one of 'begin' or 'end' not '{val}'"
                        )
                    attrs["pos"] = val
                case "pos", None:
                    raise AttributeError(
                        "Attribute 'pos' is required and cannot have a value of None"
                    )
                case "x", str():
                    try:
                        attrs["x"] = str(int(val))
                    except ValueError:
                        raise ValueError(
                            "Value for attribute 'x' cannot be converted to a "
                            f"number. Found value: {val}"
                        )
                case "x", int():
                    attrs["x"] = str(val)
                case "type", str():
                    attrs["type"] = val
                case _:
                    raise TypeError(
                        f"Unsupported type for attribute '{key}' "
                        "cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        ph_elem: _Element = Element(_tag="it", attrib=self.make_xml_attrib_dict())
        if self.content:
            for child in self.content:
                match child:
                    case str() if not ph_elem.text:
                        ph_elem.text = child
                    case str() if ph_elem.text and not len(ph_elem):
                        ph_elem.text += child
                    case str() if not ph_elem[-1].tail:
                        ph_elem[-1].tail = child
                    case str() if ph_elem[-1].tail:
                        ph_elem[-1].tail += child
                    case Sub():
                        ph_elem.append(child.to_element())
                    case _:
                        raise TypeError(
                            "It elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return ph_elem

    def to_string(self) -> str:
        final: str = "<it "
        for key, val in self.make_xml_attrib_dict().items():
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
                            "It elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        final += "</it>"
        return final


class Ph(TmxElement):
    __attributes: tuple[str, str, str] = ("x", "type", "assoc")
    x: Optional[int | str]
    type: Optional[str]
    assoc: Optional[Literal["p", "f", "b"]]
    content: Optional[MutableSequence[str | Sub]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
                ToAssign.pop("content")
            else:
                self.content = []
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "sub":
                                self.content.append(Sub(XmlElement=child))
                            case _:
                                raise ValueError
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in self.__attributes:
            if Attribute in ToAssign.keys():
                setattr(self, Attribute, ToAssign.get(Attribute))
        if self.x:
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass

    def make_xml_attrib_dict(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val: Optional[str | int] = getattr(self, key, None)
            match key, val:
                case "assoc", str():
                    if val not in ("p", "f", "b"):
                        raise ValueError(
                            f"'assoc' must be one of 'p', 'f' or 'b' not '{val}'"
                        )
                    attrs["assoc"] = val
                case "x", int():
                    attrs["x"] = str(val)
                case "x", str():
                    try:
                        attrs["x"] = str(int(val))
                    except ValueError:
                        raise ValueError(
                            "Value for attribute 'x' cannot be converted to a "
                            f"number. Found value: {val}"
                        )
                case "type", str():
                    attrs["type"] = val
                case _:
                    raise TypeError(
                        f"Unsupported type for attribute '{key}' "
                        "cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        ph_elem: _Element = Element(_tag="ph", attrib=self.make_xml_attrib_dict())
        if self.content:
            for child in self.content:
                match child:
                    case str() if not ph_elem.text:
                        ph_elem.text = child
                    case str() if ph_elem.text and not len(ph_elem):
                        ph_elem.text += child
                    case str() if not ph_elem[-1].tail:
                        ph_elem[-1].tail = child
                    case str() if ph_elem[-1].tail:
                        ph_elem[-1].tail += child
                    case Sub():
                        ph_elem.append(child.to_element())
                    case _:
                        raise TypeError(
                            "Ph elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return ph_elem

    def to_string(self) -> str:
        final: str = "<ph "
        for key, val in self.make_xml_attrib_dict().items():
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
                            "Ph elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        final += "</ph>"
        return final


class Bpt(TmxElement):
    __attributes: tuple[str, str, str] = ("i", "x", "type")
    i: Optional[int | str]
    x: Optional[int | str]
    type: Optional[str]
    content: Optional[MutableSequence[str | Sub]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
                ToAssign.pop("content")
            else:
                self.content = []
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "sub":
                                self.content.append(Sub(XmlElement=child))
                            case _:
                                raise ValueError
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in self.__attributes:
            if Attribute in ToAssign.keys():
                setattr(self, Attribute, ToAssign.get(Attribute))
        if self.x:
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass
        if self.i:
            try:
                self.i = int(self.i)
            except (ValueError, TypeError):
                pass

    def make_xml_attrib_dict(self) -> dict[str, str]:
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
                case "i" | "x", str():
                    try:
                        attrs[key] = str(int(val))
                    except ValueError:
                        raise ValueError(
                            f"Value for attribute '{key}' cannot be converted to a "
                            f"number. Found value: {val}"
                        )
                case "i" | "x", int():
                    attrs[key] = str(val)
                case _:
                    raise TypeError(
                        f"Unsupported type for attribute '{key}' "
                        "cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        bpt_elem: _Element = Element(_tag="bpt", attrib=self.make_xml_attrib_dict())
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
        for key, val in self.make_xml_attrib_dict().items():
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
    content: Optional[MutableSequence[str | Sub]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
                ToAssign.pop("content")
            else:
                self.content = []
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "sub":
                                self.content.append(Sub(XmlElement=child))
                            case _:
                                raise ValueError
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in self.__attributes:
            if Attribute in ToAssign.keys():
                setattr(self, Attribute, ToAssign.get(Attribute))
        if self.i:
            try:
                self.i = int(self.i)
            except (ValueError, TypeError):
                pass

    def make_xml_attrib_dict(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val: Optional[str | int] = getattr(self, key, None)
            match key, val:
                case "i", None:
                    raise AttributeError(
                        "Attribute 'i' is required and cannot" "have a value of None"
                    )
                case "i", int():
                    try:
                        attrs["i"] = str(int(val))
                    except ValueError:
                        raise ValueError(
                            "Value for attribute 'i' cannot be converted to a "
                            f"number. Found value: {val}"
                        )
                case "i", str():
                    attrs[key] = val
                case _:
                    raise TypeError(
                        f"Unsupported type for attribute '{key}' "
                        "cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        ept_elem: _Element = Element(_tag="ept", attrib=self.make_xml_attrib_dict())
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
                            "Bpt elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return ept_elem

    def to_string(self) -> str:
        final: str = "<bpt "
        for key, val in self.make_xml_attrib_dict().items():
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


class Hi(TmxElement):
    __attributes: tuple[str, str] = ("x", "type")
    x: Optional[int | str]
    type: Optional[str]
    content: Optional[MutableSequence[str | Bpt | Ept | It | Ph | "Hi"]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
                ToAssign.pop("content")
            else:
                self.content = []
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "bpt":
                                self.content.append(Bpt(XmlElement=child))
                            case "ept":
                                self.content.append(Ept(XmlElement=child))
                            case "it":
                                self.content.append(It(XmlElement=child))
                            case "hi":
                                self.content.append(Hi(XmlElement=child))
                            case "ph":
                                self.content.append(Ph(XmlElement=child))
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in self.__attributes:
            if Attribute in ToAssign.keys():
                setattr(self, Attribute, ToAssign.get(Attribute))
        if self.x:
            try:
                self.i = int(self.x)
            except (ValueError, TypeError):
                pass

    def make_xml_attrib_dict(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if self.type and isinstance(self.type, str):
            attrs["type"] = self.type
        else:
            raise TypeError(
                "Unsupported type for attribute 'type' "
                "cannot build xml compliant attribute dict"
            )
        if self.x and isinstance(self.x, (str, int)):
            attrs["x"] = str(self.x)
        else:
            raise TypeError(
                "Unsupported type for attribute 'x' "
                "cannot build xml compliant attribute dict"
            )
        return attrs

    def to_element(self) -> _Element:
        sub_elem: _Element = Element(_tag="hi", attrib=self.make_xml_attrib_dict())
        if self.content:
            for child in self.content:
                match child:
                    case str() if not sub_elem.text:
                        sub_elem.text = child
                    case str() if sub_elem.text and not len(sub_elem):
                        sub_elem.text += child
                    case str() if not sub_elem[-1].tail:
                        sub_elem[-1].tail = child
                    case str() if sub_elem[-1].tail:
                        sub_elem[-1].tail += child
                    case Bpt() | Ept() | It() | Ph() | Hi():
                        sub_elem.append(child.to_element())
                    case _:
                        raise TypeError(
                            "Sub elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return sub_elem

    def to_string(self) -> str:
        final: str = "<hi "
        for key, val in self.make_xml_attrib_dict().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.content:
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Bpt() | Ept() | It() | Ph() | Hi():
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "Hi elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        final += "</hi>"
        return final
