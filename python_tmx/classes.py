from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Iterable, Literal
from xml.etree.ElementTree import Element

from .errors import InccorectTagError, NonEmptyTagError


class TmxTag(ABC):
    def export(self) -> Element:
        raise NotImplementedError


class Sub(TmxTag):
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
                        f"Expected <sub> but found <{xml_element.tag}>"
                    )
                elif len(xml_element) == 0:
                    self.content = content if content is not None else xml_element.text
                else:
                    self.content = (
                        [xml_element.text] if xml_element.text is not None else []
                    )
                    for child in xml_element:
                        if child.tag not in [
                            "bpt",
                            "ept",
                            "it",
                            "ph",
                            "hi",
                        ]:
                            raise InccorectTagError(
                                f"Expected one of <bpt>, <ept>, <it>, <ph>, <hi> but found <{child.tag}>"
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
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
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


class Ut(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | Iterable[str | Sub] | None = None,
        x: int | str | None = None,
    ) -> None:
        """
        The Ut class constructor(TmxTag). Can be created from parsing a <ut> xml Element.
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
                        f"Expected <ut> but found <{xml_element.tag}>"
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
                                f"Expected <sub> but found <{child.tag}>"
                            )
                        self.content.append(Sub(xml_element=child))
                        self.content.append(child.tail)
                self.x = xml_element.get("x") if x is None else x
            case None:
                self.content = content
                self.x = x
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
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


class Note(TmxTag):
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


class Prop(TmxTag):
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


class Map(TmxTag):
    def __init__(
        self,
        xml_element: Element | None,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "map":
                    raise InccorectTagError(
                        f"expected <map> but found <{xml_element.tag}>"
                    )
                if xml_element.text is not None:
                    raise NonEmptyTagError(
                        f"<map> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                if len(xml_element) != 0:
                    raise NonEmptyTagError(
                        f"<map> tags are not allowed to have children but found {len(xml_element)}"
                    )
                self.unicode = (
                    unicode if unicode is not None else xml_element.get("unicode")
                )
                self.code = code if code is not None else xml_element.get("code")
                self.ent = ent if ent is not None else xml_element.get("ent")
                self.subst = subst if subst is not None else xml_element.get("subst")
            case None:
                self.unicode = unicode
                self.code = code
                self.ent = ent
                self.subst = subst

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


class Ude(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        maps: Iterable[Map] | None = None,
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "ude":
                    raise InccorectTagError(
                        f"Expected <ude> but found <{xml_element.tag}>"
                    )
                if xml_element.text is not None:
                    raise NonEmptyTagError(
                        f"<ude> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                self.name = name if name is not None else xml_element.get("name")
                self.base = base if base is not None else xml_element.get("base")

            case None:
                self.maps = maps
                self.name = name
                self.base = base
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        final = Element("ude")
        if self.name:
            final.set("name", self.name)
        if self.base:
            final.set("code", self.base)
        for map in self.maps:
            final.append(map.export())
        return final


class Header(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
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
        match xml_element:
            case Element():
                if xml_element.tag != "header":
                    raise InccorectTagError(
                        f"Expected <header> but found <{xml_element.tag}>"
                    )
                if xml_element.text is not None:
                    raise NonEmptyTagError(
                        f"<header> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
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
                self.segtype = (
                    segtype if segtype is not None else xml_element.get("segtype")
                )
                self.o_tmf = o_tmf if o_tmf is not None else xml_element.get("o_tmf")
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
                    o_encoding
                    if o_encoding is not None
                    else xml_element.get("o-encoding")
                )
                self.creationdate = (
                    creationdate
                    if creationdate is not None
                    else xml_element.get("creationdate")
                )
                self.creationid = (
                    creationid
                    if creationid is not None
                    else xml_element.get("creationid")
                )
                self.changedate = (
                    changedate
                    if changedate is not None
                    else xml_element.get("changedate")
                )
                self.changeid = (
                    changeid if changeid is not None else xml_element.get("changeid")
                )
                if len(xml_element) == 0:
                    self.notes = notes
                    self.props = props
                    self.udes = udes
                else:
                    self.notes = []
                    self.props = []
                    self.udes = []
                    for child in xml_element:
                        match child.tag:
                            case "note" if notes is not None:
                                self.notes.append(Note(xml_element=child))
                            case "prop" if props is not None:
                                self.props.append(Prop(xml_element=child))
                            case "ude" if udes is not None:
                                self.udes.append(Ude(xml_element=child))
                            case _:
                                raise InccorectTagError(
                                    f"expected one of note, prop, ude but found {child.tag}"
                                )
            case None:
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
                self.notes = notes
                self.props = props
                self.udes = udes
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
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
        if self.notes is not None:
            for note in self.notes:
                final.append(note.export())
        if self.props is not None:
            for prop in self.props:
                final.append(prop.export())
        if self.udes is not None:
            for ude in self.udes:
                final.append(ude.export())
        return final
