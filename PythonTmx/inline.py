from __future__ import annotations

from typing import Iterable, Literal
from xml.etree.ElementTree import Element as std_Element

from errors import IncorrectTagError
from lxml.etree import Element as lxml_Element_Factory
from lxml.etree import _Element as lxml_Element_type

__all__ = ["Bpt", "Ept", "Hi", "It", "Ph", "Ut", "Sub"]
type xml_Element = lxml_Element_type | std_Element


class Ut:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Sub] | str | None = [],
        x: int | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "ut":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="ut"
                )
            self.x = x if x is not None else xml_element.get("x")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = [xml_element.text]
            else:
                self.content = []
                if xml_element.text:
                    self.content.append(xml_element.text)
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child.tag, expected_element="sub"
                        )
                    self.content.append(Sub(xml_element=child))
                    if child.tail is not None:
                        self.content.append(child.tail)
        else:
            self.x = x
            self.content = content
        try:
            self.x = int(self.x)
        except (ValueError, TypeError):
            pass

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("ut") if ElementType == "lxml" else std_Element("ut")
        )

        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if child.text is None:
                        elem.text = elem
                    case str() if not len(child):
                        elem.text += elem
                    case str():
                        elem[-1].tail = elem
                    case Sub():
                        elem.append(child.export())
                    case _:
                        raise TypeError("only strings and Sub object are allowed")
        elem.attrib = self.make_attrib_dict()
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        if self.x:
            return {"x": str(self.x)}
        return {}


