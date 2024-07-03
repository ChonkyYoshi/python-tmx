from __future__ import annotations

from logging import getLogger
from typing import MutableSequence, Optional

from lxml.etree import Element, _Element

from PythonTmx.core import TmxElement
from PythonTmx.helpers import make_xml_string

logger = getLogger("PythonTmx Logger")


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
        strict: bool = False,
        **attribs,
    ) -> None:
        """
        Initializes a Hi object.

        Can be used either from scratch or by passing it a lxml `_Element`.
        Note that it is possible to override any values parsed from the
        lxml `_Element` by passing the desired values as a function argument.

        Enabling strict mode during initialization will validate that *only*
        attributes defined in the tmx spec are present, and that their value
        is of the required type.

        Args:
            lxml_element (Optional[_Element], optional):
            the lxml `_Element` to parse data from. Defaults to None.
            strict (bool, optional): enables strict mode. Defaults to False.

        Raises:

        """

        def set_attributes(
            lxml_element: Optional[_Element], strict: bool, **attribs
        ) -> None:
            if lxml_element:
                self.x = (
                    lxml_element.get("x", None)
                    if not attribs.get("x", None)
                    else attribs.get("x", None)
                )
                self.type = (
                    lxml_element.get("type", None)
                    if not attribs.get("type", None)
                    else attribs.get("type", None)
                )
            else:
                self.x = attribs.get("x", None)
                self.type = attribs.get("type", None)
                try:
                    if self.x is not None:
                        self.x = int(self.x)
                except (ValueError, TypeError) as e:
                    if strict:
                        e.add_note(
                            "Value for attribute 'x' must be convertible to an int"
                        )
                        raise e
                    logger.warning(
                        "Value for attribute 'x' is not convertible to an int"
                    )
                try:
                    assert isinstance(self.type, (str, type(None)))
                except AssertionError:
                    raise TypeError("Value for attribute 'type' must be a string")

        def parse_element(lxml_element: _Element, strict: bool) -> None:
            if lxml_element.text:
                self.content.append(lxml_element.text)
            if len(lxml_element):
                for child in lxml_element:
                    match child.tag:
                        case "bpt":
                            self.content.append(Bpt(child, strict))
                        case "ept":
                            self.content.append(Ept(child, strict))
                        case "it":
                            self.content.append(It(child, strict))
                        case "Hi":
                            self.content.append(Hi(child, strict))
                        case "ph":
                            self.content.append(Ph(child, strict))
                        case _:
                            if strict:
                                raise ValueError(
                                    "Unknown element encountered when parsing "
                                    f"lxml_element children. '{child.tag}' "
                                    "elements are not allowed inside a hi element"
                                )
                            logger.warning(f"ignoring unknown element '{child.tag}'")
                    if child.tail:
                        self.content.append(child.tail)

        match lxml_element:
            case None:
                self.content = []
            case _Element():
                parse_element(lxml_element, strict)
            case _ if attribs.get("content", None):
                self.content = attribs["content"]
                attribs.pop("content")
            case _:
                raise TypeError(
                    "lxml_element must be of type _Element or None, "
                    f"not '{type(lxml_element).__name__}'"
                )
        set_attributes(lxml_element, strict, **attribs)

    def serialize_attributes(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val = getattr(self, key, None)
            if val is not None:
                match key, val:
                    case "x", int():
                        attrs["x"] = str(val)
                    case "x", str():
                        try:
                            attrs["x"] = str(int(val))
                        except ValueError:
                            raise ValueError(
                                "Attribute 'x' must be convertible to an int. "
                                "Cannot serialize attributes"
                            )
                    case "x", _:
                        raise TypeError(
                            "Unsupported type for attribute 'x'. Expected a string "
                            f"or an int, but got {type(key).__name__}. "
                            "Cannot serialize attributes"
                        )
                    case "type", str():
                        attrs["type"] = val
                    case "type", _:
                        raise TypeError(
                            "Unsupported type for attribute 'type'. "
                            f"Expected a string but got {type(key).__name__}. "
                            "Cannot serialize attributes"
                        )
        return attrs

    def to_element(
        self,
    ) -> _Element:
        hi_elem: _Element = Element(_tag="hi", attrib=self.serialize_attributes())
        for child in self.content:
            match child:
                case str() if not hi_elem.text:
                    hi_elem.text = child
                case str() if hi_elem.text and not len(hi_elem):
                    hi_elem.text += child
                case str() if not hi_elem[-1].tail:
                    hi_elem[-1].tail = child
                case str() if hi_elem[-1].tail:
                    hi_elem[-1].tail += child
                case Bpt() | Ept() | It() | Ph() | Hi():
                    hi_elem.append(child.to_element())
                case _:
                    raise TypeError(
                        "Only strings, Bpt, Ept, It, Ph, or Hi object "
                        "are allowed inside a hi element but "
                        f"encountered a '{type(child).__name__}'"
                    )
        return hi_elem

    def to_string(self) -> str:
        final: str = "<hi"
        final += "".join(
            [
                f' {make_xml_string(key)}="{make_xml_string(val)}"'
                for key, val in self.serialize_attributes().items()
            ]
        )
        final += ">"
        for child in self.content:
            match child:
                case str():
                    final += child
                case Bpt() | Ept() | It() | Ph() | Hi():
                    final += child.to_string()
                case _:
                    raise TypeError(
                        "Only strings, Bpt, Ept, It, Ph, or Hi object "
                        "are allowed inside a hi element but "
                        f"encountered '{type(child).__name__}'"
                    )
        final += "</hi>"
        return final


Hi(lxml_element=123, x=[2, 1], strict=False)
