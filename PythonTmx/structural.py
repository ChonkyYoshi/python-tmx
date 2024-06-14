from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Literal
from xml.etree.ElementTree import SubElement

from errors import (
    IncorrectTagError,
    MissingRequiredAttributeError,
)
from inline import Bpt, Ept, Hi, It, Ph
from lxml.etree import Element, _Element

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
            if xml_element.tag != "header":
                raise IncorrectTagError(xml_element, "header")
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
                    case "creationid":
                        self.creationid = creationid if creationid else val
                    case "changedate":
                        self.changedate = changedate if changedate else val
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
        try:
            self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
        except (ValueError, TypeError):
            pass
        try:
            self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
        except (ValueError, TypeError):
            pass

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
            if xml_element.tag != "prop":
                raise IncorrectTagError(xml_element, "prop")
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
            if xml_element.tag != "note":
                raise IncorrectTagError(xml_element, "note")
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
            if xml_element.tag != "ude":
                raise IncorrectTagError(xml_element, "ude")
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
            if xml_element.tag != "map":
                raise IncorrectTagError(xml_element, "map")
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
        xml_element: _Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = [],
    ) -> None:
        if xml_element is None:
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

    def export(self) -> _Element:
        element: _Element = Element("seg")
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if element.text is None:
                        element.text = child
                    case str() if not len(element):
                        element.text += child
                    case str():
                        element[-1].tail = child
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        element.append(child.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="bpt, ept, ph, hi or it",
                            found_element=child,
                        )
        return element


