"""note object definition"""
from dataclasses import dataclass
from lxml.etree import Element, _Element


@dataclass(kw_only=True, slots=True)
class note:
    """Note - used for comments.\n
    Attributes:
        - Required:
            - value
        - Optional attributes:
            - lang
            - oencoding\n
    """

    text: str
    xmllang: str | None = None
    oencoding: str | None = None

    @property
    def _element(self) -> _Element:
        """Returns a <note> lxml Element with tmx-compliant attributes"""
        note_elem: _Element = Element("note", attrib=self._attrib)
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
