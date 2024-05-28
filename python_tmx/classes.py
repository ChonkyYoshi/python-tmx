from __future__ import annotations

from datetime import datetime
from typing import Iterable, Literal
from xml.etree.ElementTree import Element, parse, tostring

from errors import InccorectTagError


class Sub:
    def __init__(
        self,
        xml_element: Element | None = Element("sub"),
        content: str | Iterable[str | Sub] | None = None,
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "sub":
                    raise InccorectTagError(
                        f"Element is not a <sub> but <{xml_element.tag}>.",
                        element=xml_element,
                    )
                elif len(xml_element) == 0:
                    self.content = content if content is not None else xml_element.text
                else:
                    self.content = (
                        [xml_element.text] if xml_element.text is not None else []
                    )
                    for child in xml_element:
                        if child.tag not in ["bpt", "ept", "it", "ph", "hi", "sub"]:
                            raise InccorectTagError(
                                f"Encountered a <{child.tag}> element inside a <sub> element. <ut> elements can only contain <sub> elements.",
                                element=child,
                            )
                        self.content.append(Sub(xml_element=child))
                        self.content.append(child.tail)
                self.datatype = (
                    xml_element.get("datatype") if datatype is None else datatype
                )
                self.type_ = xml_element.get("type") if type_ is None else type_
            case None:
                self.content = content
                self.datatype = datatype
                self.type_ = type_
            case _:
                raise TypeError(
                    f"xml_Element can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        final = Element("sub")
        if self.datatype:
            final.set("datatype", self.datatype)
        if self.type_:
            final.set("type", self.type_)
        final.text, final.tail = "", ""
        if isinstance(self.content, str):
            final.text = self.content
        else:
            for id, element in enumerate(self.content):
                if isinstance(element, str):
                    if id == 0:
                        final.text = element
                    elif isinstance(self.content[id - 1], str):
                        final.text += element
                    else:
                        final[-1].tail += element
                elif isinstance(element, Sub):
                    final.append(element.export())
        return final


class Ut:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | Iterable[str | Sub] | None = None,
        x: int | str | None = None,
    ) -> None:
        """
        The Ut class constructor. Can be created from parsing a <ut> xml Element.
        if `content` and/or `x` are passed to the constructor, their value will override
        the values parsed from `xml_element`

        Args:
            xml_element (Element | None, optional):
            An Element object to convert to a Ut object. Defaults to None.

            content (str | Iterable[str  |  Sub] | None, optional):
            The contents of the element. Defaults to None.

            x (int | None, optional):
            Used to match inline elements between <tuv> in the same tu. Defaults to None.

        Raises:
            TagError: if `xml_element` is not a <ut> or if any child element is not a <sub>
            TypeError: if any of the arguments are of the wrong type
        """
        match xml_element:
            case Element():
                if xml_element.tag != "ut":
                    raise InccorectTagError(
                        f"Element is not a <ut> but <{xml_element.tag}>.",
                        element=xml_element,
                    )
                elif len(xml_element) == 0:
                    self.content = xml_element.text if content is None else content
                else:
                    self.content = (
                        [xml_element.text] if xml_element.text is not None else []
                    )
                    for child in xml_element:
                        if child.tag != "sub":
                            raise InccorectTagError(
                                f"Encountered a <{child.tag}> element inside a <ut> element. <ut> elements can only contain <sub> elements.",
                                element=child,
                            )
                        self.content.append(Sub(xml_element=child))
                        self.content.append(child.tail)
                self.x = xml_element.get("x") if x is None else x
            case None:
                self.content = content
                self.x = x
            case _:
                raise TypeError(
                    f"xml_Element can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        final = Element("ut")
        if self.x:
            final.set("x", self.x)
        final.text, final.tail = "", ""
        if isinstance(self.content, str):
            final.text = self.content
        else:
            for id, element in enumerate(self.content):
                if isinstance(element, str):
                    if id == 0:
                        final.text = element
                    elif isinstance(self.content[id - 1], str):
                        final.text += element
                    else:
                        final[-1].tail += element
                elif isinstance(element, Sub):
                    final.append(element.export())
        return final


class Note:
    def __init__(
        self,
        xml_element: Element | None,
        text: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
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
        final = Element("note")
        final.text = self.text
        if self.lang:
            final.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
        if self.o_encoding:
            final.set("o-encoding", self.o_encoding)
        return final


class Prop:
    def __init__(
        self,
        xml_element: Element | None = None,
        text: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
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
        final = Element("prop")
        final.text = self.text
        if self.lang:
            final.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
        if self.type_:
            final.set("type", self.type_)
        if self.o_encoding:
            final.set("o-encoding", self.o_encoding)
        return final


class Map:
    def __init__(
        self,
        xml_element: Element | None,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        self.unicode = unicode if unicode is not None else xml_element.get("unicode")
        self.code = code if code is not None else xml_element.get("code")
        self.ent = ent if ent is not None else xml_element.get("ent")
        self.subst = subst if subst is not None else xml_element.get("subst")

    def export(self) -> Element:
        final = Element("map")
        if self.unicode:
            final.set("unicode", self.unicode)
        if self.code:
            final.set("code", self.code)
        if self.ent:
            final.set("ent", self.ent)
        if self.subst:
            final.set("subst", self.subst)
        return final


class Ude:
    def __init__(
        self,
        xml_element: Element | None = None,
        maps: Iterable[Map] | None = None,
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        self.maps = (
            maps
            if maps is not None
            else (
                [Map(map) for map in xml_element if map.tag == "map"]
                if xml_element is not None
                else None
            )
        )
        self.name = name if name is not None else xml_element.get("name")
        self.base = base if base is not None else xml_element.get("base")

    def export(self) -> Element:
        final = Element("ude")
        if self.name:
            final.set("name", self.name)
        if self.base:
            final.set("code", self.base)
        for map in self.maps:
            final.append(map.export())
        return final


class Header:
    def __init__(
        self,
        xml_element: Element | None | None = Element("header"),
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
        self.creationtool = (
            creationtool
            if creationtool is not None
            else xml_element.get("creationtool")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else xml_element.get("creationtoolversion")
        )
        self.segtype = segtype if segtype is not None else xml_element.get("segtype")
        self.o_tmf = o_tmf if o_tmf is not None else xml_element.get("o_tmf")
        self.adminlang = (
            adminlang if adminlang is not None else xml_element.get("adminlang")
        )
        self.srclang = srclang if srclang is not None else xml_element.get("srclang")
        self.datatype = (
            datatype if datatype is not None else xml_element.get("datatype")
        )
        self.o_encoding = (
            o_encoding if o_encoding is not None else xml_element.get("o-encoding")
        )
        self.creationdate = (
            creationdate
            if creationdate is not None
            else xml_element.get("creationdate")
        )
        self.creationid = (
            creationid if creationid is not None else xml_element.get("creationid")
        )
        self.changedate = (
            changedate if changedate is not None else xml_element.get("changedate")
        )
        self.changeid = (
            changeid if changeid is not None else xml_element.get("changeid")
        )
        self.notes = (
            notes
            if notes is not None
            else (
                [Note(note) for note in xml_element if note.tag == "note"]
                if xml_element is not None
                else None
            )
        )
        self.props = (
            props
            if props is not None
            else (
                [Prop(prop) for prop in xml_element if prop.tag == "prop"]
                if xml_element is not None
                else None
            )
        )
        self.udes = (
            udes
            if udes is not None
            else (
                [Ude(ude) for ude in xml_element if ude.tag == "ude"]
                if xml_element is not None
                else None
            )
        )

    def export(self) -> Element:
        final = Element("header")
        if self.creationtool:
            final.set("creationtool", self.creationtool)
        if self.creationtoolversion:
            final.set("creationtoolversion", self.creationtoolversion)
        if self.segtype:
            final.set("segtype", self.segtype)
        if self.o_tmf:
            final.set("o-tmf", self.o_tmf)
        if self.adminlang:
            final.set("adminlang", self.adminlang)
        if self.srclang:
            final.set("srclang", self.srclang)
        if self.datatype:
            final.set("datatype", self.datatype)
        if self.o_encoding:
            final.set("o-encoding", self.o_encoding)
        if self.creationdate:
            final.set("creationdate", self.creationdate)
        if self.creationid:
            final.set("creationid", self.creationid)
        if self.changedate:
            final.set("changedate", self.changedate)
        if self.changeid:
            final.set("changeid", self.changeid)
        for note in self.notes:
            final.append(note.export())
        for prop in self.props:
            final.append(prop.export())
        for ude in self.udes:
            final.append(ude.export())
        return final


a = Header(xml_element=parse("a.tmx").getroot())
print(tostring(a.export()))
