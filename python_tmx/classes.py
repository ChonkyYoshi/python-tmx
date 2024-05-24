from __future__ import annotations
from datetime import datetime
from typing import Iterable, Literal
from xml.etree.ElementTree import Element


class ph:
    def __init__(
        self,
        content: str | Iterable[str | sub],
        x: int | None = None,
        type_: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        self.content = content
        self.x = x
        self.type_ = type_
        self.assoc = assoc


class bpt:
    def __init__(
        self,
        content: str | Iterable[str | sub],
        i: int,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.i = i
        self.x = x
        self.type_ = type_


class ept:
    def __init__(
        self,
        content: str | Iterable[str | sub],
        i: int,
    ) -> None:
        self.content = content
        self.i = i


class it:
    def __init__(
        self,
        content: str | Iterable[str | sub],
        pos: Literal["begin", "end"],
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.pos = pos
        self.x = x
        self.type_ = type_


class hi:
    def __init__(
        self,
        content: str | Iterable[str | ph | bpt | ept | it | hi],
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.x = x
        self.type_ = type_


class sub:
    def __init__(
        self,
        content: str | Iterable[str | ph | bpt | ept | it | hi],
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.datatype = datatype
        self.type_ = type_


class ut:
    def __init__(
        self,
        content: str | Iterable[str | sub],
        x: int | None = None,
    ) -> None:
        self.content = content
        self.x = x


class seg:
    def __init__(
        self,
        content: str | Iterable[str | ph | bpt | ept | it | hi],
    ) -> None:
        self.content = content


class note:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.content = content if content is not None else self.xml_element.text
        self.lang = (
            lang
            if lang is not None
            else self.xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.o_encoding = (
            o_encoding if o_encoding is not None else self.xml_element.get("o-encoding")
        )


class prop:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.content = content if content is not None else self.xml_element.text
        self.type_ = type_ if type_ is not None else self.xml_element.get("type")
        self.lang = (
            lang
            if lang is not None
            else self.xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.o_encoding = (
            o_encoding if o_encoding is not None else self.xml_element.get("o-encoding")
        )


class map:
    def __init__(
        self,
        xml_element: Element | None = None,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.unicode = (
            unicode if unicode is not None else self.xml_element.get("unicode")
        )
        self.code = code if code is not None else self.xml_element.get("code")
        self.ent = ent if ent is not None else self.xml_element.get("ent")
        self.subst = subst if subst is not None else self.xml_element.get("subst")


class ude:
    def __init__(
        self,
        xml_element: Element | None = None,
        maps: Iterable[map] | None = None,
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        self.xml_element = xml_element
        if len(self.xml_element) == 0:
            self.maps = maps
        else:
            self.maps = [map(map_) for map_ in self.xml_element.iterfind("map")]
        self.name = name if name is not None else self.xml_element.get("name")
        self.base = base if base is not None else self.xml_element.get("base")


class tuv:
    def __init__(
        self,
        segment: seg,
        lang: str,
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
        notes: Iterable[note] | None = None,
        props: Iterable[prop] | None = None,
    ) -> None:
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
        self.notes = notes
        self.props = props


class tu:
    def __init__(
        self,
        xml_element: Element | None = None,
        tuvs: Iterable[tuv] | None = None,
        tuid: int | str | None = None,
        o_encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | str | None = None,
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
        notes: Iterable[note] | None = None,
        props: Iterable[prop] | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.tuid = tuid if tuid is not None else self.xml_element.get("tuid")
        self.o_encoding = (
            o_encoding if o_encoding is not None else self.xml_element.get("o_encoding")
        )
        self.datatype = (
            datatype if datatype is not None else self.xml_element.get("datatype")
        )
        self.usagecount = (
            usagecount if usagecount is not None else self.xml_element.get("usagecount")
        )
        self.lastusagedate = (
            lastusagedate
            if lastusagedate is not None
            else self.xml_element.get("lastusagedate")
        )
        self.creationtool = (
            creationtool
            if creationtool is not None
            else self.xml_element.get("creationtool")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else self.xml_element.get("creationtoolversion")
        )
        self.creationdate = (
            creationdate
            if creationdate is not None
            else self.xml_element.get("creationdate")
        )
        self.creationid = (
            creationid if creationid is not None else self.xml_element.get("creationid")
        )
        self.changedate = (
            changedate if changedate is not None else self.xml_element.get("changedate")
        )
        self.segtype = (
            segtype if segtype is not None else self.xml_element.get("segtype")
        )
        self.changeid = (
            changeid if changeid is not None else self.xml_element.get("changeid")
        )
        self.o_tmf = o_tmf if o_tmf is not None else self.xml_element.get("o_tmf")
        self.srclang = (
            srclang if srclang is not None else self.xml_element.get("srclang")
        )
        if len(self.xml_element) == 0:
            self.notes = notes
            self.props = props
        else:
            self.notes = [
                note(note_) for note_ in self.xml_element if note_.tag == "note"
            ]
            self.props = [
                prop(prop_) for prop_ in self.xml_element if prop_.tag == "prop"
            ]


class header:
    def __init__(
        self,
        xml_element: Element | None | None = None,
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
        notes: Iterable[note] | None = None,
        props: Iterable[prop] | None = None,
        udes: Iterable[ude] | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.creationtool = (
            creationtool
            if creationtool is not None
            else self.xml_element.get("creationtool")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else self.xml_element.get("creationtoolversion")
        )
        self.segtype = (
            segtype if segtype is not None else self.xml_element.get("segtype")
        )
        self.o_tmf = o_tmf if o_tmf is not None else self.xml_element.get("o_tmf")
        self.adminlang = (
            adminlang if adminlang is not None else self.xml_element.get("adminlang")
        )
        self.srclang = (
            srclang if srclang is not None else self.xml_element.get("srclang")
        )
        self.datatype = (
            datatype if datatype is not None else self.xml_element.get("datatype")
        )
        self.o_encoding = (
            o_encoding if o_encoding is not None else self.xml_element.get("o_encoding")
        )
        self.creationdate = (
            creationdate
            if creationdate is not None
            else self.xml_element.get("creationdate")
        )
        self.creationid = (
            creationid if creationid is not None else self.xml_element.get("creationid")
        )
        self.changedate = (
            changedate if changedate is not None else self.xml_element.get("changedate")
        )
        self.changeid = (
            changeid if changeid is not None else self.xml_element.get("changeid")
        )
        if len(self.xml_element) == 0:
            self.notes = notes
            self.props = props
            self.udes = udes
        else:
            self.notes = [
                note(note_) for note_ in self.xml_element if note_.tag == "note"
            ]
            self.props = [
                prop(prop_) for prop_ in self.xml_element if prop_.tag == "prop"
            ]
            self.udes = [ude(ude_) for ude_ in self.xml_element if ude_.tag == "ude"]


class tmx:
    def __init__(self, header_: header, tus: Iterable[tu]) -> None:
        self.header_ = header_
        self.tus = tus
