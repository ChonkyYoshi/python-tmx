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


def LoadHeader(header_element: Element) -> Header:
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


def LoadTmx(file: PathLike) -> Tmx:
    tmx_tree: ElementTree = parse(file)
    tmx_root: Element = tmx_tree.getroot()
    header: Header = LoadHeader(tmx_root.find("header"))
    tmx: Tmx = Tmx(header=header, tus=list())
    for tmx_tu in tmx_root.iter("tu"):
        tu: Tu = Tu(
            tuvs=list(),
            tuid=int(tmx_tu.get("tuid")) if tmx_tu.get("tuid") is not None else None,
            encoding=tmx_tu.get("o-encoding"),
            datatype=tmx_tu.get("datatype"),
            usagecount=tmx_tu.get("usagecount"),
            lastusagedate=tmx_tu.get("lastusagedate"),
            creationtool=tmx_tu.get("creationtool"),
            creationtoolversion=tmx_tu.get("creationtoolversion"),
            creationdate=datetime.strptime(
                tmx_tu.get("creationdate"), "%Y%m%dT%H%M%SZ"
            ).replace(tzinfo=UTC)
            if tmx_tu.get("creationdate") is not None
            else None,
            creationid=tmx_tu.get("creationid"),
            changedate=datetime.strptime(
                tmx_tu.get("changedate"), "%Y%m%dT%H%M%SZ"
            ).replace(tzinfo=UTC)
            if tmx_tu.get("changedate") is not None
            else None,
            segtype=tmx_tu.get("segtype"),
            changeid=tmx_tu.get("changeid"),
            tmf=tmx_tu.get("o-tmf"),
            srclang=tmx_tu.get("srclang"),
            notes=ParseNotes(tmx_tu),
            props=ParseProps(tmx_tu),
        )
        for tmx_tuv in tmx_tu.iter("tuv"):
            tu.tuvs.append(
                Tuv(
                    content=ParseSeg(tmx_tuv.find("seg")),
                    lang=tmx_tuv.get("{http://www.w3.org/XML/1998/namespace}lang"),
                    datatype=tmx_tuv.get("datatype"),
                    usagecount=tmx_tuv.get("usagecount"),
                    lastusagedate=tmx_tuv.get("lastusagedate"),
                    creationtool=tmx_tuv.get("creationtool"),
                    creationtoolversion=tmx_tuv.get("creationtoolversion"),
                    creationdate=datetime.strptime(
                        tmx_tuv.get("creationdate"), "%Y%m%dT%H%M%SZ"
                    ).replace(tzinfo=UTC)
                    if tmx_tuv.get("creationdate") is not None
                    else None,
                    creationid=tmx_tuv.get("creationid"),
                    changedate=datetime.strptime(
                        tmx_tuv.get("changedate"), "%Y%m%dT%H%M%SZ"
                    ).replace(tzinfo=UTC)
                    if tmx_tuv.get("changedate") is not None
                    else None,
                    changeid=tmx_tuv.get("changeid"),
                    tmf=tmx_tuv.get("o-tmf"),
                    notes=ParseNotes(tmx_tuv),
                    props=ParseProps(tmx_tuv),
                )
            )
        tmx.tus.append(tu)
    return tmx


a: Tmx = LoadTmx("example.tmx")
a.Dump("a.tmx")
