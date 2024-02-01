from .inline import bpt, ept, hi, it, ph, run
from lxml.etree import XMLParser, _Element, _ElementTree, parse
from .structural import header, note, prop, tmx, tu, tuv
from pathlib import Path


def load_prop(prop_elem: _Element) -> prop:
    prop_obj = prop()
    prop_obj.text = prop_elem.text
    prop_obj.prop_type = prop_elem.attrib.get("type")
    if prop_elem.attrib.get("o-encoding", None) is not None:
        prop_obj.oencoding = prop_elem.attrib.get("o-encoding")
    if (
        prop_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", None)
        is not None
    ):
        prop_obj.oencoding = prop_elem.attrib.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        )
    return prop_obj


def load_note(note_elem: _Element) -> note:
    note_obj = prop()
    note_obj.text = note_elem.text
    if note_elem.attrib.get("o-encoding", None) is not None:
        note_obj.oencoding = note_elem.attrib.get("o-encoding")
    if (
        note_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", None)
        is not None
    ):
        note_obj.oencoding = note_elem.attrib.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        )
    return note_obj


def load_header(header_elem: _Element) -> header:
    header_obj = header()
    for prop_elem in header_elem.findall("prop"):
        header_obj.props.append(load_prop(prop_elem))
    for note_elem in header_elem.findall("note"):
        header_obj.notes.append(load_note(note_elem))
    for attribute in [
        "creationtool",
        "creationtoolversion",
        "segtype",
        "o-tmf",
        "adminlang",
        "srclang",
        "datatype",
        "o-encoding",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
    ]:
        if header_elem.attrib.get(attribute, None) is not None:
            if attribute == "o-tmf":
                header_obj.otmf = header_elem.attrib.get(attribute)
            elif attribute == "o-encoding":
                header_obj.oenconding = header_elem.attrib.get(attribute)
            else:
                if attribute in header_obj.__slots__:
                    setattr(header_obj, attribute, header_elem.attrib.get(attribute))
    return header_obj


def load_ph(ph_elem: _Element) -> tuple[ph, run]:
    ph_run: ph = ph()
    tail_run: run = run()
    ph_run.text = ph_elem.text
    ph_run.x = ph_elem.attrib.get("x")
    ph_run.assoc = ph_elem.attrib.get("assoc")
    ph_run.ph_type = ph_elem.attrib.get("type")
    tail_run.text = ph_elem.tail
    return ph_run, tail_run


def load_bpt(bpt_elem: _Element) -> tuple[bpt, run]:
    bpt_run: bpt = bpt()
    tail_run: run = run()
    bpt_run.text = bpt_elem.text
    bpt_run.i = bpt_elem.get("i")
    bpt_run.x = bpt_elem.attrib.get("x")
    bpt_run.bpt_type = bpt_elem.attrib.get("type")
    tail_run.text = bpt_elem.tail
    return bpt_run, tail_run


def load_ept(ept_elem: _Element) -> tuple[bpt, run]:
    ept_run: ept = ept(i=ept_elem.get("i"))
    tail_run: run = run()
    ept_run.text = ept_elem.text
    tail_run.text = ept_elem.tail
    return ept_run, tail_run


def load_hi(hi_elem: _Element) -> tuple[bpt, run]:
    hi_run: hi = hi()
    tail_run: run = run()
    hi_run.text = hi_elem.text
    hi_run.x = hi_elem.attrib.get("x")
    hi_run.hi_type = hi_elem.attrib.get("type")
    tail_run.text = hi_elem.tail
    return hi_run, tail_run


def load_it(it_elem: _Element) -> tuple[bpt, run]:
    it_run: it = it()
    tail_run: run = run()
    it_run.text = it_elem.text
    it_run.x = it_elem.attrib.get("x")
    it_run.pos = it_elem.attrib.get("pos")
    it_run.it_type = it_elem.attrib.get("type")
    tail_run.text = it_elem.tail
    return it_run, tail_run


