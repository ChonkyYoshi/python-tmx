from typing import Literal, Optional, Self

from lxml.etree import _Element

from PythonTmx.core.base import TmxAttributes, TmxElement

__all__ = ["Bpt", "Ept", "Hi", "It", "Ph", "Sub", "Ut"]


class Sub(TmxElement): ...


class Bpt(TmxElement):
    """
    <bpt>

    Begin paired tag - The `Bpt` element is used to delimit the beginning of
    a paired sequence of native codes.
    Each `Bpt` has a corresponding `Ept` element within the element it's in.

    Required attributes:
        * i: int | str -- used to pair a `Bpt` elements with `Ept` elements.
        Provides support to markup a possibly overlapping range of codes.

    Optional attributes:
        * x: int | str -- used to pair elements between each `Tuv` element
        of a given `Tu` element.
        Facilitates the pairing of allied codes in source and target text,
        even if the order of code occurrence differs between the two because of
        the translation syntax. Note that an `Ept` element is matched based
        on the x attribute of its corresponding `bpt` element.
        * type: str -- the kind of data the element represents.

    Contents: A list of strings and `Sub` elements
    """

    content: list[Sub | str]
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.i,)
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    i = str | int
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[list[Sub | str]] = None,
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
        elif content is not None:
            self.content.extend(content)


class Ept(TmxElement):
    """
    <ept>

    End paired tag - The `Ept` element is used to delimit the beginning of
    a paired sequence of native codes.
    Each `Ept` has a corresponding `Bpt` element within the element it's in.

    Required attributes:
        * i: int | str -- used to pair a `Bpt` elements with `Ept` elements.
        Provides support to markup a possibly overlapping range of codes.

    Optional attributes: None

    Contents: A list of strings and `Sub` elements
    """

    content: list[Sub | str]
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.i,)
    _optional_attributes = tuple()
    i = str | int

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[list[Sub | str]] = None,
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
        elif content is not None:
            self.content.extend(content)


class It(TmxElement):
    """
    <it>

    Isolated tag - The `It` element is used to delimit a beginning/ending
    sequence of native codes that does not have its corresponding
    ending/beginning within the segment.

    Required attributes:
        * pos: "begin" | "end" -- whether this is a beginning or ending tag

    Optional attributes:
        * x: int | str -- used to pair elements between each `Tuv` element
        of a given `Tu` element.
        Facilitates the pairing of allied codes in source and target text,
        even if the order of code occurrence differs between the two because of
        the translation syntax. Note that an `Ept` element is matched based
        on the x attribute of its corresponding `bpt` element.
        * type: str -- the kind of data the element represents.

    Contents: A list of strings and `Sub` elements
    """

    content: list[Sub | str]
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.pos,)
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    pos: Literal["begin", "end"]
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[list[Sub | str]] = None,
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
        elif content is not None:
            self.content.extend(content)


class Ph(TmxElement):
    """
    <ph>

    Placeholder - The `Ph` element is used to delimit a sequence of native
    standalone codes in the segment.

    Required attributes: None

    Optional attributes:
        * x: int | str -- used to pair elements between each `Tuv` element
        of a given `Tu` element.
        Facilitates the pairing of allied codes in source and target text,
        even if the order of code occurrence differs between the two because of
        the translation syntax. Note that an `Ept` element is matched based
        on the x attribute of its corresponding `bpt` element.
        * type: str -- the kind of data the element represents.
        * assoc: "p", "f", "b" -- whether this is associated with the text
        prior or after:
            - "p": the element is associated with the text preceding the element
            - "f": the element is associated with the text following the element
            - "b": the element is associated with the text on both sides

    Contents: A list of strings and `Sub` elements
    """

    content: list[Sub | str]
    _allowed_content = Sub, str
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.x, TmxAttributes.type, TmxAttributes.assoc
    assoc: Literal["p", "f", "b"]
    x = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[list[Sub | str]] = None,
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
        elif content is not None:
            self.content.extend(content)


