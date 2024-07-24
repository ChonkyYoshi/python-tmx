from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Iterator, Optional, Type

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


class ExtraTextError(Exception):
    def __init__(self, element: str, extra_text: str) -> None:
        super().__init__(
            f"{element} elements are not allowed to have inside text but got {extra_text}"
        )


class ExtraTailError(Exception):
    def __init__(self, element: str, extra_tail: str) -> None:
        super().__init__(
            f"{element} elements are not allowed to have tail text but got {extra_tail}"
        )


class TmxtagError(Exception):
    def __init__(self, expected_tag: str, found_tag: str) -> None:
        super().__init__(
            f"Incorrect tag. Expected <{expected_tag}> but got <{found_tag}>"
        )


class TmxElement:
    content: list
    _required_attributes: tuple[TmxAttributes, ...]
    _optional_attributes: tuple[TmxAttributes, ...]
    _allowed_content: tuple[Type, ...]

    def __init__(self, **kwargs) -> None:
        # only takes care of setting attributes, parsing source_element's content
        # is done in each subclass individually to have custom behavior
        source_element: Optional[_Element] = kwargs.get("source_element", None)
        self.content = []
        if (
            source_element is not None
            and source_element.tag != self.__class__.__name__.lower()
        ):
            raise TmxtagError(self.__class__.__name__.lower(), source_element.tag)
        for attribute in (*self._required_attributes, *self._optional_attributes):
            if source_element is not None:
                self.__setattr__(
                    attribute.name,
                    source_element.get(
                        attribute.value, kwargs.get(attribute.name, None)
                    ),
                )
            else:
                self.__setattr__(attribute.name, kwargs.get(attribute.name, None))

    def xml_attrib(self) -> dict[str, str]:
        """
        Validates that an elements has all its required attributes,
        check that the values are strings or an accepted alternative
        and returns a dict ready to be used as an lxml Element attrib dict.

        Raises TmxError if:
            * a required attribute has a value of None.
            * an attribute with restricted value (e.g. segtype) has an
            incorrect value.
            * the attribute is not a string or an accepted alternative.

        Returns a dict of the element's attributes ready to be serialized by lxml
        """
        xml_attributes: dict[str, str] = dict()
        for attribute in (*self._required_attributes, *self._optional_attributes):
            value = self.__getattribute__(attribute.name)
            if value is None:
                if attribute.name in self._required_attributes:
                    raise TmxError(
                        f"Required attribute {attribute.name} is missing from element {self.__class__.__name__}"
                    ) from AttributeError
                else:
                    continue
            match attribute:
                case TmxAttributes.x | TmxAttributes.i | TmxAttributes.usagecount:
                    if not isinstance(value, int):
                        try:
                            value = int(value)
                        except (TypeError, ValueError) as e:
                            raise TmxError(
                                f"Value for attribute {attribute.name} must an int or convertible to an int but got {value} of type '{value.__class__.__name__}'"
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
                                f"Value for attribute {attribute.name} must be a datetime object or a str in the format of YYYYMMDDTHHMMSSZ but got {value} of type '{value.__class__.__name__}'"
                            ) from e
                    xml_attributes[attribute.value] = value.strftime(r"%Y%m%dT%H%M%SZ")
                case TmxAttributes.assoc:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{value.__class__.__name__}'"
                            )
                        value = value.lower()
                        if value not in ("p", "f", "b"):
                            raise ValueError(
                                f"Expected one of p, f or b but got {value}"
                            )
                        xml_attributes[attribute.value] = value
                    except (TypeError, ValueError) as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str and one of p, f or b but got {value} of type '{value.__class__.__name__}'"
                        ) from e
                case TmxAttributes.pos:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{value.__class__.__name__}'"
                            )
                        value = value.lower()
                        if value not in ("begin", "end"):
                            raise ValueError(
                                f"Expected one of begin or end but got {value}"
                            )
                        xml_attributes[attribute.value] = value
                    except (TypeError, ValueError) as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str and one of begin or end but got {value} of type '{value.__class__.__name__}'"
                        ) from e
                case TmxAttributes.segtype:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{value.__class__.__name__}'"
                            )
                        value = value.lower()
                        if value not in ("block", "paragraph", "sentence", "phrase"):
                            raise ValueError(
                                f"Expected one of block, paragraph, sentence or phrase but got {value}"
                            )
                        xml_attributes[attribute.value] = value
                    except (TypeError, ValueError) as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str and one of block, paragraph, sentence or phrase but got {value} of type '{value.__class__.__name__}'"
                        ) from e
                case TmxAttributes.unicode:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{value.__class__.__name__}'"
                            )
                        if (
                            getattr(self, "code") is None
                            and getattr(self, "ent") is None
                            and getattr(self, "subst") is None
                        ):
                            raise ValueError(
                                "At least one the optional attributes must be set"
                            )
                        xml_attributes[attribute.value] = value
                    except TypeError as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str and at least one the optional attributes must be set but got {value} of type '{value.__class__.__name__}'"
                        ) from e
                    except ValueError as e:
                        raise TmxError(*e.args) from e
                case _:
                    try:
                        if not isinstance(value, str):
                            raise TypeError(
                                f"Expected a str but got '{value.__class__.__name__}'"
                            )
                        xml_attributes[attribute.value] = value
                    except TypeError as e:
                        raise TmxError(
                            f"Value for attribute {attribute.name} must be a str but got {value} of type '{value.__class__.__name__}'"
                        ) from e
        return xml_attributes

    def to_element(self) -> _Element:
        """
        Converts a tmx element to a valid lxml element.

        Raises a TmxError if:
            * the element contains unauthorized children (e.g. Ude elements in
            a Tu element)
            * The element has an imbalanced count of Ept and Bpt elements
            * an Ude element doesn't have a base attribute when one of its Map
            elements has a 'code' attribute

        Returns an lxml element that represents that tmx element
        """
        elem = Element(self.__class__.__name__.lower(), self.xml_attrib())
        bpt, ept = 0, 0
        base, code = False, False
        elem.text = ""
        if hasattr(self, "props"):
            for prop in self.props:
                elem.append(prop.to_element())
        if hasattr(self, "notes"):
            for note in self.notes:
                elem.append(note.to_element())
        if isinstance(self.content, str):
            elem.text = self.content
            return elem
        for item in self.content:
            match item:
                case x if type(x) not in self._allowed_content:
                    raise TmxError(
                        f"'{self.__class__.__name__}' are not allowed to have '{item.__class__.__name__}' elements in their content"
                    )
                case str():
                    if len(elem):
                        if elem[-1].tail:
                            elem[-1].tail += item
                        else:
                            elem[-1].tail = item
                    else:
                        elem.text += item
                case TmxElement():
                    if item.__class__.__name__ == "Bpt":
                        bpt += 1
                    if item.__class__.__name__ == "Ept":
                        ept += 1
                    if hasattr(item, "base"):
                        base = True
                    if hasattr(item, "code"):
                        base = True
                    elem.append(item.to_element())
        if bpt - ept > 0:
            raise TmxError(
                f"Element '{self.__class__.__name__}' has {bpt - ept} bpt element without their corresponding ept elements"
            )
        elif bpt - ept < 0:
            raise TmxError(
                f"Element '{self.__class__.__name__}' has {ept - bpt} ept element without their corresponding bpt elements"
            )
        if code and not base:
            raise TmxError(
                "Ude element 'base' attribute cannot be None as at least one of its Map elements has a 'code' attribute"
            )
        return elem

    def iter_text(self) -> Iterator[str]:
        """
        Opposite of iter_element, recursively iterates over an element and yields
        any str
        """
        if isinstance(self.content, str):
            yield self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    yield item
                else:
                    yield from item.iter_text()

    def iter_element(
        self,
    ) -> Iterator[TmxElement]:
        """
        Opposite of iter_text, recursively iterates over an element and
        yields all Tmx elements it finds.
        """
        if isinstance(self.content, str):
            pass
        else:
            for item in self.content:
                if not isinstance(item, str):
                    yield item
                    yield from item.iter()
