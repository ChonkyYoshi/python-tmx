from typing import Iterator
from classes import hi, it, note, ph, prop, map, sub, ude, tuv, tu, header
from xml.etree.ElementTree import Element, fromstring


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


def load_tuv(tuv_elem: Element) -> tuv:
    return tuv(
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


def load_ph(ph_elem: Element) -> tuple[ph, str | None]:
    ph_obj = ph(
        content=ph_elem.text,
        x=ph_elem.get("x"),
        type_=ph_elem.get("type"),
        assoc=ph_elem.get("assoc"),
    )
    if len(ph_elem) == 0:
        return ph_obj, ph_elem.tail
    else:
        ph_obj.content = [ph_obj.content]
        for elem in ph_elem.iter():
            if elem.tag == 'sub':
                ph_obj.content.extend(load_sub(elem))
            else:
                raise NotImplementedError("Non Sub tag in ph content")
        return ph_obj, ph_elem.tail

def load_it(it_elem: Element) -> tuple[it, str | None]:
    it_obj = it(
        content=it_elem.text,
        pos=it_elem.get("pos"),
        x=it_elem.get("x"),
        type_=it_elem.get("type"),
    )
    if len(it_elem) == 0:
        return it_obj, it_elem.tail
    else:
        it_obj.content = [it_obj.content]
        for elem in it_elem.iter():
            if elem.tag == 'sub':
                it_obj.content.extend(load_sub(elem))
            else:
                raise NotImplementedError("Non Sub tag in it content")
        return it_obj, it_obj.tail

def load_hi(hi_elem: Element) -> tuple[hi, str | None]:
    hi_obj = hi(
        content=hi_elem.text,
        x=hi_elem.get("x"),
        type_=hi_elem.get("type"),
    )
    if len(hi_elem) == 0:
        return hi_obj, hi_elem.tail
    else:
        hi_obj.content = [hi_obj.content]
        for elem in hi_elem.iter():
            for elem in hi_elem.iter():
                match elem.tag:
                    case 'ph':
                        hi_obj.content.extend(load_ph(elem))
                    case 'it':
                        hi_obj.content.extend(load_it(elem))
                    case 'hi':
                        hi_obj.content.extend(load_hi(elem))
        return hi_obj, hi_obj.tail


def load_sub(sub_elem: Element) -> tuple[sub, str | None]:
    sub_obj:sub = sub(
            content=sub_elem.text,
            datatype=sub_elem.get("datatype"),
            type_=sub_elem.get("type"),
        )
    if len(sub_elem) == 0:
        return sub_obj, sub_elem.tail
    else:
        sub_obj.content = [sub_obj.content]
        for elem in sub_elem.iter():
            match elem.tag:
                case 'ph':
                    sub_obj.content.extend(load_ph(elem))
                case 'it':
                    sub_obj.content.extend(load_it(elem))




def iterchildren(root_element:Element) -> Iterator[Element]:
    children:list[Element] = root_element.findall("*")
    for child in children:
        yield child

def iterdescendants(root_element:Element) -> Iterator[Element]:
    children:list[Element] = root_element.findall("*")
    for child in children:
        yield child
        if len(child) != 0:
            for grandchild in iterdescendants(child):
                yield grandchild

a = fromstring("""<root><child1><subchild1><subsubchild1></subsubchild1></subchild1></child1><child2></child2></root>""")
for child in iterdescendants(a):
    print(child.tag)