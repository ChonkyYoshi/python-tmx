from datetime import datetime
from re import match
from typing import Any, Callable, Literal, Optional
from xml.etree.ElementTree import Element

from PythonTmx.protocols import TmxElement, _XmlElement


class Map(TmxElement):
    unicode: str
    code: str
    ent: str
    subst: str

    def __init__(
        self,
        XmlElement: Optional[_XmlElement] = None,
        strict: bool = True,
        **attribs,
    ) -> None:
        def _parse_attributes(attrib: dict[str, Any], strict) -> None:
            for key, val in attrib.items():
                match key, val:
                    case "unicode" | "code" | "ent" | "subst", str():
                        setattr(self, key, val)
                    case "unicode" | "code" | "ent" | "subst", _:
                        if strict:
                            raise TypeError(
                                f"attribute '{key}' does not supports values "
                                f"of type '{type(val).__name__}'"
                            )
                        setattr(self, key, val)
                    case _:
                        raise AttributeError(f"Unknown attribute found: '{key}'")

        if XmlElement is not None:
            if attribs:
                attrs: dict = XmlElement.attrib | attribs
                _parse_attributes(attrs, strict)
            else:
                _parse_attributes(XmlElement.attrib, strict)
        else:
            _parse_attributes(attribs, strict)


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
        **attribs,
    ) -> None:
        if XmlElement is not None:
            attrs: dict = XmlElement.attrib | attribs
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
            val: str | datetime | None = getattr(self, key, None)
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


a = fromstring("""<header
  creationtool="XYZTool"
  creationtoolversion="1.01-023"
  datatype="PlainText"
  segtype="sentence"
  adminlang="en-us"
  srclang="EN"
  o-tmf="ABCTransMem"
  creationdate="20020101T163812Z"
  creationid="ThomasJ"
  changedate="20020413T023401Z"
  changeid="Amity"
  o-encoding="iso-8859-1"
 />""")

b = Header(XmlElement=a)
