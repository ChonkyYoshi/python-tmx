import re
from typing import MutableSequence, Optional

from PythonTmx.core import ElementLike, TmxElement


class Map(TmxElement):
    _allowed_attributes = ("unicode", "code", "ent", "subst")
    _allowed_children = tuple()
    unicode: Optional[str]
    code: Optional[str]
    ent: Optional[str]
    subst: Optional[str]

    def __init__(self, xml_element: Optional[ElementLike] = None, **kwargs) -> None:
        super().__init__(xml_element, **kwargs)
        if xml_element is not None:
            if len(xml_element):
                raise ValueError("map elements are not allowed to have content")
            if (xml_element.text and not re.match(r"[\n\s]*", xml_element.text)) or (
                xml_element.tail and not re.match(r"[\n\s]*", xml_element.tail)
            ):
                raise ValueError("map elements are not allowed to have text or a tail")

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.unicode is None:
            raise AttributeError("Attribute 'unicode' is required")
        for key in self._allowed_attributes:
            val = getattr(self, key)
            if val is None:
                continue
            if not isinstance(val, str):
                raise TypeError(
                    f"Attribute {key} must be a string but got {type(val).__name__}"
                )
            attr_dict[key] = val
        return attr_dict


class Ude(TmxElement):
    _content: MutableSequence[Map]
    _allowed_attributes = ("name", "base")
    _allowed_children = tuple("Map")
    name: Optional[str]
    base: Optional[str]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[Map]] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if (xml_element.text and not re.match(r"[\n\s]*", xml_element.text)) or (
                xml_element.tail and not re.match(r"[\n\s]*", xml_element.tail)
            ):
                raise ValueError("ude elements are not allowed to have text or a tail")
            if len(xml_element):
                for child in xml_element:
                    match child.tag:
                        case "map":
                            self._content.append(Map(child))
                        case _:
                            raise ValueError(f"found unexpected '{child.tag}' tag")
                    if child.tail:
                        self._content.append(child.tail)

        super().__init__(xml_element, **kwargs)
        if xml_element is None:
            if content:
                self._content = content
            else:
                self._content = []
        else:
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.name is None:
            raise AttributeError("Attribute 'name' is required")
        if not isinstance(self.name, str):
            raise TypeError(
                "Attribute 'name' must be a string but "
                f"got {type(self.name).__name__}"
            )
        attr_dict["name"] = self.name
        if self.base is None:
            for item in self._content:
                if item.code is not None:
                    raise AttributeError(
                        "Value for attribute 'code' cannot be None if at "
                        "least one of its map elements has a value for "
                        "attribute 'code'"
                    )
        elif not isinstance(self.base, str):
            raise TypeError(
                "Attribute 'base' must be a string but "
                f"got {type(self.base).__name__}"
            )
        attr_dict["base"] = "base"
        return attr_dict


class Note(TmxElement):
    _content: MutableSequence[str]
    _allowed_attributes = ("lang", "oencoding")
    _allowed_children = tuple()
    lang: Optional[str]
    oencoding: Optional[str]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(xml_element, **kwargs)
        if xml_element is None:
            if content:
                self._content = content
            else:
                self._content = []
        else:
            if content:
                self._content = content
            else:
                self._content = [xml_element.text] if xml_element.text else []
            if len(xml_element):
                raise ValueError("note elements are not allowed to have content")
            if xml_element.tail and not re.match(r"[\n\s]*", xml_element.tail):
                raise ValueError("note elements are not allowed to have text or a tail")

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.lang is not None:
            if not isinstance(self.lang, str):
                raise TypeError(
                    "Attribute 'lang' must be a string but "
                    f"got {type(self.lang).__name__}"
                )
            attr_dict["{http://www.w3.org/XML/1998/namespace}:lang"] = self.lang
        if self.oencoding is not None:
            if not isinstance(self.oencoding, str):
                raise TypeError(
                    "Attribute 'oencoding' must be a string but "
                    f"got {type(self.oencoding).__name__}"
                )
            attr_dict["o-encoding"] = self.oencoding
        return attr_dict


class Prop(TmxElement):
    _content: MutableSequence[str]
    _allowed_attributes = ("lang", "oencoding", "type")
    _allowed_children = tuple()
    lang: Optional[str]
    oencoding: Optional[str]
    type: Optional[str]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(xml_element, **kwargs)
        if xml_element is None:
            if content:
                self._content = content
            else:
                self._content = []
        else:
            if content:
                self._content = content
            else:
                self._content = [xml_element.text] if xml_element.text else []
            if len(xml_element):
                raise ValueError("prop elements are not allowed to have content")
            if xml_element.tail and not re.match(r"[\n\s]*", xml_element.tail):
                raise ValueError("prop elements are not allowed to have text or a tail")

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.lang is not None:
            if not isinstance(self.lang, str):
                raise TypeError(
                    "Attribute 'lang' must be a string but "
                    f"got {type(self.lang).__name__}"
                )
            attr_dict["{http://www.w3.org/XML/1998/namespace}:lang"] = self.lang
        if self.oencoding is not None:
            if not isinstance(self.oencoding, str):
                raise TypeError(
                    "Attribute 'oencoding' must be a string but "
                    f"got {type(self.oencoding).__name__}"
                )
            attr_dict["o-encoding"] = self.oencoding
        if self.type is not None:
            if not isinstance(self.type, str):
                raise TypeError(
                    "Attribute 'type' must be a string but "
                    f"got {type(self.type).__name__}"
                )
            attr_dict["type"] = self.type
        return attr_dict


class Header(TmxElement):
    _content: MutableSequence[Ude | Prop | Note]
    _allowed_attributes = (
        "creationtool",
        "creationtoolversion",
        "segtype",
        "otmf",
        "adminlang",
        "srclang",
        "datatype",
        "oencoding",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
    )
    _allowed_children = ("Ude", "Note", "Prop")
    lang: Optional[str]
    oencoding: Optional[str]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        content: Optional[MutableSequence[Ude | Prop | Note]] = None,
        **kwargs,
    ) -> None:
        def parse_element(xml_element: ElementLike) -> None:
            self._content = []
            if (xml_element.text and not re.match(r"[\n\s]*", xml_element.text)) or (
                xml_element.tail and not re.match(r"[\n\s]*", xml_element.tail)
            ):
                raise ValueError(
                    "header elements are not allowed to have text or a tail"
                )
            if len(xml_element):
                for child in xml_element:
                    match child.tag:
                        case "ude":
                            self._content.append(Ude(child))
                        case "note":
                            self._content.append(Note(child))
                        case "prop":
                            self._content.append(Prop(child))
                        case _:
                            raise ValueError(f"found unexpected '{child.tag}' tag")

        super().__init__(xml_element, **kwargs)
        if xml_element is None:
            if content:
                self._content = content
            else:
                self._content = []
        else:
            if content:
                self._content = content
            else:
                parse_element(xml_element)

    def serialize_attrs(self) -> dict[str, str]:
        attr_dict: dict[str, str] = dict()
        if self.lang is not None:
            if not isinstance(self.lang, str):
                raise TypeError(
                    "Attribute 'lang' must be a string but "
                    f"got {type(self.lang).__name__}"
                )
            attr_dict["{http://www.w3.org/XML/1998/namespace}:lang"] = self.lang
        if self.oencoding is not None:
            if not isinstance(self.oencoding, str):
                raise TypeError(
                    "Attribute 'oencoding' must be a string but "
                    f"got {type(self.oencoding).__name__}"
                )
            attr_dict["o-encoding"] = self.oencoding
        return attr_dict
