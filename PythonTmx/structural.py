from __future__ import annotations

from datetime import datetime
from re import MULTILINE, match
from typing import Any, Iterable, Literal

from errors import (
    ExtraTextError,
    IncorrectTagError,
    MissingRequiredAttributeError,
)
from inline import Bpt, Ept, Hi, It, Ph
from lxml.etree import Element, XMLParser, _Element, parse

__all__ = ["Header", "Map", "Note", "Prop", "Seg", "Tmx", "Tu", "Tuv", "Ude"]


class Header:
    __attrib = {
        "creationtool": None,
        "creationtoolversion": None,
        "segtype": None,
        "o-tmf": None,
        "adminlang": None,
        "srclang": None,
        "datatype": None,
        "o-encoding": None,
        "creationdate": None,
        "creationid": None,
        "changedate": None,
        "changeid": None,
    }

    def __init__(
        self,
        xml_element: _Element | None = None,
        notes: Iterable[Note] | None = [],
        props: Iterable[Prop] | None = [],
        udes: Iterable[Ude] | None = [],
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
    ) -> None:
        if xml_element is not None:
            for attr in self.__attrib:
                val = xml_element.get(attr)
                match attr:
                    case "creationtool":
                        self.creationtool = creationtool if creationtool else val
                    case "creationtoolversion":
                        self.creationtoolversion = (
                            creationtoolversion if creationtoolversion else val
                        )
                    case "segtype":
                        self.segtype = segtype if segtype else val
                    case "o-tmf":
                        self.o_tmf = o_tmf if o_tmf else val
                    case "adminlang":
                        self.adminlang = adminlang if adminlang else val
                    case "srclang":
                        self.srclang = srclang if srclang else val
                    case "datatype":
                        self.datatype = datatype if datatype else val
                    case "o-encoding":
                        self.o_encoding = o_encoding if o_encoding else val
                    case "creationdate":
                        self.creationdate = creationdate if creationdate else val
                        try:
                            self.creationdate = datetime.strptime(
                                self.creationdate, r"%Y%m%dT%H%M%SZ"
                            )
                        except (ValueError, TypeError):
                            pass
                    case "creationid":
                        self.creationid = creationid if creationid else val
                    case "changedate":
                        self.changedate = changedate if changedate else val
                        try:
                            self.changedate = datetime.strptime(
                                self.changedate, r"%Y%m%dT%H%M%SZ"
                            )
                        except (ValueError, TypeError):
                            pass
                    case "changeid":
                        self.changeid = changeid if changeid else val
            self.notes = (
                notes
                if notes
                else [Note(note) for note in xml_element if note.tag == "note"]
            )
            self.props = (
                props
                if props
                else [Prop(prop) for prop in xml_element if prop.tag == "prop"]
            )
            self.udes = (
                udes if udes else [Ude(ude) for ude in xml_element if ude.tag == "ude"]
            )
        else:
            self.notes = notes
            self.props = props
            self.udes = udes
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

    def __setattr__(self, name: str, value: Any) -> None:
        _name = name.replace("_", "-")
        if _name in self.__attrib.keys():
            if isinstance(value, datetime):
                self.__attrib[_name] = value.strftime(r"%Y%m%dT%H%M%SZ")
            else:
                self.__attrib[_name] = value
        super().__setattr__(name, value)

    def export(self) -> _Element:
        elem: _Element = Element(
            "header", {attr: val for attr, val in self.__attrib.items() if val}
        )
        elem.extend([note.export() for note in self.notes])
        elem.extend([prop.export() for prop in self.props])
        elem.extend([ude.export() for ude in self.udes])
        return elem


