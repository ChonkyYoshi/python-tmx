"""tuv object definition"""
from dataclasses import dataclass, field
from typing import Literal
from note import note
from prop import prop
from segment import segment

type Segtype = Literal["block", "paragraph", "sentence", "phrase"]


@dataclass(kw_only=True, slots=True)
class tuv:
    """tuid, o-encoding, datatype, usagecount, lastusagedate, creationtool, creationtoolversion, creationdate, creationid, changedate, segtype, changeid, o-tmf, srclang."""

    xmllang: str | None = None
    oenconding: str | None = None
    datatype: str | None = None
    usagecount: str | None = None
    lastusagedate: str | None = None
    creationtool: str | None = None
    creationtoolversion: str | None = None
    creationdate: str | None = None
    creationid: str | None = None
    changedate: str | None = None
    segtype: Segtype | None = None
    changeid: str | None = None
    otmf: str | None = None
    notes: list[note] = field(default_factory=list)
    props: list[prop] = field(default_factory=list)
    segments: list[segment] = field(default_factory=list)
