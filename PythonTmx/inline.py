from __future__ import annotations

from logging import LoggerAdapter, getLogger
from typing import Any, Literal, MutableSequence, Optional

from lxml.etree import Element, _Element

from PythonTmx.base import TmxElement
from PythonTmx.helpers import make_xml_string

_logger = getLogger("PythonTmx")


class Sub(TmxElement):
    __attributes: tuple[str, str] = ("type", "datatype")
    type: Optional[int | str]
    datatype: Optional[str]
    content: Optional[MutableSequence[str | Bpt | Ept | It | Ph | Hi]]
    extra: Optional[dict]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        super().__init__()
        self.content, self.extra = [], {}
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
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
                            case _:
                                self.__logger.debug(
                                    f"Ignoring unknown element {child.tag} encountered when building Sub object."
                                )
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))
            else:
                self.extra[Attribute] = ToAssign[Attribute]
        if len(self.extra):
            self.__logger.debug(f"Stored {len(self.extra)} extra attributes")
        if self.extra:
            self.__logger.debug(f"Keeping {len(self.extra)} extra attributes")

    def tmx_attributes(self) -> dict[str, str]:
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

    def to_element(self, export_extra: bool = False) -> _Element:
        sub_elem: _Element = Element(_tag="sub", attrib=self.tmx_attributes())
        if self.extra and export_extra:
            self.__logger.info(
                "Tmx compliance is not guaranteed when exporting extra attributes."
            )
            sub_elem.attrib.update(self.extra.items())  # type: ignore
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

    def to_string(self, export_extra: bool = False) -> str:
        final: str = "<sub "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.extra and export_extra:
            self.__logger.info(
                "Tmx compliance is not guaranteed when exporting extra attributes."
            )
            for key, val in self.extra.items():
                final += f'{make_xml_string(str(key))}="{make_xml_string(str(val))}" '
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
    extra: Optional[dict]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content, self.extra = [], {}
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
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
                                self.__logger.debug(
                                    f"Ignoring unknown element {child.tag} encountered when building It object."
                                )
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))
            else:
                self.extra[Attribute] = ToAssign[Attribute]
        if len(self.extra):
            self.__logger.debug(f"Stored {len(self.extra)} extra attributes")
        if self.x:
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass

    def tmx_attributes(self) -> dict[str, str]:
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

    def to_element(self, export_extra: bool = False) -> _Element:
        ph_elem: _Element = Element(_tag="it", attrib=self.tmx_attributes())
        if self.extra and export_extra:
            self.__logger.info(
                "Tmx compliance is not guaranteed when exporting extra attributes."
            )
            ph_elem.attrib.update(self.extra)  # type: ignore
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

    def to_string(self, export_extra: bool = False) -> str:
        final: str = "<it "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.extra and export_extra:
            self.__logger.info(
                "Tmx compliance is not guaranteed when exporting extra attributes."
            )
            for key, val in self.extra.items():
                final += f'{make_xml_string(str(key))}="{make_xml_string(str(val))}" '
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
    extra: Optional[dict]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        self.content, self.extra = [], {}
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
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
                                self.__logger.debug(
                                    f"Ignoring unknown element {child.tag} encountered when building It object."
                                )
                        if child.tail:
                            self.content.append(child.tail)
        else:
            ToAssign = attribs
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))
            else:
                self.extra[Attribute] = ToAssign[Attribute]
        if len(self.extra):
            self.__logger.debug(f"Keeping {len(self.extra)} extra attributes")
        if self.x:
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass

    def tmx_attributes(self) -> dict[str, str]:
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

    def to_element(self, export_extra: bool = False) -> _Element:
        ph_elem: _Element = Element(_tag="ph", attrib=self.tmx_attributes())
        if self.extra and export_extra:
            self.__logger.info(
                "Tmx compliance is not guaranteed when exporting extra attributes."
            )
            ph_elem.attrib.update(self.extra)  # type: ignore
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

    def to_string(self, export_extra: bool = False) -> str:
        final: str = "<ph "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.extra and export_extra:
            self.__logger.info(
                "Tmx compliance is not guaranteed when exporting extra attributes."
            )
            for key, val in self.extra.items():
                final += f'{make_xml_string(str(key))}="{make_xml_string(str(val))}" '
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
    unknown_attributes: dict
    unknown_elements: MutableSequence[_Element]
    __logger = LoggerAdapter(_logger, {"ClassName": "Hi"})

    def __init__(
        self,
        XmlElement: Optional[_Element] = None,
        keep_unknown_attributes: bool = False,
        keep_unknown_children: bool = False,
        **attribs,
    ) -> None:
        self.unknown_attributes = {}
        self.unknown_elements = []
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content = ToAssign.get("content")
            else:
                self.content = []
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "sub":
                                self.content.append(Sub(XmlElement=child))
                            case _ if keep_unknown_children:
                                self.__logger.debug(
                                    "Storing unknown element encountered while"
                                    "building Hi element from an Xml element.\n"
                                    f"Name of the Element: {child.tag}"
                                )
                                self.unknown_elements.append(child)
                        if child.tail:
                            self.content.append(child.tail)
                if len(self.unknown_elements):
                    self.__logger.debug(
                        f"{len(self.unknown_elements)} unkown elements stored"
                    )
        else:
            ToAssign = attribs
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))
            elif keep_unknown_attributes:
                self.unknown_attributes[Attribute] = ToAssign[Attribute]
        if len(self.unknown_attributes):
            self.__logger.debug(
                f"Stored {len(self.unknown_attributes)} extra attributes"
            )
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

    @property
    def tmx_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if self.i:
            if isinstance(self.i, int):
                attrs["i"] = str(self.i)
            elif isinstance(self.i, str):
                try:
                    attrs["i"] = str(int(self.i))
                except ValueError:
                    raise ValueError(
                        "Value for attribute 'x' cannot be converted to a number."
                        f" Found value: {self.i}"
                    )
            else:
                raise TypeError(
                    "Unsupported type for attribute 'i' "
                    "cannot build xml compliant attribute dict"
                )
        return attrs

    def to_element(self, keep_unknown_attributes: bool = False) -> _Element:
        bpt_elem: _Element = Element(_tag="bpt", attrib=self.tmx_attributes)
        if keep_unknown_attributes:
            if len(self.unknown_attributes):
                self.__logger.debug(
                    f"Adding {len(self.unknown_attributes)} to the element"
                )
                bpt_elem.attrib.update(self.unknown_attributes)
            else:
                self.__logger.debug("Object has no unknown attributes to export")
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
                            "content can only consist of Sub objects or string"
                            f"not '{type(child).__name__}"
                        )
        return bpt_elem

    def to_string(self, keep_unknown_attributes: bool = False) -> str:
        final: str = "<bpt"
        for key, val in self.tmx_attributes.items():
            final += f' {make_xml_string(key)}="{make_xml_string(val)}"'
        if keep_unknown_attributes:
            if len(self.unknown_attributes):
                self.__logger.debug(
                    f"Adding {len(self.unknown_attributes)} to the element"
                )
                for key, val in self.unknown_attributes.items():
                    final += (
                        f' {make_xml_string(str(key))}="{make_xml_string(str(val))}"'
                    )
            else:
                self.__logger.debug("Object has no unknown attributes to export")
        final += ">"
        if self.content:
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Sub():
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "content can only consist of Sub objects or string"
                            f"not '{type(child).__name__}"
                        )
        final += "</bpt>"
        return final


