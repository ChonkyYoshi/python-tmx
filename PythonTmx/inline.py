from __future__ import annotations

from logging import getLogger
from typing import (
    Literal,
    MutableSequence,
    Optional,
)

from PythonTmx.core import ElementLike, InlineElement

logger = getLogger("PythonTmx Logger")


class Sub(InlineElement):
    _content: MutableSequence[str | Ph | It | Ept | Bpt | Hi]
    _allowed_attributes = (
        "datatype",
        "type",
    )
    _allowed_children = ("Ph", "It", "Ept", "Bpt", "Hi")
    i: Optional[int]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[
            Optional[MutableSequence[str | Ph | It | Ept | Bpt | Hi]]
        ] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if xml_element.text:
                self._content.append(xml_element.text)
            if len(xml_element):
                for child in xml_element:
                    match child.tag:
                        case "bpt":
                            self._content.append(Bpt(child))
                        case "ept":
                            self._content.append(Ept(child))
                        case "it":
                            self._content.append(It(child))
                        case "hi":
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
            self.i = kwargs.get("i", None)
        else:
            self.x = kwargs.get("x", xml_element.get("x", None))
            self.type = kwargs.get("type", xml_element.get("type", None))
            self.i = kwargs.get("i", xml_element.get("i", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.i is None:
            raise AttributeError("Attribute 'i' is required")
        try:
            val = int(self.i)
            attr_dict["i"] = str(val)
        except ValueError:
            raise ValueError(
                f"attribute 'i' must be a number but {val} "
                "cannot be converted to an int"
            )
        if self.type is not None:
            if not isinstance(self.type, str):
                raise TypeError(
                    "attribute 'type' must be a str but got "
                    f"'{type(self.type).__name__}'"
                )
            attr_dict["type"] = self.type
        if self.x is not None:
            try:
                val = int(self.x)
                attr_dict["x"] = str(val)
            except ValueError:
                raise ValueError(
                    f"attribute 'x' must be a number but {val} "
                    "cannot be converted to an int"
                )
        return attr_dict


class Ept(InlineElement):
    _content: MutableSequence[str | Sub]
    _allowed_attributes = ("i",)
    _allowed_children = ("Sub",)
    i: Optional[int]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Sub]] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if xml_element.text:
                self._content.append(xml_element.text)
            if len(xml_element):
                for child in xml_element:
                    match child.tag:
                        case "sub":
                            self._content.append(Sub(child))
                        case _:
                            raise ValueError(f"found unexpected '{child.tag}' tag")
                    if child.tail:
                        self._content.append(child.tail)

        if xml_element is None:
            self._content = content if content is not None else []
            self.i = kwargs.get("i", None)
        else:
            self.i = kwargs.get("i", xml_element.get("i", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.i is None:
            raise AttributeError("Attribute 'i' is required")
        try:
            val = int(self.i)
            attr_dict["i"] = str(val)
        except ValueError:
            raise ValueError(
                f"attribute 'i' must be a number but {val} "
                "cannot be converted to an int"
            )
        return attr_dict


class Bpt(InlineElement):
    _content: MutableSequence[str | Sub]
    _allowed_attributes = ("x", "type", "i")
    _allowed_children = ("Sub",)
    i: Optional[int]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Sub]] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if xml_element.text:
                self._content.append(xml_element.text)
            if len(xml_element):
                for child in xml_element:
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
            self.i = kwargs.get("i", None)
        else:
            self.x = kwargs.get("x", xml_element.get("x", None))
            self.type = kwargs.get("type", xml_element.get("type", None))
            self.i = kwargs.get("i", xml_element.get("i", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.i is None:
            raise AttributeError("Attribute 'i' is required")
        try:
            val = int(self.i)
            attr_dict["i"] = str(val)
        except ValueError:
            raise ValueError(
                f"attribute 'i' must be a number but {val} "
                "cannot be converted to an int"
            )
        if self.type is not None:
            if not isinstance(self.type, str):
                raise TypeError(
                    "attribute 'type' must be a str but got "
                    f"'{type(self.type).__name__}'"
                )
            attr_dict["type"] = self.type
        if self.x is not None:
            try:
                val = int(self.x)
                attr_dict["x"] = str(val)
            except ValueError:
                raise ValueError(
                    f"attribute 'x' must be a number but {val} "
                    "cannot be converted to an int"
                )
        return attr_dict


class It(InlineElement):
    _content: MutableSequence[str | Sub]
    _allowed_attributes = ("x", "type", "pos")
    _allowed_children = ("Sub",)
    x: Optional[int]
    type: Optional[str]
    pos: Optional[Literal["begin", "end"]]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Sub]] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if xml_element.text:
                self._content.append(xml_element.text)
            if len(xml_element):
                for child in xml_element:
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
            self.pos = kwargs.get("pos", None)
        else:
            self.x = kwargs.get("x", xml_element.get("x", None))
            self.type = kwargs.get("type", xml_element.get("type", None))
            self.pos = kwargs.get("pos", xml_element.get("pos", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.type is not None:
            if not isinstance(self.type, str):
                raise TypeError(
                    "attribute 'type' must be a str but got "
                    f"'{type(self.type).__name__}'"
                )
            attr_dict["type"] = self.type
        if self.x is not None:
            try:
                val = int(self.x)
                attr_dict["x"] = str(val)
            except ValueError:
                raise ValueError(
                    f"attribute 'x' must be a number but {val} "
                    "cannot be converted to an int"
                )
        if self.pos is not None:
            if not isinstance(self.pos, str):
                raise TypeError(
                    "attribute 'pos' must be a str but got "
                    f"'{type(self.pos).__name__}'"
                )
            if self.pos.lower() not in ("begin", "end"):
                raise ValueError(
                    "attribute 'pos' must be one 'begin', or 'end' but "
                    f"got {self.pos}"
                )
            attr_dict["pos"] = self.pos.lower()
        return attr_dict


class Ph(InlineElement):
    _content: MutableSequence[str | Sub]
    _allowed_attributes = ("x", "type", "assoc")
    _allowed_children = ("Sub",)
    x: Optional[int]
    type: Optional[str]
    assoc: Optional[Literal["p", "f", "b"]]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Sub]] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if xml_element.text:
                self._content.append(xml_element.text)
            if len(xml_element):
                for child in xml_element:
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
            self.type = kwargs.get("type", xml_element.get("type", None))
            self.assoc = kwargs.get("assoc", xml_element.get("assoc", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.type is not None:
            if not isinstance(self.type, str):
                raise TypeError(
                    "attribute 'type' must be a str but got "
                    f"'{type(self.type).__name__}'"
                )
            attr_dict["type"] = self.type
        if self.x is not None:
            try:
                val = int(self.x)
                attr_dict["x"] = str(val)
            except ValueError:
                raise ValueError(
                    f"attribute 'x' must be a number but {val} "
                    "cannot be converted to an int"
                )
        if self.assoc is not None:
            if not isinstance(self.assoc, str):
                raise TypeError(
                    "attribute 'assoc' must be a str but got "
                    f"'{type(self.assoc).__name__}'"
                )
            if self.assoc.lower() not in ("f", "b", "p"):
                raise ValueError(
                    "attribute 'assoc' must be one 'f', 'b' or 'p' but "
                    f"got {self.assoc}"
                )
            attr_dict["assoc"] = self.assoc.lower()
        return attr_dict


class Hi(InlineElement):
    _content: MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    _allowed_attributes = ("x", "type")
    _allowed_children = ("Bpt", "Ept", "Self", "It", "Ph")
    x: Optional[int]
    type: Optional[str]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str | Ph | It | Ept | Bpt | Hi]] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if xml_element.text:
                self._content.append(xml_element.text)
            if len(xml_element):
                for child in xml_element:
                    match child.tag:
                        case "bpt":
                            self._content.append(Bpt(child))
                        case "ept":
                            self._content.append(Ept(child))
                        case "it":
                            self._content.append(It(child))
                        case "hi":
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
            self.type = kwargs.get("type", xml_element.get("type", None))
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.type is not None:
            if not isinstance(self.type, str):
                raise TypeError(
                    "attribute 'type' must be a str but got "
                    f"'{type(self.type).__name__}'"
                )
            attr_dict["type"] = self.type
        if self.x is not None:
            try:
                val = int(self.x)
                attr_dict["x"] = str(val)
            except ValueError:
                raise ValueError(
                    f"attribute 'x' must be a number but {val} "
                    "cannot be converted to an int"
                )
        return attr_dict
