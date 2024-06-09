from __future__ import annotations

from datetime import datetime
from re import MULTILINE, match
from typing import Iterable, Literal
from xml.etree.ElementTree import Element

from PythonTmx.errors import (
    ExtraChildrenError,
    ExtraTextError,
    IncorrectTagError,
    MissingRequiredAttributeError,
)


class Header:
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


class Prop:
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


class Note:
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
                element.append(map_.export())
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
            match key:
                case _ if val is None:
                    continue
                case _ if not isinstance(val, str):
                    raise TypeError(f"attribute {key} must be a string not {type(val)}")
                case _:
                    element.set(key, val)
        return element
