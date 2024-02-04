from structural import tmx, header, Segtype, note, prop
from lxml.etree import XMLParser, _Element, _ElementTree, parse
from datetime import datetime, UTC

xml = "{http://www.w3.org/XML/1998/namespace}"


def LoadTmx(file, encoding: str = "utf8") -> tmx:
    tmx_tree: _ElementTree = parse(
        file, XMLParser(encoding=encoding, remove_blank_text=True)
    )
    tmx_root: _Element = tmx_tree.getroot()
    header_element: _Element = tmx_root.find("header", None)
    final_header: header = header(
        creationtool=header_element.get("creationtool", default=None),
        creationtoolversion=header_element.get("creationtoolversion", default=None),
        segtype=Segtype[header_element.get("segtype", default=None).upper()],
        adminlang=header_element.get("adminlang", default=None),
        otmf=header_element.get("o-tmf", default=None),
        srclang=header_element.get("srclang", default=None),
        datatype=header_element.get("datatype", default=None),
        oencoding=header_element.get("o-encoding", default=None),
        creationdate=datetime.strptime(
            header_element.get("creationdate", default=None), "%Y%m%dT%H%M%SZ"
        ).replace(tzinfo=UTC),
        creationid=header_element.get("creationid", default=None),
        changedate=datetime.strptime(
            header_element.get("changedate", default=None), "%Y%m%dT%H%M%SZ"
        ).replace(tzinfo=UTC),
        changeid=header_element.get("changeid", default=None),
        notes=[
            note(
                text=note_element.text,
                xml_lang=note_element.get(f"{xml}lang"),
                oencoding=encoding,
            )
            for note_element in header_element.iterchildren("note")
        ],
        props=[
            prop(
                text=prop_element.text,
                _type=prop_element.get("type"),
                xml_lang=prop_element.get(f"{xml}lang"),
                oencoding=encoding,
            )
            for prop_element in header_element.iterchildren("prop")
        ],
    )
    return tmx(_header=final_header, body=list())


a = LoadTmx("a.tmx", encoding="utf8")
print(a._header.adminlang)