class Ept(TmxElement):
    __attributes: tuple[str] = ("i",)
    i: Optional[int | str]
    content: Optional[MutableSequence[str | Sub]]
    unknown_attributes: dict
    unknown_elements: MutableSequence[_Element]
    __logger = LoggerAdapter(_logger, {"ClassName": "Hi"})

    def __init__(
        self,
        XmlElement: Optional[_Element] = None,
        keep_unknown_attributes: bool = False,
        keep_unknown_children: bool = False,
        **attribs,
    ) -> None:
        self.unknown_attributes = {}
        self.unknown_elements = []
        self.content = []
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in ToAssign.keys():
                self.content.append(ToAssign.get("content"))
            else:
                if len(XmlElement):
                    if XmlElement.text:
                        self.content.append(XmlElement.text)
                    for child in XmlElement:
                        match child.tag:
                            case "sub":
                                self.content.append(Sub(XmlElement=child))
                            case _ if keep_unknown_children:
                                self.__logger.debug(
                                    "Storing unknown element encountered while"
                                    "building Hi element from an Xml element.\n"
                                    f"Name of the Element: {child.tag}"
                                )
                                self.unknown_elements.append(child)
                        if child.tail:
                            self.content.append(child.tail)
                if len(self.unknown_elements):
                    self.__logger.debug(
                        f"{len(self.unknown_elements)} unkown elements stored"
                    )
        else:
            ToAssign = attribs
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))
            elif keep_unknown_attributes:
                self.unknown_attributes[Attribute] = ToAssign[Attribute]
        if len(self.unknown_attributes):
            self.__logger.debug(
                f"Stored {len(self.unknown_attributes)} extra attributes"
            )
        if self.i:
            try:
                self.i = int(self.i)
            except (ValueError, TypeError):
                pass

    @property
    def tmx_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if self.i:
            if isinstance(self.i, int):
                attrs["i"] = str(self.i)
            elif isinstance(self.i, str):
                try:
                    attrs["i"] = str(int(self.i))
                except ValueError:
                    raise ValueError(
                        "Value for attribute 'x' cannot be converted to a number."
                        f" Found value: {self.i}"
                    )
            else:
                raise TypeError(
                    "Unsupported type for attribute 'i' "
                    "cannot build xml compliant attribute dict"
                )
        return attrs

    def to_element(self, keep_unknown_attributes: bool = False) -> _Element:
        ept_elem: _Element = Element(_tag="ept", attrib=self.tmx_attributes)
        if keep_unknown_attributes:
            if len(self.unknown_attributes):
                self.__logger.debug(
                    f"Adding {len(self.unknown_attributes)} to the element"
                )
                ept_elem.attrib.update(self.unknown_attributes)
            else:
                self.__logger.debug("Object has no unknown attributes to export")
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
                            "content can only consist of Sub objects or string"
                            f"not '{type(child).__name__}"
                        )
        return ept_elem

    def to_string(self, keep_unknown_attributes: bool = False) -> str:
        final: str = "<ept"
        for key, val in self.tmx_attributes.items():
            final += f' {make_xml_string(key)}="{make_xml_string(val)}"'
        if keep_unknown_attributes:
            if len(self.unknown_attributes):
                self.__logger.debug(
                    f"Adding {len(self.unknown_attributes)} to the element"
                )
                for key, val in self.unknown_attributes.items():
                    final += (
                        f' {make_xml_string(str(key))}="{make_xml_string(str(val))}"'
                    )
            else:
                self.__logger.debug("Object has no unknown attributes to export")
        final += ">"
        if self.content:
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Sub():
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "content can only consist of Sub objects or string"
                            f"not '{type(child).__name__}"
                        )
        final += "</ept>"
        return final


