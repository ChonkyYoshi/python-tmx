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

    text: str
    prop_type: str
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
        attrs["type"] = self.prop_type
        if self.xmllang is not None:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.xmllang
        if self.oencoding is not None:
            attrs["o-encoding"] = self.oencoding
        return attrs
