from datetime import datetime
from os import PathLike
from typing import Iterable, Literal, Protocol, runtime_checkable
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent


@runtime_checkable
class InlineElement(Protocol):
    @property
    def _attrib(self) -> dict[str, str]:
        raise NotImplementedError

    @property
    def _XmlElement(self) -> Element:
        raise NotImplementedError


@runtime_checkable
class StructuralElement(Protocol):
    @property
    def _attrib(self) -> dict[str, str]:
        raise NotImplementedError

    @property
    def _XmlElement(self) -> Element:
        raise NotImplementedError


class Note(StructuralElement):
    __slots__ = ["text", "lang", "encoding"]

    def __init__(
        self, text: str, lang: str | None = None, encoding: str | None = None
    ) -> None:
        self.text = text
        self.lang = lang
        self.encoding = encoding

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "{http://www.w3.org/XML/1998/namespace}lang": self.lang,
            "o-encoding": self.encoding,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("note", attrib=self._attrib)
        elem.text = self.text
        return elem


class Prop(StructuralElement):
    __slots__ = ["text", "_type", "lang", "encoding"]

    def __init__(
        self,
        text: str,
        _type: str,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        self.text = text
        self._type = _type
        self.lang = lang
        self.encoding = encoding

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "{http://www.w3.org/XML/1998/namespace}lang": self.lang,
            "type": self._type,
            "o-encoding": self.encoding,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("prop", attrib=self._attrib)
        elem.text = self.text
        return elem


class Header(StructuralElement):
    __slots__ = [
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
        notes: Iterable[Note] | None = [],
        props: Iterable[Prop] | None = [],
    ) -> None:
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

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "creationtool": self.creationtool,
            "creationtoolversion": self.creationtoolversion,
            "segtype": self.segtype,
            "o-tmf": self.tmf,
            "adminlang": self.adminlang,
            "srclang": self.srclang,
            "datatype": self.datatype,
            "o-encoding": self.encoding,
            "creationdate": datetime.strftime(self.creationdate, "%Y%m%dT%H%M%SZ")
            if isinstance(self.creationdate, datetime)
            else self.creationdate,
            "creationid": self.creationid,
            "changedate": datetime.strftime(self.changedate, "%Y%m%dT%H%M%SZ")
            if isinstance(self.changedate, datetime)
            else self.changedate,
            "changeid": self.changeid,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("header", attrib=self._attrib)
        for note in self.notes:
            elem.append(note._XmlElement)
        for prop in self.props:
            elem.append(prop._XmlElement)
        return elem


class Ph(InlineElement):
    __slots__ = ["x", "_type", "assoc", "content"]

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

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "type": self._type,
            "assoc": self.assoc,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("ph", attrib=self._attrib)
        elem.text = self.content
        return elem


class It(InlineElement):
    __slots__ = ["x", "_type", "content"]

    def __init__(
        self,
        content: str,
        x: int | None = None,
        _type: str | None = None,
    ) -> None:
        self.x = x
        self._type = _type
        self.content = content

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "type": self._type,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("it", attrib=self._attrib)
        elem.text = self.content
        return elem


class Hi(InlineElement):
    __slots__ = ["x", "_type", "content"]

    def __init__(
        self,
        content: str,
        x: int | None = None,
        _type: str | None = None,
    ) -> None:
        self.content = content
        self.x = x
        self._type = _type

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "type": self._type,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("hi", attrib=self._attrib)
        elem.text = self.content
        return elem


class Bpt(InlineElement):
    __slots__ = ["content", "i", "x", "_type"]

    def __init__(
        self, content: str, i: int, x: int | None = None, _type: str | None = None
    ) -> None:
        self.content = content
        self.i = i
        self.x = x
        self._type = _type

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "i": str(self.i),
            "type": self._type,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("bpt", attrib=self._attrib)
        elem.text = self.content
        return elem


class Ept(InlineElement):
    __slots__ = ["content", "i"]

    def __init__(self, content: str, i: int) -> None:
        self.content = content
        self.i = i

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "i": str(self.i),
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("ept", attrib=self._attrib)
        elem.text = self.content
        return elem


class Tuv(StructuralElement):
    __slots__ = [
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
        content: Iterable[str | InlineElement],
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
        notes: Iterable[Note] | None = [],
        props: Iterable[Prop] | None = [],
    ) -> None:
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

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "{http://www.w3.org/XML/1998/namespace}lang": self.lang,
            "o-encoding": self.encoding,
            "datatype": self.datatype,
            "usagecount": self.usagecount,
            "creationtool": self.creationtool,
            "creationtoolversion": self.creationtoolversion,
            "creationdate": datetime.strftime(self.creationdate, "%Y%m%dT%H%M%SZ")
            if isinstance(self.creationdate, datetime)
            else self.creationdate,
            "creationid": self.creationid,
            "changedate": datetime.strftime(self.changedate, "%Y%m%dT%H%M%SZ")
            if isinstance(self.changedate, datetime)
            else self.changedate,
            "changeid": self.changeid,
            "o-tmf": self.tmf,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("tuv", attrib=self._attrib)
        for note in self.notes:
            elem.append(note._XmlElement)
        for prop in self.props:
            elem.append(prop._XmlElement)
        seg: Element = SubElement(elem, "seg")
        # content: list = [
        #     run._XmlElement if isinstance(run, InlineElement) else run
        #     for run in self.content
        # ]
        attach: Element = None
        for id, run in enumerate(self.content):
            if id == 0:
                if isinstance(run, str):
                    seg.text = run
                else:
                    attach = run._XmlElement
                    seg.append(attach)
            else:
                if isinstance(run, str):
                    if attach is None:
                        seg.text += run
                    else:
                        if attach.tail is None:
                            attach.tail = run
                        else:
                            attach.tail += run
                else:
                    new = run._XmlElement
                    seg.append(new)
                    attach = new
        return elem


class Tu(StructuralElement):
    __slots__ = [
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
        notes: Iterable[Note] | None = [],
        props: Iterable[Prop] | None = [],
    ) -> None:
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

    @property
    def _attrib(self) -> dict[str, str]:
        attrs: dict = {
            "tuid": str(self.tuid) if self.tuid is not None else None,
            "o-encoding": self.encoding,
            "datatype": self.datatype,
            "usagecount": self.usagecount,
            "lastusagedate": self.lastusagedate,
            "creationtool": self.creationtool,
            "creationtoolversion": self.creationtoolversion,
            "creationdate": datetime.strftime(self.creationdate, "%Y%m%dT%H%M%SZ")
            if isinstance(self.creationdate, datetime)
            else self.creationdate,
            "creationid": self.creationid,
            "changedate": datetime.strftime(self.changedate, "%Y%m%dT%H%M%SZ")
            if isinstance(self.changedate, datetime)
            else self.changedate,
            "segtype": self.segtype,
            "srclang": self.srclang,
            "changeid": self.changeid,
            "o-tmf": self.tmf,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    @property
    def _XmlElement(self) -> Element:
        elem: Element = Element("tu", attrib=self._attrib)
        for note in self.notes:
            elem.append(note._XmlElement)
        for prop in self.props:
            elem.append(prop._XmlElement)
        for tuv in self.tuvs:
            elem.append(tuv._XmlElement)
        return elem


class Tmx(StructuralElement):
    __slots__ = ["header", "tus"]

    def __init__(self, header: Header, tus: Iterable[Tu]) -> None:
        self.header = header
        self.tus = tus

    def Dump(self, file: PathLike) -> None:
        tmx: Element = Element("tmx", attrib={"version": "1.4"})
        tmx.append(self.header._XmlElement)
        body: Element = SubElement(tmx, "body")
        for tu in self.tus:
            body.append(tu._XmlElement)
        tree = ElementTree(tmx)
        indent(tree, "    ")
        tree.write(file, encoding="utf-8", xml_declaration=True)
