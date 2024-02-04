from datetime import datetime
from enum import Enum

from inline import bpt, ept, hi, it, ph, text_run


class Segtype(Enum):
    BLOCK = "block"
    PARAGRAPH = "paragraph"
    PHRASE = "phrase"
    SENTENCE = "sentence"


class note:
    __slots__ = [
        "text",
        "xml_lang",
        "oencoding",
    ]

    def __init__(
        self, text: str, xml_lang: str | None = None, oencoding: str | None = None
    ) -> None:
        self.text = text
        self.xml_lang = xml_lang
        self.oencoding = oencoding


class prop:
    __slots__ = [
        "text",
        "_type",
        "xml_lang",
        "oencoding",
    ]

    def __init__(
        self,
        text: str,
        _type: str,
        xml_lang: str | None = None,
        oencoding: str | None = None,
    ) -> None:
        self.text = text
        self._type = _type
        self.xml_lang = xml_lang
        self.oencoding = oencoding


class tuv:
    __slots__ = [
        "seg",
        "xml_lang",
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
        "notes",
        "props",
    ]

    def __init__(
        self,
        seg: list[text_run | ph | it | hi | bpt | ept],
        xml_lang: str,
        oencoding: str | None = None,
        datatype: str | None = None,
        usagecount: str | int | None = None,
        lastusagedate: str | datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        changeid: str | datetime | None = None,
        otmf: str | None = None,
        notes: list[note] | None = None,
        props: list[prop] | None = None,
    ) -> None:
        self.seg = seg
        self.xml_lang = xml_lang
        self.oencoding = oencoding
        self.datatype = datatype
        self.usagecount = usagecount
        self.lastusagedate = lastusagedate
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.changeid = changeid
        self.otmf = otmf
        self.notes = notes
        self.props = props


class tu:
    __slots__ = [
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
        "notes",
        "props",
    ]

    def __init__(
        self,
        tuid: str | int | None = None,
        oencoding: str | None = None,
        datatype: str | None = None,
        usagecount: str | int | None = None,
        lastusagedate: str | datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        segtype: Segtype | None = None,
        changeid: str | datetime | None = None,
        otmf: str | None = None,
        srclang: str | None = None,
        notes: list[note] | None = None,
        props: list[prop] | None = None,
    ) -> None:
        self.tuid = tuid
        self.oencoding = oencoding
        self.datatype = datatype
        self.usagecount = usagecount
        self.lastusagedate = lastusagedate
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.segtype = segtype
        self.changeid = changeid
        self.otmf = otmf
        self.srclang = srclang
        self.notes = notes
        self.props = props


class header:
    __slots__ = [
        "creationtool",
        "creationtoolversion",
        "segtype",
        "otmf",
        "adminlang",
        "srclang",
        "datatype",
        "segtype",
        "oencoding",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
        "notes",
        "props",
    ]

    def __init__(
        self,
        creationtool: str,
        creationtoolversion: str,
        segtype: Segtype,
        otmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        oencoding: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        changeid: str | None = None,
        notes: list[note] | None = None,
        props: list[prop] | None = None,
    ) -> None:
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.segtype = segtype
        self.otmf = otmf
        self.adminlang = adminlang
        self.srclang = srclang
        self.datatype = datatype
        self.oencoding = oencoding
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.changeid = changeid
        self.notes = notes
        self.props = props


class tmx:
    __slots__ = ["_header", "body"]

    def __init__(self, _header: header, body: list[tu]) -> None:
        self._header = _header
        self.body = body
