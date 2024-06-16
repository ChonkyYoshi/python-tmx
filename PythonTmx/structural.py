from datetime import datetime
from re import match
from typing import Iterable, Literal
from warnings import warn
from xml.etree.ElementTree import Element as std_Element

from errors import IncorrectTagError
from inline import Bpt, Ept, Hi, It, Ph
from lxml.etree import Element as lxml_Element_Factory
from lxml.etree import _Element as lxml_Element_type

__all__ = ["Header", "Map", "Note", "Prop", "Seg", "Tmx", "Tu", "Tuv", "Ude"]

type xml_Element = lxml_Element_type | std_Element


class Prop:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        text: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "prop":
                raise IncorrectTagError(xml_element.tag, "prop")
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("prop")
            if ElementType == "lxml"
            else std_Element("prop")
        )
        elem.text = self.text
        elem.attrib = self.make_attrib_dict()
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.type_:
            attrs["type"] = self.type_
        else:
            raise AttributeError("Required attribute type is missing")
        if self.lang:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
        if self.o_encoding:
            attrs["o-encoding"] = self.o_encoding
        return attrs


class Note:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        text: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "note":
                raise IncorrectTagError(xml_element.tag, "note")
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("note")
            if ElementType == "lxml"
            else std_Element("note")
        )
        elem.text = self.text
        elem.attrib = self.make_attrib_dict()
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.lang:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
        if self.o_encoding:
            attrs["o-encoding"] = self.o_encoding
        return attrs


class Map:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "map":
                raise IncorrectTagError(xml_element.tag, "map")
            self.unicode = unicode if unicode else xml_element.get("unicode")
            self.code = code if code else xml_element.get("code")
            self.ent = ent if ent else xml_element.get("ent")
            self.subst = subst if subst else xml_element.get("subst")
        else:
            self.unicode = unicode
            self.code = code
            self.ent = ent
            self.subst = subst

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("map") if ElementType == "lxml" else std_Element("map")
        )
        elem.attrib = self.make_attrib_dict()
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.unicode:
            attrs["unicode"] = self.unicode
        else:
            raise AttributeError("Required attribute unicode is missing")
        if self.code:
            attrs["code"] = self.code
        if self.ent:
            attrs["ent"] = self.ent
        if self.subst:
            attrs["subst"] = self.subst


class Ude:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        maps: Iterable[Map] | None = [],
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "ude":
                raise IncorrectTagError(xml_element.tag, "ude")
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("ude") if ElementType == "lxml" else std_Element("ude")
        )
        elem.attrib = self.make_attrib_dict()
        for map_ in self.maps:
            if map_.code and not self.base:
                raise AttributeError(
                    "attribute base is required since at least one of the Map elements has a code attribute."
                )
            elem.append(map_.make_element())
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.name:
            attrs["name"] = self.name
        if self.base:
            attrs["base"] = self.base
        return attrs


