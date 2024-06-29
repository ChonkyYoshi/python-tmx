from datetime import datetime
from re import match
from typing import Any, Callable, Iterable, Literal, Optional

from lxml.etree import Element

from PythonTmx.protocols import TmxElement, _XmlElement


class Map(TmxElement):
    unicode: Optional[str]
    code: Optional[str]
    ent: Optional[str]
    subst: Optional[str]

    def __init__(
        self,
        XmlElement: Optional[_XmlElement] = None,
        **attribs: dict[str, Any],
    ) -> None:
        if XmlElement is not None:
            attrs: dict[str, Any] = XmlElement.attrib | attribs  # type: ignore
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

    def to_element(self, factory: Callable = Element) -> _XmlElement:
        return factory("map", self.attrib)

    def to_string(self) -> str:
        attrs: dict = self.attrib
        final: str = "<map "
        for key, val in attrs.items():
            final += f'{key}="{val}" '
        final += "/>"
        return final


class Ude(TmxElement):
    name: Optional[str]
    base: Optional[str]
    maps: Optional[Iterable[Map]]

    def __init__(
        self,
        XmlElement: Optional[_XmlElement] = None,
        **attribs: dict[str, Any],
    ) -> None:
        if XmlElement is not None:
            attrs: dict[str, Any] = XmlElement.attrib | attribs  # type: ignore
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
            raise AttributeError(f"Attribute '{key}' is required and cannot"
                        "have a value of None")
        elif not isinstance(self.name, str):
            

        return attrs

    def to_element(self, factory: Callable = Element) -> _XmlElement:
        return factory("map", self.attrib)

    def to_string(self) -> str:
        attrs: dict = self.attrib
        final: str = "<map "
        for key, val in attrs.items():
            final += f'{key}="{val}" '
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

    def __init__(
        self,
        XmlElement: Optional[_XmlElement] = None,
        **attribs: dict[str, Any],
    ) -> None:
        if XmlElement is not None:
            attrs: dict[str, Any] = XmlElement.attrib | attribs  # type: ignore
        else:
            attrs = attribs
        self.creationtool = attrs.get("creationtoool")
        self.creationtoolversion = attrs.get("creationtoolversion")
        self.segtype = attrs.get("segtype")
        self.otmf = attrs.get("o-tmf")
        self.adminlang = attrs.get("creationtoool")
        self.srclang = attrs.get("creationtoool")
        self.datatype = attrs.get("creationtoool")
        self.oencoding = attrs.get("creationtoool")
        self.creationdate = attrs.get("creationtoool")
        self.creationid = attrs.get("creationtoool")
        self.changedate = attrs.get("creationtoool")
        self.changeid = attrs.get("creationtoool")

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
                        f"Attribute '{key}' is required and cannot"
                        "have a value of None"
                    )
                case _:
                    raise TypeError(f"Unsupported type for attribute '{key}'")
        return attrs

    def to_element(self, factory: Callable = Element) -> _XmlElement:
        return factory("header", self.attrib)

    def to_string(self) -> str:
        attrs: dict = self.attrib
        final: str = "<header "
        for key, val in attrs.items():
            final += f'{key}="{val}" '
        final += "/>"
        return final
