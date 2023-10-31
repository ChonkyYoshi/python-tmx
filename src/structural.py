"""structural tags definitions"""
from dataclasses import dataclass, field
from lxml.etree import Element, _Element
from typing import Literal
from inline import run
from errors import MissingRequiredAttribute

Segtype = Literal["block", "paragraph", "sentence", "phrase"]


@dataclass(kw_only=True, slots=True)
class note:
    """Note - used for comments.\n
    Attributes:
        - Required:
            - text
        - Optional attributes:
            - lang
            - oencoding\n
    """

    text: str | None = None
    xmllang: str | None = None
    oencoding: str | None = None

    @property
    def _element(self) -> _Element:
        """Returns a <note> lxml Element with tmx-compliant attributes"""
        note_elem: _Element = Element("note", attrib=self._attrib)
        if self.text is None:
            raise MissingRequiredAttribute("Required attribute 'text' missing")
        else:
            note_elem.text = self.text
        note_elem.text = self.text
        return note_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element function, converts object's properties to a tmx-compliant dict of attributes, discards any attribute with a value of None"""
        attrs: dict = {}
        if self.xmllang is not None:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.xmllang
        if self.oencoding is not None:
            attrs["o-encoding"] = self.oencoding
        return attrs


@dataclass(kw_only=True, slots=True)
class prop:
    """Property - used to define the various properties of the parent element (or of the document when used in the header.\n
    These properties are not defined by the standard.\n
    Attributes:
        - Required:
            - text
            - prop_type
        - Optional attributes:
            - lang
            - oencoding\n
    """

    text: str | None = None
    prop_type: str | None = None
    xmllang: str | None = None
    oencoding: str | None = None

    @property
    def _element(self) -> Element:
        """Returns a <prop> lxml Element with tmx-compliant attributes"""
        prop_elem: Element = Element("prop", attrib=self._attrib)
        prop_elem.text = self.text
        return prop_elem

    @property
    def _attrib(self) -> dict[str, str]:
        """For use in _element function, converts object's properties to a tmx-compliant dict of attributes, discards any attribute with a value of None"""
        attrs: dict = {}
        if self.prop_type is None:
            raise MissingRequiredAttribute("Missing required attribute prop_type")
        else:
            attrs["type"] = self.prop_type
        if self.xmllang is not None:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.xmllang
        if self.oencoding is not None:
            attrs["o-encoding"] = self.oencoding
        return attrs


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
        if self.xmllang is None:
            raise MissingRequiredAttribute("Missing required attribute xml:lang")
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
                if attr_name == "otmf":
                    attrs["o-tmf"] = attr_value
                else:
                    attrs[attr_name] = attr_value
        return attrs


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
                if attr_name == "oencoding":
                    attrs["o-encoding"] = attr_value
                elif attr_name == "otmf":
                    attrs["o-tmf"] = attr_value
                else:
                    attrs[attr_name] = attr_value
        return attrs


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
                if attr_name == "oencoding":
                    attrs["o-encoding"] = attr_value
                if attr_name == "otmf":
                    attrs["o-tmf"] = self.otmf
                else:
                    attrs[attr_name] = attr_value
        for attr_name in [
            "creationtool"
            "creationtoolversion"
            "segtype"
            "o-tmf"
            "adminlang"
            "srclang"
            "datatype"
        ]:
            if attr_name not in attrs.keys():
                raise MissingRequiredAttribute(
                    f"Missing Required attribute {attr_name}"
                )
        return attrs


@dataclass(kw_only=True, slots=True)
class tmx:
    header: header
    tus: list[tu]
