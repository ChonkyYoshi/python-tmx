from __future__ import annotations
from datetime import datetime
from typing import Iterable, Literal
from xml.etree.ElementTree import Element



class sub:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | Iterable[str] | None = None,
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.datatype = (
            datatype if datatype is not None else self.xml_element.get("datatype")
        )
        self.type_ = type_ if type_ is not None else self.xml_element.get("type")
        self.content = content if content is not None else self.xml_element.text


class ut:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | Iterable[str | sub] | None = None,
        x: int | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.x = x if x is not None else self.xml_element.get("x")


class seg:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | Iterable[str | ut | sub] | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.content = (
            content
            if content is not None
            else (self.xml_element.text if len(self.xml_element) == 0 else [].extend([]))
        )


class note:
    def __init__(
        self,
        xml_element: Element | None = None,
        text: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.text = text if text is not None else self.xml_element.text
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
        text: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        self.xml_element = xml_element
        self.text = text if text is not None else self.xml_element.text
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
        self.maps = (
            maps
            if maps is not None
            else (
                [map(map_) for map_ in self.xml_element if map_.tag == "map"]
                if self.xml_element is not None
                else None
            )
        )
        self.name = name if name is not None else self.xml_element.get("name")
        self.base = base if base is not None else self.xml_element.get("base")


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
        self.notes = (
            notes
            if notes is not None
            else (
                [note(note_) for note_ in self.xml_element if note_.tag == "note"]
                if self.xml_element is not None
                else None
            )
        )
        self.props = (
            props
            if props is not None
            else (
                [prop(prop_) for prop_ in self.xml_element if prop_.tag == "prop"]
                if self.xml_element is not None
                else None
            )
        )
        self.udes = (
            udes
            if udes is not None
            else (
                [ude(ude_) for ude_ in self.xml_element if ude_.tag == "ude"]
                if self.xml_element is not None
                else None
            )
        )
