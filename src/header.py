"""header object definition"""
from dataclasses import dataclass, field
from typing import Literal

from lxml.etree import Element, _Element
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

    @property
    def _element(self) -> _Element:
        """Returns a <header> lxml Element with tmx-compliant attributes and all props and notes as xml SubElements"""
        header_elem: _Element = Element("header", attrib=self._attrib)
        for note_obj in self.notes:
            header_elem.append(note_obj._element)
        for prop_obj in self.props:
            header_elem.append(prop_obj._element)
        return header_elem

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
