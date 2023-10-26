"""note object definition"""
from dataclasses import dataclass
from xml.etree.ElementTree import Element


@dataclass(kw_only=True, slots=True)
class prop:
    """Property - used to define the various properties of the parent element (or of the document when used in the header.\n
    These properties are not defined by the standard.\n
    Attributes:
        - Required:
            - value
            - prop_type
        - Optional attributes:
            - lang
            - oencoding\n
    """

    value: str
    prop_type: str
    xmllang: str | None = None
    oencoding: str | None = None

    def _to_element(self) -> Element:
        """Returns a <prop> xml Element with tmx-compliant attribute names and values and all props and notes as xml SubElements"""
        prop_elem: Element = Element("prop", attrib=self._make_attrib())
        prop_elem.text = self.value
        return prop_elem

    def _make_attrib(self) -> dict[str, str]:
        """For use in _to_element function, converts object's properties to a tmx-compliant dict of attributes"""
        attrs: dict = {}
        attrs["type"] = self.prop_type
        if self.xmllang is not None:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.xmllang
        if self.oencoding is not None:
            attrs["o-encoding"] = self.oencoding
        return attrs
