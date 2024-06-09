from __future__ import annotations

from datetime import datetime
from re import MULTILINE, match
from typing import Iterable, Literal
from xml.etree.ElementTree import Element

from PythonTmx.errors import IncorrectTagError, MissingRequiredAttributeError
from PythonTmx.structural import Header, Note, Prop


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
            except ValueError:
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
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
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
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
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
            except ValueError:
                pass
            self.i = i if i is not None else xml_element.get("i")
            try:
                self.i = int(self.i)
            except ValueError:
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
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
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
            except ValueError:
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
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
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
            except ValueError:
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
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
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
            except ValueError:
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
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
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
            except ValueError:
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
                        raise TypeError(
                            f"Expected a string or a Sub object but found {type(elem)}"
                        )
        return element


class Seg:
    def __init__(
        self,
        xml_element: Element | None = None,
        content: Iterable[str | Bpt | Ept | It | Ph | Hi] | str | None = None,
    ) -> None:
        if not isinstance(xml_element, Element):
            self.content = content
        else:
            if xml_element.tag != "seg":
                raise IncorrectTagError(
                    found_element=xml_element, expected_element="seg"
                )
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
        element: Element = Element("seg")
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


class Tuv:
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
        segment: Seg | None = None,
        lang: str | None = None,
        o_encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: datetime | str | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        changeid: str | None = None,
        o_tmf: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "tuv":
                    raise IncorrectTagError(
                        found_element=xml_element.tag, expected_element="tuv"
                    )
                if xml_element.text is not None and not match(
                    r"^[\n\s]+$", xml_element.text, flags=MULTILINE
                ):
                    raise ValueError(
                        f"<tuv> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case "segment":
                            self.segment = Seg(xml_element=xml_element.find("seg"))
                        case "lang":
                            self.lang = xml_element.get(
                                "{http://www.w3.org/XML/1998/namespace}lang"
                            )
                        case (
                            "datatype"
                            | "creationtool"
                            | "creationtoolversion"
                            | "creationid"
                            | "changeid"
                        ):
                            self.__setattr__(attr, xml_element.get(attr))
                        case "creationdate" | "changedate" | "lastusagedate":
                            try:
                                self.__setattr__(
                                    attr,
                                    datetime.strptime(
                                        xml_element.get(attr.replace("_", "-")),
                                        r"%Y%m%dT%H%M%SZ",
                                    ),
                                )
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "o_tmf" | "o_encoding":
                            self.__setattr__(
                                attr, xml_element.get(attr.replace("_", "-"))
                            )
                        case "usagecount":
                            try:
                                self.__setattr__(attr, int(xml_element.get(attr)))
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "props":
                            self.props = [
                                Prop(prop) for prop in xml_element if prop.tag == "prop"
                            ]
                        case "notes":
                            self.notes = [
                                Note(note) for note in xml_element if note.tag == "note"
                            ]
            case None:
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    self.__setattr__(attr, val)
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("tuv")
        for attr, val in vars(self).items():
            if val is None:
                continue
            if attr[1] == "_":
                element.set(attr.replace("_", "-"), val)
                continue
            if isinstance(val, datetime):
                element.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                continue
            if attr == "lang":
                element.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                continue
            if isinstance(val, int):
                element.set(attr, str(val))
                continue
            if isinstance(val, str):
                element.set(attr, val)
                continue
            if isinstance(val, Seg):
                element.append(val.export())
                continue
            if isinstance(val, Iterable):
                element.extend([elem.export() for elem in val])
                continue
        return element


class Tu:
    def __init__(
        self,
        xml_element: Element | None = None,
        notes: Iterable[Note] | None = None,
        props: Iterable[Prop] | None = None,
        tuvs: Iterable[Tuv] | None = None,
        tuid: int | None = None,
        o_encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: datetime | str | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | str | None = None,
        creationid: str | None = None,
        changedate: datetime | str | None = None,
        segtype: Literal["block", "paragraph" | "sentence" | "phrase"] | None = None,
        changeid: str | None = None,
        o_tmf: str | None = None,
        srclang: str | None = None,
    ) -> None:
        match xml_element:
            case Element():
                if xml_element.tag != "tu":
                    raise IncorrectTagError(
                        found_element=xml_element.tag, expected_element="tu"
                    )
                if xml_element.text is not None and not match(
                    r"^[\n\s]+$", xml_element.text, flags=MULTILINE
                ):
                    raise ValueError(
                        f"<tuv> tags are not allowed to have text but element has the following:\n{xml_element.text}"
                    )
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    if val is not None:
                        self.__setattr__(attr, val)
                        continue
                    match attr:
                        case "tuvs":
                            self.tuvs = [
                                Tuv(xml_element=child)
                                for child in xml_element
                                if child.tag == "tuv"
                            ]
                        case (
                            "datatype"
                            | "creationtool"
                            | "creationtoolversion"
                            | "creationid"
                            | "segtype"
                            | "changeid"
                            | "srclang"
                        ):
                            self.__setattr__(attr, xml_element.get(attr))
                        case "creationdate" | "changedate" | "lastusagedate":
                            try:
                                self.__setattr__(
                                    attr,
                                    datetime.strptime(
                                        xml_element.get(attr.replace("_", "-")),
                                        r"%Y%m%dT%H%M%SZ",
                                    ),
                                )
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "o_tmf" | "o_encoding":
                            self.__setattr__(
                                attr, xml_element.get(attr.replace("_", "-"))
                            )
                        case "usagecount" | "tuid":
                            try:
                                self.__setattr__(attr, int(xml_element.get(attr)))
                            except TypeError:
                                self.__setattr__(attr, None)
                        case "props":
                            self.props = [
                                Prop(prop) for prop in xml_element if prop.tag == "prop"
                            ]
                        case "notes":
                            self.notes = [
                                Note(note) for note in xml_element if note.tag == "note"
                            ]
            case None:
                for attr, val in locals().items():
                    if attr in ("self", "xml_element"):
                        continue
                    self.__setattr__(attr, val)
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("tu")
        for attr, val in vars(self).items():
            if val is None:
                continue
            if attr[1] == "_":
                element.set(attr.replace("_", "-"), val)
                continue
            if isinstance(val, datetime):
                element.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                continue
            if isinstance(val, int):
                element.set(attr, str(val))
                continue
            if isinstance(val, str):
                element.set(attr, val)
                continue
            if isinstance(val, Iterable):
                element.extend([elem.export() for elem in val])
                continue
            if isinstance(val, Seg):
                element.append(val.export())
                continue
        return element


class Tmx:
    def __init__(
        self,
        xml_element: Element | None = None,
        header: Header | None = None,
        tus: Iterable[Tu] | None = None,
    ) -> None:
        match xml_element:
            case Element():
                self.tus = [
                    Tu(xml_element=child)
                    for child in xml_element.find("body")
                    if child.tag == "tu"
                ]
                self.header = Header(xml_element=xml_element.find("header"))
            case None:
                self.tus = tus
                self.header = header
            case _:
                raise TypeError(
                    f"`xml_Element` can only be of type Element or None not {type(xml_element)}"
                )

    def export(self) -> Element:
        element: Element = Element("tmx", version="1.4")
        element.append(self.header.export())
        body = Element("body")
        body.extend([tu.export() for tu in self.tus])
        element.append(body)
        return element
