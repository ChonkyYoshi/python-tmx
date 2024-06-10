from __future__ import annotations

from datetime import datetime
from re import MULTILINE, match
from typing import Iterable, Literal
from xml.etree.ElementTree import Element

from errors import (
    ExtraChildrenError,
    ExtraTextError,
    IncorrectTagError,
    MissingRequiredAttributeError,
)
from inline import Bpt, Ept, Hi, It, Ph


class Header:
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
        udes: Iterable[Ude] | None = None,
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
        if not isinstance(xml_element, Element):
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
        else:
            if xml_element.tag != "header":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="header"
                )
            if xml_element.text is not None and not match(
                r"^[\n\s]+$", xml_element.text, flags=MULTILINE
            ):
                raise ExtraTextError(element=xml_element)
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
            self.udes = (
                udes
                if udes is not None
                else [Ude(ude) for ude in xml_element if ude.tag == "ude"]
            )
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
                except (ValueError, TypeError):
                    self.changedate = xml_element.get("changedate")
            self.changeid = (
                changeid if changeid is not None else xml_element.get("changeid")
            )

    def export(self) -> Element:
        element: Element = Element("header")
        for key, val in vars(self).items():
            match key, val:
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
                case "udes", _ if isinstance(val, Iterable):
                    for ude in val:
                        if not isinstance(ude, Ude):
                            raise TypeError(
                                f"udes should only contain Ude objects, not {type(ude)}"
                            )
                        element.insert(0, ude.export())
                case (
                    "creationtool"
                    | "creationtoolversion"
                    | "adminlang"
                    | "srclang"
                    | "datatype"
                    | "segtype"
                    | "o_tmf",
                    None,
                ):
                    raise MissingRequiredAttributeError(element=element, attribute=key)
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
                case "o_tmf" | "o_encoding", str():
                    key = key.replace("_", "-")
                    element.set(key, val)
                case "creationdate" | "changedate", datetime():
                    element.set(key, val.strftime(r"%Y%m%dT%H%M%SZ"))
                case "creationdate" | "changedate", str():
                    val = val.upper()
                    if not match(r"\d{8}T\d{6}Z", val):
                        raise ValueError(
                            f"attribute {key} is not formatted correctly. if using a string, value should be formatted as YYYYMMDDTHHMMSSZ."
                        )
                    element.set(key, val)
                case _, None:
                    pass
                case _, _:
                    raise TypeError(
                        f"cannot serialize attribute {key} with value {val}"
                    )
        return element


class Prop:
    def __init__(
        self,
        xml_element: Element | None = None,
        text: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.text = text
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
            self.text = text if text is not None else xml_element.text
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
            match key, val:
                case "type_", None:
                    raise MissingRequiredAttributeError(
                        element=element, attribute="type_"
                    )
                case "type_", str():
                    element.set("type", val)
                case "lang", str():
                    element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                case "o_encoding", str():
                    element.set("o-encoding", val)
                case "text", (str()):
                    element.text = self.text
                case _, None:
                    pass
                case _, _:
                    raise TypeError(
                        f"cannot serialize attribute {key} with value {val}"
                    )
        return element


class Note:
    def __init__(
        self,
        xml_element: Element | None = None,
        text: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.text = text
            self.lang = lang
            self.o_encoding = o_encoding
        else:
            if xml_element.tag != "note":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="note"
                )
            if len(xml_element):
                raise ExtraChildrenError(element=xml_element)
            self.text = text if text is not None else xml_element.text
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
            match key, val:
                case "lang", str():
                    element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                case "o_encoding", str():
                    element.set("o-encoding", val)
                case "text", (str()):
                    element.text = self.text
                case _, None:
                    pass
                case _, _:
                    raise TypeError(
                        f"cannot serialize attribute {key} with value {val}"
                    )
        return element


class Ude:
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
                element.insert(0, map_.export())
            if need_base and not self.base:
                raise MissingRequiredAttributeError(element=element, attribute="base")
            elif self.base:
                element.set("base", self.base)
        if not self.name:
            raise MissingRequiredAttributeError(element=element, attribute="base")
        element.set("name", self.name)
        return element


class Map:
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
            match key, val:
                case "map", str():
                    element.set(key, val)
                case _, str():
                    element.set(key, val)
                case _, None:
                    pass
                case _, _:
                    raise TypeError(
                        f"cannot serialize attribute {key} with value {val}"
                    )
        return element


class Seg:
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
        tus: Iterable[Tu] | None = None,
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
