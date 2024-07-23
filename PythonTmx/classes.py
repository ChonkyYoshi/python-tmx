from __future__ import annotations

from datetime import datetime
from io import BytesIO, StringIO
from os import PathLike
from typing import Iterable, Literal, MutableSequence, Optional, override

from lxml.etree import Element, ElementTree, _Element

from PythonTmx.core import ExtraTailError, ExtraTextError, TmxAttributes, TmxElement


class Prop(TmxElement):
    type: str
    xmllang: Optional[str]
    oencoding: Optional[str]
    _required_attributes = (TmxAttributes.type,)
    _optional_attributes = TmxAttributes.xmllang, TmxAttributes.oencoding
    _allowed_content = (str,)

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[str] = None,
        type: Optional[str] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            type=type,
            xmllang=xmllang,
            oencoding=oencoding,
        )
        if source_element is not None:
            if source_element.text:
                self.content += source_element.text
            elif content is not None:
                self.content += content


class Note(TmxElement):
    xmllang: Optional[str]
    oencoding: Optional[str]
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.xmllang, TmxAttributes.oencoding
    _allowed_content = (str,)

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[str] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            content=content,
            xmllang=xmllang,
            oencoding=oencoding,
        )
        if source_element is not None:
            if source_element.text:
                self.content += source_element.text
            elif content is not None:
                self.content += content


class Map(TmxElement):
    unicode: str
    code: Optional[str]
    ent: Optional[str]
    subst: Optional[str]
    _required_attributes = (TmxAttributes.unicode,)
    _optional_attributes = TmxAttributes.code, TmxAttributes.ent, TmxAttributes.subst
    _allowed_content = tuple()

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        unicode: Optional[str] = None,
        code: Optional[str] = None,
        ent: Optional[str] = None,
        subst: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            unicode=unicode,
            code=code,
            ent=ent,
            subst=subst,
        )
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("map", source_element.text)
            if source_element.tail:
                raise ExtraTailError("map", source_element.tail)


class Ude(TmxElement):
    name: str
    base: Optional[str]
    _required_attributes = (TmxAttributes.name,)
    _optional_attributes = (TmxAttributes.base,)
    _allowed_content = (Map,)

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[Iterable[Map]] = None,
        name: Optional[str] = None,
        base: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            name=name,
            base=base,
        )
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("ude", source_element.text)
            if source_element.tail:
                raise ExtraTailError("ude", source_element.tail)
            if len(source_element):
                for map_ in source_element:
                    self.content.append(Map(map_))
            else:
                if content is not None:
                    self.content.extend(content)


