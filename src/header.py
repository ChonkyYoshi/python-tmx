"""header object definition"""
from dataclasses import dataclass, field
from typing import Literal
from xml.etree.ElementTree import Element
from note import note
from prop import prop


@dataclass(kw_only=True, slots=True)
class header:
    """File header - contains information pertaining to the whole document.\n
    Attributes:
        - Required:
            - creationtool
            - creationtoolversion
            - segtype
            - otmf
            - adminlang
            - srclang
            - datatype.
        - Optional attributes:
            - oencoding
            - creationdate
            - creationid
            - changedate
            - changeid
            - notes
            - props\n
    """

    creationtool: str
    creationtoolversion: str
    segtype: Literal["block", "paragraph", "sentence", "phrase"]
    otmf: str
    adminlang: str
    srclang: str
    datatype: str
    oenconding: str | None = None
    creationdate: str | None = None
    creationid: str | None = None
    changedate: str | None = None
    changeid: str | None = None
    notes: list[note] = field(default_factory=list)
    props: list[prop] = field(default_factory=list)

    def _to_element(self) -> Element:
        """Returns a <header> xml Element with tmx-compliant attribute names and values and all props and notes as xml SubElements"""
        header_elem: Element = Element("header", attrib=self._make_attrib())
        for note_obj in self.notes:
            header_elem.append(note_obj._to_element())
        for prop_obj in self.props:
            header_elem.append(prop_obj._to_element())
        return header_elem

    def _make_attrib(self) -> dict[str, str]:
        """For use in _to_element function, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        for attr in [
            "creationtool",
            "creationtoolversion",
            "segtype",
            "adminlang",
            "srclang",
            "datatype",
            "oenconding",
            "creationdate",
            "creationid",
            "changedate",
            "changeid",
        ]:
            if getattr(self, attr) is not None:
                attrs[attr] = getattr(self, attr)
        if self.otmf is not None:
            attrs["o-tmf"] = self.otmf
        if self.oenconding is not None:
            attrs["o-encoding"] = self.oenconding
        return attrs
