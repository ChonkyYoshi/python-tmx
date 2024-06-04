from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from re import MULTILINE, match
from typing import Any, Iterable, Literal
from xml.etree.ElementTree import Element

__all__ = [
    "Tmx",
    "Header",
    "Note",
    "Prop",
    "Ude",
    "Map",
    "Tu",
    "Tuv",
    "Seg",
    "Hi",
    "It",
    "Ph",
    "Bpt",
    "Ept",
    "Ut",
    "Sub",
]


class IncorrectTagError(Exception):
    def __init__(self, found_tag: str, expected_tag: str) -> None:
        super().__init__(f"Expected {expected_tag} but found {found_tag}")


class TmxTag(ABC):
    @abstractmethod
    def export(self) -> Element: ...


class Header(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
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
                            try:
                                self.__setattr__(
                                    attr,
                                    datetime.strptime(
                                        xml_element.get(attr.replace("_", "-")),
                                        r"%Y%m%dT%H%M%SZ",
                                    ),
                                )
                            except TypeError:
                                self.__setattr__(attr, None)
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
        content: str | None = None,
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
        xml_element: Element = Element("map")
        for attr, val in vars(self).items():
            if val is None:
                continue
            xml_element.set(attr, val)
        return xml_element


class Ut(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        x: int | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "ut":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="ut"
                    )
                self.x = (
                    x
                    if x is not None
                    else (
                        int(xml_element.attrib["x"])
                        if xml_element.attrib["x"] is not None
                        else None
                    )
                )
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        if child.tag != "sub":
                            raise IncorrectTagError(
                                expected_tag="sub", found_tag=child.tag
                            )
                        self.content.append(Sub(child))
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("ut")
        xml_element.text, xml_element.tail = "", ""
        if self.x is not None:
            xml_element.set("x", str(self.x))
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Sub():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class Sub(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[Bpt] | str | None = None,
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "sub":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="ut"
                    )
                self.datatype = (
                    datatype if datatype is not None else xml_element.get("datatype")
                )
                self.type_ = type_ if type_ is not None else xml_element.get("type")
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        if child.tag != "sub":
                            raise IncorrectTagError(
                                expected_tag="sub", found_tag=child.tag
                            )
                        self.content.append(Sub(child))
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("sub")
        xml_element.text, xml_element.tail = "", ""
        if self.datatype is not None:
            xml_element.set("datatype", self.datatype)
        if self.type_ is not None:
            xml_element.set("type", self.type_)
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Sub():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class Bpt(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "bpt":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="bpt"
                    )
                if i is not None:
                    self.i = i
                else:
                    try:
                        self.i = int(xml_element.get("i"))
                    except TypeError:
                        self.i = None
                self.type_ = type_ if type_ is not None else xml_element.get("type")
                if x is not None:
                    self.x = x
                else:
                    try:
                        self.x = int(xml_element.get("x"))
                    except TypeError:
                        self.x = None
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        if child.tag != "sub":
                            raise IncorrectTagError(
                                expected_tag="sub", found_tag=child.tag
                            )
                        self.content.append(Sub(child))
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("bpt")
        xml_element.text, xml_element.tail = "", ""
        if self.i is not None:
            xml_element.set("i", str(self.i))
        if self.x is not None:
            xml_element.set("x", str(self.x))
        if self.type_ is not None:
            xml_element.set("type", self.type_)
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Sub():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class Ept(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "ept":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="ept"
                    )
                if i is not None:
                    self.i = i
                else:
                    try:
                        self.i = int(xml_element.get("i"))
                    except TypeError:
                        self.i = None
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        if child.tag != "sub":
                            raise IncorrectTagError(
                                expected_tag="sub", found_tag=child.tag
                            )
                        self.content.append(Sub(child))
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("ept")
        xml_element.text, xml_element.tail = "", ""
        if self.i is not None:
            xml_element.set("i", str(self.i))
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Sub():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class It(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        pos: Literal["begin" | "end"] | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "it":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="it"
                    )
                self.pos = pos if pos is not None else xml_element.get("pos")
                if x is not None:
                    self.x = x
                else:
                    try:
                        self.x = int(xml_element.get("x"))
                    except TypeError:
                        self.x = None
                self.type_ = type_ if type_ is not None else xml_element.get("type")
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        if child.tag != "sub":
                            raise IncorrectTagError(
                                expected_tag="sub", found_tag=child.tag
                            )
                        self.content.append(Sub(child))
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("it")
        xml_element.text, xml_element.tail = "", ""
        if self.x is not None:
            xml_element.set("x", str(self.x))
        if self.type_ is not None:
            xml_element.set("type", self.type_)
        if self.pos is not None:
            xml_element.set("pos", self.pos)
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Sub():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class Ph(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "ph":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="ph"
                    )
                if x is not None:
                    self.x = x
                else:
                    try:
                        self.x = int(xml_element.get("x"))
                    except TypeError:
                        self.x = None
                self.type_ = type_ if type_ is not None else xml_element.get("type")
                self.assoc = assoc if assoc is not None else xml_element.get("assoc")
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        if child.tag != "sub":
                            raise IncorrectTagError(
                                expected_tag="sub", found_tag=child.tag
                            )
                        self.content.append(Sub(child))
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("ph")
        xml_element.text, xml_element.tail = "", ""
        if self.x is not None:
            xml_element.set("x", str(self.x))
        if self.assoc is not None:
            xml_element.set("assoc", self.assoc)
        if self.type_ is not None:
            xml_element.set("type", self.type_)
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Sub():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class Seg(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "seg":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="seg"
                    )
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        match child.tag:
                            case "ph":
                                self.content.append(Ph(xml_element=child))
                            case "bpt":
                                self.content.append(Bpt(xml_element=child))
                            case "ept":
                                self.content.append(Ept(xml_element=child))
                            case "it":
                                self.content.append(It(xml_element=child))
                            case "hi":
                                self.content.append(Hi(xml_element=child))
                            case _:
                                raise IncorrectTagError(
                                    found_tag=child.tag,
                                    expected_tag="one of ph, bpt, ept, hi, it",
                                )
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("seg")
        xml_element.text, xml_element.tail = "", ""
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Bpt() | Ept() | Hi() | It() | Ph():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class Hi(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "hi":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="hi"
                    )
                if x is not None:
                    self.x = x
                else:
                    try:
                        self.x = int(xml_element.get("x"))
                    except TypeError:
                        self.x = None
                self.type_ = type_ if type_ is not None else xml_element.get("type")
                if content is not None:
                    self.content = content
                elif len(xml_element) == 0:
                    self.content = xml_element.text
                else:
                    self.content = []
                    if xml_element.text is not None:
                        self.content.append(xml_element.text)
                    for child in xml_element:
                        match child.tag:
                            case "ph":
                                self.content.append(Ph(xml_element=child))
                            case "bpt":
                                self.content.append(Bpt(xml_element=child))
                            case "ept":
                                self.content.append(Ept(xml_element=child))
                            case "it":
                                self.content.append(It(xml_element=child))
                            case "hi":
                                self.content.append(Hi(xml_element=child))
                            case _:
                                raise IncorrectTagError(
                                    found_tag=child.tag,
                                    expected_tag="one of ph, bpt, ept, hi, it",
                                )
                        if child.tail is not None:
                            self.content.append(child.tail)
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
        xml_element: Element = Element("hi")
        xml_element.text, xml_element.tail = "", ""
        if self.x is not None:
            xml_element.set("x", str(self.x))
        if self.type_ is not None:
            xml_element.set("type", self.type_)
        if isinstance(self.content, str):
            xml_element.text = self.content
            return xml_element
        for part in self.content:
            match part:
                case str() if len(xml_element) == 0:
                    xml_element.text += part
                case str():
                    xml_element[-1].tail += part
                case Bpt() | Ept() | Hi() | It() | Ph():
                    xml_element.append(part.export())
                case _:
                    raise TypeError
        return xml_element


class Tuv(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
        segment: Seg | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: datetime | str | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        changeid: str | None = None,
        o_tmf: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "tuv":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="tuv"
                    )
                if xml_element.text is not None and not match(
                    r"^[\n\s]+$", xml_element.text, flags=MULTILINE
                ):
                    raise ValueError(
                        f"<tuv> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case "segment":
                            self.segment = Seg(xml_element=xml_element.find("seg"))
                        case "lang":
                            self.lang = xml_element.get(
                                "{http://www.w3.org/XML/1998/namespace}lang"
                            )
                        case (
                            "datatype"
                            | "creationtool"
                            | "creationtoolversion"
                            | "creationid"
                            | "changeid"
                        ):
                            self.__setattr__(attr, xml_element.get(attr))
                        case "creationdate" | "changedate" | "lastusagedate":
                            try:
                                self.__setattr__(
                                    attr,
                                    datetime.strptime(
                                        xml_element.get(attr.replace("_", "-")),
                                        r"%Y%m%dT%H%M%SZ",
                                    ),
                                )
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "o_tmf" | "o_encoding":
                            self.__setattr__(
                                attr, xml_element.get(attr.replace("_", "-"))
                            )
                        case "usagecount":
                            try:
                                self.__setattr__(attr, int(xml_element.get(attr)))
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "props":
                            self.props = [
                                Prop(prop) for prop in xml_element if prop.tag == "prop"
                            ]
                        case "notes":
                            self.notes = [
                                Note(note) for note in xml_element if note.tag == "note"
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
        element: Element = Element("tuv")
        for attr, val in vars(self).items():
            if val is None:
                continue
            if attr[1] == "_":
                element.set(attr.replace("_", "-"), val)
                continue
            if isinstance(val, datetime):
                element.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                continue
            if attr == "lang":
                element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                continue
            if isinstance(val, int):
                element.set(attr, str(val))
                continue
            if isinstance(val, str):
                element.set(attr, val)
                continue
            if isinstance(val, Seg):
                element.append(val.export())
                continue
            if isinstance(val, Iterable):
                element.extend([elem.export() for elem in val])
                continue
        return element


class Tu(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
        tuvs: Iterable[Tuv] | None = None,
        tuid: int | None = None,
        o_encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: datetime | str | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        segtype: Literal["block", "paragraph" | "sentence" | "phrase"] | None = None,
        changeid: str | None = None,
        o_tmf: str | None = None,
        srclang: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "tu":
                    raise IncorrectTagError(
                        found_tag=xml_element.tag, expected_tag="tu"
                    )
                if xml_element.text is not None and not match(
                    r"^[\n\s]+$", xml_element.text, flags=MULTILINE
                ):
                    raise ValueError(
                        f"<tuv> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case "tuvs":
                            self.tuvs = [
                                Tuv(xml_element=child)
                                for child in xml_element
                                if child.tag == "tuv"
                            ]
                        case (
                            "datatype"
                            | "creationtool"
                            | "creationtoolversion"
                            | "creationid"
                            | "segtype"
                            | "changeid"
                            | "srclang"
                        ):
                            self.__setattr__(attr, xml_element.get(attr))
                        case "creationdate" | "changedate" | "lastusagedate":
                            try:
                                self.__setattr__(
                                    attr,
                                    datetime.strptime(
                                        xml_element.get(attr.replace("_", "-")),
                                        r"%Y%m%dT%H%M%SZ",
                                    ),
                                )
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "o_tmf" | "o_encoding":
                            self.__setattr__(
                                attr, xml_element.get(attr.replace("_", "-"))
                            )
                        case "usagecount" | "tuid":
                            try:
                                self.__setattr__(attr, int(xml_element.get(attr)))
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "props":
                            self.props = [
                                Prop(prop) for prop in xml_element if prop.tag == "prop"
                            ]
                        case "notes":
                            self.notes = [
                                Note(note) for note in xml_element if note.tag == "note"
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
        element: Element = Element("tu")
        for attr, val in vars(self).items():
            if val is None:
                continue
            if attr[1] == "_":
                element.set(attr.replace("_", "-"), val)
                continue
            if isinstance(val, datetime):
                element.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                continue
            if isinstance(val, int):
                element.set(attr, str(val))
                continue
            if isinstance(val, str):
                element.set(attr, val)
                continue
            if isinstance(val, Iterable):
                element.extend([elem.export() for elem in val])
                continue
            if isinstance(val, Seg):
                element.append(val.export())
                continue
        return element


class Tmx(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        header: Header | None = None,
        tus: Iterable[Tu] | None = None,
    ) -> None:
        match xml_element:
            case Element():
                self.tus = [
                    Tu(xml_element=child)
                    for child in xml_element.find("body")
                    if child.tag == "tu"
                ]
                self.header = Header(xml_element=xml_element.find("header"))
            case None:
                self.tus = tus
                self.header = header
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("tmx", version="1.4")
        element.append(self.header.export())
        body = Element("body")
        body.extend([tu.export() for tu in self.tus])
        element.append(body)
        return element
