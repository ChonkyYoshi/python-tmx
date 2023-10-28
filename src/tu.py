"""tu object definition"""
from dataclasses import dataclass, field
from typing import Literal
from note import note
from prop import prop
from tuv import tuv
from lxml.etree import _Element, Element

type Segtype = Literal["block", "paragraph", "sentence", "phrase"]


@dataclass(kw_only=True, slots=True)
class tu:
    """
    Translation unit - contains the data for a given translation unit.\n
    Attributes:
        - Required:
            - None
        - Optional:
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
            - srclang."""

    tuid: str | None = None
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
    srclang: str | None = None
    notes: list[note] = field(default_factory=list)
    props: list[prop] = field(default_factory=list)
    tuvs: list[tuv] = field(default_factory=list)

    @property
    def _element(self) -> _Element:
        """Returns a <tu> lxml Element with tmx-compliant attributes and all props, notes and tuvs as xml SubElements"""
        tu_elem: _Element = Element("tu", attrib=self._attrib)
        for note_obj in self.notes:
            tu_elem.append(note_obj._element)
        for prop_obj in self.props:
            tu_elem.append(prop_obj._element)
        for tuv_obj in self.tuvs:
            tu_elem.append(tuv_obj._element)
        return tu_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element function, converts object's properties to a tmx-compliant dict of attributes, discards any attribute with a value of None"""
        attrs: dict = {}
        for attr_name in [
            "creationtool"
            "creationtoolversion"
            "segtype"
            "otmf"
            "adminlang"
            "srclang"
            "datatype"
            "oencoding"
            "creationdate"
            "creationid"
            "changedate"
            "changeid"
        ]:
            attr_value = getattr(self, attr_name, None)
            if attr_value is not None:
                match attr_name:
                    case "oencoding":
                        attrs["o-encoding"] = self.oenconding
                    case "otmf":
                        attrs["o-tmf"] = self.otmf
                    case _:
                        attrs[attr_name] = attr_value
        return attrs
