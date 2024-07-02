from datetime import datetime
from logging import getLogger
from re import match
from typing import Any, Literal, Optional, Sequence

from lxml.etree import Element, _Element

from PythonTmx.base import TmxElement
from PythonTmx.helpers import make_xml_string

logger = getLogger()


class Prop(TmxElement):
    __attributes: tuple[str, str, str] = ("type", "lang", "oencoding")
    type: Optional[str]
    lang: Optional[str]
    oencoding: Optional[str]
    content: Optional[Sequence[Any]]
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
                        self.content.append(child)
        else:
            ToAssign = attribs
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))
            else:
                self.extra[Attribute] = ToAssign[Attribute]

    def tmx_attributes(self) -> dict[str, str]:
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

    def to_element(self, export_extra: bool = False) -> _Element:
        hi_elem: _Element = Element(_tag="hi", attrib=self.tmx_attributes())
        if self.extra and export_extra:
            logger.info(
                "updating xml compliant dict with extra attributes. "
                "Compatibility cannot be guaranteed if resulting element is "
                "included in a tmx file.\n"
                "Note: `str(value)` is called on all elements of the dict and "
                "all the resulting values are escaped for xml compliance"
            )
            hi_elem.attrib.update(self.extra)  # type: ignore
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
                            "Sub elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        return hi_elem

    def to_string(self, export_extra: bool = False) -> str:
        final: str = "<hi "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.extra and export_extra:
            logger.info(
                "updating xml compliant dict with extra attributes. "
                "Compatibility cannot be guaranteed if resulting element is "
                "included in a tmx file.\n"
                "Note: `str()` is called on both all keys and all values of "
                "the dict and all the resulting strings are xml escaped"
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
                            "Hi elements content can only consist of Sub objects "
                            f"or string but found '{type(child).__name__}"
                        )
        final += "</hi>"
        return final


class Note(TmxElement):
    lang: Optional[str]
    oencoding: Optional[str]
    text: Optional[str]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        if XmlElement is None:
            self.lang = attribs.get("lang")
            self.oencoding = attribs.get("oencoding")
            self.text = attribs.get("text")
        else:
            if "lang" in attribs.keys():
                self.lang = attribs["lang"]
            else:
                self.lang = XmlElement.get("{http://www.w3.org/XML/1998/namespace}lang")
            if "oencoding" in attribs.keys():
                self.oencoding = attribs["oencoding"]
            else:
                self.oencoding = XmlElement.get("o-encoding")
            if "text" in attribs.keys():
                self.text = attribs["text"]
            else:
                self.text = XmlElement.text

    def tmx_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if isinstance(self.lang, str):
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
        elif self.lang is None:
            pass
        else:
            raise TypeError(
                "Unsupported type for attribute 'lang' "
                "Cannot build xml compliant attribute dict"
            )
        if hasattr(self, "oencoding"):
            if isinstance(self.oencoding, str):
                attrs["o-encoding"] = self.oencoding
            elif self.oencoding is None:
                pass
            else:
                raise TypeError(
                    "Unsupported type for attribute 'oencoding' "
                    "Cannot build xml compliant attribute dict"
                )
        return attrs

    def to_element(self) -> _Element:
        note_elem: _Element = Element(_tag="note", attrib=self.tmx_attributes())
        note_elem.text = self.text if self.text else ""
        return note_elem

    def to_string(self) -> str:
        final: str = "<note "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.text is not None:
            if isinstance(self.text, str):
                final += self.text
            else:
                raise TypeError(
                    "Unsupported type for attribute 'text' cannot export to string"
                )
        else:
            final += " "
        final += "</note>"
        return final