class Prop:
    __attrib = {
        "type": None,
        "{http://www.w3.org/XML/1998/namespace}lang": None,
        "o-encoding": None,
    }

    def __init__(
        self,
        xml_element: _Element | None = None,
        text: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        if xml_element is not None:
            self.type_ = type_ if type_ else xml_element.get("type")
            self.o_encoding = (
                o_encoding if o_encoding else xml_element.get("o-encoding")
            )
            self.lang = (
                lang
                if lang
                else xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
            )
            self.text = text if text else xml_element.text
        else:
            self.o_encoding = o_encoding
            self.type_ = type_
            self.lang = lang
            self.text = text

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "o_encoding":
            self.__attrib["o-encoding"] = value
        elif name == "lang":
            self.__attrib["{http://www.w3.org/XML/1998/namespace}lang"] = value
        elif name == "type_":
            self.__attrib["type"] = value
        else:
            pass
        super().__setattr__(name, value)

    def export(self) -> _Element:
        elem: _Element = Element(
            "prop", {attr: val for attr, val in self.__attrib.items() if val}
        )
        elem.text = self.text
        return elem


class Note:
    __attrib = {
        "{http://www.w3.org/XML/1998/namespace}lang": None,
        "o-encoding": None,
    }

    def __init__(
        self,
        xml_element: _Element | None = None,
        text: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        if xml_element is not None:
            self.o_encoding = (
                o_encoding if o_encoding else xml_element.get("o-encoding")
            )
            self.lang = (
                lang
                if lang
                else xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
            )
            self.text = text if text else xml_element.text
        else:
            self.o_encoding = o_encoding
            self.lang = lang
            self.text = text

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "o_encoding":
            self.__attrib["o-encoding"] = value
        elif name == "lang":
            self.__attrib["{http://www.w3.org/XML/1998/namespace}lang"] = value
        else:
            pass
        super().__setattr__(name, value)

    def export(self) -> _Element:
        elem: _Element = Element(
            "note", {attr: val for attr, val in self.__attrib.items() if val}
        )
        elem.text = self.text
        return elem


class Ude:
    __attrib = {"name": None, "base": None}

    def __init__(
        self,
        xml_element: _Element | None = None,
        maps: Iterable[Map] | None = [],
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        if xml_element is not None:
            self.base = base if base else xml_element.get("base")
            self.name = name if name else xml_element.get("name")
            self.maps = (
                maps
                if maps
                else [Map(map_) for map_ in xml_element if map_.tag == "map"]
            )
        else:
            self.base = base
            self.name = name
            self.maps = maps

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"base", "name"}:
            self.__attrib[name] = value
        pass
        super().__setattr__(name, value)

    def export(self) -> _Element:
        elem: _Element = Element(
            "ude", {attr: val for attr, val in self.__attrib.items() if val}
        )
        if self.maps and not self.base:
            for map_ in self.maps:
                if map_.code:
                    raise MissingRequiredAttributeError(elem, "base")
                elem.append(map_.export())
            return elem
        elem.extend([map_.export() for map_ in self.maps])
        return elem


class Map:
    __attrib = {"unicode": None, "code": None, "ent": None, "subst": None}

    def __init__(
        self,
        xml_element: _Element | None = None,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        if xml_element is not None:
            self.unicode = unicode if unicode else xml_element.get("unicode")
            self.code = code if code else xml_element.get("code")
            self.ent = ent if ent else xml_element.get("ent")
            self.subst = subst if subst else xml_element.get("subst")
        else:
            self.unicode = unicode
            self.code = code
            self.ent = ent
            self.subst = subst

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__attrib.keys():
            self.__attrib[name] = value
        super().__setattr__(name, value)

    def export(self) -> _Element:
        elem: _Element = Element(
            "map", {attr: val for attr, val in self.__attrib.items() if val}
        )
        return elem


class Seg:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = [],
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
                self.content = [xml_element.text]
            else:
                self.content = []
                if xml_element.text is not None:
                    self.content.append(xml_element.text)
                for child in xml_element:
                    match child.tag:
                        case "ph":
                            self.content.append(Ph(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "bpt":
                            self.content.append(Bpt(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "ept":
                            self.content.append(Ept(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "hi":
                            self.content.append(Hi(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "it":
                            self.content.append(It(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case _:
                            raise IncorrectTagError(
                                expected_element="bpt, ept, ph, hi or it",
                                found_element=child,
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
                        element.insert(0, elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="bpt, ept, ph, hi or it",
                            found_element=elem,
                        )
        return element


class Tuv:
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = [],
        props: Iterable[Prop] | None = [],
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
        if not isinstance(xml_element, Element):
            self.notes = notes
            self.props = props
            self.segment = segment
            self.lang = lang
            self.o_encoding = o_encoding
            self.datatype = datatype
            self.usagecount = usagecount
            self.lastusagedate = lastusagedate
            self.creationtool = creationtool
            self.creationtoolversion = creationtoolversion
            self.creationdate = creationdate
            self.creationid = creationid
            self.changedate = changedate
            self.changeid = changeid
            self.o_tmf = o_tmf
        else:
            if xml_element.tag != "tuv":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="tuv"
                )
            if xml_element.text is not None and not match(
                r"^[\n\s]+$", xml_element.text, flags=MULTILINE
            ):
                raise ExtraTextError(element=xml_element)
            if len(xml_element):
                self.segment = Seg(xml_element.find("seg"))
                self.props = [Prop(prop) for prop in xml_element if prop.tag == "prop"]
                self.notes = [Note(note) for note in xml_element if note.tag == "note"]
            self.lang = (
                lang
                if lang is not None
                else xml_element.attrib.get(
                    "{http://www.w3.org/XML/1998/namespace}lang"
                )
            )
            self.o_encoding = (
                o_encoding
                if o_encoding is not None
                else xml_element.attrib.get("o-encoding")
            )
            self.datatype = (
                datatype if datatype is not None else xml_element.attrib.get("datatype")
            )
            if usagecount is not None:
                self.usagecount = usagecount
            else:
                try:
                    self.usagecount = int(xml_element.get("usagecount"))
                except (ValueError, TypeError):
                    self.usagecount = xml_element.get("usagecount")
            if lastusagedate is not None:
                self.lastusagedate = lastusagedate
            else:
                try:
                    self.lastusagedate = datetime.strptime(
                        xml_element.get("lastusagedate"),
                        r"%Y%m%dT%H%M%SZ",
                    )
                except TypeError:
                    self.lastusagedate = xml_element.get("lastusagedate")
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
                except (ValueError, TypeError):
                    self.changedate = xml_element.get("changedate")
            self.changeid = (
                changeid if changeid is not None else xml_element.get("changeid")
            )

    def export(self) -> Element:
        element: Element = Element("tuv")
        for key, val in vars(self).items():
            match key, val:
                case "segment", Seg():
                    element.insert(0, val.export())
                case "notes", _ if isinstance(val, Iterable):
                    for note in val:
                        if not isinstance(note, Note):
                            raise TypeError(
                                f"notes should only contain Note objects, not {type(note)}"
                            )
                        element.insert(0, note.export())
                case "props", _ if isinstance(val, Iterable):
                    for prop in val:
                        if not isinstance(prop, Prop):
                            raise TypeError(
                                f"props should only contain Prop objects, not {type(prop)}"
                            )
                        element.insert(0, prop.export())
                case "lang", None:
                    raise MissingRequiredAttributeError(element=element, attribute=key)
                case "lang", str():
                    element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                case (
                    "datatype"
                    | "creationtool"
                    | "creationtoolversion"
                    | "creationid"
                    | "changeid",
                    str(),
                ):
                    element.set(key, val)
                case "o_tmf" | "o_encoding", str():
                    key = key.replace("_", "-")
                    element.set(key, val)
                case "creationdate" | "changedate" | "lastusagedate", datetime():
                    element.set(key, val.strftime(r"%Y%m%dT%H%M%SZ"))
                case "creationdate" | "changedate" | "lastusagedate", str():
                    val = val.upper()
                    if not match(r"\d{8}T\d{6}Z", val):
                        raise ValueError(
                            f"attribute {key} is not formatted correctly. if using a string, value should be formatted as YYYYMMDDTHHMMSSZ."
                        )
                    element.set(key, val)
                case "usagecount", str() | int():
                    element.set(key, str(val))
                case _, None:
                    pass
                case _, _:
                    raise TypeError(
                        f"cannot serialize attribute {key} with value {val}"
                    )
        return element


class Tu:
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = [],
        props: Iterable[Prop] | None = [],
        tuvs: Iterable[Tuv] | None = [],
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
        if not isinstance(xml_element, Element):
            self.notes = notes
            self.props = props
            self.tuvs = tuvs
            self.tuid = tuid
            self.o_encoding = o_encoding
            self.datatype = datatype
            self.usagecount = usagecount
            self.lastusagedate = lastusagedate
            self.creationtool = creationtool
            self.creationtoolversion = creationtoolversion
            self.creationdate = creationdate
            self.creationid = creationid
            self.changedate = changedate
            self.segtype = segtype
            self.changeid = changeid
            self.o_tmf = o_tmf
            self.srclang = srclang
        else:
            if xml_element.tag != "tu":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="tu"
                )
            if xml_element.text is not None and not match(
                r"^[\n\s]+$", xml_element.text, flags=MULTILINE
            ):
                raise ExtraTextError(element=xml_element)

            self.tuvs = (
                tuvs
                if tuvs is not None
                else [Tuv(tuv) for tuv in xml_element if tuv.tag == "tuv"]
            )
            self.props = (
                props
                if props is not None
                else [Prop(prop) for prop in xml_element if prop.tag == "prop"]
            )
            self.notes = (
                notes
                if notes is not None
                else [Note(note) for note in xml_element if note.tag == "note"]
            )
            if tuid is not None:
                self.tuid = tuid
            else:
                try:
                    self.tuid = int(xml_element.get("tuid"))
                except (ValueError, TypeError):
                    self.tuid = xml_element.get("tuid")
            self.o_encoding = (
                o_encoding
                if o_encoding is not None
                else xml_element.attrib.get("o-encoding")
            )
            self.datatype = (
                datatype if datatype is not None else xml_element.attrib.get("datatype")
            )
            if usagecount is not None:
                self.usagecount = usagecount
            else:
                try:
                    self.usagecount = int(xml_element.get("usagecount"))
                except (ValueError, TypeError):
                    self.usagecount = xml_element.get("usagecount")
            if lastusagedate is not None:
                self.lastusagedate = lastusagedate
            else:
                try:
                    self.lastusagedate = datetime.strptime(
                        xml_element.get("lastusagedate"),
                        r"%Y%m%dT%H%M%SZ",
                    )
                except TypeError:
                    self.lastusagedate = xml_element.get("lastusagedate")
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
                except (ValueError, TypeError):
                    self.changedate = xml_element.get("changedate")
            self.segtype = (
                segtype if segtype is not None else xml_element.get("segtype")
            )
            self.changeid = (
                changeid if changeid is not None else xml_element.get("changeid")
            )
            self.srclang = (
                srclang if srclang is not None else xml_element.attrib.get("srclang")
            )

    def export(self) -> Element:
        element: Element = Element("tu")
        for key, val in vars(self).items():
            match key, val:
                case "notes", _ if isinstance(val, Iterable):
                    for note in val:
                        if not isinstance(note, Note):
                            raise TypeError(
                                f"notes should only contain Note objects, not {type(note)}"
                            )
                        element.insert(0, note.export())
                case "tuvs", _ if isinstance(val, Iterable):
                    for tuv in val:
                        if not isinstance(tuv, Tuv):
                            raise TypeError(
                                f"tuv should only contain Tuv objects, not {type(tuv)}"
                            )
                        element.insert(0, tuv.export())
                case "props", _ if isinstance(val, Iterable):
                    for prop in val:
                        if not isinstance(prop, Prop):
                            raise TypeError(
                                f"props should only contain Prop objects, not {type(prop)}"
                            )
                        element.insert(0, prop.export())
                case (
                    "datatype"
                    | "creationtool"
                    | "creationtoolversion"
                    | "creationid"
                    | "changeid"
                    | "srclang",
                    str(),
                ):
                    element.set(key, val)
                case "o_tmf" | "o_encoding", str():
                    key = key.replace("_", "-")
                    element.set(key, val)
                case "segtype", str():
                    if val not in (
                        "block",
                        "paragraph",
                        "sentence",
                        "phrase",
                    ):
                        raise ValueError(
                            f"attribute segtype must be one of block, paragraph, sentence or phrase not {val}"
                        )
                    element.set(key, val)
                case "creationdate" | "changedate" | "lastusagedate", datetime():
                    element.set(key, val.strftime(r"%Y%m%dT%H%M%SZ"))
                case "creationdate" | "changedate" | "lastusagedate", str():
                    val = val.upper()
                    if not match(r"\d{8}T\d{6}Z", val):
                        raise ValueError(
                            f"attribute {key} is not formatted correctly. if using a string, value should be formatted as YYYYMMDDTHHMMSSZ."
                        )
                    element.set(key, val)
                case "usagecount" | "tuid", str() | int():
                    element.set(key, str(val))
                case _, None:
                    pass
                case _, _:
                    raise TypeError(
                        f"cannot serialize attribute {key} with value {val}"
                    )
        return element


class Tmx:
    def __init__(
        self,
        xml_element: Element | None = None,
        header: Header | None = None,
        tus: Iterable[Tu] | None = [],
    ) -> None:
        if not isinstance(xml_element, Element):
            self.header = header
            self.tus = tus
        else:
            if xml_element.tag != "tmx":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="tmx"
                )
            if xml_element.text is not None and not match(
                r"^[\n\s]+$", xml_element.text, flags=MULTILINE
            ):
                raise ExtraTextError(element=xml_element)
            self.header = (
                header
                if header is not None
                else Header(xml_element=xml_element.find("header"))
            )
            self.tus = (
                tus if tus is not None else [Tu(tu) for tu in xml_element.iter("tu")]
            )

    def export(self) -> Element:
        element: Element = Element("tmx", version="1.4")
        element.insert(0, self.header.export())
        body = Element("body")
        body.extend([tu.export() for tu in self.tus])
        element.append(body)
        return element


a = parse("a.xml", XMLParser(encoding="utf-8", remove_blank_text=True)).getroot()
b = Header(a)
c = b.export()