class Tuv:
    __attrib = {
        "{http://www.w3.org/XML/1998/namespace}lang": None,
        "o-encoding": None,
        "datatype": None,
        "usagecount": None,
        "lastusagedate": None,
        "creationtool": None,
        "creationtoolversion": None,
        "creationdate": None,
        "creationid": None,
        "changedate": None,
        "changeid": None,
        "o-tmf": None,
    }

    def __init__(
        self,
        xml_element: _Element | None = None,
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
        if xml_element is not None:
            if xml_element.tag != "tuv":
                raise IncorrectTagError(xml_element, "tuv")
            for attr in self.__attrib:
                val = xml_element.get(attr)
                match attr:
                    case "{http://www.w3.org/XML/1998/namespace}lang":
                        self.lang = (
                            lang
                            if lang
                            else xml_element.get(
                                "{http://www.w3.org/XML/1998/namespace}lang"
                            )
                        )
                    case "o-encoding":
                        self.o_encoding = o_encoding if o_encoding else val
                    case "datatype":
                        self.datatype = datatype if datatype else val
                    case "usagecount":
                        self.usagecount = usagecount if usagecount else val
                    case "lastusagedate":
                        self.lastusagedate = lastusagedate if lastusagedate else val
                    case "creationtool":
                        self.creationtool = creationtool if creationtool else val
                    case "creationtoolversion":
                        self.creationtoolversion = (
                            creationtoolversion if creationtoolversion else val
                        )
                    case "creationdate":
                        self.creationdate = creationdate if creationdate else val
                    case "creationid":
                        self.creationid = creationid if creationid else val
                    case "changedate":
                        self.changedate = changedate if changedate else val
                    case "changeid":
                        self.changeid = changeid if changeid else val
                    case "o-tmf":
                        self.o_tmf = o_tmf if o_tmf else val
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
            self.segment = Seg(xml_element=xml_element.find("seg"))
        else:
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
        try:
            self.usagecount = int(self.usagecount)
        except (ValueError, TypeError):
            pass
        try:
            self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
        except (ValueError, TypeError):
            pass
        try:
            self.lastusagedate = datetime.strptime(
                self.lastusagedate, r"%Y%m%dT%H%M%SZ"
            )
        except (ValueError, TypeError):
            pass
        try:
            self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
        except (ValueError, TypeError):
            pass

    def __setattr__(self, name: str, value: Any) -> None:
        _name = name.replace("_", "-")
        if _name in self.__attrib.keys():
            if isinstance(value, datetime):
                self.__attrib[_name] = value.strftime(r"%Y%m%dT%H%M%SZ")
            elif isinstance(value, int):
                self.__attrib[_name] = str(value)
            else:
                self.__attrib[_name] = value
        super().__setattr__(name, value)

    def export(self) -> _Element:
        elem: _Element = Element(
            "header", {attr: val for attr, val in self.__attrib.items() if val}
        )
        elem.append(self.segment.export())
        elem.extend([note.export() for note in self.notes])
        elem.extend([prop.export() for prop in self.props])
        return elem


class Tu:
    __attrib = {
        "tuid": None,
        "o-encoding": None,
        "datatype": None,
        "usagecount": None,
        "lastusagedate": None,
        "creationtool": None,
        "creationtoolversion": None,
        "creationdate": None,
        "creationid": None,
        "changedate": None,
        "segtype": None,
        "changeid": None,
        "o-tmf": None,
        "srclang": None,
    }

    def __init__(
        self,
        xml_element: _Element | None = None,
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
        if xml_element is not None:
            if xml_element.tag != "tu":
                raise IncorrectTagError(xml_element, "tu")
            for attr in self.__attrib:
                val = xml_element.get(attr)
                match attr:
                    case "tuid":
                        self.tuid = tuid if tuid else xml_element.get("tuid")
                    case "o-encoding":
                        self.o_encoding = o_encoding if o_encoding else val
                    case "datatype":
                        self.datatype = datatype if datatype else val
                    case "usagecount":
                        self.usagecount = usagecount if usagecount else val
                    case "lastusagedate":
                        self.lastusagedate = lastusagedate if lastusagedate else val
                    case "creationtool":
                        self.creationtool = creationtool if creationtool else val
                    case "creationtoolversion":
                        self.creationtoolversion = (
                            creationtoolversion if creationtoolversion else val
                        )
                    case "creationdate":
                        self.creationdate = creationdate if creationdate else val
                    case "creationid":
                        self.creationid = creationid if creationid else val
                    case "changedate":
                        self.changedate = changedate if changedate else val
                    case "changeid":
                        self.changeid = changeid if changeid else val
                    case "segtype":
                        self.segtype = segtype if segtype else val
                    case "o-tmf":
                        self.o_tmf = o_tmf if o_tmf else val
                    case "srclang":
                        self.srclang = srclang if srclang else val
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
            self.tuvs = (
                tuvs if tuvs else [Tuv(Tuv) for Tuv in xml_element if Tuv.tag == "Tuv"]
            )
        else:
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
        try:
            self.tuid = int(self.tuid)
        except (ValueError, TypeError):
            pass
        try:
            self.usagecount = int(self.usagecount)
        except (ValueError, TypeError):
            pass
        try:
            self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
        except (ValueError, TypeError):
            pass
        try:
            self.lastusagedate = datetime.strptime(
                self.lastusagedate, r"%Y%m%dT%H%M%SZ"
            )
        except (ValueError, TypeError):
            pass
        try:
            self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
        except (ValueError, TypeError):
            pass

    def __setattr__(self, name: str, value: Any) -> None:
        _name = name.replace("_", "-")
        if _name in self.__attrib.keys():
            if isinstance(value, datetime):
                self.__attrib[_name] = value.strftime(r"%Y%m%dT%H%M%SZ")
            elif isinstance(value, int):
                self.__attrib[_name] = str(value)
            else:
                self.__attrib[_name] = value
        super().__setattr__(name, value)

    def export(self) -> _Element:
        elem: _Element = Element(
            "header", {attr: val for attr, val in self.__attrib.items() if val}
        )
        elem.extend([tuv.export() for tuv in self.tuvs])
        elem.extend([note.export() for note in self.notes])
        elem.extend([prop.export() for prop in self.props])
        return elem


class Tmx:
    def __init__(
        self,
        xml_element: _Element | None = None,
        header: Header | None = None,
        tus: Iterable[Tu] | None = [],
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "tmx":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="tmx"
                )
            self.header = (
                header
                if header is not None
                else Header(xml_element=xml_element.find("header"))
            )
            self.tus = (
                tus if tus is not None else [Tu(tu) for tu in xml_element.iter("tu")]
            )

    def export(self) -> _Element:
        element: _Element = Element("tmx", version="1.4")
        element.insert(0, self.header.export())
        body = SubElement(element, "body")
        body.extend([tu.export() for tu in self.tus])
        return element
