from __future__ import annotations

from logging import getLogger
from typing import (
    Callable,
    Literal,
    MutableSequence,
    Optional,
    Self,
)

from PythonTmx.core import ElementLike, InlineElement

logger = getLogger("PythonTmx Logger")


class Sub(InlineElement): ...


class Bpt(InlineElement): ...


class Ept(InlineElement): ...


class It(InlineElement): ...


class Ph(InlineElement):
    _content: MutableSequence[str | Sub]
    _allowed_attributes = ("x", "type", "assoc")
    _allowed_children = (Sub,)
    x: Optional[int]
    type: Optional[str]
    assoc: Optional[Literal["p", "f", "b"]]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Sub]] = None,
        **kwargs,
    ) -> None:
        def parse_element(lxml_element: ElementLike) -> None:
            self._content = []
            if lxml_element.text:
                self._content.append(lxml_element.text)
            if len(lxml_element):
                for child in lxml_element:
                    match child.tag:
                        case "sub":
                            self._content.append(Sub(child))
                        case _:
                            raise ValueError(f"found unexpected '{child.tag}' tag")
                    if child.tail:
                        self._content.append(child.tail)

        if xml_element is None:
            self._content = content if content is not None else []
            self.x = kwargs.get("x", None)
            self.type = kwargs.get("type", None)
            self.assoc = kwargs.get("assoc", None)
        else:
            self.x = kwargs.get("x", xml_element.get("x", None))
            self.type = kwargs.get("type", xml_element.get("x", None))
            self.assoc = kwargs.get("assoc", xml_element.get("assoc", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize(
        self,
        method: Literal["str", "bytes"] | Callable[[str], ElementLike],
    ) -> str | bytes | ElementLike:
        def _serialize_attrs() -> dict[str, str]:
            attr_dict: dict[str, str] = dict()
            for key in self._allowed_attributes:
                val = getattr(self, key)
                match (key, val):
                    case _, None:
                        pass
                    case "x" | "type", str():
                        attr_dict[key] = val
                    case "x", int():
                        attr_dict[key] = str(val)
                    case "assoc", str():
                        if val not in ("p", "f", "b"):
                            raise ValueError(
                                "Attribute 'assoc' must be one of 'p', 'f' "
                                f"or 'b' not {val}"
                            )
                        attr_dict[key] = val

                    case _:
                        raise TypeError(
                            f"unsupported type {type(val).__name__} for attribute {key}"
                        )
            return attr_dict

        def _to_string() -> str:
            elem = "<ph "
            elem += " ".join(
                f'{key}="{val}"' for key, val in _serialize_attrs().items()
            )
            elem += ">"
            if len(self._content):
                elem += "".join(
                    item if isinstance(item, str) else item.serialize("str")
                    for item in self
                )
            elem += "</ph>"
            return elem

        def _to_element(factory: Callable[[str], ElementLike]) -> ElementLike:
            elem = factory("ph")
            elem.text, elem.tail = "", ""
            for key, val in _serialize_attrs().items():
                elem.set(key, val)
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
            case f if callable(f):
                return _to_element(factory=method)
            case _:
                raise ValueError


class Hi(InlineElement):
    _content: MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    _allowed_attributes = ("x", "type")
    _allowed_children = (Bpt, Ept, Self, It, Ph)
    x: Optional[int]
    type: Optional[str]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Ph | It | Ept | Bpt | Hi]] = None,
        **kwargs,
    ) -> None:
        def parse_element(lxml_element: ElementLike) -> None:
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
                            raise ValueError(f"found unexpected '{child.tag}' tag")
                    if child.tail:
                        self._content.append(child.tail)

        if xml_element is None:
            self._content = content if content is not None else []
            self.x = kwargs.get("x", None)
            self.type = kwargs.get("type", None)
        else:
            self.x = kwargs.get("x", xml_element.get("x", None))
            self.type = kwargs.get("type", xml_element.get("x", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize(
        self,
        method: Literal["str", "bytes"] | Callable[[str], ElementLike],
    ) -> str | bytes | ElementLike:
        def _serialize_attrs() -> dict[str, str]:
            attr_dict: dict[str, str] = dict()
            for key in self._allowed_attributes:
                val = getattr(self, key)
                match (key, val):
                    case _, None:
                        pass
                    case "x" | "type", str():
                        attr_dict[key] = val
                    case "x", int():
                        attr_dict[key] = str(val)
                    case _:
                        raise TypeError(
                            f"unsupported type {type(val).__name__} for attribute {key}"
                        )
            return attr_dict

        def _to_string() -> str:
            elem = "<hi "
            elem += " ".join(
                f'{key}="{val}"' for key, val in _serialize_attrs().items()
            )
            elem += ">"
            if len(self._content):
                elem += "".join(
                    item if isinstance(item, str) else item.serialize("str")
                    for item in self
                )
            elem += "</hi>"
            return elem

        def _to_element(factory: Callable[[str], ElementLike]) -> ElementLike:
            elem = factory("hi")
            elem.text, elem.tail = "", ""
            for key, val in _serialize_attrs().items():
                elem.set(key, val)
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
            case f if callable(f):
                return _to_element(factory=method)
            case _:
                raise ValueError
