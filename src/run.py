"""run object definition"""
from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True, slots=True)
class run:
    text: str


@dataclass(kw_only=True, slots=True)
class bpt(run):
    i: str
    x: str | None = None
    bpt_type: str | None = None


@dataclass(kw_only=True, slots=True)
class ept(run):
    i: str


@dataclass(kw_only=True, slots=True)
class hi(run):
    x: str | None = None
    hi_type: str | None = None


@dataclass(kw_only=True, slots=True)
class it:
    pos: Literal["begin", "end"]
    x: str | None = None
    it_type: str | None = None


@dataclass(kw_only=True, slots=True)
class ph(run):
    x: str | None = None
    ph_type: str | None = None
    assoc: Literal["p", "f", "b"] | None = None