class Ut(TmxElement):
    """
    <ut>

    Unknown Tag - The `Ut` element is used to delimit a sequence
    of native unknown codes in the segment.

    This element has been DEPRECATED. Use the guidelines outlined in the
    Rules for Inline Elements section on the official Tmx Documentation
    to choose which inline element to use instead of `Ut`.

    Required attributes: None

    Optional attributes:
        * x: int | str -- used to pair elements between each `Tuv` element
        of a given `Tu` element.
        Facilitates the pairing of allied codes in source and target text,
        even if the order of code occurrence differs between the two because of
        the translation syntax. Note that an `Ept` element is matched based
        on the x attribute of its corresponding `bpt` element.

    Contents: A list of strings and `Sub` elements
    """

    content: list[Sub | str]
    _allowed_content = Sub, str
    _required_attributes = (TmxAttributes.x,)
    _optional_attributes = tuple()
    x = Optional[str | int]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[list[Sub | str]] = None,
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
        elif content is not None:
            self.content.extend(content)


class Hi(TmxElement):
    """
    <hi>

    Highlight - The `Hi` element delimits a section of text that has
    special meaning, such as a terminological unit, a proper name,
    an item that should not be modified, etc.
    It can be used for various processing tasks.
    For example, to indicate to a Machine Translation tool proper names
    that should not be translated; for terminology verification, to mark
    suspect expressions after a grammar checking.

    Required attributes: None

    Optional attributes:
        * x: int | str -- used to pair elements between each `Tuv` element
        of a given `Tu` element.
        Facilitates the pairing of allied codes in source and target text,
        even if the order of code occurrence differs between the two because of
        the translation syntax. Note that an `Ept` element is matched based
        on the x attribute of its corresponding `bpt` element.
        * type: str -- the kind of data the element represents.

    Contents: A list of strings, `Sub`, `Bpt`, `Ept`, `It`, `Ph` or `Hi`.

    Note: each `Bpt` element must have a subsequent corresponding `Ept` element.
    """

    content: list[Bpt | Ept | Ph | It | Ut | Self | str]
    _allowed_content = Bpt, Ept, Ph, It, Ut
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.x, TmxAttributes.type
    i = Optional[str | int]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[list[Bpt | Ept | Ph | It | Ut | Self | str]] = None,
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
                        self.content.append(Hi(item))  # type:ignore
                    if item.tag == "it":
                        self.content.append(It(item))
                    if item.tag == "ut":
                        self.content.append(Ut(item))
                    if item.tail:
                        self.content.append(item.tail)
        elif content is not None:
            self.content.extend(content)


class Sub(TmxElement):  # type: ignore
    """
    <sub>

    Sub-flow - The `Sub` element is used to delimit sub-flow text inside
    a sequence of native code,
    for example: the definition of a footnote or the text of
    title in a HTML anchor element.

    Note that sub-flow are related to segmentation and can cause
    interoperability issues when one tool uses sub-flow within its main segment,
    while another extract the sub-flow text as an independent segment.

    Required attributes: None

    Optional attributes:
        * type: str -- the kind of data the element represents.
        * datatype: str -- the type of data contained in the element.

    Contents: A list of strings, `Sub`, `Bpt`, `Ept`, `It`, `Ph` or `Hi`.

    Note: each `Bpt` element must have a subsequent corresponding `Ept` element.
    """

    content: list[Bpt | Ept | Ph | It | Ut | Self | str]
    _allowed_content = Bpt, Ept, Hi, Ph, It, Ut
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.datatype, TmxAttributes.type
    datatype = Optional[str]
    type = Optional[str]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[list[Bpt | Ept | Ph | It | Ut | Self | str]] = None,
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
                        self.content.append(Hi(item))  # type: ignore
                    if item.tag == "it":
                        self.content.append(It(item))
                    if item.tag == "ut":
                        self.content.append(Ut(item))
                    if item.tail:
                        self.content.append(item.tail)
        elif content is not None:
            self.content.extend(content)