def load_tuv(tuv_elem: _Element) -> tuv:
    tuv_obj: tuv = tuv()
    tuv_obj.xmllang = tuv_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    for prop_elem in tuv_elem.findall("prop"):
        tuv_obj.props.append(load_prop(prop_elem))
    for note_elem in tuv_elem.findall("note"):
        tuv_obj.notes.append(load_note(note_elem))
    for attribute in [
        "oencoding",
        "datatype",
        "usagecount",
        "lastusagedate",
        "creationtool",
        "creationtoolversion",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
        "otmf",
    ]:
        if tuv_elem.attrib.get(attribute, None) is not None:
            if attribute == "o-encoding":
                tuv_obj.oenconding = tuv_elem.attrib.get(attribute)
            if attribute == "o-tmf":
                tuv_obj.otmf = tuv_elem.attrib.get(attribute)
            else:
                if attribute in tuv_obj.__slots__:
                    setattr(tuv_obj, attribute, tuv_elem.attrib.get(attribute))
    seg_elem: _Element = tuv_elem.find("seg")
    if seg_elem.text is not None:
        tuv_obj.runs.append(run(text=seg_elem.text))
    part: _Element
    for part in seg_elem.iterdescendants():
        match part.tag:
            case "ph":
                ph_run, tail_run = load_ph(part)
                tuv_obj.runs.append(ph_run)
                tuv_obj.runs.append(tail_run)
            case "bpt":
                bpt_run, tail_run = load_bpt(part)
                tuv_obj.runs.append(bpt_run)
                tuv_obj.runs.append(tail_run)
            case "ept":
                ept_run, tail_run = load_ept(part)
                tuv_obj.runs.append(ept_run)
                tuv_obj.runs.append(tail_run)
            case "hi":
                hi_run, tail_run = load_hi(part)
                tuv_obj.runs.append(hi_run)
                tuv_obj.runs.append(tail_run)
            case "it":
                it_run, tail_run = load_it(part)
                tuv_obj.runs.append(it_run)
                tuv_obj.runs.append(tail_run)
    return tuv_obj


def load_tu(tu_elem: _Element) -> tu:
    tu_obj: tu = tu()
    for prop_elem in tu_elem.findall("prop"):
        tu_obj.props.append(load_prop(prop_elem))
    for note_elem in tu_elem.findall("note"):
        tu_obj.notes.append(load_note(note_elem))
    for attribute in [
        "tuid",
        "oencoding",
        "datatype",
        "usagecount",
        "lastusagedate",
        "creationtool",
        "creationtoolversion",
        "creationdate",
        "creationid",
        "changedate",
        "segtype",
        "changeid",
        "otmf",
        "srclang",
    ]:
        value = tu_elem.attrib.get(attribute, None)
        if value is not None:
            if attribute == "o-encoding":
                tu_obj.oenconding = value
            if attribute == "o-tmf":
                tu_obj.otmf = value
            else:
                setattr(tu_obj, attribute, value)
    for tuv_elem in tu_elem.findall("tuv"):
        tu_obj.tuvs.append(load_tuv(tuv_elem))
    return tu_obj


def load_tmx(file: Path | str) -> tmx:
    """Parse a tmx file using lxml and returns a tmx object"""
    tmx_obj = tmx()
    tmx_parser: XMLParser = XMLParser(
        encoding="utf-8", remove_blank_text=True, resolve_entities=False, recover=True
    )
    tmx_file: Path = Path(file)
    tmx_tree: _ElementTree = parse(tmx_file, tmx_parser)
    tmx_root: _Element = tmx_tree.getroot()
    tmx_header_elem: _Element = tmx_root.find("header")
    tmx_obj.Header: header = load_header(tmx_header_elem)
    for tu_elem in tmx_root.iter("tu"):
        tmx_obj.tus.append(load_tu(tu_elem))
    return tmx_obj
