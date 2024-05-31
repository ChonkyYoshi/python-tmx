from __future__ import annotations

from abc import ABC
from datetime import datetime
from re import MULTILINE, match
from typing import Iterable, Literal
from xml.etree.ElementTree import Element, tostring

from errors import InccorectTagError, MissingRequiredAttributeError, NonEmptyTagError


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
        match xml_element:
            case Element():
                if xml_element.tag != "note":
                    raise InccorectTagError(
                        f"expected <note> but found <{xml_element.tag}>"
                    )
                if len(xml_element) != 0:
                    raise NonEmptyTagError(
                        f"<note> tags are not allowed to have children but found {len(xml_element)}"
                    )
                self.text = text if text is not None else xml_element.text
                self.lang = (
                    lang
                    if lang is not None
                    else xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
                )
                self.o_encoding = (
                    o_encoding
                    if o_encoding is not None
                    else xml_element.get("o-encoding")
                )
            case None:
                self.text = text
                self.lang = lang
                self.o_encoding = o_encoding
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        final = Element("note")
        for attr, val in vars(self).items():
            match attr:
                case "content":
                    final.text = val
                case "lang" if val is not None:
                    final.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
                case "o_encoding" if val is not None:
                    final.set("o-encoding", self.o_encoding)
        tostring(final)
        return final


class Prop(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        content: str | None = None,
        type_: str | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "prop":
                    raise InccorectTagError(
                        f"expected <prop> but found <{xml_element.tag}>"
                    )
                self.content = content if content is not None else xml_element.text
                self.lang = (
                    lang
                    if lang is not None
                    else xml_element.get("{http://www.w3.org/XML/1998/namespace}lang")
                )
                self.type_ = type_ if type_ is not None else xml_element.get("type")
                self.o_encoding = (
                    o_encoding
                    if o_encoding is not None
                    else xml_element.get("o-encoding")
                )
            case None:
                self.content = content
                self.type_ = type_
                self.lang = lang
                self.o_encoding = o_encoding
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        final = Element("prop")
        for attr, val in vars(self).items():
            match attr:
                case "content":
                    final.text = val
                case "type_":
                    if val is None:
                        raise MissingRequiredAttributeError(
                            "required attribute `type_` is missing from prop object"
                        )
                    final.set("type", val)
                case "lang" if val is not None:
                    final.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
                case "o_encoding" if val is not None:
                    final.set("o-encoding", self.o_encoding)
        tostring(final)
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
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        final = Element("map")
        if self.unicode is None:
            raise MissingRequiredAttributeError(
                "required attribute `unicode` is missing from map object"
            )
        final.set("unicode", self.unicode)
        if self.code is not None:
            final.set("code", self.code)
        if self.ent is not None:
            final.set("ent", self.ent)
        if self.subst is not None:
            final.set("subst", self.subst)
        tostring(final)
        return final


class Ude(TmxTag):
    def __init__(
        self,
        xml_element: Element | None = None,
        maps: Iterable[Map] | None = [],
        name: str | None = None,
        base: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "ude":
                    raise InccorectTagError(
                        f"Expected <ude> but found <{xml_element.tag}>"
                    )
                if xml_element.text is not None and not match(
                    r"[\n\s]+", xml_element.text, flags=MULTILINE
                ):
                    raise NonEmptyTagError(
                        f"<ude> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                self.maps = maps if maps is not None else []
                if len(xml_element) != 0:
                    for child in xml_element:
                        if child.tag == "map":
                            self.maps.append(Map(xml_element=child))
                        else:
                            raise InccorectTagError(
                                f"expected a <map> but found a <{child.tag}"
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
        base_required = False
        if self.name is None:
            raise MissingRequiredAttributeError(
                "required attribute `name` is missing from ude object"
            )
        final.set("name", self.name)
        for map_ in self.maps:
            if map_.code is not None and not base_required:
                base_required = True
            final.append(map_.export())
        if base_required and self.base is None:
            raise MissingRequiredAttributeError(
                "required attribute `base` is missing from ude object because one or more of its `map` objects has a `code` attribute"
            )
        if self.base is not None:
            final.set("base", self.base)
        tostring(final)
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
                if xml_element.text is not None and not match(
                    r"^[\n\s]+$", xml_element.text, flags=MULTILINE
                ):
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
                    o_encoding
                    if o_encoding is not None
                    else xml_element.get("o-encoding")
                )
                self.creationdate = (
                    creationdate
                    if creationdate is not None
                    else datetime.strptime(
                        xml_element.get("creationdate"), r"%Y%m%dT%H%M%SZ"
                    )
                )
                self.creationid = (
                    creationid
                    if creationid is not None
                    else xml_element.get("creationid")
                )
                self.changedate = (
                    changedate
                    if changedate is not None
                    else datetime.strptime(
                        xml_element.get("changedate"), r"%Y%m%dT%H%M%SZ"
                    )
                )
                self.changeid = (
                    changeid if changeid is not None else xml_element.get("changeid")
                )
                self.notes = notes if notes is not None else []
                self.props = props if props is not None else []
                self.udes = udes if udes is not None else []
                if len(xml_element) != 0:
                    for child in xml_element:
                        match child.tag:
                            case "note" if notes is None:
                                self.notes.append(Note(xml_element=child))
                            case "prop" if props is None:
                                self.props.append(Prop(xml_element=child))
                            case "ude" if udes is None:
                                self.udes.append(Ude(xml_element=child))
                            case _:
                                raise InccorectTagError(
                                    f"expected one of note, prop, ude but found <{child.tag}>"
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
                self.notes = notes if notes else []
                self.props = props if props else []
                self.udes = udes if udes else []
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        final = Element("header")
        for attr in [
            "creationtool",
            "creationtoolversion",
            "segtype",
            "o_tmf",
            "adminlang",
            "srclang",
            "datatype",
            "o_encoding",
            "creationdate",
            "creationid",
            "changedate",
            "changeid",
        ]:
            val = self.__getattribute__(attr)
            match attr:
                case (
                    "creationtool"
                    | "creationtoolversion"
                    | "adminlang"
                    | "srclang"
                    | "datatype"
                    | "segtype"
                    | "o_tmf"
                ):
                    if val is None:
                        raise AttributeError(
                            f"required attribute `{attr}` is missing from header object"
                        )
                    if not isinstance(val, str):
                        raise TypeError(
                            f"attribute `{attr}` must be of type string not {type(val)}"
                        )
                    if attr == "segtype" and val.lower() not in [
                        "block",
                        "paragraph",
                        "sentence",
                        "phrase",
                    ]:
                        raise AttributeError(
                            f"`segtype` must be one of block, paragraph, sentence or phrase not {val}"
                        )
                    if attr == "o_tmf":
                        final.set("o-tmf", val)
                        continue
                    if attr == "o_encoding":
                        final.set("o-encoding", val)
                        continue
                    final.set(attr, val)
                case "creationdate" | "changedate" if val is not None:
                    if isinstance(val, datetime):
                        final.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                    elif isinstance(val, str):
                        if not match(r"^\d{8}T\d{6}Z$", val):
                            raise ValueError
                        final.set(attr, val)
                case "creationid" | "changeid" if val is not None:
                    final.set(attr, val)
            if self.notes is not None:
                final.extend([note.export() for note in self.notes])
            if self.props is not None:
                final.extend([prop.export() for prop in self.props])
            if self.udes is not None:
                final.extend([ude.export() for ude in self.udes])
        return final
