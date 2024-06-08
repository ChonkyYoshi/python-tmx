from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from re import MULTILINE, match
from typing import Iterable, Literal
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
    def __init__(self, found_element: Element, expected_element: str) -> None:
        super().__init__(
            f"Expected {expected_element} Element but found {found_element.tag} instead"
        )


class ExtraChildrenError(Exception):
    def __init__(self, element: Element) -> None:
        if len(element):
            super().__init__(
                f"Element {element.tag} is not allowed to have children but element has {len(element)} children"
            )


class ExtraTextError(Exception):
    def __init__(self, element: Element) -> None:
        if len(element):
            super().__init__(
                f"Element {element.tag} is not allowed to have text but element has the following text data:\n{element.tail}"
            )


class MissingRequiredAttributeError(Exception):
    def __init__(self, element: Element, attribute: str) -> None:
        super().__init__(
            f"Element {element.tag} is missing required attribute {attribute}"
        )


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
        if not isinstance(xml_element, Element):
            self.notes = notes
            self.props = props
            self.creationtool = creationtool
            self.creationtoolversion = creationtoolversion
            self.segtype = segtype
            self.o_tmf = o_tmf
            self.adminlang = adminlang
            self.srclang = srclang
            self.datatype = datatype
            self.o_encoding = o_encoding
            self.creationdate = creationdate
            self.creationid = creationid
            self.changedate = changedate
            self.changeid = changeid
            self.udes = udes
        else:
            if xml_element.tag != "header":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="header"
                )
            if xml_element.text is not None and not match(
                r"^[\n\s]+$", xml_element.text, flags=MULTILINE
            ):
                raise ExtraTextError(element=xml_element)
            self.creationtool = (
                creationtool
                if creationtool is not None
                else xml_element.attrib.get("creationtool")
            )
            self.creationtoolversion = (
                creationtoolversion
                if creationtoolversion is not None
                else xml_element.get("creationtoolversion")
            )
            self.segtype = (
                segtype if segtype is not None else xml_element.get("segtype")
            )
            self.o_tmf = o_tmf if o_tmf is not None else xml_element.get("o-tmf")
            self.adminlang = (
                adminlang if adminlang is not None else xml_element.get("adminlang")
            )
            self.srclang = (
                srclang if srclang is not None else xml_element.get("srclang")
            )
            self.datatype = (
                datatype if datatype is not None else xml_element.get("datatype")
            )
            self.o_encoding = (
                o_encoding if o_encoding is not None else xml_element.get("o-encoding")
            )
            if creationdate is not None:
                self.creationdate = creationdate
            else:
                try:
                    self.creationdate = datetime.strptime(
                        xml_element.get("creationdate"),
                        r"%Y%m%dT%H%M%SZ",
                    )
                except TypeError:
                    self.creationdate = xml_element.get("creationdate")
            self.creationid = (
                creationid if creationid is not None else xml_element.get("creationid")
            )
            if changedate is not None:
                self.changedate = changedate
            else:
                try:
                    self.changedate = datetime.strptime(
                        xml_element.get("changedate"),
                        r"%Y%m%dT%H%M%SZ",
                    )
                except ValueError:
                    self.changedate = xml_element.get("changedate")
            self.changeid = (
                changeid if changeid is not None else xml_element.get("changeid")
            )
            if len(xml_element):
                self.props = [Prop(prop) for prop in xml_element.iter("prop")]
                self.notes = [Note(note) for note in xml_element.iter("note")]
                self.udes = [Ude(ude) for ude in xml_element.iter("ude")]

    def export(self) -> Element:
        element: Element = Element("header")
        for key, val in vars(self).items():
            match key:
                case "notes" | "props" | "udes" if val is not None:
                    element.extend([child.export() for child in val])
                case (
                    "creationtool"
                    | "creationtoolversion"
                    | "adminlang"
                    | "srclang"
                    | "datatype"
                    | "segtype"
                    | "o_tmf"
                ) if val is None:
                    raise MissingRequiredAttributeError(element=element, attribute=key)
                case (
                    "creationtool"
                    | "creationtoolversion"
                    | "adminlang"
                    | "srclang"
                    | "datatype"
                    | "segtype"
                    | "o_tmf"
                    | "o_encoding"
                    | "creationid"
                    | "changeid"
                ) if not isinstance(val, str):
                    raise TypeError(f"attribute {key} must be a string not {type(val)}")
                case "segtype" if val not in (
                    "block",
                    "paragraph",
                    "sentence",
                    "phrase",
                ):
                    raise ValueError(
                        f"segtype must be one of block, paragraph, sentence or phrase not {val}"
                    )
                case "creationdate" | "changedate" if not isinstance(
                    val, (str, datetime)
                ):
                    raise TypeError(
                        f"attribute {key} must be a string or a dateitme not {type(val)}"
                    )
                case "creationdate" | "changedate":
                    try:
                        element.set(key, val.strftime(r"%Y%m%dT%H%M%SZ"))
                    except TypeError:
                        val = val.upper()
                        if not match(r"\d{8}T\d{6}Z", val):
                            raise ValueError(
                                f"attribute {key} is not formatted correctly. if using a string, value should be formatted as YYYYMMDDTHHMMSSZ."
                            )
                        element.set(key, val)
                case (
                    "creationtool"
                    | "creationtoolversion"
                    | "adminlang"
                    | "srclang"
                    | "datatype"
                    | "creationid"
                    | "changeid"
                    | "segtype"
                ):
                    element.set(key, val)
                case "o_tmf" | "o_encoding":
                    element.set(key.replace("_", "-"), val)
        return element


