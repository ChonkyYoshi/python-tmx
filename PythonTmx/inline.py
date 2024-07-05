from __future__ import annotations

from logging import getLogger
from typing import MutableSequence, Optional, Self

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


class Hi(InlineElement):
    """
    Delimits a section of text that has special meaning,
    such as a terminological unit, a proper name,
    an item that should not be modified, etc.

    Required attributes:
        None.

    Optional attributes:
        x: int | str
        type: str

    Contents:
        MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    """

    _content: MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    _allowed_attributes = ("x", "type")
    _allowed_children = (Bpt, Ept, Self, It, Ph)

    def __init__(
        self,
        lxml_element: Optional[_Element] = None,
        content: Optional[MutableSequence] = None,
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

        if lxml_element is None:
            for attribute in self._allowed_attributes:
                self.__setattr__(attribute, kwargs.get(attribute, None))
            self._content = content if content is not None else []
        elif isinstance(lxml_element, _Element):
            for attribute in self._allowed_attributes:
                if attribute in kwargs.keys():
                    self.__setattr__(attribute, kwargs.get(attribute, None))
                else:
                    self.__setattr__(attribute, lxml_element.get(attribute, None))
            if content is not None:
                self._content = content
            else:
                self._content = []
                parse_element(lxml_element)
        else:
            raise TypeError(
                f"expected lxml_element to be an _Element not "
                f"'{type(lxml_element).__name__}'"
            )
