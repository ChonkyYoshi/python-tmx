from __future__ import annotations

from typing import Iterable, Literal
from xml.etree.ElementTree import Element

from PythonTmx.errors import IncorrectTagError, MissingRequiredAttributeError


class Ut:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        x: int | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.content = content
        else:
            if xml_element.tag != "ut":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="ut"
                )
            self.x = x if x is not None else xml_element.get("x")
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("ut")
        if self.x is None:
            pass
        elif isinstance(self.x, (int, str)):
            element.set("x", str(self.x))
        else:
            raise TypeError(
                f"attribute x must be a string or an int not {type(self.x)}"
            )
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="sub",
                            found_element=elem,
                        )
        return element


class Sub:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | Ph | Hi | It] | str | None = None,
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.datatype = datatype
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "sub":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="sub"
                )
            self.datatype = (
                datatype if datatype is not None else xml_element.get("datatype")
            )
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    match child.tag:
                        case "ph":
                            self.content += Ph(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "bpt":
                            self.content += Bpt(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "ept":
                            self.content += Ept(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "hi":
                            self.content += Hi(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "it":
                            self.content += It(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case _:
                            raise IncorrectTagError(
                                found_element=child,
                                expected_element="bpt, ept, ph, hi or it",
                            )

    def export(self) -> Element:
        element: Element = Element("sub")
        if self.datatype is None:
            pass
        elif isinstance(self.datatype, str):
            element.set("datatype", self.datatype)
        else:
            raise TypeError(
                f"attribute datatype must be a string not {type(self.datatype)}"
            )
        if self.type_ is None:
            pass
        elif isinstance(self.type_, str):
            element.set("type", self.type_)
        else:
            raise TypeError(f"attribute type_ must be a string not {type(self.type_)}")
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        element.append(elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="sub",
                            found_element=elem,
                        )
        return element


class Bpt:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.i = i
            self.x = x
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "bpt":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="bpt"
                )
            self.x = x if x is not None else xml_element.get("x")
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass
            self.i = i if i is not None else xml_element.get("i")
            try:
                self.i = int(self.i)
            except (ValueError, TypeError):
                pass
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("bpt")
        if self.i is None:
            raise MissingRequiredAttributeError(element=element, attribute="i")
        elif not isinstance(self.i, (int, str)):
            raise TypeError(
                f"attribute i must be a string or an int not {type(self.x)}"
            )
        else:
            element.set("i", str(self.i))
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", self.x)
        if not isinstance(self.type_, str):
            pass
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="sub",
                            found_element=elem,
                        )
        return element


class Ept:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.i = i
            self.content = content
        else:
            if xml_element.tag != "ept":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="ept"
                )
            self.i = i if i is not None else xml_element.get("i")
            try:
                self.i = int(self.i)
            except (ValueError, TypeError):
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("ept")
        if self.i is None:
            raise MissingRequiredAttributeError(element=element, attribute="i")
        elif not isinstance(self.i, (int, str)):
            raise TypeError(
                f"attribute i must be a string or an int not {type(self.x)}"
            )
        else:
            element.set("i", str(self.i))
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="sub",
                            found_element=elem,
                        )
        return element


class It:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        pos: Literal["begin", "end"] | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.pos = pos
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "it":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="it"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.pos = pos if pos is not None else xml_element.get("pos")
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("it")
        if self.pos is None:
            raise MissingRequiredAttributeError(element=element, attribute="pos")
        elif not isinstance(self.pos, str):
            raise TypeError(f"attribute pos must be a string not {type(self.pos)}")
        elif self.pos not in ("begin", "end"):
            raise ValueError(
                f"attribute pos must be a one of begin or end not {self.pos}"
            )
        else:
            element.set("pos", self.pos)
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", str(self.x))
        if not isinstance(self.type_, str):
            pass
        else:
            element.set("type", self.type_)
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="sub",
                            found_element=elem,
                        )
        return element


class Ph:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.type_ = type_
            self.assoc = assoc
            self.content = content
        else:
            if xml_element.tag != "ph":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="ph"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.assoc = assoc if assoc is not None else xml_element.get("assoc")
            self.type_ = type_ if type_ is not None else xml_element.get("type_")
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail

    def export(self) -> Element:
        element: Element = Element("ph")
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", str(self.x))
        if not isinstance(self.type_, str):
            pass
        else:
            element.set("type", self.type_)
        if not isinstance(self.assoc, str):
            pass
        elif self.assoc not in ("p", "f", "b"):
            raise ValueError(
                f"attribute assoc must be a one of p, f or b not {self.assoc}"
            )
        else:
            element.set("assoc", self.assoc)
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Sub():
                        element.append(elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="sub",
                            found_element=elem,
                        )
        return element


class Hi:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.x = x
            self.type_ = type_
            self.content = content
        else:
            if xml_element.tag != "hi":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="hi"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.type_ = type_ if type_ is not None else xml_element.get("type")
            try:
                self.x = int(self.x)
            except (ValueError, TypeError):
                pass
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = xml_element.text
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    match child.tag:
                        case "ph":
                            self.content += Ph(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "bpt":
                            self.content += Bpt(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "ept":
                            self.content += Ept(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "hi":
                            self.content += Hi(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case "it":
                            self.content += It(xml_element=child)
                            if child.tail is not None:
                                self.content += child.tail
                        case _:
                            raise IncorrectTagError(
                                found_element=child,
                                expected_element="bpt, ept, ph, hi or it",
                            )

    def export(self) -> Element:
        element: Element = Element("hi")
        if not isinstance(self.x, (int, str)):
            pass
        else:
            element.set("x", str(self.x))
        if not isinstance(self.type_, str):
            pass
        else:
            element.set("type", self.type_)
        if isinstance(self.content, str):
            element.text = self.content
        else:
            for elem in self.content:
                match elem:
                    case str() if element.text is None:
                        element.text = elem
                    case str() if not len(element):
                        element.text += elem
                    case str():
                        element[-1].tail = elem
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        element.append(elem.export())
                    case _:
                        raise IncorrectTagError(
                            expected_element="bpt, ept, ph, hi or it",
                            found_element=elem,
                        )
        return element
