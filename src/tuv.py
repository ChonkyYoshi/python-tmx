"""tuv object definition"""
from dataclasses import dataclass, field
from typing import Literal

from lxml.etree import Element, _Element
from note import note
from prop import prop
from run import run

type Segtype = Literal["block", "paragraph", "sentence", "phrase"]


@dataclass(kw_only=True, slots=True)
class tuv:
    """
    Translation Unit Variant - specifies text in a given language.\n
    Attributes:
        - Required:
            - xmllang
        - Optional
            - tuid
            - oencoding
            - datatype
            - usagecount
            - lastusagedate
            - creationtool
            - creationtoolversion
            - creationdate
            - creationid
            - changedate
            - segtype
            - changeid
            - otmf
            - srclang.\n"""

    xmllang: str
    tuid: str | None = None
    oencoding: str | None = None
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
    runs: list[run] = field(default_factory=list)

    @property
    def _element(self) -> _Element:
        """Returns a <tuv> lxml Element with tmx-compliant attributes and all props, notes as xml SubElements. The list of runs is converted to a <seg> SubElement"""
        tuv_elem: _Element = Element("tuv", attrib=self._attrib)
        for note_obj in self.notes:
            tuv_elem.append(note_obj._element)
        for prop_obj in self.props:
            tuv_elem.append(prop_obj._element)
        seg_elem: _Element = Element("seg")
        for i in self.runs:
            seg_elem.append(i._element)
        a: _Element = seg_elem[0]
        if a.tag == "fake":
            seg_elem.text = a.text
            seg_elem.remove(a)
        _run: _Element
        for _run in seg_elem.iter():
            if _run.tag == "fake":
                if _run.getprevious().tail is not None:
                    _run.getprevious().tail += _run.text
                else:
                    _run.getprevious().tail = _run.text
                seg_elem.remove(_run)
        tuv_elem.append(seg_elem)
        return tuv_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element property, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        for attr_name in [
            "xmllang",
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
        ]:
            attr_value = getattr(self, attr_name, None)
            if attr_value is not None:
                match attr_name:
                    case "xmllang":
                        attrs[
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        ] = self.xmllang
                    case "otmf":
                        attrs["o-tmf"] = self.otmf
                    case _:
                        attrs[attr_name] = attr_value
        return attrs
