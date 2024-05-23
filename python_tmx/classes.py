from __future__ import annotations
from datetime import datetime
from typing import Iterable, Literal

type InlineElement = ph | bpt | ept | it | hi | sub | ut


class ph:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
        x: int | None = None,
        type_: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        self.content = content
        self.x = x
        self.type_ = type_
        self.assoc = assoc


class bpt:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
        i: int,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.i = i
        self.x = x
        self.type_ = type_


class ept:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
        i: int,
    ) -> None:
        self.content = content
        self.i = i


class it:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
        pos: Literal["begin", "end"],
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.pos = pos
        self.x = x
        self.type_ = type_


class hi:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.x = x
        self.type_ = type_


class sub:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        self.content = content
        self.datatype = datatype
        self.type_ = type_


class ut:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
        x: int | None = None,
    ) -> None:
        self.content = content
        self.x = x


class seg:
    def __init__(
        self,
        content: str | Iterable[str | InlineElement],
    ) -> None:
        self.content = content


class note:
    def __init__(
        self,
        content: str,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        self.content = content
        self.lang = lang
        self.o_encoding = o_encoding


class prop:
    def __init__(
        self,
        content: str,
        type_: str,
        lang: str | None = None,
        o_encoding: str | None = None,
    ) -> None:
        self.content = content
        self.type_ = type_
        self.lang = lang
        self.o_encoding = o_encoding


class map:
    def __init__(
        self,
        unicode: str,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        self.unicode = unicode
        self.code = code
        self.ent = ent
        self.subst = subst


class ude:
    def __init__(
        self,
        content: Iterable[map],
        name: str,
        base: str | None = None,
    ) -> None:
        self.content = content
        self.name = name
        self.base = base


class tuv:
    def __init__(
        self,
        segment: seg,
        lang: str,
        o_encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: datetime | str | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        changeid: str | None = None,
        o_tmf: str | None = None,
        notes: Iterable[note] | None = None,
        props: Iterable[prop] | None = None,
    ) -> None:
        self.segment = segment
        self.lang = lang
        self.o_encoding = o_encoding
        self.datatype = datatype
        self.usagecount = usagecount
        self.lastusagedate = lastusagedate
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.changeid = changeid
        self.o_tmf = o_tmf
        self.notes = notes
        self.props = props


class tu:
    def __init__(
        self,
        tuvs: Iterable[tuv],
        tuid: int | str | None = None,
        o_encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | str | None = None,
        lastusagedate: datetime | str | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        changeid: str | None = None,
        o_tmf: str | None = None,
        srclang: str | None = None,
        notes: Iterable[note] | None = None,
        props: Iterable[prop] | None = None,
    ) -> None:
        self.tuvs = tuvs
        self.tuid = tuid
        self.o_encoding = o_encoding
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
        self.o_tmf = o_tmf
        self.srclang = srclang
        self.notes = notes
        self.props = props


class header:
    def __init__(
        self,
        creationtool: str,
        creationtoolversion: str,
        segtype: Literal["block", "paragraph", "sentence", "phrase"],
        o_tmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        o_encoding: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        changeid: str | None = None,
        notes: Iterable[note] | None = None,
        props: Iterable[prop] | None = None,
        udes: Iterable[ude] | None = None,
    ) -> None:
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.segtype = segtype
        self.o_tmf = o_tmf
        self.adminlang = adminlang
        self.srclang = srclang
        self.datatype = datatype
        self.o_encoding = o_encoding
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.changeid = changeid
        self.notes = notes
        self.props = props
        self.udes = udes


class tmx:
    def __init__(self, header_: header, tus: Iterable[tu]) -> None:
        self.header_ = header_
        self.tus = tus