class Header(TmxElement):
    _required_attributes = (
        TmxAttributes.creationtool,
        TmxAttributes.creationtoolversion,
        TmxAttributes.segtype,
        TmxAttributes.otmf,
        TmxAttributes.adminlang,
        TmxAttributes.srclang,
        TmxAttributes.datatype,
    )
    _optional_attributes = (
        TmxAttributes.oencoding,
        TmxAttributes.creationdate,
        TmxAttributes.creationid,
        TmxAttributes.changedate,
        TmxAttributes.changeid,
    )
    _allowed_content = (Ude,)
    creationtool: str
    creationtoolversion: str
    segtype: Literal["block", "paragraph", "sentence", "phrase"]
    otmf: Optional[str]
    adminlang: Optional[str]
    srclang: Optional[str]
    datatype: Optional[str]
    oencoding: Optional[str]
    creationdate: Optional[str | datetime]
    creationid: Optional[str]
    changedate: Optional[str | datetime]
    changeid: Optional[str]
    props: Optional[MutableSequence[Prop]]
    notes: Optional[MutableSequence[Note]]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[Iterable[Ude]] = None,
        creationtool: Optional[str] = None,
        creationtoolversion: Optional[str] = None,
        segtype: Optional[Literal["block", "paragraph", "sentence", "phrase"]] = None,
        otmf: Optional[str] = None,
        adminlang: Optional[str] = None,
        srclang: Optional[str] = None,
        datatype: Optional[str] = None,
        oencoding: Optional[str] = None,
        creationdate: Optional[str | datetime] = None,
        creationid: Optional[str] = None,
        changedate: Optional[str | datetime] = None,
        changeid: Optional[str] = None,
        notes: Optional[Iterable[Note]] = None,
        props: Optional[Iterable[Prop]] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            creationtool=creationtool,
            creationtoolversion=creationtoolversion,
            segtype=segtype,
            otmf=otmf,
            adminlang=adminlang,
            srclang=srclang,
            datatype=datatype,
            oencoding=oencoding,
            creationdate=creationdate,
            creationid=creationid,
            changedate=changedate,
            changeid=changeid,
        )
        self.notes, self.props = [], []
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("header", source_element.text)
            if source_element.tail:
                raise ExtraTailError("header", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "ude":
                        self.content.append(Ude(item))
                    if item.tag == "note":
                        self.notes.append(Note(item))
                    if item.tag == "prop":
                        self.props.append(Prop(item))
            else:
                if content is not None:
                    self.content.extend(content)
                if props is not None:
                    self.props.extend(props)
                if notes is not None:
                    self.notes.extend(notes)


class Sub(TmxElement): ...


class Bpt(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.i,)
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    i = str | int
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        i: Optional[str | int] = None,
        x: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            i=i,
            x=x,
            type=type,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Ept(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.i,)
    _optional_attributes = tuple()
    i = str | int

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        i: Optional[str | int] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            i=i,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class It(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.pos,)
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    pos: Literal["begin", "end"]
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        pos: Optional[Literal["begin", "end"]] = None,
        x: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            pos=pos,
            x=x,
            type=type,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Ph(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.x, TmxAttributes.type, TmxAttributes.assoc
    assoc: Literal["p", "f", "b"]
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        assoc: Optional[Literal["p", "f", "b"]] = None,
        x: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            assoc=assoc,
            x=x,
            type=type,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Ut(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.x,)
    _optional_attributes = tuple()
    x = Optional[str | int]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        x: Optional[str | int] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            x=x,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Hi(TmxElement):
    _allowed_content = Bpt, Ept, Ph, It, Ut
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    i = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        i: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        self._allowed_content += (Hi,)  # type: ignore
        super().__init__(source_element=source_element, i=i, type=type)
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    if item.tag == "bpt":
                        self.content.append(Bpt(item))
                    if item.tag == "ept":
                        self.content.append(Ept(item))
                    if item.tag == "ph":
                        self.content.append(Ph(item))
                    if item.tag == "hi":
                        self.content.append(Hi(item))
                    if item.tag == "it":
                        self.content.append(It(item))
                    if item.tag == "ut":
                        self.content.append(Ut(item))
                    if item.tail:
                        self.content.append(item.tail)


class Sub(TmxElement):  # type: ignore
    _allowed_content = Bpt, Ept, Hi, Ph, It, Ut
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.datatype, TmxAttributes.type
    datatype = Optional[str]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        datatype: Optional[str] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(source_element=source_element, datatype=datatype, type=type)
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    if item.tag == "bpt":
                        self.content.append(Bpt(item))
                    if item.tag == "ept":
                        self.content.append(Ept(item))
                    if item.tag == "ph":
                        self.content.append(Ph(item))
                    if item.tag == "hi":
                        self.content.append(Hi(item))
                    if item.tag == "it":
                        self.content.append(It(item))
                    if item.tag == "ut":
                        self.content.append(Ut(item))
                    if item.tail:
                        self.content.append(item.tail)


class Seg(TmxElement):
    _allowed_content = str, Sub, Ut, Ph, It, Hi, Bpt, Ept
    _required_attributes = tuple()
    _optional_attributes = tuple()

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        datatype: Optional[str] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(source_element=source_element, datatype=datatype, type=type)
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    if item.tag == "bpt":
                        self.content.append(Bpt(item))
                    if item.tag == "ept":
                        self.content.append(Ept(item))
                    if item.tag == "ph":
                        self.content.append(Ph(item))
                    if item.tag == "hi":
                        self.content.append(Hi(item))
                    if item.tag == "it":
                        self.content.append(It(item))
                    if item.tag == "ut":
                        self.content.append(Ut(item))
                    if item.tag == "sub":
                        self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Tuv(TmxElement):
    _required_attributes = (TmxAttributes.xmllang,)
    _optional_attributes = (
        TmxAttributes.oencoding,
        TmxAttributes.datatype,
        TmxAttributes.usagecount,
        TmxAttributes.lastusagedate,
        TmxAttributes.creationtool,
        TmxAttributes.creationtoolversion,
        TmxAttributes.creationdate,
        TmxAttributes.creationid,
        TmxAttributes.changedate,
        TmxAttributes.changeid,
        TmxAttributes.otmf,
    )
    _allowed_content = (Seg,)
    xmllang: Optional[str]
    oencoding: Optional[str]
    datatype: Optional[str]
    usagecount: Optional[str]
    lastusagedate: Optional[str]
    creationtool: Optional[str]
    creationtoolversion: Optional[str]
    creationdate: Optional[str]
    creationid: Optional[str]
    changedate: Optional[str]
    changeid: Optional[str]
    otmf: Optional[str]
    props: Optional[MutableSequence[Prop]]
    notes: Optional[MutableSequence[Note]]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[Seg] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
        datatype: Optional[str] = None,
        usagecount: Optional[str] = None,
        lastusagedate: Optional[str] = None,
        creationtool: Optional[str] = None,
        creationtoolversion: Optional[str] = None,
        creationdate: Optional[str] = None,
        creationid: Optional[str] = None,
        changedate: Optional[str] = None,
        changeid: Optional[str] = None,
        otmf: Optional[str] = None,
        notes: Optional[Iterable[Note]] = None,
        props: Optional[Iterable[Prop]] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            xmllang=xmllang,
            oencoding=oencoding,
            datatype=datatype,
            usagecount=usagecount,
            lastusagedate=lastusagedate,
            creationtool=creationtool,
            creationtoolversion=creationtoolversion,
            creationdate=creationdate,
            creationid=creationid,
            changedate=changedate,
            changeid=changeid,
            otmf=otmf,
        )
        self.notes, self.props = [], []
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("tuv", source_element.text)
            if source_element.tail:
                raise ExtraTailError("tuv", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "seg":
                        if len(self.content) != 0:
                            raise ValueError("Only one seg element per tuv")
                        self.content.append(Seg(item))
                    if item.tag == "note":
                        self.notes.append(Note(item))
                    if item.tag == "prop":
                        self.props.append(Prop(item))
            else:
                if content is not None:
                    self.content.append(content)
                if props is not None:
                    self.props.extend(props)
                if notes is not None:
                    self.notes.extend(notes)


class Tu(TmxElement):
    _required_attributes = tuple()
    _optional_attributes = (
        TmxAttributes.tuid,
        TmxAttributes.oencoding,
        TmxAttributes.datatype,
        TmxAttributes.usagecount,
        TmxAttributes.lastusagedate,
        TmxAttributes.creationtool,
        TmxAttributes.creationtoolversion,
        TmxAttributes.creationdate,
        TmxAttributes.creationid,
        TmxAttributes.changedate,
        TmxAttributes.segtype,
        TmxAttributes.changeid,
        TmxAttributes.otmf,
        TmxAttributes.srclang,
    )
    _allowed_content = (Tuv,)
    tuid: Optional[str]
    xmllang: Optional[str]
    oencoding: Optional[str]
    datatype: Optional[str]
    usagecount: Optional[str]
    lastusagedate: Optional[str]
    creationtool: Optional[str]
    creationtoolversion: Optional[str]
    creationdate: Optional[str]
    creationid: Optional[str]
    changedate: Optional[str]
    segtype: Optional[Literal["block", "paragraph", "sentence", "phrase"]]
    changeid: Optional[str]
    otmf: Optional[str]
    srclang: Optional[str]
    props: Optional[MutableSequence[Prop]]
    notes: Optional[MutableSequence[Note]]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[Iterable[Tuv]] = None,
        tuid: Optional[str] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
        datatype: Optional[str] = None,
        usagecount: Optional[str] = None,
        lastusagedate: Optional[str] = None,
        creationtool: Optional[str] = None,
        creationtoolversion: Optional[str] = None,
        creationdate: Optional[str] = None,
        creationid: Optional[str] = None,
        changedate: Optional[str] = None,
        segtype: Optional[Literal["block", "paragraph", "sentence", "phrase"]] = None,
        changeid: Optional[str] = None,
        otmf: Optional[str] = None,
        srclang: Optional[str] = None,
        notes: Optional[Iterable[Note]] = None,
        props: Optional[Iterable[Prop]] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            tuid=tuid,
            xmllang=xmllang,
            oencoding=oencoding,
            datatype=datatype,
            usagecount=usagecount,
            lastusagedate=lastusagedate,
            creationtool=creationtool,
            creationtoolversion=creationtoolversion,
            creationdate=creationdate,
            creationid=creationid,
            changedate=changedate,
            segtype=segtype,
            changeid=changeid,
            otmf=otmf,
            srclang=srclang,
        )
        self.notes, self.props = [], []
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("tu", source_element.text)
            if source_element.tail:
                raise ExtraTailError("tu", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "tuv":
                        self.content.append(Tuv(item))
                    if item.tag == "note":
                        self.notes.append(Note(item))
                    if item.tag == "prop":
                        self.props.append(Prop(item))
            else:
                if content is not None:
                    self.content.extend(content)
                if props is not None:
                    self.props.extend(props)
                if notes is not None:
                    self.notes.extend(notes)


class Tmx(TmxElement):
    _allowed_content = (Tu,)
    _required_attributes = (TmxAttributes.version,)
    _optional_attributes = tuple()
    version: str = "1.4"
    header: Header

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        header: Optional[Header] = None,
        content: Optional[Iterable[Tu]] = None,
    ) -> None:
        super().__init__(source_element=source_element)
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("tmx", source_element.text)
            if source_element.tail:
                raise ExtraTailError("tmx", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "body":
                        for tu in item:
                            if tu.tag == "tu":
                                self.content.append(Tu(tu))
                    if item.tag == "header":
                        self.header = Header(item)
            else:
                if content is not None:
                    self.content.extend(content)
                    if header is not None:
                        self.header = header
                    else:
                        self.header = Header()

    @override
    def to_element(self) -> _Element:
        elem = Element("tmx", version=self.version)
        elem.append(self.header.to_element())
        body = Element("body")
        elem.append(body)
        for tu in self.content:
            body.append(tu.to_element())
        return elem

    def export_to_file(self, file: str | bytes | PathLike | StringIO | BytesIO) -> None:
        ElementTree(self.to_element()).write(
            file, encoding=self.header.oencoding, xml_declaration=True
        )