class Prop(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.content = content
            self.type_ = type_
            self.lang = lang
            self.o_encoding = o_encoding
        else:
            if xml_element.tag != "prop":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="prop"
                )
            if len(xml_element):
                raise ExtraChildrenError(element=xml_element)
            self.content = content if content is not None else xml_element.text
            self.type_ = type_ if type_ is not None else xml_element.get("type")
            self.lang = (
                lang
                if lang is not None
                else xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
            )
            self.o_encoding = (
                o_encoding if o_encoding is not None else xml_element.get("o-encoding")
            )

    def export(self) -> Element:
        element: Element = Element("prop")
        for key, val in vars(self).items():
            match key:
                case "type_" if val is None:
                    raise MissingRequiredAttributeError(
                        element=element, attribute="type_"
                    )
                case _ if val is None:
                    continue
                case _ if not isinstance(val, str):
                    raise TypeError(f"attribute {key} must be a string not {type(val)}")
                case "content":
                    element.text = self.content
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
        if not isinstance(xml_element, Element):
            self.content = content
            self.lang = lang
            self.o_encoding = o_encoding
        else:
            if xml_element.tag != "note":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="note"
                )
            if len(xml_element):
                raise ExtraChildrenError(element=xml_element)
            self.content = content if content is not None else xml_element.text
            self.lang = (
                lang
                if lang is not None
                else xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
            )
            self.o_encoding = (
                o_encoding if o_encoding is not None else xml_element.get("o-encoding")
            )

    def export(self) -> Element:
        element: Element = Element("note")
        for key, val in vars(self).items():
            match key:
                case _ if val is None:
                    continue
                case _ if not isinstance(val, str):
                    raise TypeError(f"attribute {key} must be a string not {type(val)}")
                case "content":
                    element.text = self.content
                case "lang":
                    element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                case "o_encoding":
                    element.set("o-encoding", val)
        return element


class Ude(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        maps: Iterable[Map] | None = None,
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.maps = maps
            self.name = name
            self.base = base
        else:
            if xml_element.tag != "ude":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="ude"
                )
            if xml_element.text is not None and not match(
                r"^[\n\s]+$", xml_element.text, flags=MULTILINE
            ):
                raise ExtraTextError(element=xml_element)
            self.maps = (
                maps
                if maps is not None
                else [Map(xml_element=map_) for map_ in xml_element.iter("map")]
            )
            self.name = name if name is not None else xml_element.get("name")
            self.base = base if base is not None else xml_element.get("base")

    def export(self) -> Element:
        element: Element = Element("ude")
        if len(self.maps):
            for map_ in self.maps:
                if map_.code is not None:
                    need_base = True
                element.append(map_.export())
            if need_base and not self.base:
                raise MissingRequiredAttributeError(element=element, attribute="base")
            elif self.base:
                element.set("base", self.base)
        if not self.name:
            raise MissingRequiredAttributeError(element=element, attribute="base")
        element.set("name", self.name)
        return element


class Map(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        unicode: Iterable[Map] | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.unicode = unicode
            self.code = code
            self.ent = ent
            self.subst = subst
        else:
            if xml_element.tag != "map":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="map"
                )
            if len(xml_element):
                raise ExtraChildrenError(element=xml_element)
            if xml_element.text is not None and not match(
                r"^[\n\s]+$", xml_element.text, flags=MULTILINE
            ):
                raise ExtraTextError(element=xml_element)
            self.unicode = (
                unicode if unicode is not None else xml_element.get("unicode")
            )
            self.code = code if code is not None else xml_element.get("code")
            self.ent = ent if ent is not None else xml_element.get("ent")
            self.subst = subst if subst is not None else xml_element.get("subst")

    def export(self) -> Element:
        element: Element = Element("map")
        for key, val in vars(self).items():
            match key:
                case _ if val is None:
                    continue
                case _ if not isinstance(val, str):
                    raise TypeError(f"attribute {key} must be a string not {type(val)}")
                case _:
                    element.set(key, val)
        return element


