from __future__ import annotations

from logging import getLogger
from typing import MutableSequence, Optional

from lxml.etree import Element, _Element

from PythonTmx.core import TmxElement
from PythonTmx.helpers import make_xml_string

logger = getLogger()


class Sub(TmxElement): ...


class Bpt(TmxElement): ...


class Ept(TmxElement): ...


class It(TmxElement): ...


class Ph(TmxElement): ...


class Hi(TmxElement):
    __attributes: tuple[str, ...] = ("x", "type")
    x: Optional[int | str]
    type: Optional[str]
    content: MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    unknown_attributes: Optional[dict]

    def __init__(
        self,
        lxml_element: Optional[_Element] = None,
        strict: bool = False,
        **attribs,
    ) -> None:
        def set_attributes(attributes: dict, strict: bool) -> None:
            logger.debug("Setting attributes")
            for attribute in attributes:
                match attribute:
                    case "x":
                        self.x = attributes.get("x")
                    case "type":
                        self.type = attributes.get("type")
                    case _:
                        if strict:
                            raise AttributeError(
                                "extra attributes are not allowed when strict mode is "
                                "enabled"
                            )
                        logger.debug(
                            "Storing unknown attributes "
                            f"{attribute} = {attributes.get(attribute)}"
                        )
                        if not self.unknown_attributes:
                            self.unknown_attributes = {}
                        self.unknown_attributes[attribute] = attributes[attribute]

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
                                    "Forbidden tag encountered when parsing "
                                    f"lxml_element children. '{child.tag}' "
                                    "elements are not allowed inside a hi element"
                                )
                            logger.debug(f"ignoring forbidden element '{child.tag}'")
                    if child.tail:
                        self.content.append(child.tail)

        logger.debug(
            f"Initializing Hi object{" with strict mode enabled." if strict else"."}"
        )
        if lxml_element is None:
            set_attributes(attribs, strict)
            if attribs.get("content"):
                self.content = attribs["content"]
        elif isinstance(lxml_element, _Element):
            parse_element(lxml_element, strict)
            set_attributes(dict(lxml_element.attrib.items()) | attribs, strict)
        else:
            raise TypeError(
                "lxml_element must be an lxml '_Element' object "
                f"or None, not '{type(lxml_element).__name}'"
            )
        logger.debug("Hi object initialized")

    def serialize_attributes(self, export_unknown_attributes: bool) -> dict[str, str]:
        logger.debug(
            "serializing attributes"
            f"{" with keep_unknown enabled." if export_unknown_attributes else"."}"
        )
        attrs: dict[str, str] = {}
        for key in self.__attributes:
            val = getattr(self, key, None)
            if val is not None:
                match key, val:
                    case "x", int():
                        logger.debug("converting self.x back to a str")
                        attrs["x"] = str(val)
                    case "x", str():
                        try:
                            logger.debug("confirming self.x is an int")
                            attrs["x"] = str(int(val))
                        except ValueError:
                            raise ValueError(
                                f"Attribute 'x' must be convertible to an int. "
                                f"Cannot convert {val} to an int"
                            )
                    case "x", _:
                        raise TypeError(
                            "Unsupported type for attribute 'x'. Expected a string "
                            f"or an int, but got {type(key).__name__}"
                        )
                    case "type", str():
                        attrs["type"] = val
                    case "type", _:
                        raise TypeError(
                            "Unsupported type for attribute 'type'. "
                            f"Expected a string but got {type(key).__name__}"
                        )
            else:
                logger.debug(f"attribute {key} has a value of None, skipping")
        logger.debug("tmx_attributes dict created, returning")
        return attrs

    def to_element(
        self,
        export_unknown_attributes: bool = False,
    ) -> _Element:
        logger.debug(
            "calling to_element with "
            f"export_unknown_attributes = {export_unknown_attributes}"
        )
        hi_elem: _Element = Element(
            _tag="hi", attrib=self.serialize_attributes(export_unknown_attributes)
        )
        if export_unknown_attributes:
            if self.unknown_attributes and len(self.unknown_attributes):
                logger.debug(
                    f"Adding {len(self.unknown_attributes)} unknown attributes"
                )
                hi_elem.attrib.update(self.unknown_attributes)
            else:
                logger.debug("No unknown attributes stored for that object")
        if self.content:
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
                            f"encountered '{type(child).__name__}"
                        )
        logger.debug("Hi object successfully converted to a lxml element")
        return hi_elem

    def to_string(self, export_unknown_attributes: bool = False) -> str:
        logger.debug(
            f"calling to_string with keep_unknown_attributes = {export_unknown_attributes}"
        )
        final: str = "<hi"
        final += "".join(
            [
                f' {make_xml_string(str(key))}="{make_xml_string(str(val))}"'
                for key, val in self.serialize_attributes(
                    export_unknown_attributes
                ).items()
            ]
        )

        if export_unknown_attributes:
            if self.unknown_attributes and len(self.unknown_attributes):
                logger.debug(
                    f"Adding {len(self.unknown_attributes)} unknown attributes"
                )
                final += "".join(
                    (
                        f' {make_xml_string(str(key))}="{make_xml_string(str(val))}"'
                        for key, val in self.unknown_attributes.items()
                    )
                )

            else:
                logger.debug("No unknown attributes stored for that object")
        final += ">"
        if self.content:
            for child in self.content:
                match child:
                    case str():
                        final += child
                    case Bpt() | Ept() | It() | Ph() | Hi():
                        logger.debug(
                            f"converting a {type(child).__name__} object to string"
                        )
                        final += child.to_string()
                    case _:
                        raise TypeError(
                            "Only strings, Bpt, Ept, It, Ph, or Hi object "
                            "are allowed inside a hi element but "
                            f"encountered '{type(child).__name__}"
                        )
        final += "</hi>"
        logger.debug("Hi object successfully converted to a string")
        return final


Hi(x=2, strict=True)