class Header:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
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
                raise IncorrectTagError(xml_element.tag, "header")
            self.creationtool = (
                creationtool if creationtool else xml_element.get("creationtool")
            )
            self.creationtoolversion = (
                creationtoolversion
                if creationtoolversion
                else xml_element.get("creationtoolversion")
            )
            self.segtype = segtype if segtype else xml_element.get("segtype")
            self.o_tmf = o_tmf if o_tmf else xml_element.get("o-tmf")
            self.adminlang = adminlang if adminlang else xml_element.get("adminlang")
            self.srclang = srclang if srclang else xml_element.get("srclang")
            self.datatype = datatype if datatype else xml_element.get("datatype")
            self.o_encoding = (
                o_encoding if o_encoding else xml_element.get("o-encoding")
            )
            self.creationdate = (
                creationdate if creationdate else xml_element.get("creationdate")
            )
            self.creationid = (
                creationid if creationid else xml_element.get("creationid")
            )
            self.changedate = (
                changedate if changedate else xml_element.get("changedate")
            )
            self.changeid = changeid if changeid else xml_element.get("changeid")
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("header")
            if ElementType == "lxml"
            else std_Element("header")
        )
        elem.attrib = self.make_attrib_dict()
        elem.extend([ude.make_element(ElementType) for ude in self.udes])
        elem.extend([note.make_element(ElementType) for note in self.notes])
        elem.extend([prop.make_element(ElementType) for prop in self.props])
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.creationtool:
            attrs["creationtool"] = self.creationtool
        else:
            raise AttributeError("Required attribute creationtool is missing")
        if self.creationtoolversion:
            attrs["creationtoolversion"] = self.creationtoolversion
        else:
            raise AttributeError("Required attribute creationtoolversion is missing")
        if self.segtype in ("block", "paragraph", "sentence", "phrase"):
            attrs["segtype"] = self.segtype
        else:
            raise AttributeError(
                "Requried attribute segtype must be one of block, paragraph, sentence or phrase"
            )
        if self.adminlang:
            attrs["adminlang"] = self.adminlang
        else:
            raise AttributeError("Required attribute adminlang is missing")
        if self.srclang:
            attrs["srclang"] = self.srclang
        else:
            raise AttributeError("Required attribute srclang is missing")
        if self.datatype:
            attrs["datatype"] = self.datatype
        else:
            raise AttributeError("Required attribute datatype is missing")
        if self.changeid:
            attrs["changeid"] = self.changeid
        if self.creationid:
            attrs["creationid"] = self.creationid
        if self.o_encoding:
            attrs["o-encoding"] = self.o_encoding
        if self.creationdate:
            try:
                attrs["creationdate"] = self.creationdate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.creationdate):
                        warn(
                            "value for creationdate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["creationdate"] = self.creationdate
                except TypeError:
                    pass
        if self.creationid:
            attrs["creationid"] = self.creationid
        if self.changedate:
            try:
                attrs["changedate"] = self.changedate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.changedate):
                        warn(
                            "value for changedate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["changedate"] = self.changedate
                except TypeError:
                    pass
        if self.changeid:
            attrs["changeid"] = self.changeid
        return attrs


class Seg:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = [],
    ) -> None:
        if xml_element is None:
            self.content = content
        else:
            if xml_element.tag != "seg":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="seg"
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
                                found_element=child.tag,
                            )

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("seg") if ElementType == "lxml" else std_Element("seg")
        )
        if self.content:
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if elem.text is None:
                        elem.text = child
                    case str() if not len(elem):
                        elem.text += child
                    case str():
                        elem[-1].tail = child
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        elem.append(child.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="bpt, ept, ph, hi or it",
                            found_element=child,
                        )
        return elem


