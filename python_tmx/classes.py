from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from re import MULTILINE, match
from typing import Any, Iterable, Literal
from xml.etree.ElementTree import Element, parse, tostring


class IncorrectTagError(Exception):
    def __init__(self, found_tag: str, expected_tag: str) -> None:
        super().__init__(f"Expected <{expected_tag} but found <{found_tag}>")


class TmxTag(ABC):
    @abstractmethod
    def export(self) -> Element: ...


class Header(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        o_tmf: str | None = None,
        adminlang: str | None = None,
        srclang: str | None = None,
        datatype: str | None = None,
        o_encoding: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        changeid: str | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
        udes: Iterable[Ude] | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "header":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="header"
                    )
                if xml_element.text is not None and not match(
                    r"^[\n\s]+$", xml_element.text, flags=MULTILINE
                ):
                    raise ValueError(
                        f"<header> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case (
                            "creationtool"
                            | "creationtoolversion"
                            | "segtype"
                            | "adminlang"
                            | "srclang"
                            | "datatype"
                            | "creationid"
                            | "changeid"
                        ):
                            self.__setattr__(attr, xml_element.get(attr))
                        case "creationdate" | "changedate":
                            self.__setattr__(
                                attr,
                                datetime.strptime(
                                    xml_element.get(attr.replace("_", "-")),
                                    r"%Y%m%dT%H%M%SZ",
                                ),
                            )
                        case "o_tmf" | "o_encoding":
                            self.__setattr__(
                                attr, xml_element.get(attr.replace("_", "-"))
                            )
                        case "props" | "notes" | "udes" if len(xml_element) == 0:
                            continue
                        case "props":
                            self.props = [
                                Prop(prop) for prop in xml_element if prop.tag == "prop"
                            ]
                        case "notes":
                            self.notes = [
                                Note(note) for note in xml_element if note.tag == "note"
                            ]
                        case "udes":
                            self.udes = [
                                Ude(ude) for ude in xml_element if ude.tag == "ude"
                            ]
            case None:
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    self.__setattr__(attr, val)
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("header")
        for attr, val in vars(self).items():
            if val is None:
                continue
            if attr[1] == "_":
                element.set(attr.replace("_", "-"), val)
                continue
            if isinstance(val, datetime):
                element.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                continue
            if isinstance(val, str):
                element.set(attr, val)
                continue
            if isinstance(val, Iterable):
                element.extend([elem.export() for elem in val])
                continue
        return element


class Prop(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Any | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "prop":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="prop"
                    )
                for attr, val in locals().items():
                    if attr in ["self", "xml_element"]:
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case "content":
                            self.content = xml_element.text
                        case "type_":
                            self.type_ = xml_element.get("type")
                        case "lang":
                            self.lang = xml_element.get(
                                "{http://www.w3.org/XML/1998/namespace}lang"
                            )
                        case "o_encoding":
                            self.o_encoding = xml_element.get("o-encoding")
            case None:
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    self.__setattr__(attr, val)
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("prop")
        for attr, val in vars(self).items():
            if val is None:
                continue
            match attr:
                case "content":
                    element.text = val
                case "type_":
                    element.set("type", val)
                case "lang":
                    element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                case "o_encoding":
                    element.set("o-encoding", val)
        return element


class Note(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Any | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "note":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="note"
                    )
                for attr, val in locals().items():
                    if attr in ["self", "xml_element"]:
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case "content":
                            self.content = xml_element.text
                        case "lang":
                            self.lang = xml_element.get(
                                "{http://www.w3.org/XML/1998/namespace}lang"
                            )
                        case "o_encoding":
                            self.o_encoding = xml_element.get("o-encoding")
            case None:
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    self.__setattr__(attr, val)
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("note")
        for attr, val in vars(self).items():
            if val is None:
                continue
            match attr:
                case "content":
                    element.text = val
                case "lang":
                    element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                case "o_encoding":
                    element.set("o-encoding", val)
        return element


class Ude(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        maps: Iterable[map] | None = None,
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "ude":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="ude"
                    )
                for attr, val in locals().items():
                    if attr in ["self", "xml_element"]:
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case "name":
                            self.name = xml_element.get("name")
                        case "base":
                            self.base = xml_element.get("base")
                        case "maps":
                            if len(xml_element) == 0:
                                self.maps = None
                                continue
                            self.maps = [
                                Map(map_) for map_ in xml_element if map_.tag == "map"
                            ]
            case None:
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    self.__setattr__(attr, val)
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("ude")
        for attr, val in vars(self).items():
            if val is None:
                continue
            match attr:
                case "name" | "base":
                    element.set(attr, val)
                case "maps":
                    element.extend([elem.export() for elem in self.maps])
        return element


class Map(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "map":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="map"
                    )
                for attr, val in locals().items():
                    if attr in ["self", "xml_element"]:
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    else:
                        self.__setattr__(attr, xml_element.get(attr))
            case None:
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    self.__setattr__(attr, val)
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("map")
        for attr, val in vars(self).items():
            if val is None:
                continue
            element.set(attr, val)
        return element


a = Header(parse("a.tmx").getroot())
print(tostring(a.export()))