class Sub:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Bpt | Ept | Ph | Hi | It] | str | None = None,
        datatype: str | None = None,
        type_: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "sub":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="sub"
                )
            self.datatype = (
                datatype if datatype is not None else xml_element.get("datatype")
            )
            self.type_ = type_ if type_ is not None else xml_element.get("type")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = [xml_element.text]
            else:
                self.content = []
                if xml_element.text is not None:
                    self.content.append(xml_element.text)
                for child in xml_element:
                    match child.tag:
                        case "ph":
                            self.content.append(Ph(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "bpt":
                            self.content.append(Bpt(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "ept":
                            self.content.append(Ept(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "hi":
                            self.content.append(Hi(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case "it":
                            self.content.append(It(xml_element=child))
                            if child.tail is not None:
                                self.content.append(child.tail)
                        case _:
                            raise IncorrectTagError(
                                found_element=child.tag,
                                expected_element="bpt, ept, ph, hi or it",
                            )

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("sub") if ElementType == "lxml" else std_Element("sub")
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if elem.text is None:
                        elem.text = elem
                    case str() if not len(elem):
                        elem.text += elem
                    case str():
                        elem[-1].tail = elem
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        elem.append(child.export())
                    case _:
                        raise TypeError(
                            "only strings, Bpt, Ept, Ph, Hi, and It object are allowed"
                        )
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.datatype:
            attrs["datatype"] = self.datatype
        if self.type_:
            attrs["type"] = self.type_
        return attrs


class Bpt:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "bpt":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="bpt"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.i = i if i is not None else xml_element.get("i")
            self.type_ = type_ if type_ is not None else xml_element.get("type")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = [xml_element.text]
            else:
                self.content = []
                if xml_element.text is not None:
                    self.content.append(xml_element.text)
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child.tag, expected_element="sub"
                        )
                    self.content.append(Sub(xml_element=child))
                    if child.tail is not None:
                        self.content.append(child.tail)
        try:
            self.x = int(self.x)
        except (ValueError, TypeError):
            pass
        try:
            self.i = int(self.i)
        except (ValueError, TypeError):
            pass

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("bpt") if ElementType == "lxml" else std_Element("bpt")
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if elem.text is None:
                        elem.text = elem
                    case str() if not len(elem):
                        elem.text += elem
                    case str():
                        elem[-1].tail = elem
                    case Sub():
                        elem.append(child.export())
                    case _:
                        raise TypeError("only strings and Sub object are allowed")
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.i:
            attrs["i"] = str(self.i)
        else:
            raise AttributeError("Required attribute i is missing")
        if self.x:
            attrs["x"] = str(self.x)
        if self.type_:
            attrs["type"] = str(self.type_)
        return attrs


class Ept:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        i: int | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "ept":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="ept"
                )
            self.i = i if i is not None else xml_element.get("i")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = [xml_element.text]
            else:
                self.content = ""
                if xml_element.text is not None:
                    self.content += xml_element.text
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child.tag, expected_element="sub"
                        )
                    self.content += Sub(xml_element=child)
                    if child.tail is not None:
                        self.content += child.tail
        else:
            self.content = content
            self.i = i
        try:
            self.i = int(self.i)
        except (ValueError, TypeError):
            pass

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("ept") if ElementType == "lxml" else std_Element("ept")
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if elem.text is None:
                        elem.text = elem
                    case str() if not len(elem):
                        elem.text += elem
                    case str():
                        elem[-1].tail = elem
                    case Sub():
                        elem.append(child.export())
                    case _:
                        raise TypeError("only strings and Sub object are allowed")
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        if self.i:
            return {"i": str(self.i)}
        else:
            raise AttributeError("Required attribute i is missing")


class It:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        pos: Literal["begin", "end"] | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "it":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="it"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.pos = pos if pos is not None else xml_element.get("pos")
            self.type_ = type_ if type_ is not None else xml_element.get("type")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = [xml_element.text]
            else:
                self.content = []
                if xml_element.text is not None:
                    self.content.append(xml_element.text)
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child.tag, expected_element="sub"
                        )
                    self.content.append(Sub(xml_element=child))
                    if child.tail is not None:
                        self.content.append(child.tail)
        else:
            self.x = x
            self.pos = pos
            self.type_ = type_
            self.content = content
        try:
            self.x = int(self.x)
        except (ValueError, TypeError):
            pass

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("it") if ElementType == "lxml" else std_Element("it")
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if elem.text is None:
                        elem.text = elem
                    case str() if not len(elem):
                        elem.text += elem
                    case str():
                        elem[-1].tail = elem
                    case Sub():
                        elem.append(child.export())
                    case _:
                        raise TypeError(
                            "only strings and Sub object are allowed inside"
                        )
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.pos in ("begin", "end"):
            attrs["pos"] = self.pos
        else:
            raise AttributeError("Required attribute pos must be one of begin or end")
        if self.x:
            attrs["x"] = str(self.x)
        if self.type_:
            attrs["type"] = str(self.type_)
        return attrs


class Ph:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Sub] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        if xml_element is not None:
            if xml_element.tag != "it":
                raise IncorrectTagError(
                    found_element=xml_element.tag, expected_element="it"
                )
            self.x = x if x is not None else xml_element.get("x")
            self.assoc = assoc if assoc is not None else xml_element.get("assoc")
            self.type_ = type_ if type_ is not None else xml_element.get("type")
            if content is not None:
                self.content = content
            elif not len(xml_element):
                self.content = [xml_element.text]
            else:
                self.content = []
                if xml_element.text is not None:
                    self.content.append(xml_element.text)
                for child in xml_element:
                    if child.tag != "sub":
                        raise IncorrectTagError(
                            found_element=child.tag, expected_element="sub"
                        )
                    self.content.append(Sub(xml_element=child))
                    if child.tail is not None:
                        self.content.append(child.tail)
        else:
            self.x = x
            self.type_ = type_
            self.content = content
            self.assoc = assoc
        try:
            self.x = int(self.x)
        except (ValueError, TypeError):
            pass

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("ph") if ElementType == "lxml" else std_Element("ph")
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if elem.text is None:
                        elem.text = elem
                    case str() if not len(elem):
                        elem.text += elem
                    case str():
                        elem[-1].tail = elem
                    case Sub():
                        elem.append(child.export())
                    case _:
                        raise TypeError(
                            "only strings and Sub object are allowed inside"
                        )
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.assoc:
            attrs["assoc"] = self.assoc
        if self.x:
            attrs["x"] = str(self.x)
        if self.type_:
            attrs["type"] = str(self.type_)
        return attrs


class Hi:
    def __init__(
        self,
        xml_element: xml_Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = None,
        x: int | None = None,
        type_: str | None = None,
    ) -> None:
        if xml_element is not None:
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

    def make_element(
        self, ElementType: Literal["lxml", "ElementTree"] = "lxml"
    ) -> xml_Element:
        elem = (
            lxml_Element_Factory("hi") if ElementType == "lxml" else std_Element("hi")
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for child in self.content:
                match child:
                    case str() if elem.text is None:
                        elem.text = elem
                    case str() if not len(elem):
                        elem.text += elem
                    case str():
                        elem[-1].tail = elem
                    case Bpt() | Ept() | Ph() | Hi() | It():
                        elem.append(child.export())
                    case _:
                        raise TypeError(
                            "only strings, Bpt, Ept, Ph, Hi, and It object are allowed"
                        )
        return elem

    def make_attrib_dict(self) -> dict[str, str]:
        attrs = {}
        if self.x:
            attrs["x"] = str(self.x)
        if self.type_:
            attrs["type"] = self.type_
        return attrs
