from . import *
from os import PathLike
from xml.etree.ElementTree import Element, ElementTree, XMLParser, parse


def load_note(note_elem: Element) -> note:
    return note(
        content=note_elem.text,
        lang=note_elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
        o_encoding=note_elem.get("o-encoding"),
    )


def load_prop(prop_elem: Element) -> note:
    return prop(
        content=prop_elem.text,
        type_=prop_elem.get("type"),
        lang=prop_elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
        o_encoding=prop_elem.get("o-encoding"),
    )


def load_map(map_elem: Element) -> map:
    return map(
        unicode=map_elem.get("unicode"),
        ent=map_elem.get("ent"),
        subst=map_elem.get("subst"),
        code=map_elem.get("code"),
    )


def load_ude(ude_elem: Element) -> ude:
    return ude(
        content=[load_map(_map) for _map in ude_elem.iterfind("map")],
        name=ude_elem.get("name"),
        base=ude_elem.get("base"),
    )


def load_header(header_elem: Element) -> header:
    return header(
        creationtool=header_elem.get("creationtool"),
        creationtoolversion=header_elem.get("creationtoolversion"),
        segtype=header_elem.get("segtype"),
        o_tmf=header_elem.get("o-tmf"),
        adminlang=header_elem.get("adminlang"),
        srclang=header_elem.get("srclang"),
        datatype=header_elem.get("datatype"),
        o_encoding=header_elem.get("o-encoding"),
        creationdate=header_elem.get("creationdate"),
        creationid=header_elem.get("creationid"),
        changedate=header_elem.get("changedate"),
        changeid=header_elem.get("changeid"),
        notes=[load_note(_note) for _note in header_elem.iterfind("note")],
        props=[load_prop(_prop) for _prop in header_elem.iterfind("prop")],
        udes=[load_ude(_ude) for _ude in header_elem.iterfind("ude")],
    )


def load_seg(seg_elem: Element) -> seg:
    return seg("")


def load_tuv(tuv_elem: Element) -> tuv:
    return tuv(
        segment=seg(load_seg(tuv_elem.find("seg"))),
        lang=tuv_elem.get("lang"),
        o_encoding=tuv_elem.get("o-encoding"),
        datatype=tuv_elem.get("datatype"),
        usagecount=tuv_elem.get("usagecount"),
        lastusagedate=tuv_elem.get("lastusagedate"),
        creationtool=tuv_elem.get("creationtool"),
        creationtoolversion=tuv_elem.get("creationtoolversion"),
        creationdate=tuv_elem.get("creationdate"),
        creationid=tuv_elem.get("creationid"),
        changedate=tuv_elem.get("changedate"),
        changeid=tuv_elem.get("changeid"),
        o_tmf=tuv_elem.get("o-tmf"),
        notes=[load_note(_note) for _note in tuv_elem.iterfind("note")],
        props=[load_prop(_prop) for _prop in tuv_elem.iterfind("prop")],
    )


def load_tu(tu_elem: Element) -> tu:
    return tu(
        tuvs=[load_tuv(_tuv) for _tuv in tu_elem.iterfind("tuv")],
        tuid=tu_elem.get("tuid"),
        o_encoding=tu_elem.get("o-encoding"),
        datatype=tu_elem.get("datatype"),
        usagecount=tu_elem.get("usagecount"),
        lastusagedate=tu_elem.get("lastusagedate"),
        creationtool=tu_elem.get("creationtool"),
        creationtoolversion=tu_elem.get("creationtoolversion"),
        creationdate=tu_elem.get("creationdate"),
        creationid=tu_elem.get("creationid"),
        changedate=tu_elem.get("changedate"),
        segtype=tu_elem.get("segtype"),
        changeid=tu_elem.get("changeid"),
        o_tmf=tu_elem.get("o-tmf"),
        srclang=tu_elem.get("srclang"),
        notes=[load_note(_note) for _note in tu_elem.iterfind("note")],
        props=[load_prop(_prop) for _prop in tu_elem.iterfind("prop")],
    )


def load_tmx(file: PathLike, encoding: str | None = None) -> tmx:
    tree: ElementTree = parse(
        file,
        XMLParser(encoding=encoding),
    )
    _header: header = load_header(
        header_elem=tree.find("header"),
    )
    return tmx(header_=_header, tus=[tu(tuvs=[tuv(seg(""), lang="en-us")])])
