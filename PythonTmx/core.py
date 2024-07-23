from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Generator, MutableSequence

from lxml.etree import Element, _Element


class TmxAttributes(Enum):
    adminlang = "adminlang"
    assoc = "assoc"
    base = "base"
    changedate = "changedate"
    changeid = "changeid"
    code = "code"
    creationdate = "creationdate"
    creationid = "creationid"
    creationtool = "creationtool"
    creationtoolversion = "creationtoolversion"
    datatype = "datatype"
    ent = "ent"
    i = "i"
    lastusagedate = "lastusagedate"
    name = "name"
    oencoding = "o-encoding"
    otmf = "o-tmf"
    pos = "pos"
    segtype = "segtype"
    srclang = "srclang"
    subst = "subst"
    tuid = "tuid"
    type = "type"
    unicode = "unicode"
    usagecount = "usagecount"
    version = "version"
    x = "x"
    xmllang = "{http://www.w3.org/XML/1998/namespace}lang"


class TmxError(Exception):
    pass


class TmxElement:
    content: MutableSequence[TmxElement | str] | str
    _required_attributes: tuple[TmxAttributes, ...]
    _optional_attributes: tuple[TmxAttributes, ...]

    def xml_attrib(self) -> dict[str, str]:
        xml_attributes: dict[str, str] = dict()
        for attribute in self._required_attributes:
            value = self.__getattribute__(attribute.name)
            if value is None:
                raise ValueError(
                    f"Required attribute {attribute.name} is missing from element {self.__class__.__name__}"
                )
            match attribute:
                case TmxAttributes.x | TmxAttributes.i | TmxAttributes.usagecount:
                    if not isinstance(value, int):
                        try:
                            value = int(value)
                        except (TypeError, ValueError) as e:
                            raise TmxError(
                                f"Value for attribute {attribute.name} must an int or convertible to an int but got {value} of type '{type(value).__name__}'"
                            ) from e
                    xml_attributes[attribute.value] = str(value)
                case (
                    TmxAttributes.creationdate
                    | TmxAttributes.changedate
                    | TmxAttributes.lastusagedate
                ):
                    if not isinstance(value, datetime):
                        try:
                            value = datetime.strptime(value, r"%Y%m%dT%H%M%SZ")
                        except (ValueError, TypeError) as e:
                            raise TmxError(
                                f"Value for attribute {attribute.name} must be a datetime object or a str in the format of YYYYMMDDTHHMMSSZ but got {value} of type '{type(value).__name__}'"
                            ) from e
                    xml_attributes[attribute.value] = value.strftime(r"%Y%m%dT%H%M%SZ")
                case TmxAttributes.assoc:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{type(value).__name__}'"
                            )
                        value = value.lower()
                        if value not in ("p", "f", "b"):
                            raise ValueError(
                                f"Expected one of p, f or b but got {value}"
                            )
                        xml_attributes[attribute.value] = value
                    except (TypeError, ValueError) as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str and one of p, f or b but got {value} of type '{type(value).__name__}'"
                        ) from e
                case TmxAttributes.pos:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{type(value).__name__}'"
                            )
                        value = value.lower()
                        if value not in ("begin", "end"):
                            raise ValueError(
                                f"Expected one of begin or end but got {value}"
                            )
                        xml_attributes[attribute.value] = value
                    except (TypeError, ValueError) as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str and one of begin or end but got {value} of type '{type(value).__name__}'"
                        ) from e
                case TmxAttributes.segtype:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{type(value).__name__}'"
                            )
                        value = value.lower()
                        if value not in ("block", "paragraph", "sentence", "phrase"):
                            raise ValueError(
                                f"Expected one of block, paragraph, sentence or phrase but got {value}"
                            )
                        xml_attributes[attribute.value] = value
                    except (TypeError, ValueError) as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str and one of block, paragraph, sentence or phrase but got {value} of type '{type(value).__name__}'"
                        ) from e
                case _:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{type(value).__name__}'"
                            )
                        xml_attributes[attribute.value] = value
                    except TypeError as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str but got {value} of type '{type(value).__name__}'"
                        ) from e
        return xml_attributes

    def to_element(self) -> _Element:
        elem = Element(self.__class__.__name__, self.xml_attrib())
        elem.text = ""
        for item in self.content:
            match item:
                case str():
                    if len(elem):
                        if elem[-1].tail:
                            elem[-1].tail += item
                        else:
                            elem[-1].tail = item
                    else:
                        elem.text += item
                case TmxElement():
                    elem.append(item.to_element())
        return elem

    def iter_text(self) -> Generator[str, None, None]:
        if isinstance(self.content, str):
            yield self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    yield item
                else:
                    yield from item.iter_text()

    def iter(
        self,
    ) -> Generator[TmxElement, None, None]:
        if isinstance(self.content, str):
            pass
        else:
            for item in self.content:
                if not isinstance(item, str):
                    yield item
                    yield from item.iter()