class Ut(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        x: int | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.content = content
        else:
            if xml_element.tag != "ut":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="ut"
                )
            self.x = x if x is not None else xml_element.get("x")
            try:
                self.x = int(self.x)
            except ValueError:
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("ut")
        if self.x is None:
            pass
        elif isinstance(self.x, (int, str)):
            element.set("x", str(self.x))
        else:
            raise TypeError(
                f"attribute x must be a string or an int not {type(self.x)}"
            )
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class Sub(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | Ph | Hi | It] | str | None = None,
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.datatype = datatype
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "sub":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="sub"
                )
            self.datatype = (
                datatype if datatype is not None else xml_element.get("datatype")
            )
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    match child.tag:
                        case "ph":
                            self.content += Ph(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "bpt":
                            self.content += Bpt(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "ept":
                            self.content += Ept(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "hi":
                            self.content += Hi(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "it":
                            self.content += It(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case _:
                            raise IncorrectTagError(
                                found_element=child,
                                expected_element="bpt, ept, ph, hi or it",
                            )

    def export(self) -> Element:
        element: Element = Element("sub")
        if self.datatype is None:
            pass
        elif isinstance(self.datatype, str):
            element.set("datatype", self.datatype)
        else:
            raise TypeError(
                f"attribute datatype must be a string not {type(self.datatype)}"
            )
        if self.type_ is None:
            pass
        elif isinstance(self.type_, str):
            element.set("type", self.type_)
        else:
            raise TypeError(f"attribute type_ must be a string not {type(self.type_)}")
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class Bpt(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.i = i
            self.x = x
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "bpt":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="bpt"
                )
            self.x = x if x is not None else xml_element.get("x")
            try:
                self.x = int(self.x)
            except ValueError:
                pass
            self.i = i if i is not None else xml_element.get("i")
            try:
                self.i = int(self.i)
            except ValueError:
                pass
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("bpt")
        if self.i is None:
            raise MissingRequiredAttributeError(element=element, attribute="i")
        elif not isinstance(self.i, (int, str)):
            raise TypeError(
                f"attribute i must be a string or an int not {type(self.x)}"
            )
        else:
            element.set("i", str(self.i))
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", self.x)
        if not isinstance(self.type_, str):
            pass
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class Ept(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.i = i
            self.content = content
        else:
            if xml_element.tag != "ept":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="ept"
                )
            self.i = i if i is not None else xml_element.get("i")
            try:
                self.i = int(self.i)
            except ValueError:
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("ept")
        if self.i is None:
            raise MissingRequiredAttributeError(element=element, attribute="i")
        elif not isinstance(self.i, (int, str)):
            raise TypeError(
                f"attribute i must be a string or an int not {type(self.x)}"
            )
        else:
            element.set("i", str(self.i))
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class It(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        pos: Literal["begin", "end"] | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.pos = pos
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "it":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="it"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.pos = pos if pos is not None else xml_element.get("pos")
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            try:
                self.x = int(self.x)
            except ValueError:
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("it")
        if self.pos is None:
            raise MissingRequiredAttributeError(element=element, attribute="pos")
        elif not isinstance(self.pos, str):
            raise TypeError(f"attribute pos must be a string not {type(self.pos)}")
        elif self.pos not in ("begin", "end"):
            raise ValueError(
                f"attribute pos must be a one of begin or end not {self.pos}"
            )
        else:
            element.set("pos", self.pos)
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", str(self.x))
        if not isinstance(self.type_, str):
            pass
        else:
            element.set("type", self.type_)
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class Ph(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.type_ = type_
            self.assoc = assoc
            self.content = content
        else:
            if xml_element.tag != "ph":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="ph"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.assoc = assoc if assoc is not None else xml_element.get("assoc")
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            try:
                self.x = int(self.x)
            except ValueError:
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("ph")
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", str(self.x))
        if not isinstance(self.type_, str):
            pass
        else:
            element.set("type", self.type_)
        if not isinstance(self.assoc, str):
            pass
        elif self.assoc not in ("p", "f", "b"):
            raise ValueError(
                f"attribute assoc must be a one of p, f or b not {self.assoc}"
            )
        else:
            element.set("assoc", self.assoc)
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class Hi(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "hi":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="hi"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.type_ = type_ if type_ is not None else xml_element.get("type")
            try:
                self.x = int(self.x)
            except ValueError:
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    match child.tag:
                        case "ph":
                            self.content += Ph(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "bpt":
                            self.content += Bpt(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "ept":
                            self.content += Ept(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "hi":
                            self.content += Hi(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "it":
                            self.content += It(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case _:
                            raise IncorrectTagError(
                                found_element=child,
                                expected_element="bpt, ept, ph, hi or it",
                            )

    def export(self) -> Element:
        element: Element = Element("hi")
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", str(self.x))
        if not isinstance(self.type_, str):
            pass
        else:
            element.set("type", self.type_)
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class Seg(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.content = content
        else:
            if xml_element.tag != "seg":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="seg"
                )
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    match child.tag:
                        case "ph":
                            self.content += Ph(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "bpt":
                            self.content += Bpt(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "ept":
                            self.content += Ept(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "hi":
                            self.content += Hi(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "it":
                            self.content += It(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case _:
                            raise IncorrectTagError(
                                found_element=child,
                                expected_element="bpt, ept, ph, hi or it",
                            )

    def export(self) -> Element:
        element: Element = Element("seg")
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        element.append(elem.export())
                    case _:
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


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
                        found_element=xml_element.tag, expected_element="tuv"
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
                        found_element=xml_element.tag, expected_element="tu"
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


# elem = parse("a.tmx").getroot()
# head = Header(xml_element=elem)
# head_elem = head.export()
# exp_tree = ElementTree(head_elem)
# exp_tree.write("b.tmx", encoding="utf-8")
