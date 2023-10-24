"""shared classes definitions"""
from lxml.etree import _Element, Element

from abc import ABC
from typing import Any
from re import search

xml = "{http://www.w3.org/XML/1998/namespace}"


class StructuralElement(ABC):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        super().__init__()

    @property
    def _tmx_attrib(self) -> dict:
        attrs: dict = dict()
        for key in vars(self).keys():
            if key == "lang":
                attrs[f"{xml}lang"] = getattr(self, key)
            elif key in ["tmf", "encoding"]:
                attrs[f"o-{key}"] = getattr(self, key)
            elif search(r"\w+_type$", key):
                attrs["type"] = getattr(self, key)
            else:
                attrs[key] = getattr(self, key)
        return attrs

    @property
    def _element(self) -> _Element:
        elem: _Element = Element(self.name)
        for key, value in self._tmx_attrib.items():
            elem.set(key, str(value))
        return elem


class prop(StructuralElement):
    """StructuralElement subclass reprenting a <prop> tag.\n

    Requried attributes:\n
        - prop_type\n
        - value\n
    Optional attributes (None by default):\n
        - lang\n
        - encoding\n
    """

    def __init__(
        self,
        prop_type: str,
        value: Any,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        self.prop_type: str = prop_type
        self.value: Any = value
        self.lang: str | None = lang
        self.encoding: str | None = encoding
        super().__init__()
