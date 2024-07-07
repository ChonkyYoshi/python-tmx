from __future__ import annotations

from logging import getLogger
from typing import (
    Any,
    Callable,
    Generator,
    Literal,
    MutableSequence,
    Optional,
    Protocol,
    Self,
)
from xml.etree.ElementTree import Element

from lxml.etree import Element as lxmlElement
from lxml.etree import _Element

from PythonTmx.core import InlineElement

logger = getLogger("PythonTmx Logger")


class TmxInvalidAttributeError(Exception): ...


class TmxInvalidContentError(Exception): ...


class TmxParseError(Exception): ...


class Sub(InlineElement): ...


class Bpt(InlineElement): ...


class Ept(InlineElement): ...


class It(InlineElement): ...


class Ph(InlineElement): ...


class ElementLike(Protocol):
    text: Optional[str]
    tail: Optional[str]

    def __iter__(self) -> Generator[Self, None, None]: ...
    def get(key: str, default: Optional[Any]) -> Any: ...


class Hi(InlineElement):
    _content: MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    _allowed_attributes = ("x", "type", "_content")
    _allowed_children = (Bpt, Ept, Self, It, Ph)
    x: Optional[int]
    type: Optional[str]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Ph | It | Ept | Bpt | Hi]] = None,
        **kwargs,
    ) -> None:
        def parse_element(lxml_element: _Element) -> None:
            self._content = []
            if lxml_element.text:
                self._content.append(lxml_element.text)
            if len(lxml_element):
                for child in lxml_element:
                    match child.tag:
                        case "bpt":
                            self._content.append(Bpt(child))
                        case "ept":
                            self._content.append(Ept(child))
                        case "it":
                            self._content.append(It(child))
                        case "Hi":
                            self._content.append(Hi(child))
                        case "ph":
                            self._content.append(Ph(child))
                        case _:
                            raise TmxParseError(f"found unexpected '{child.tag}' tag")
                    if child.tail:
                        self._content.append(child.tail)

        if xml_element is None:
            self._content = content if content is not None else []
            self.x = kwargs.get("x", None)
            self.type = kwargs.get("type", None)
        else:
            self.x = kwargs.get("x", xml_element.get("x", None))
            self.type = kwargs.get("type", xml_element.get("x", None))
            self._content = (
                content if content is not None else parse_element(xml_element)
            )

    def serialize(
        self,
        method: Literal["str"]
        | Literal["bytes"]
        | Literal["lxml"]
        | Literal["ElementTree"],
    ) -> str | bytes | _Element | Element:
        def _to_string() -> str:
            elem = "<hi"
            if self.x:
                elem += f' x="{str(self.x)}"'
            if self.type:
                elem += f' type"{self.type}"'
            elem += ">"
            if len(self._content):
                elem += "".join(
                    item if isinstance(item, str) else item.serialize("str")
                    for item in self
                )
            elem += "</hi>"
            return elem

        def _to_element(factory: Callable) -> _Element | Element:
            elem = factory("hi")
            elem.text, elem.tail = "", ""
            if self.x:
                elem.set("x", str(self.x))
            if self.type:
                elem.set("type", self.type)
            if len(self._content):
                for item in self._content:
                    match item:
                        case str() if not len(elem):
                            elem.text += item
                        case str():
                            elem[-1].tail += item
                        case _:
                            elem.append(item.serialize(method))
            return elem

        match method:
            case "str":
                return _to_string()
            case "bytes":
                return _to_string().encode()
            case "lxml":
                return _to_element(factory=lxmlElement)
            case "ElementTree":
                return _to_element(factory=Element)
            case _:
                raise ValueError
