from datetime import datetime
from re import match
from typing import Callable, Literal, Optional, Sequence

from lxml.etree import Element, _Element

from PythonTmx.base_class import TmxElement
from PythonTmx.helpers import escape_for_xml


class Map(TmxElement):
    unicode: Optional[str]
    code: Optional[str]
    ent: Optional[str]
    subst: Optional[str]

    def __init__(
        self,
        XmlElement: Optional[_Element] = None,
        **attribs,
    ) -> None:
        if XmlElement is not None:
            attrs: dict = {key: val for key, val in XmlElement.attrib.items()} | attribs
        else:
            attrs = attribs
        self.unicode = attrs.get("unicode")
        self.code = attrs.get("code")
        self.ent = attrs.get("ent")
        self.subst = attrs.get("subst")

    @property
    def attrib(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in ("unicode", "code", "ent", "subst"):
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
                    raise TypeError(f"Unsupported type for attribute '{key}'")
        return attrs

    def to_element(self) -> _Element:
        return Element(_tag="map", attrib=self.attrib)

    def to_string(self) -> str:
        attrs: dict = self.attrib
        final: str = "<map "
        for key, val in attrs.items():
            final += f'{escape_for_xml(key)}="{escape_for_xml(val)}" '
        final += "/>"
        return final


class Ude(TmxElement):
    name: Optional[str]
    base: Optional[str]
    maps: Optional[Sequence[Map]]

    def __init__(
        self,
        XmlElement: Optional[_Element] = None,
        **attribs,
    ) -> None:
        if XmlElement is not None:
            attrs: dict = {key: val for key, val in XmlElement.attrib.items()} | attribs
        else:
            attrs = attribs
        self.name = attrs.get("name")
        self.base = attrs.get("base")
        if attrs.get("maps", None) is not None:
            self.maps = attrs.get("maps")
        elif XmlElement is not None and len(XmlElement):
            self.maps = [Map(child) for child in XmlElement if child.tag == "map"]
        else:
            self.maps = []

    @property
    def attrib(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        if self.name is None:
            raise AttributeError(
                "Attribute 'name' is required and cannot have a value of None"
            )
        elif not isinstance(self.name, str):
            raise TypeError(
                f"type {type(self.name).__name__} is not supported for "
                "attribute 'name'"
            )
        else:
            attrs["name"] = self.name
        if self.base is not None:
            if not isinstance(self.base, str):
                raise TypeError(
                    f"type {type(self.base).__name__} is not supported for "
                    "attribute 'name'"
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

    def to_element(
        self, factory: Callable[[str, dict], _Element] = Element
    ) -> _Element:
        element: _Element = factory("ude", self.attrib)
        if self.maps and len(self.maps):
            for map_ in self.maps:
                if isinstance(map_, Map):
                    element.append(map_.to_element())
                else:
                    raise TypeError
        return element

    def to_string(self) -> str:
        attrs: dict = self.attrib
        final: str = "<ude "
        for key, val in attrs.items():
            final += f'{escape_for_xml(key)}="{escape_for_xml(val)}" '
        if self.maps and len(self.maps):
            final += ">"
            for map_ in self.maps:
                final += map_.to_string()
            final += "</ude>"
        else:
            final += "/>"
        return final


class Header(TmxElement):
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

    def __init__(
        self,
        XmlElement: Optional[_Element] = None,
        **attribs,
    ) -> None:
        if XmlElement is not None:
            attrs: dict = {key: val for key, val in XmlElement.attrib.items()} | attribs
        else:
            attrs = attribs
        self.creationtool = attrs.get("creationtool")
        self.creationtoolversion = attrs.get("creationtoolversion")
        self.segtype = attrs.get("segtype")
        self.otmf = attrs.get("o-tmf")
        self.adminlang = attrs.get("adminlang")
        self.srclang = attrs.get("srclang")
        self.datatype = attrs.get("datatype")
        self.oencoding = attrs.get("o-encoding")
        self.creationdate = attrs.get("creationdate")
        self.creationid = attrs.get("creationid")
        self.changedate = attrs.get("changedate")
        self.changeid = attrs.get("changeid")

        if attrs.get("udes", None) is not None:
            self.udes = attrs.get("udes")
        elif XmlElement is not None and len(XmlElement):
            self.udes = [Ude(child) for child in XmlElement if child.tag == "ude"]
        else:
            self.udes = ()
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

    @property
    def attrib(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in (
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
        ):
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
                        f"type '{type(val).__name__}' is not "
                        f"supported type for attribute '{key}'"
                    )
        return attrs

    def to_element(self) -> _Element:
        element = Element("header", self.attrib)
        if self.udes and len(self.udes):
            element.extend([ude.to_element() for ude in self.udes])
        return element

    def to_string(self) -> str:
        attrs: dict = self.attrib
        final: str = "<header "
        for key, val in attrs.items():
            final += f'{escape_for_xml(key)}="{escape_for_xml(val)}" '
        if self.udes and len(self.udes):
            final += ">"
            for ude in self.udes:
                final += ude.to_string()
            final += "</header>"
        else:
            final += "/>"
        return final
