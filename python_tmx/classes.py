from datetime import datetime
from os import PathLike
from typing import Iterable, Literal, Protocol, runtime_checkable
from xml.etree.ElementTree import Element, ElementTree, SubElement


@runtime_checkable
class TmxElement(Protocol):

    def _make_xml_attrib(self) -> dict[str, str]:
        """
        Private method.

        Creates the attribute dict for the _make_xml_element method.
        Keys have the name adjusted as needed to be tmx compliant
        (e.g. encoding -> o-encoding)
        """
        raise NotImplementedError

    def _make_xml_element(self, force:bool) -> Element:
        """
        Private method.

        Convert an Element into a XML Element Tree Element.
        Object's content becomes the Element's text.
        Attributes are from the _make_xml_attrib method.

        Note: Setting 'force' to True will call str(self.content)
        if the content is not a string object to avoid serializing errors.
        """
        raise NotImplementedError


class Note(TmxElement):
    """
    Class used to represent a <note> tag

    Attributes
    --------
    Required:
        content: str
            The actual content of the note
    Optional:
        lang: str
            The language of the note's content
        encoding : str
            The encoding of the note's content
    """

    __slots__ = ["content", "lang", "encoding"]

    def __init__(
        self, content: str, lang: str | None = None, encoding: str | None = None
    ) -> None:
        self.content = content
        self.lang = lang
        self.encoding = encoding

    def _make_xml_attrib(self) -> dict[str, str]:
        attrs: dict[str, str] = {
            "{http://www.w3.org/XML/1998/namespace}lang": self.lang,
            "o-encoding": self.encoding,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem = Element("note", attrib=self._make_xml_attrib())
        if not isinstance(self.content, str):
            elem.text = str(self.content)
        else:
            elem.text = self.content
        return elem


class Prop(TmxElement):
    """
    Class used to represent a <prop> tag

    Attributes
    --------
    Required:
        content: str
            The actual content of the prop.
        _type: str
            The type of the prop. Usually in the form of "x-foo"
    Optional:
        lang: str
            The language of the prop's content
        encoding: str
            The enconding of the prop's content
    """

    __slots__ = ["content", "_type", "lang", "encoding"]

    def __init__(
        self,
        content: str,
        _type: str,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        self.content = content
        self._type = _type
        self.lang = lang
        self.encoding = encoding

    def _make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "{http://www.w3.org/XML/1998/namespace}lang": self.lang,
            "type": self._type,
            "o-encoding": self.encoding,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("prop", attrib=self._make_xml_attrib())
        if not isinstance(self.content, str):
            elem.text = str(self.content)
        else:
            elem.text = self.content
        return elem

class Header(Element):
    """
    The `<header>` object

    Contains general info regarding a tmx file. For many attributes,
    if not defined at the tu/tuv level, the attributes from the header
    will be used as the default.

    Attributes:
        creationtool:
            A string that represents the tool used to create the tmx file
        creationtoolversion:
            A string that represents the version of the tool used to
            create the tmx
        segtype:
            One of "block", "paragraph", "sentence" or "phrase".
            Represents the segmentation of the content.
            Use "phrase" for simple list of words or small non-verbal sentences.
            Use "sentence" if each segment contain a single sentence.
            Use "paragraph" if there can be multiple sentences in a segment.
            Use "block" if none of the other options is adequate.
        tmf:
            A string that represents the format of the original
            translation memory where the contents of the file were stored.
        adminlang:
            Default language for any content not contained in segments.
            Namely inside props and notes, unless specified otherwise.
        srclang:
            Default source language for a tu unless specified otherwise.
            can be set "*all*" if there is no source language.
    """

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
    def _make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "creationtool": self.creationtool,
            "creationtoolversion": self.creationtoolversion,
            "segtype": self.segtype,
            "o-tmf": self.tmf,
            "adminlang": self.adminlang,
            "srclang": self.srclang,
            "datatype": self.datatype,
            "o-encoding": self.encoding,
            "creationdate": (
                datetime.strftime(self.creationdate, "%Y%m%dT%H%M%SZ")
                if isinstance(self.creationdate, datetime)
                else self.creationdate
            ),
            "creationid": self.creationid,
            "changedate": (
                datetime.strftime(self.changedate, "%Y%m%dT%H%M%SZ")
                if isinstance(self.changedate, datetime)
                else self.changedate
            ),
            "changeid": self.changeid,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("header", attrib=self._make_xml_attrib())
        for note in self.notes:
            elem.append(note._make_xml_element())
        for prop in self.props:
            elem.append(prop._make_xml_element())
        return elem


class Ph(Element):
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
    def _make_xml_make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "type": self._type,
            "assoc": self.assoc,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("ph", attrib=self._make_xml_make_xml_attrib)
        elem.text = self.content
        return elem


class It(Element):
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
    def _make_xml_make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "type": self._type,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("it", attrib=self._make_xml_make_xml_attrib)
        elem.text = self.content
        return elem


class Hi(Element):
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
    def _make_xml_make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "type": self._type,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("hi", attrib=self._make_xml_make_xml_attrib)
        elem.text = self.content
        return elem


class Bpt(Element):
    __slots__ = ["content", "i", "x", "_type"]

    def __init__(
        self, content: str, i: int, x: int | None = None, _type: str | None = None
    ) -> None:
        self.content = content
        self.i = i
        self.x = x
        self._type = _type

    @property
    def _make_xml_make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "x": str(self.x),
            "i": str(self.i),
            "type": self._type,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("bpt", attrib=self._make_xml_make_xml_attrib)
        elem.text = self.content
        return elem


class Ept(Element):
    __slots__ = ["content", "i"]

    def __init__(self, content: str, i: int) -> None:
        self.content = content
        self.i = i

    @property
    def _make_xml_make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "i": str(self.i),
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("ept", attrib=self._make_xml_make_xml_attrib)
        elem.text = self.content
        return elem


class Tuv(Element):
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
        content: Iterable[str | Element],
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
    def _make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "{http://www.w3.org/XML/1998/namespace}lang": self.lang,
            "o-encoding": self.encoding,
            "datatype": self.datatype,
            "usagecount": self.usagecount,
            "creationtool": self.creationtool,
            "creationtoolversion": self.creationtoolversion,
            "creationdate": (
                datetime.strftime(self.creationdate, "%Y%m%dT%H%M%SZ")
                if isinstance(self.creationdate, datetime)
                else self.creationdate
            ),
            "creationid": self.creationid,
            "changedate": (
                datetime.strftime(self.changedate, "%Y%m%dT%H%M%SZ")
                if isinstance(self.changedate, datetime)
                else self.changedate
            ),
            "changeid": self.changeid,
            "o-tmf": self.tmf,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("tuv", attrib=self._make_xml_attrib())
        for note in self.notes:
            elem.append(note._make_xml_element())
        for prop in self.props:
            elem.append(prop._make_xml_element())
        seg: Element = SubElement(elem, "seg")
        attach: Element = None
        for id, run in enumerate(self.content):
            if id == 0:
                if isinstance(run, str):
                    seg.text = run
                else:
                    attach = run._make_xml_element()
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
                    new = run._make_xml_element()
                    seg.append(new)
                    attach = new
        return elem


class Tu(Element):
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
    def _make_xml_attrib(self) -> dict[str, str]:
        attrs: dict = {
            "tuid": str(self.tuid) if self.tuid is not None else None,
            "o-encoding": self.encoding,
            "datatype": self.datatype,
            "usagecount": self.usagecount,
            "lastusagedate": self.lastusagedate,
            "creationtool": self.creationtool,
            "creationtoolversion": self.creationtoolversion,
            "creationdate": (
                datetime.strftime(self.creationdate, "%Y%m%dT%H%M%SZ")
                if isinstance(self.creationdate, datetime)
                else self.creationdate
            ),
            "creationid": self.creationid,
            "changedate": (
                datetime.strftime(self.changedate, "%Y%m%dT%H%M%SZ")
                if isinstance(self.changedate, datetime)
                else self.changedate
            ),
            "segtype": self.segtype,
            "srclang": self.srclang,
            "changeid": self.changeid,
            "o-tmf": self.tmf,
        }
        return {key: value for key, value in attrs.items() if value is not None}

    def _make_xml_element(self) -> Element:
        elem: Element = Element("tu", attrib=self._make_xml_attrib())
        for note in self.notes:
            elem.append(note._make_xml_element())
        for prop in self.props:
            elem.append(prop._make_xml_element())
        for tuv in self.tuvs:
            elem.append(tuv._make_xml_element())
        return elem


class Tmx(Element):
    __slots__ = ["header", "tus"]

    def __init__(self, header: Header, tus: Iterable[Tu]) -> None:
        self.header = header
        self.tus = tus

    def Dump(self, file: PathLike) -> None:
        tmx: Element = Element("tmx", attrib={"version": "1.4"})
        tmx.append(self.header._make_xml_element())
        body: Element = SubElement(tmx, "body")
        for tu in self.tus:
            body.append(tu._make_xml_element())
        tree = ElementTree(tmx)
        tree.write(file, encoding="utf-8", xml_declaration=True)