class Map(TmxElement):
    __attributes: tuple[str, ...] = ("unicode", "code", "ent", "subst")
    unicode: Optional[str]
    code: Optional[str]
    ent: Optional[str]
    subst: Optional[str]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))

    def tmx_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val: Optional[str] = getattr(self, key, None)
            match key, val:
                case _, str():
                    attrs[key] = val
                case "unicode", None:
                    raise AttributeError(
                        f"Attribute '{key}' is required and cannot"
                        "have a value of None"
                    )
                case _:
                    raise TypeError(
                        f"Unsupported type for attribute '{key}' "
                        "Cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        return Element(_tag="map", attrib=self.tmx_attributes())

    def to_string(self) -> str:
        final: str = "<map "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        final += "/>"
        return final


class Ude(TmxElement):
    __attributes: tuple[str, ...] = (
        "name",
        "base",
        "maps",
    )
    name: Optional[str]
    base: Optional[str]
    maps: Optional[Sequence[Map]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if len(XmlElement) and "maps" not in ToAssign.keys():
                ToAssign["maps"] = [
                    Map(child) for child in XmlElement.iterchildren("map")
                ]
        for Attribute in ToAssign.keys():
            if Attribute in self.__attributes:
                setattr(self, Attribute, ToAssign.get(Attribute))

    def tmx_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if self.name is None:
            raise AttributeError(
                "Attribute 'name' is required and cannot have a value of None"
            )
        elif not isinstance(self.name, str):
            raise TypeError(
                "Unsupported type for attribute 'name' "
                "Cannot build xml compliant attribute dict"
            )
        else:
            attrs["name"] = self.name
        if self.base is not None:
            if not isinstance(self.base, str):
                raise TypeError(
                    "Unsupported type for attribute 'base' "
                    "Cannot build xml compliant attribute dict"
                )
            if self.maps and len(self.maps):
                if (
                    len(
                        [
                            1
                            for map_ in self.maps
                            if isinstance(map_, Map) and map_.code is not None
                        ]
                    )
                    and not self.base
                ):
                    raise AttributeError(
                        "Value for attribute 'base' cannot be None since "
                        "at least one of its Map element has a 'code' attribute"
                    )
            attrs["base"] = self.base
        return attrs

    def to_element(self) -> _Element:
        element: _Element = Element("ude", self.tmx_attributes())
        if self.maps and len(self.maps):
            for map_ in self.maps:
                if isinstance(map_, Map):
                    element.append(map_.to_element())
                else:
                    raise TypeError
        return element

    def to_string(self) -> str:
        final: str = "<ude "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.maps and len(self.maps):
            final += ">"
            for map_ in self.maps:
                final += map_.to_string()
            final += "</ude>"
        else:
            final += "/>"
        return final


class Header(TmxElement):
    __attributes: tuple[str, ...] = (
        "creationtool",
        "creationtoolversion",
        "segtype",
        "otmf",
        "adminlang",
        "srclang",
        "datatype",
        "oencoding",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
    )
    creationtool: Optional[str]
    creationtoolversion: Optional[str]
    segtype: Optional[Literal["paragraph", "block", "sentence", "phrase"]]
    otmf: Optional[str]
    adminlang: Optional[str]
    srclang: Optional[str]
    datatype: Optional[str]
    oencoding: Optional[str]
    creationdate: Optional[str] | datetime
    creationid: Optional[str]
    changedate: Optional[str] | datetime
    changeid: Optional[str]
    udes: Optional[Sequence[Ude]]
    props: Optional[Sequence[Prop]]
    notes: Optional[Sequence[Note]]

    def __init__(self, XmlElement: _Element | None = None, **attribs) -> None:
        if XmlElement is not None:
            ToAssign: dict = dict(XmlElement.attrib.items()) | attribs
            if len(XmlElement):
                if "udes" not in ToAssign.keys():
                    self.udes = [Ude(child) for child in XmlElement.iterchildren("ude")]
                if "props" not in ToAssign.keys():
                    self.props = [
                        Prop(child) for child in XmlElement.iterchildren("prop")
                    ]
                if "notes" not in ToAssign.keys():
                    self.notes = [
                        Note(child) for child in XmlElement.iterchildren("note")
                    ]
        for Attribute in ToAssign.keys():
            if Attribute.replace("-", "") in self.__attributes:
                setattr(self, Attribute.replace("-", ""), ToAssign.get(Attribute))

        if isinstance(self.creationdate, str):
            try:
                self.creationdate = datetime.strptime(
                    self.creationdate, r"%Y%m%dT%H%M%SZ"
                )
            except (ValueError, TypeError):
                pass
        if isinstance(self.changedate, str):
            try:
                self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
            except (ValueError, TypeError):
                pass

    def tmx_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val: Optional[str | datetime] = getattr(self, key, None)
            match key, val:
                case (
                    "creationtool"
                    | "creationtoolversion"
                    | "adminlang"
                    | "srclang"
                    | "datatype"
                    | "creationid"
                    | "changeid",
                    str(),
                ):
                    attrs[key] = val
                case "creationdate" | "changedate", str():
                    if not match(r"^\d{8}T\d{6}Z$", val):
                        raise ValueError(
                            f"Value for '{key}' is not of the correct format"
                        )
                    attrs[key] = val
                case "creationdate" | "changedate", datetime():
                    attrs[key] = val.strftime(r"%Y%m%dT%H%M%SZ")
                case "segtype", str():
                    if val not in ("paragraph", "block", "sentence", "phrase"):
                        raise ValueError(
                            "segtype must be one of 'block', 'paragraph', "
                            f"'sentence' or 'phrase' not '{val}'"
                        )
                    attrs[key] = val
                case "otmf" | "oencoding", str():
                    attrs["o-" + key[1:]] = val
                case (
                    "creationtool"
                    | "creationtoolversion"
                    | "segtype"
                    | "otmf"
                    | "adminlang"
                    | "srclang"
                    | "datatype",
                    None,
                ):
                    raise AttributeError(
                        f"Attribute '{key}' is required and cannot "
                        "have a value of None"
                    )
                case _:
                    raise TypeError(
                        f"Unsupported type for attribute '{key}' "
                        "Cannot build xml compliant attribute dict"
                    )
        return attrs

    def to_element(self) -> _Element:
        element = Element("header", self.tmx_attributes())
        if self.udes and len(self.udes):
            element.extend([ude.to_element() for ude in self.udes])
        if self.notes and len(self.notes):
            element.extend([note.to_element() for note in self.notes])
        if self.props and len(self.props):
            element.extend([prop.to_element() for prop in self.props])
        return element

    def to_string(self) -> str:
        final: str = "<header "
        for key, val in self.tmx_attributes().items():
            final += f'{make_xml_string(key)}="{make_xml_string(val)}" '
        if self.udes and len(self.udes):
            final += ">"
            for ude in self.udes:
                final += ude.to_string()
            final += "</header>"
        else:
            final += "/>"
        return final
