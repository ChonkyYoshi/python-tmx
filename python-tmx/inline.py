"""inline tags definition"""
from dataclasses import dataclass, field
from typing import Literal

from lxml.etree import Element, _Element


@dataclass(kw_only=True, slots=True)
class run:
    text: str | None = None
    name: str = field(init=False, repr=False)

    def __post_init__(self):
        self.name = self.__class__.__name__

    @property
    def _element(self) -> _Element:
        """Returns a fake <fake> lxml Element to keep document order"""
        run_elem: _Element = Element("fake")
        run_elem.text = self.text
        return run_elem


@dataclass(kw_only=True, slots=True)
class bpt(run):
    i: str | None = None
    x: str | None = None
    bpt_type: str | None = None

    @property
    def _element(self) -> _Element:
        """Returns a <bpt> lxml Element with tmx-compliant attribute names"""
        bpt_elem: _Element = Element("bpt", attrib=self._attrib)
        bpt_elem.text = self.text
        return bpt_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element property, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        attrs["i"] = self.i
        if self.x is not None and self.x != "":
            attrs["x"] = self.x
        if self.bpt_type is not None and self.bpt_type != "":
            attrs["type"] = self.bpt_type
        return attrs


@dataclass(kw_only=True, slots=True)
class ept(run):
    i: str

    @property
    def _element(self) -> _Element:
        """Returns a <ept> lxml Element with tmx-compliant attribute names"""
        ept_elem: _Element = Element("ept", attrib={"i": self.i})
        ept_elem.text = self.text
        return ept_elem


@dataclass(kw_only=True, slots=True)
class hi(run):
    x: str | None = None
    hi_type: str | None = None

    @property
    def _element(self) -> _Element:
        """Returns a <hi> lxml Element with tmx-compliant attribute names"""
        hi_elem: _Element = Element("bpt", attrib=self._attrib)
        hi_elem.text = self.text
        return hi_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element property, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        if self.x is not None:
            attrs["x"] = self.x
        if self.hi_type is not None:
            attrs["type"] = self.hi_type
        return attrs


@dataclass(kw_only=True, slots=True)
class it(run):
    pos: Literal["begin", "end"]
    x: str | None = None
    it_type: str | None = None

    @property
    def _element(self) -> _Element:
        """Returns a <it> lxml Element with tmx-compliant attribute names"""
        it_elem: _Element = Element("it", attrib=self._attrib)
        it_elem.text = self.text
        return it_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element property, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        attrs["pos"] = self.pos
        if self.x is not None:
            attrs["x"] = self.x
        if self.it_type is not None:
            attrs["type"] = self.it_type
        return attrs


@dataclass(kw_only=True, slots=True)
class ph(run):
    x: str | None = None
    ph_type: str | None = None
    assoc: Literal["p", "f", "b"] | None = None

    @property
    def _element(self) -> _Element:
        """Returns a <ph> lxml Element with tmx-compliant attribute names"""
        ph_elem: _Element = Element("ph", attrib=self._attrib)
        ph_elem.text = self.text
        return ph_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element property, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        if self.x is not None:
            attrs["x"] = self.x
        if self.ph_type is not None:
            attrs["type"] = self.ph_type
        if self.assoc is not None:
            attrs["assoc"] = self.assoc
        return attrs
