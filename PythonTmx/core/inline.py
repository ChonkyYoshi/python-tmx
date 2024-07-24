from typing import Literal, Optional

from lxml.etree import _Element

from PythonTmx.core.base import TmxAttributes, TmxElement

__all__ = ["Bpt", "Ept", "Hi", "It", "Ph", "Sub", "Ut"]


class Sub(TmxElement): ...


class Bpt(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.i,)
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    i = str | int
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        i: Optional[str | int] = None,
        x: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            i=i,
            x=x,
            type=type,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Ept(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.i,)
    _optional_attributes = tuple()
    i = str | int

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        i: Optional[str | int] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            i=i,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class It(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.pos,)
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    pos: Literal["begin", "end"]
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        pos: Optional[Literal["begin", "end"]] = None,
        x: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            pos=pos,
            x=x,
            type=type,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Ph(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.x, TmxAttributes.type, TmxAttributes.assoc
    assoc: Literal["p", "f", "b"]
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        assoc: Optional[Literal["p", "f", "b"]] = None,
        x: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            assoc=assoc,
            x=x,
            type=type,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Ut(TmxElement):
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.x,)
    _optional_attributes = tuple()
    x = Optional[str | int]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        x: Optional[str | int] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            x=x,
        )
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    self.content.append(Sub(source_element=item))
                    if item.tail:
                        self.content.append(item.tail)


class Hi(TmxElement):
    _allowed_content = Bpt, Ept, Ph, It, Ut
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    i = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        i: Optional[str | int] = None,
        type: Optional[str] = None,
    ) -> None:
        self._allowed_content += (Hi,)  # type: ignore
        super().__init__(source_element=source_element, i=i, type=type)
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    if item.tag == "bpt":
                        self.content.append(Bpt(item))
                    if item.tag == "ept":
                        self.content.append(Ept(item))
                    if item.tag == "ph":
                        self.content.append(Ph(item))
                    if item.tag == "hi":
                        self.content.append(Hi(item))
                    if item.tag == "it":
                        self.content.append(It(item))
                    if item.tag == "ut":
                        self.content.append(Ut(item))
                    if item.tail:
                        self.content.append(item.tail)


class Sub(TmxElement):  # type: ignore
    _allowed_content = Bpt, Ept, Hi, Ph, It, Ut
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.datatype, TmxAttributes.type
    datatype = Optional[str]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        datatype: Optional[str] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(source_element=source_element, datatype=datatype, type=type)
        if source_element is not None:
            if source_element.text:
                self.content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    if item.tag == "bpt":
                        self.content.append(Bpt(item))
                    if item.tag == "ept":
                        self.content.append(Ept(item))
                    if item.tag == "ph":
                        self.content.append(Ph(item))
                    if item.tag == "hi":
                        self.content.append(Hi(item))
                    if item.tag == "it":
                        self.content.append(It(item))
                    if item.tag == "ut":
                        self.content.append(Ut(item))
                    if item.tail:
                        self.content.append(item.tail)
