from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import enums
import lxml.etree as et


@dataclass
class prop:
    text: str
    prop_type: str
    lang: str
    encoding: str


@dataclass
class note:
    text: str
    lang: str
    encoding: str


@dataclass
class run:
    text: str


@dataclass
class bpt(run):
    i: str | int
    x: str | int
    type: str


@dataclass
class ept(run):
    i: str | int


@dataclass
class hi(run):
    pass


@dataclass
class it(run):
    pos: enums.Pos
    x: int | str
    type: str


@dataclass
class ph(run):
    x: int | str
    type: str
    assoc: enums.Assoc


@dataclass
class tuv:
    runs: list[run]
    lang: str
    encoding: str
    datatype: str
    usagecount: int | str
    lastusagedate: str | datetime
    creationtool: str
    creationtoolversion: str
    creationdate: str | datetime
    creationid: str
    changedate: str | datetime
    changeid: str
    tmf: str
    props: list[prop]
    notes: list[note]


@dataclass
class tu:
    tuvs: list[tuv]
    tuid: str
    encoding: str
    datatype: str
    usagecount: int | str
    lastusagedate: str | datetime
    creationtool: str
    creationtoolversion: str
    creationdate: str | datetime
    creationid: str
    changedate: str | datetime
    changeid: str
    segtype: enums.Segtype
    tmf: str
    srclang: str
    props: list[prop]
    notes: list[note]


@dataclass
class header:
    creationtool: str
    creationtoolversion: str
    segtype: enums.Segtype
    tmf: str
    adminlang: str
    srclang: str
    datatype: str
    encoding: str
    creationdate: str | datetime
    creationid: str
    changedate: str | datetime
    changeid: str
    props: list[prop]
    notes: list[note]


@dataclass
class tmx:
    header: header
    tus: list[tu]
