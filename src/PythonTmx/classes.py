from typing import Literal, Iterable
from datetime import datetime
from xml.etree.ElementTree import Element


class Note:
    __slots__ = ["text", "lang", "encoding", "_name"]

    def __init__(
        self, text: str, lang: str | None = None, encoding: str | None = None
    ) -> None:
        self._name = "note"
        self.text = text
        self.lang = lang
        self.encoding = encoding


class Prop:
    __slots__ = ["text", "_type", "lang", "encoding", "_name"]

    def __init__(
        self,
        text: str,
        _type: str,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        self._name = "prop"
        self.text = text
        self._type = _type
        self.lang = lang
        self.encoding = encoding


class Header:
    __slots__ = [
        "_name",
        "creationtool",
        "creationtoolversion",
        "segtype",
        "tmf",
        "adminlang",
        "srclang",
        "datatype",
        "encoding",
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
        segtype: Literal["block", "paragraph", "sentence", "phrase"],
        tmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        encoding: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | None = None,
        changeid: str | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
    ) -> None:
        self._name = "header"
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.segtype = segtype
        self.tmf = tmf
        self.adminlang = adminlang
        self.srclang = srclang
        self.datatype = datatype
        self.encoding = encoding
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.changeid = changeid
        self.notes = notes
        self.props = props


class Ph:
    __slots__ = ["x", "_type", "assoc", "content", "_name"]

    def __init__(
        self,
        content: str,
        x: int | None = None,
        _type: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        self.x = x
        self._type = _type
        self.assoc = assoc
        self.content = content
        self._name = "ph"


class It:
    __slots__ = ["x", "_type", "content", "_name"]

    def __init__(
        self,
        content: str,
        x: int | None = None,
        _type: str | None = None,
    ) -> None:
        self.x = x
        self._type = _type
        self.content = content
        self._name = "it"


class Hi:
    __slots__ = ["x", "_type", "content", "_name"]

    def __init__(
        self,
        content: str,
        x: int | None = None,
        _type: str | None = None,
    ) -> None:
        self.content = content
        self.x = x
        self._type = _type
        self._name = "hi"


class Bpt:
    __slots__ = ["i", "x", "_type", "_name"]

    def __init__(self, i: int, x: int | None = None, _type: str | None = None) -> None:
        self.i = i
        self.x = x
        self._type = _type
        self._name = "bpt"


class Ept:
    __slots__ = ["i", "_name"]

    def __init__(self, i: int) -> None:
        self.i = i
        self._name = "ept"


class Tuv:
    __slots__ = [
        "_name",
        "content",
        "lang",
        "encoding",
        "datatype",
        "usagecount",
        "lastusagedate",
        "creationtool",
        "creationtoolversion",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
        "tmf",
        "notes",
        "props",
    ]

    def __init__(
        self,
        content: Iterable[str | Ph | It | Hi | Bpt | Ept],
        lang: str,
        encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: str | datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        changeid: str | None = None,
        tmf: str | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
    ) -> None:
        self._name = "tuv"
        self.content = content
        self.lang = lang
        self.encoding = encoding
        self.datatype = datatype
        self.usagecount = usagecount
        self.lastusagedate = lastusagedate
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.changeid = changeid
        self.tmf = tmf
        self.notes = notes
        self.props = props


class Tu:
    __slots__ = [
        "_name",
        "tuvs",
        "tuid",
        "encoding",
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
        "tmf",
        "srclang",
        "notes",
        "props",
    ]

    def __init__(
        self,
        tuid: int | None = None,
        tuvs: Iterable[Tuv] | None = None,
        encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: str | datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        changeid: str | None = None,
        tmf: str | None = None,
        srclang: str | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
    ) -> None:
        self._name = "tu"
        self.tuid = tuid
        self.tuvs = tuvs
        self.encoding = encoding
        self.datatype = datatype
        self.usagecount = usagecount
        self.lastusagedate = lastusagedate
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.segtype = segtype
        self.srclang = srclang
        self.changeid = changeid
        self.tmf = tmf
        self.notes = notes
        self.props = props


class Tmx:
    __slots__ = ["_header", "tus"]

    def __init__(self, _header: Header, tus: Iterable[Tu]) -> None:
        self.header = _header
        self.tus = tus