class Hi(TmxElement):
    __attributes: tuple[str, str] = ("x", "type")
    x: Optional[int | str]
    type: Optional[str]
    content: Optional[MutableSequence[str | Bpt | Ept | It | Ph | Hi]]
    unknown_attributes: dict
    unknown_elements: MutableSequence[_Element]
    __logger = LoggerAdapter(_logger, {"ClassName": "Hi"})

    def __setattr__(self, name: str, value: Any) -> None:
        self.__logger.debug(f"setting self.{name} to {value}")
        return super().__setattr__(name, value)

    def __getattr__(self, name: str, value: Any) -> None:
        self.__logger.debug(f"accessing self.{name}")
        return super().__setattr__(name, value)

    def __init__(
        self,
        XmlElement: Optional[_Element] = None,
        keep_unknown_attributes: bool = False,
        keep_unknown_children: bool = False,
        **attribs,
    ) -> None:
        self.__logger.debug(
            "initializing Hi Object, with "
            f"'keep_unknown_attributes = {keep_unknown_attributes}'"
            f"  and 'keep_unknown_children = {keep_unknown_children}'"
        )
        self.unknown_attributes = {}
        self.unknown_elements = []
        self.content = []
        if XmlElement is not None:
            self.__logger.debug("XmlElement provided")
            _attributes: dict = dict(XmlElement.attrib.items()) | attribs
            if "content" in _attributes.keys():
                self.__logger(
                    "content argument provided, overriding value from XmlElement"
                )
                self.content = _attributes.get("content")
            else:
                if XmlElement.text:
                    self.__logger.debug("XmlElement has text, adding to self.content")
                    self.content += [XmlElement.text]
                if len(XmlElement):
                    self.__logger.debug("Parsing XmlElement children")
                    for child in XmlElement:
                        match child.tag:
                            case "bpt":
                                self.__logger.debug(
                                    "found a bpt tag, creating a Bpt object from it"
                                )
                                self.content += [Bpt(XmlElement=child)]
                            case "ept":
                                self.__logger.debug(
                                    "found a ept tag, creating a Ept object from it"
                                )
                                self.content += [Ept(XmlElement=child)]
                            case "it":
                                self.__logger.debug(
                                    "found a it tag, creating a It object from it"
                                )
                                self.content += [It(XmlElement=child)]
                            case "hi":
                                self.__logger.debug(
                                    "found a hi tag, creating a Hi object from it"
                                )
                                self.content += [Hi(XmlElement=child)]
                            case "ph":
                                self.__logger.debug(
                                    "found a ph tag, creating a Ph object from it"
                                )
                                self.content += [Ph(XmlElement=child)]
                            case _:
                                self.__logger.debug(
                                    f"found an unknown tag '{child.tag}'"
                                )
                                if keep_unknown_children:
                                    self.__logger.debug(
                                        "storing the unknown element in self.unknown_children"
                                    )
                                    self.unknown_elements += [child]
                        if child.tail:
                            self.__logger.debug(
                                "Child element has a tail, adding to self.content"
                            )
                            self.content += [child.tail]
                if len(self.unknown_elements):
                    self.__logger.debug(
                        f"{len(self.unknown_elements)} unkown elements stored"
                    )
        else:
            _attributes = attribs
        for _attribute in _attributes.keys():
            if _attribute in self.__attributes:
                setattr(self, _attribute, _attributes.get(_attribute))
            elif keep_unknown_attributes:
                self.__logger.debug(
                    f"unknown attribute '{_attribute}' found, keeping in self.unknown_attributes"
                )
                self.unknown_attributes[_attribute] = _attributes[_attribute]
            else:
                self.__logger.debug(
                    f"unknown attribute '{_attribute}' found, discarding"
                )
        if len(self.unknown_attributes):
            self.__logger.debug(
                f"{len(self.unknown_attributes)} unkown attributes stored"
            )
        if self.x:
            if not isinstance(self.x, int):
                try:
                    self.__logger.debug("trying to convert self.x to an int")
                    self.x = int(self.x)
                    self.__logger.debug("self.x succesfully converted to an int")
                except ValueError:
                    self.__logger.debug(
                        f"the string '{self.x}' cannot be converted to an int"
                    )
                except TypeError:
                    self.__logger.debug(
                        f"cannot convert a {type(self.x).__name__} to an int"
                    )
        self.__logger.debug("Hi object initialized")

    @property
    def tmx_attributes(self) -> dict[str, str]:
        self.__logger.debug("calling tmx_attributes")
        _tmx_attrs: dict[str, str] = {}
        for key in self.__attributes:
            val = getattr(self, key, None)
            if val is not None:
                match key, val:
                    case "x", int():
                        self.__logger.debug("converting self.x back to a str")
                        _tmx_attrs["x"] = str(val)
                    case "x", str():
                        try:
                            self.__logger.debug("confirming self.x is an int")
                            _tmx_attrs["x"] = str(int(val))
                        except ValueError:
                            raise ValueError(
                                f"Attribute 'x' must be convertible to an int. "
                                f"Cannot convert {val} to an int"
                            )
                    case "x", _:
                        raise TypeError(
                            "Unsupported type for attribute 'x'. Expected a string "
                            f"or an int, but got {type(key).__name__}"
                        )
                    case "type", str():
                        _tmx_attrs["type"] = val
                    case "type", _:
                        raise TypeError(
                            "Unsupported type for attribute 'type'. "
                            f"Expected a string but got {type(key).__name__}"
                        )
                    case _:
                        raise AssertionError(
                            "Reached unreachable code. Most probably because self.__attributes has been modified."
                        )
            else:
                self.__logger.debug(f"attribute {key} has a value of None, skipping")
        self.__logger.debug("tmx_attributes dict created, returning")
        return _tmx_attrs

    def to_element(self, keep_unknown_attributes: bool = False) -> _Element:
        hi_elem: _Element = Element(_tag="hi", attrib=self.tmx_attributes)
        if keep_unknown_attributes:
            if len(self.unknown_attributes):
                self.__logger.debug(
                    f"Adding {len(self.unknown_attributes)} to the element"
                )
                hi_elem.attrib.update(self.unknown_attributes)
            else:
                self.__logger.debug("Object has no unknown attributes to export")
        if self.content:
            for child in self.content:
                match child:
                    case str() if not hi_elem.text:
                        hi_elem.text = child
                    case str() if hi_elem.text and not len(hi_elem):
                        hi_elem.text += child
                    case str() if not hi_elem[-1].tail:
                        hi_elem[-1].tail = child
                    case str() if hi_elem[-1].tail:
                        hi_elem[-1].tail += child
                    case Bpt() | Ept() | It() | Ph() | Hi():
                        hi_elem.append(child.to_element())
                    case _:
                        raise TypeError(
                            "content can only consist of Sub objects or string"
                            f"not '{type(child).__name__}"
                        )
        return hi_elem

    def to_string(self, keep_unknown_attributes: bool = False) -> str:
        self.__logger.debug(
            f"calling to_string with keep_unknown_attributes = {keep_unknown_attributes}"
        )
        final: str = "<hi"
        self.__logger.debug("converting tmx attributes to xml strings")
        final += "".join(
            [
                f' {make_xml_string(str(key))}="{make_xml_string(str(val))}"'
                for key, val in self.tmx_attributes.items()
            ]
        )
        if keep_unknown_attributes:
            if len(self.unknown_attributes):
                self.__logger.debug("converting unknown attributes to xml strings")
                final += "".join(
                    (
                        f' {make_xml_string(str(key))}="{make_xml_string(str(val))}"'
                        for key, val in self.unknown_attributes.items()
                    )
                )
            else:
                self.__logger.debug("Object has no unknown attributes to export")
        final += ">"
        if self.content:
            self.__logger.debug("converting all items in self.content to strings")
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Bpt() | Ept() | It() | Ph() | Hi():
                        self.__logger.debug(
                            f"encountered a {type(child).__name__} object. Converting to string"
                        )
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "content can only consist of Bpt, Ept, It, Ph, Hi "
                            f"objects or strings not '{type(child).__name__}"
                        )
        final += "</hi>"
        self.__logger.debug("Element converted to a string, returning")
        return final
