from classes import *
from xml.etree.ElementTree import ElementTree, Element, SubElement, parse
from os import PathLike


def ParseTmx(file: PathLike) -> Tmx:
    tmx_tree: ElementTree = parse(file)
    tmx_root: Element = tmx_tree.getroot()
    tmx_root_header: Element = tmx_root.find("header")
    final_header: Header = Header(
        creationtool=tmx_root_header.get("creationtool"),
        creationtoolversion=tmx_root_header.get("creationtoolversion"),
        segtype=tmx_root_header.get("segtype"),
        tmf=tmx_root_header.get("tmf"),
        adminlang=tmx_root_header.get("adminlang"),
        srclang=tmx_root_header.get("srclang"),
        datatype=tmx_root_header.get("datatype"),
        encoding=tmx_root_header.get("o-encoding"),
        creationdate=tmx_root_header.get("creationdate"),
        creationid=tmx_root_header.get("creationid"),
        changedate=tmx_root_header.get("changedate"),
        changeid=tmx_root_header.get("changeid"),
        notes=[
            Note(
                text=_note.text,
                lang=_note.get("{http://www.w3.org/XML/1998/namespace}lang"),
                encoding=_note.get("o-encoding"),
            )
            for _note in tmx_root_header.findall("note")
        ],
        props=[
            Prop(
                text=_prop.text,
                _type=_prop.get("type"),
                lang=_prop.get("{http://www.w3.org/XML/1998/namespace}lang"),
                encoding=_prop.get("o-encoding"),
            )
            for _prop in tmx_root_header.findall("prop")
        ],
    )

    return final_header

a = ParseTmx("example.tmx")
1