class Tuv:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
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
            self.lang = (
                lang
                if lang
                else xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
            )
            self.o_encoding = (
                o_encoding if o_encoding else xml_element.get("o-encoding")
            )
            self.datatype = datatype if datatype else xml_element.get("datatype")
            self.usagecount = (
                usagecount if usagecount else xml_element.get("usagecount")
            )
            self.lastusagedate = (
                lastusagedate if lastusagedate else xml_element.get("lastusagedate")
            )
            self.creationtool = (
                creationtool if creationtool else xml_element.get("creationtool")
            )
            self.creationtoolversion = (
                creationtoolversion
                if creationtoolversion
                else xml_element.get("creationtoolversion")
            )
            self.creationdate = (
                creationdate if creationdate else xml_element.get("creationdate")
            )
            self.creationid = (
                creationid if creationid else xml_element.get("creationid")
            )
            self.changedate = (
                changedate if changedate else xml_element.get("changedate")
            )
            self.changeid = changeid if changeid else xml_element.get("changeid")
            self.o_tmf = o_tmf if o_tmf else xml_element.get("o-tmf")
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("tuv") if ElementType == "lxml" else std_Element("tuv")
        )
        elem.attrib = self.make_attrib_dict()
        elem.extend([note.export(ElementType) for note in self.notes])
        elem.extend([prop.export(ElementType) for prop in self.props])
        elem.append(self.segment.make_element(ElementType))
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.lang:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
        else:
            raise AttributeError("Required attribute lang is missing")
        if self.o_encoding:
            attrs["o-encoding"] = self.o_encoding
        if self.datatype:
            attrs["datatype"] = self.datatype
        if self.usagecount:
            attrs["usagecount"] = str(self.usagecount)
        if self.lastusagedate:
            try:
                attrs["lastusagedate"] = self.lastusagedate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.lastusagedate):
                        warn(
                            "value for lastusagedate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["lastusagedate"] = self.lastusagedate
                except TypeError:
                    pass
        if self.creationtool:
            attrs["creationtool"] = self.creationtool
        if self.creationtoolversion:
            attrs["creationtoolversion"] = self.creationtoolversion
        if self.creationdate:
            try:
                attrs["creationdate"] = self.creationdate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.creationdate):
                        warn(
                            "value for creationdate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["creationdate"] = self.creationdate
                except TypeError:
                    pass
        if self.creationid:
            attrs["creationid"] = self.creationid
        if self.changedate:
            try:
                attrs["changedate"] = self.changedate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.changedate):
                        warn(
                            "value for changedate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["changedate"] = self.changedate
                except TypeError:
                    pass
        if self.changeid:
            attrs["changeid"] = self.changeid
        if self.o_tmf:
            attrs["o-tmf"] = self.o_tmf
        return attrs


class Tu:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
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
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        changeid: str | None = None,
        o_tmf: str | None = None,
        srclang: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "tu":
                raise IncorrectTagError(xml_element, "tu")
            self.tuid = tuid if tuid else xml_element.get("tuid")
            self.o_encoding = (
                o_encoding if o_encoding else xml_element.get("o-encoding")
            )
            self.datatype = datatype if datatype else xml_element.get("datatype")
            self.usagecount = (
                usagecount if usagecount else xml_element.get("usagecount")
            )
            self.lastusagedate = (
                lastusagedate if lastusagedate else xml_element.get("lastusagedate")
            )
            self.creationtool = (
                creationtool if creationtool else xml_element.get("creationtool")
            )
            self.creationtoolversion = (
                creationtoolversion
                if creationtoolversion
                else xml_element.get("creationtoolversion")
            )
            self.creationdate = (
                creationdate if creationdate else xml_element.get("creationdate")
            )
            self.creationid = (
                creationid if creationid else xml_element.get("creationid")
            )
            self.changedate = (
                changedate if changedate else xml_element.get("changedate")
            )
            self.changeid = changeid if changeid else xml_element.get("changeid")
            self.segtype = segtype if segtype else xml_element.get("segtype")
            self.o_tmf = o_tmf if o_tmf else xml_element.get("o-tmf")
            self.srclang = srclang if srclang else xml_element.get("srclang")
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("tu") if ElementType == "lxml" else std_Element("tu")
        )
        elem.attrib = self.make_attrib_dict()
        elem.extend([note.export(ElementType) for note in self.notes])
        elem.extend([prop.export(ElementType) for prop in self.props])
        elem.extend([tuv.export(ElementType) for tuv in self.tuvs])
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.tuid:
            attrs["tuid"] = str(self.tuid)
        if self.o_encoding:
            attrs["o-encoding"] = self.o_encoding
        if self.datatype:
            attrs["datatype"] = self.datatype
        if self.usagecount:
            attrs["usagecount"] = str(self.usagecount)
        if self.lastusagedate:
            try:
                attrs["lastusagedate"] = self.lastusagedate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.lastusagedate):
                        warn(
                            "value for lastusagedate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["lastusagedate"] = self.lastusagedate
                except TypeError:
                    pass
        if self.creationtool:
            attrs["creationtool"] = self.creationtool
        if self.creationtoolversion:
            attrs["creationtoolversion"] = self.creationtoolversion
        if self.creationdate:
            try:
                attrs["creationdate"] = self.creationdate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.creationdate):
                        warn(
                            "value for creationdate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["creationdate"] = self.creationdate
                except TypeError:
                    pass
        if self.creationid:
            attrs["creationid"] = self.creationid
        if self.changedate:
            try:
                attrs["changedate"] = self.changedate.strftime(r"%Y%m%dT%H%M%SZ")
            except TypeError:
                try:
                    if not match("^\d{8}T\d{6}Z$", self.changedate):
                        warn(
                            "value for changedate doesn't match the format YYYYMMDDTHHMMSSZ, CAT Tools might not be able to parse its value."
                        )
                    attrs["changedate"] = self.changedate
                except TypeError:
                    pass
        if self.segtype in ("block", "paragraph", "sentence", "phrase"):
            attrs["segtype"] = self.segtype
        if self.changeid:
            attrs["changeid"] = self.changeid
        if self.o_tmf:
            attrs["o-tmf"] = self.o_tmf
        if self.srclang:
            attrs["srclang"] = self.srclang
        return attrs


class Tmx:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("tmx", {"version": "1.4"})
            if ElementType == "lxml"
            else std_Element("tmx", {"version": "1.4"})
        )
        body = (
            lxml_Element_Factory("body")
            if ElementType == "lxml"
            else std_Element("body")
        )
        body.extend([tu.export(ElementType) for tu in self.tus])
        elem.append(body)
        return elem
