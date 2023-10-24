"""note object definition"""
from dataclasses import dataclass
from xml.etree.ElementTree import Element


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

    value: str
    lang: str | None = None
    oencoding: str | None = None

    def _to_element(self) -> Element:
        """Returns a <note> xml Element with tmx-compliant attribute names and values and all props and notes as xml SubElements"""
        note_elem: Element = Element("header", attrib=self._make_attrib())
        note_elem.text = self.value
        return note_elem

    def _make_attrib(self) -> dict[str, str]:
        """For use in _to_element function, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        if self.lang is not None:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
        if self.oencoding is not None:
            attrs["o-encoding"] = self.oencoding
        return attrs
