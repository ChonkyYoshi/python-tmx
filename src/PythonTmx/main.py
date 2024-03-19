from datetime import UTC, datetime
from os import PathLike
from typing import Iterable
from xml.etree.ElementTree import Element, ElementTree, parse

from classes import Bpt, Ept, Header, InlineElement, Note, Ph, Prop, Tmx, Tu, Tuv


def ParseProps(element: Element) -> list[Prop]:
    return [
        Prop(
            text=_prop.text,
            _type=_prop.get("type"),
            lang=_prop.get("{http://www.w3.org/XML/1998/namespace}lang"),
            encoding=_prop.get("o-encoding"),
        )
        for _prop in element.findall("prop")
    ]


def ParseNotes(element: Element) -> list[Note]:
    return [
        Note(
            text=_note.text,
            lang=_note.get("{http://www.w3.org/XML/1998/namespace}lang"),
            encoding=_note.get("o-encoding"),
        )
        for _note in element.findall("note")
    ]


def ParseHeader(header_element: Element) -> Header:
    header: Header = Header(
        creationtool=header_element.get("creationtool"),
        creationtoolversion=header_element.get("creationtoolversion"),
        segtype=header_element.get("segtype"),
        tmf=header_element.get("o-tmf"),
        adminlang=header_element.get("adminlang"),
        srclang=header_element.get("srclang"),
        datatype=header_element.get("datatype"),
        encoding=header_element.get("o-encoding"),
        creationdate=datetime.strptime(
            header_element.get("creationdate"), "%Y%m%dT%H%M%SZ"
        ).replace(tzinfo=UTC)
        if header_element.get("creationdate") is not None
        else None,
        creationid=header_element.get("creationid"),
        changedate=datetime.strptime(
            header_element.get("changedate"), "%Y%m%dT%H%M%SZ"
        ).replace(tzinfo=UTC)
        if header_element.get("changedate") is not None
        else None,
        changeid=header_element.get("changeid"),
        notes=ParseNotes(header_element),
        props=ParseProps(header_element),
    )
    return header


def ParseSeg(element: Element):
    for seg in element.iter():
        runs: Iterable[str | InlineElement] = list()
        for _tag in seg.iter():
            match _tag.tag:
                case "seg":
                    runs.append(_tag.text)
                case "ph":
                    runs.append(
                        Ph(
                            content=_tag.text,
                            x=_tag.get("x"),
                            _type=_tag.get("type"),
                            assoc=_tag.get("assoc"),
                        )
                    )
                    runs.append(_tag.tail)
                case "bpt":
                    runs.append(
                        Bpt(
                            content=_tag.text,
                            i=int(_tag.get("i")),
                            x=int(_tag.get("x")) if _tag.get("x") is not None else None,
                            _type=_tag.get("type"),
                        )
                    )
                    runs.append(_tag.tail)
                case "ept":
                    runs.append(
                        Ept(
                            content=_tag.text,
                            i=int(_tag.get("i")),
                        )
                    )
                    runs.append(_tag.tail)
        return [run for run in runs if run is not None]


def ParseTmx(file: PathLike) -> Tmx:
    tmx_tree: ElementTree = parse(file)
    tmx_root: Element = tmx_tree.getroot()
    header: Header = ParseHeader(tmx_root.find("header"))
    tmx: Tmx = Tmx(header=header, tus=list())
    for _tu in tmx_root.iter("tu"):
        tu: Tu = Tu(
            tuvs=list(),
            tuid=int(_tu.get("tuid")) if _tu.get("tuid") is not None else None,
            encoding=_tu.get("o-encoding"),
            datatype=_tu.get("datatype"),
            usagecount=_tu.get("usagecount"),
            lastusagedate=_tu.get("lastusagedate"),
            creationtool=_tu.get("creationtool"),
            creationtoolversion=_tu.get("creationtoolversion"),
            creationdate=datetime.strptime(
                _tu.get("creationdate"), "%Y%m%dT%H%M%SZ"
            ).replace(tzinfo=UTC)
            if _tu.get("creationdate") is not None
            else None,
            creationid=_tu.get("creationid"),
            changedate=datetime.strptime(
                _tu.get("changedate"), "%Y%m%dT%H%M%SZ"
            ).replace(tzinfo=UTC)
            if _tu.get("changedate") is not None
            else None,
            segtype=_tu.get("segtype"),
            changeid=_tu.get("changeid"),
            tmf=_tu.get("o-tmf"),
            srclang=_tu.get("srclang"),
            notes=ParseNotes(_tu),
            props=ParseProps(_tu),
        )
        for _tuv in _tu.iter("tuv"):
            tu.tuvs.append(
                Tuv(
                    content=ParseSeg(_tuv.find("seg")),
                    lang=_tuv.get("{http://www.w3.org/XML/1998/namespace}lang"),
                    datatype=_tuv.get("datatype"),
                    usagecount=_tuv.get("usagecount"),
                    lastusagedate=_tuv.get("lastusagedate"),
                    creationtool=_tuv.get("creationtool"),
                    creationtoolversion=_tuv.get("creationtoolversion"),
                    creationdate=datetime.strptime(
                        _tuv.get("creationdate"), "%Y%m%dT%H%M%SZ"
                    ).replace(tzinfo=UTC)
                    if _tuv.get("creationdate") is not None
                    else None,
                    creationid=_tuv.get("creationid"),
                    changedate=datetime.strptime(
                        _tuv.get("changedate"), "%Y%m%dT%H%M%SZ"
                    ).replace(tzinfo=UTC)
                    if _tuv.get("changedate") is not None
                    else None,
                    changeid=_tuv.get("changeid"),
                    tmf=_tuv.get("o-tmf"),
                    notes=ParseNotes(_tuv),
                    props=ParseProps(_tuv),
                )
            )
        tmx.tus.append(tu)
    return tmx


a = ParseTmx("example.tmx")
a.Dump("a.tmx")
