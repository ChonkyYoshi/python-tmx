from __future__ import annotations

from logging import getLogger
from typing import MutableSequence, Optional

from lxml.etree import Element, _Element

from PythonTmx.core import TmxElement, TmxElements
from PythonTmx.helpers import make_xml_string

logger = getLogger("PythonTmx Logger")


class TmxInvalidAttributeError(Exception): ...


class TmxInvalidContentError(Exception): ...


class TmxParseError(Exception): ...


class Sub(TmxElement): ...


class Bpt(TmxElement): ...


class Ept(TmxElement): ...


class It(TmxElement): ...


class Ph(TmxElement): ...


class Hi(TmxElement):
    """
    Delimits a section of text that has special meaning,
    such as a terminological unit, a proper name,
    an item that should not be modified, etc.

    Required attributes:
        None.

    Optional attributes:
        x: Optional[int | str]
        type: Optional[str]

    Contents:
        MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    """

    __attributes: tuple[str, ...] = ("x", "type")
    x: Optional[int | str]
    type: Optional[str]
    content: MutableSequence[str | Bpt | Ept | It | Ph | Hi]

    def __init__(
        self,
        lxml_element: Optional[_Element] = None,
        **kwargs,
    ) -> None:
        """
        Constructs a Hi object either from parsing a lxml `_Element` object or
        from scratch by passing it attributes and its content as keywords
        arguments

        Note: values passed as keyword arguments override values parsed from
        lxml_element if it's not None.

        Keyword Arguments:
            lxml_element {Optional[_Element]} -- A lxml `_Element` to construct
            the object from. (default: {None})

        """

        def parse_element(lxml_element: _Element) -> None:
            """
            helper function for __init__ to parse a lxml_element and convert
            the element's children to their corresponding objects if needed

            Arguments:
                lxml_element {_Element} -- A lxml `_Element` to get content from

            Raises:
                ValueError: if an unknown or forbidden tag is found
            """
            if lxml_element.text:
                self.content.append(lxml_element.text)
            if len(lxml_element):
                for child in lxml_element:
                    match child.tag:
                        case "bpt":
                            self.content.append(Bpt(child))
                        case "ept":
                            self.content.append(Ept(child))
                        case "it":
                            self.content.append(It(child))
                        case "Hi":
                            self.content.append(Hi(child))
                        case "ph":
                            self.content.append(Ph(child))
                        case _:
                            if child.tag in (TmxElements):
                                raise TmxParseError(
                                    f"'{child.tag}' element is not allowed inside a hi"
                                )
                            raise TmxParseError(f"Unknown element '{child.tag}' found")
                    if child.tail:
                        self.content.append(child.tail)

        match lxml_element:
            case None:
                self.content = kwargs.get("content", [])
            case _Element():
                if kwargs.get("content"):
                    self.content = kwargs["content"]
                else:
                    self.content = []
                    parse_element(lxml_element)
            case _:
                raise TypeError(
                    "lxml_element must be of type _Element or None, "
                    f"not '{type(lxml_element).__name__}'"
                )

        self.x = (
            kwargs.get("x", None)
            if "x" in kwargs.keys()
            else (lxml_element.get("x", None) if lxml_element is not None else None)
        )
        self.type = (
            kwargs.get("type", None)
            if "type" in kwargs.keys()
            else (lxml_element.get("type", None) if lxml_element is not None else None)
        )

    def serialize_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        try:
            if self.x is not None:
                int(self.x)
                attrs["x"] = str(self.x)
        except ValueError as e:
            raise TmxInvalidAttributeError(
                "Value for attribute 'x' cannot be converted to an int."
                f"current value: {self.x}"
            ) from e
        except TypeError as e:
            raise TmxInvalidAttributeError(
                "Type of attribute 'x' cannot be converted to an int."
                f"current type: {type(self.x).__name__}"
            ) from e
        if self.type is not None:
            if not isinstance(self.type, str):
                raise TmxInvalidAttributeError(
                    "Value for attribute 'type' must be a string"
                )
            attrs["type"] = self.type
        if not isinstance(self.content, MutableSequence):
            raise TmxInvalidContentError(
                "content must be a MutableMutableSequence not "
                f"'{type(self.content).__name__}'"
            )
        return attrs

    def to_element(
        self,
    ) -> _Element:
        if self.content is None:
            raise TmxInvalidContentError("content cannot be None")
        elif not isinstance(self.content, MutableSequence):
            raise TmxInvalidContentError(
                "content must be a non-empty MutableSequence, "
                f"not {type(self.content).__name__}"
            )
        elif not len(self.content):
            raise TmxInvalidContentError("content must be a non-empty MutableSequence")
        lxml_element: _Element = Element(_tag="hi", attrib=self.serialize_attributes())
        for item in self.content:
            match item:
                case str() if not lxml_element.text:
                    lxml_element.text = item
                case str() if lxml_element.text and not len(lxml_element):
                    lxml_element.text += item
                case str() if not lxml_element[-1].tail:
                    lxml_element[-1].tail = item
                case str() if lxml_element[-1].tail:
                    lxml_element[-1].tail += item
                case Bpt() | Ept() | It() | Ph() | Hi():
                    lxml_element.append(item.to_element())
                case _:
                    raise TmxInvalidContentError(
                        f"'{type(item).__name__}'"
                        "objects are not allowed inside a Hi object"
                    )
        return lxml_element

    def to_string(self) -> str:
        if self.content is None:
            raise TmxInvalidContentError("content cannot be None")
        elif not isinstance(self.content, MutableSequence):
            raise TmxInvalidContentError(
                "content must be a non-empty MutableSequence, "
                f"not {type(self.content).__name__}"
            )
        elif not len(self.content):
            raise TmxInvalidContentError("content must be a non-empty MutableSequence")
        final: str = "<hi"
        final += "".join(
            [
                f' {make_xml_string(key)}="{make_xml_string(val)}"'
                for key, val in self.serialize_attributes().items()
            ]
        )
        final += ">"
        for item in self.content:
            match item:
                case str():
                    final += item
                case Bpt() | Ept() | It() | Ph() | Hi():
                    final += item.to_string()
                case _:
                    raise TmxInvalidContentError(
                        f"'{type(item).__name__}'"
                        "objects are not allowed inside a Hi object"
                    )
        final += "</hi>"
        return final


Hi(type=13, strict=True)
