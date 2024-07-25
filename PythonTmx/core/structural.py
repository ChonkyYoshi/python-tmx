from datetime import datetime
from io import BytesIO, StringIO
from os import PathLike
from typing import (
    Any,
    Generator,
    Iterable,
    Literal,
    MutableSequence,
    Optional,
    Type,
    override,
)

from lxml.etree import Element, ElementTree, _Element

from PythonTmx.core.base import (
    ExtraTailError,
    ExtraTextError,
    TmxAttributes,
    TmxElement,
)
from PythonTmx.core.inline import Bpt, Ept, Hi, It, Ph, Sub, Ut

__all__ = ["Header", "Seg", "Tmx", "Tu", "Tuv", "Prop", "Note", "Map", "Ude"]


class Prop(TmxElement):
    """
    <prop>

    Property - The `Prop` element is used to define the various properties of
    its parent element (or of the document when used in the `Header` element).
    These properties are not defined by the standard.

    As the tool parsing the tmx file is fully responsible for handling
    the content of a `Prop` element you can use it in any way you wish.
    For example the content can be a list of instructions your tool can parse,
    not only a simple text.

    It is the responsibility of each tool provider to publish the types and
    values of the properties it uses. If the tool exports unpublished
    properties types, their values should begin with the prefix "x-".

    Required attributes:
    ----
        ####  type: str
         the kind of data the element represents.

    Optional attributes:
    ----
        ####  xmllang: str
         the locale of the element's content.
        A language code as described in the [RFC 3066].
        This declared value is considered to apply to all elements within
        the content of the element where it is specified, unless overridden
        with another instance of the xml:lang attribute.
        Unlike the other TMX attributes, the values for xml:lang are not
        case-sensitive.
        Note: PythonTmx currently DOES NOT checks that the value for xmllang is
        a correct language code. If you want this feature, please open an issue
        on GitHub.
        * oencoding str -- the original or preferred code set of the data

    Contents: a str
    """

    text: str
    type: str
    xmllang: Optional[str]
    oencoding: Optional[str]
    _required_attributes = (TmxAttributes.type,)
    _optional_attributes = TmxAttributes.xmllang, TmxAttributes.oencoding
    _allowed_content = (str,)

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        text: Optional[str] = None,
        type: Optional[str] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            type=type,
            xmllang=xmllang,
            oencoding=oencoding,
        )
        if source_element is not None:
            if source_element.text is not None:
                self.text = source_element.text
            elif text is not None:
                self.text = text
            else:
                self.text = str()
        elif text is not None:
            self.text = text
        else:
            self.text = str()

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Prop elements are not allowed to have content. "
                "Please use the 'text' property instead"
            )
        return super().__setattr__(name, value)

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        if str in mask:
            yield self.text


class Note(TmxElement):
    """
    <note>

    Note - The `Note` element is used for comments.

    Required attributes:
    ---- None.

    Optional attributes:
    ----
        ####  xmllang: str
         the locale of the element's content.
        A language code as described in the [RFC 3066].
        This declared value is considered to apply to all elements within
        the content of the element where it is specified, unless overridden
        with another instance of the xml:lang attribute.
        Unlike the other TMX attributes, the values for xml:lang are not
        case-sensitive.
        Note: PythonTmx currently DOES NOT checks that the value for xmllang is
        a correct language code. If you want this feature, please open an issue
        on GitHub.
        * oencoding str -- the original or preferred code set of the data

    Contents: a str
    """

    text: str
    xmllang: Optional[str]
    oencoding: Optional[str]
    _required_attributes = tuple()
    _optional_attributes = TmxAttributes.xmllang, TmxAttributes.oencoding
    _allowed_content = (str,)

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        text: Optional[str] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            xmllang=xmllang,
            oencoding=oencoding,
        )
        if source_element is not None:
            if source_element.text is not None:
                self.text = source_element.text
            elif text is not None:
                self.text = text
            else:
                self.text = str()
        elif text is not None:
            self.text = text
        else:
            self.text = str()

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Note elements are not allowed to have content. "
                "Please use the 'text' property instead"
            )
        return super().__setattr__(name, value)

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        if str in mask:
            yield self.text


class Map(TmxElement):
    """
    <map/>

    Map - The `Map` element is used to specify a user-defined character and
    some of its properties.

    Required attributes:
    ----
        ####  unicode: str
          Unicode character value of a <map/> element.
        Its value must be a valid Unicode value (including values in the
        Private Use areas) in hexadecimal format. For example: unicode="#xF8FF".

    Optional attributes:
    ----
        ####  code: str
         The code-point value corresponding to the unicode
        character of a given `Map` element. A Hexadecimal value prefixed with
        "#x". For example: code="#x9F".
        ####  ent: str
         the entity name of the character of a given `Map` element
        ####  subst: str
         an alternative string for the character defined in a
        given `Map` element

    Note: at least one of the optional attributes should be specified.
    If the code attribute is specified, the parent `Ude` element must specify
    a base attribute.

    Contents: None
    """

    unicode: str
    code: Optional[str]
    ent: Optional[str]
    subst: Optional[str]
    _required_attributes = (TmxAttributes.unicode,)
    _optional_attributes = TmxAttributes.code, TmxAttributes.ent, TmxAttributes.subst
    _allowed_content = tuple()

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        unicode: Optional[str] = None,
        code: Optional[str] = None,
        ent: Optional[str] = None,
        subst: Optional[str] = None,
    ) -> None:
        super().__init__(unicode=unicode, code=code, ent=ent, subst=subst)
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("map", source_element.text)
            if source_element.tail:
                raise ExtraTailError("map", source_element.tail)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Map elements are empty elements and are not allowed to have content"
            )
        return super().__setattr__(name, value)

    def iter(self):
        return


class Ude(TmxElement):
    """
    <ude>

    User-Defined Encoding - The `Ude` element is used to specify a set of
    user-defined characters and/or, optionally their mapping
    from Unicode to the user-defined encoding.

    Note: PythonTmx DOES NOT make use of the encoding defined in `Ude` and `Map`.
    These are purely for use by CAT Tools.

    Required attributes:
    ----
        ####  name: str
         the name of a `Ude` element. Its value is not defined
        by the standard, but tools providers should publish the values they use.

    Optional attributes:
    ----
        ####  base: str
         the encoding upon which the re-mapping of the `Ude`
        element is based.
        Note: required if one or more of the `Map` elements contains a
        code attribute

    Contents: a list `Map` elements
    """

    maps: list[Map]
    name: str
    base: Optional[str]
    _required_attributes = (TmxAttributes.name,)
    _optional_attributes = (TmxAttributes.base,)
    _allowed_content = tuple()

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[MutableSequence[Map]] = None,
        name: Optional[str] = None,
        base: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            name=name,
            base=base,
        )
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("ude", source_element.text)
            if source_element.tail:
                raise ExtraTailError("ude", source_element.tail)
            if len(source_element):
                for map_ in source_element:
                    self.maps.append(Map(map_))
            else:
                if content is not None:
                    self.maps.extend(content)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Ude elements are not allowed to have content. "
                "Please use the 'maps' property instead"
            )
        return super().__setattr__(name, value)

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        if Map in mask or TmxElement in mask:
            yield from self.maps


class Header(TmxElement):
    """
    <header>

    File header - The `Header` element contains information pertaining
    to the whole document.

    ## Required attributes:
    ####  creationtool: str
    The tool that created the TMX document.
    ####  creationtoolversion: str
    The version of the tool that created the TMX document.
    ####  segtype: "block" | "paragraph" | "sentence" | "phrase"
    The kind of segmentation used in the `Tu` element.
    ####  otmf: str
    The format of the translation memory file from which the TMX documen
    or segment thereof have been generated.
    ####  adminlang: str
    The default language for the administrative and informative elements
    `Note` and `Prop`.
    ####  srclang: str
    The language of the source text.
    Can be set to "*all*" if any language inside a tu can be used a source.
    ####  datatype: str
    The type of data

    ## Optional attributes:
    #### oencoding: str
    The original or preferred code set of the data
    ####  creationdate: str | datetime
    The date of creation of the element.
    ####  creationid: str
    The identifier of the user who created the element
    ####  changedate: str | datetime
    The date of the last modification of
    #### changeid: str
    The identifier of the user who modified the element last

    ## Contents: None
    """

    _required_attributes = (
        TmxAttributes.creationtool,
        TmxAttributes.creationtoolversion,
        TmxAttributes.segtype,
        TmxAttributes.otmf,
        TmxAttributes.adminlang,
        TmxAttributes.srclang,
        TmxAttributes.datatype,
    )
    _optional_attributes = (
        TmxAttributes.oencoding,
        TmxAttributes.creationdate,
        TmxAttributes.creationid,
        TmxAttributes.changedate,
        TmxAttributes.changeid,
    )
    _allowed_content = tuple()
    creationtool: str
    creationtoolversion: str
    segtype: Literal["block", "paragraph", "sentence", "phrase"]
    otmf: Optional[str]
    adminlang: Optional[str]
    srclang: Optional[str]
    datatype: Optional[str]
    oencoding: Optional[str]
    creationdate: Optional[str | datetime]
    creationid: Optional[str]
    changedate: Optional[str | datetime]
    changeid: Optional[str]
    props: MutableSequence[Prop]
    notes: MutableSequence[Note]
    udes: MutableSequence[Ude]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        udes: Optional[Iterable[Ude]] = None,
        creationtool: Optional[str] = None,
        creationtoolversion: Optional[str] = None,
        segtype: Optional[Literal["block", "paragraph", "sentence", "phrase"]] = None,
        otmf: Optional[str] = None,
        adminlang: Optional[str] = None,
        srclang: Optional[str] = None,
        datatype: Optional[str] = None,
        oencoding: Optional[str] = None,
        creationdate: Optional[str | datetime] = None,
        creationid: Optional[str] = None,
        changedate: Optional[str | datetime] = None,
        changeid: Optional[str] = None,
        notes: Optional[Iterable[Note]] = None,
        props: Optional[Iterable[Prop]] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            creationtool=creationtool,
            creationtoolversion=creationtoolversion,
            segtype=segtype,
            otmf=otmf,
            adminlang=adminlang,
            srclang=srclang,
            datatype=datatype,
            oencoding=oencoding,
            creationdate=creationdate,
            creationid=creationid,
            changedate=changedate,
            changeid=changeid,
        )
        self.notes, self.props, self.udes = [], [], []
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("header", source_element.text)
            if source_element.tail:
                raise ExtraTailError("header", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "ude":
                        self.udes.append(Ude(item))
                    if item.tag == "note":
                        self.notes.append(Note(item))
                    if item.tag == "prop":
                        self.props.append(Prop(item))
            else:
                if udes is not None:
                    self.udes.extend(udes)
                if props is not None:
                    self.props.extend(props)
                if notes is not None:
                    self.notes.extend(notes)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "header elements are not allowed to have content. "
                "Please use the 'udes', 'props' or 'notes' properties instead"
            )
        return super().__setattr__(name, value)

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        if Note in mask or TmxElement in mask:
            yield from self.notes
        if Prop in mask or TmxElement in mask:
            yield from self.props
        if Ude in mask or TmxElement in mask:
            yield from self.udes


class Seg(TmxElement):
    _allowed_content = str, Sub, Ut, Ph, It, Hi, Bpt, Ept
    _required_attributes = tuple()
    _optional_attributes = tuple()

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[Iterable[str | Sub | Ut | Ph | It | Hi | Bpt | Ept]] = None,
        datatype: Optional[str] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(source_element=source_element, datatype=datatype, type=type)
        if source_element is not None:
            if source_element.text:
                self._content.append(source_element.text)
            if len(source_element):
                for item in source_element:
                    if item.tag == "bpt":
                        self._content.append(Bpt(item))
                    if item.tag == "ept":
                        self._content.append(Ept(item))
                    if item.tag == "ph":
                        self._content.append(Ph(item))
                    if item.tag == "hi":
                        self._content.append(Hi(item))
                    if item.tag == "it":
                        self._content.append(It(item))
                    if item.tag == "ut":
                        self._content.append(Ut(item))
                    if item.tag == "sub":
                        self._content.append(Sub(source_element=item))
                    if item.tail:
                        self._content.append(item.tail)
        elif content is not None:
            self._content.extend(content)

    def __iter__(self) -> Generator[str | TmxElement, None, None]:
        yield from self._content

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        for item in self:
            if isinstance(item, str):
                if str in mask:
                    yield item
            else:
                yield from item.iter(mask)


class Tuv(TmxElement):
    _required_attributes = (TmxAttributes.xmllang,)
    _optional_attributes = (
        TmxAttributes.oencoding,
        TmxAttributes.datatype,
        TmxAttributes.usagecount,
        TmxAttributes.lastusagedate,
        TmxAttributes.creationtool,
        TmxAttributes.creationtoolversion,
        TmxAttributes.creationdate,
        TmxAttributes.creationid,
        TmxAttributes.changedate,
        TmxAttributes.changeid,
        TmxAttributes.otmf,
    )
    segment: Seg
    _allowed_content = tuple()
    xmllang: Optional[str]
    oencoding: Optional[str]
    datatype: Optional[str]
    usagecount: Optional[str]
    lastusagedate: Optional[str]
    creationtool: Optional[str]
    creationtoolversion: Optional[str]
    creationdate: Optional[str]
    creationid: Optional[str]
    changedate: Optional[str]
    changeid: Optional[str]
    otmf: Optional[str]
    props: MutableSequence[Prop]
    notes: MutableSequence[Note]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        segment: Optional[Seg] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
        datatype: Optional[str] = None,
        usagecount: Optional[str] = None,
        lastusagedate: Optional[str] = None,
        creationtool: Optional[str] = None,
        creationtoolversion: Optional[str] = None,
        creationdate: Optional[str] = None,
        creationid: Optional[str] = None,
        changedate: Optional[str] = None,
        changeid: Optional[str] = None,
        otmf: Optional[str] = None,
        notes: Optional[Iterable[Note]] = None,
        props: Optional[Iterable[Prop]] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            xmllang=xmllang,
            oencoding=oencoding,
            datatype=datatype,
            usagecount=usagecount,
            lastusagedate=lastusagedate,
            creationtool=creationtool,
            creationtoolversion=creationtoolversion,
            creationdate=creationdate,
            creationid=creationid,
            changedate=changedate,
            changeid=changeid,
            otmf=otmf,
        )
        self.notes, self.props = [], []
        self.segment = None  # type: ignore
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("tuv", source_element.text)
            if source_element.tail:
                raise ExtraTailError("tuv", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "seg":
                        if self.segment is not None:
                            raise ValueError("Only one seg element per tuv")
                        self.segment = Seg(item)
                    if item.tag == "note":
                        self.notes.append(Note(item))
                    if item.tag == "prop":
                        self.props.append(Prop(item))
            else:
                if segment is not None:
                    self.segment = segment
                if props is not None:
                    self.props.extend(props)
                if notes is not None:
                    self.notes.extend(notes)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Tuv elements are not allowed to have content. "
                "Please use the 'segment' property instead"
            )
        return super().__setattr__(name, value)

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        if Note in mask or TmxElement in mask:
            yield from self.notes
        if Prop in mask or TmxElement in mask:
            yield from self.props
        if Seg in mask or TmxElement in mask:
            yield self.segment
        yield from self.segment.iter(mask)


class Tu(TmxElement):
    _required_attributes = tuple()
    _optional_attributes = (
        TmxAttributes.tuid,
        TmxAttributes.oencoding,
        TmxAttributes.datatype,
        TmxAttributes.usagecount,
        TmxAttributes.lastusagedate,
        TmxAttributes.creationtool,
        TmxAttributes.creationtoolversion,
        TmxAttributes.creationdate,
        TmxAttributes.creationid,
        TmxAttributes.changedate,
        TmxAttributes.segtype,
        TmxAttributes.changeid,
        TmxAttributes.otmf,
        TmxAttributes.srclang,
    )
    _allowed_content = ()
    tuvs: MutableSequence[Tuv]
    tuid: Optional[str]
    xmllang: Optional[str]
    oencoding: Optional[str]
    datatype: Optional[str]
    usagecount: Optional[str]
    lastusagedate: Optional[str]
    creationtool: Optional[str]
    creationtoolversion: Optional[str]
    creationdate: Optional[str]
    creationid: Optional[str]
    changedate: Optional[str]
    segtype: Optional[Literal["block", "paragraph", "sentence", "phrase"]]
    changeid: Optional[str]
    otmf: Optional[str]
    srclang: Optional[str]
    props: MutableSequence[Prop]
    notes: MutableSequence[Note]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        content: Optional[Iterable[Tuv]] = None,
        tuid: Optional[str] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
        datatype: Optional[str] = None,
        usagecount: Optional[str] = None,
        lastusagedate: Optional[str] = None,
        creationtool: Optional[str] = None,
        creationtoolversion: Optional[str] = None,
        creationdate: Optional[str] = None,
        creationid: Optional[str] = None,
        changedate: Optional[str] = None,
        segtype: Optional[Literal["block", "paragraph", "sentence", "phrase"]] = None,
        changeid: Optional[str] = None,
        otmf: Optional[str] = None,
        srclang: Optional[str] = None,
        notes: Optional[Iterable[Note]] = None,
        props: Optional[Iterable[Prop]] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            tuid=tuid,
            xmllang=xmllang,
            oencoding=oencoding,
            datatype=datatype,
            usagecount=usagecount,
            lastusagedate=lastusagedate,
            creationtool=creationtool,
            creationtoolversion=creationtoolversion,
            creationdate=creationdate,
            creationid=creationid,
            changedate=changedate,
            segtype=segtype,
            changeid=changeid,
            otmf=otmf,
            srclang=srclang,
        )
        self.notes, self.props, self.tuvs = [], [], []
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("tu", source_element.text)
            if source_element.tail:
                raise ExtraTailError("tu", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "tuv":
                        self.tuvs.append(Tuv(item))
                    if item.tag == "note":
                        self.notes.append(Note(item))
                    if item.tag == "prop":
                        self.props.append(Prop(item))
            else:
                if content is not None:
                    self.tuvs.extend(content)
                if props is not None:
                    self.props.extend(props)
                if notes is not None:
                    self.notes.extend(notes)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Tu elements are not allowed to have content. "
                "Please use the 'tuvs' property instead"
            )
        return super().__setattr__(name, value)

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        if Note in mask or TmxElement in mask:
            yield from self.notes
        if Prop in mask or TmxElement in mask:
            yield from self.props
        for item in self.tuvs:
            if Tuv in mask or TmxElement in mask:
                yield item
            yield from item.iter(mask)


class Tmx(TmxElement):
    _allowed_content = ()
    _required_attributes = (TmxAttributes.version,)
    _optional_attributes = tuple()
    version: str = "1.4"
    header: Header
    tus: MutableSequence[Tu]

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        header: Optional[Header] = None,
        content: Optional[Iterable[Tu]] = None,
    ) -> None:
        super().__init__(source_element=source_element)
        self.tus = []
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("tmx", source_element.text)
            if source_element.tail:
                raise ExtraTailError("tmx", source_element.tail)
            if len(source_element):
                for item in source_element:
                    if item.tag == "body":
                        for tu in item:
                            if tu.tag == "tu":
                                self.tus.append(Tu(tu))
                    if item.tag == "header":
                        self.header = Header(item)
            else:
                if content is not None:
                    self._content.extend(content)
                    if header is not None:
                        self.header = header
                    else:
                        self.header = Header()

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Tu elements are not allowed to have content. "
                "Please use the 'tuvs' property instead"
            )
        return super().__setattr__(name, value)

    def iter(
        self, mask: Type[Any] | tuple[Type[Any], ...] = (TmxElement, str)
    ) -> Generator[TmxElement | str, None, None]:
        for item in self.tus:
            if Tu in mask or TmxElement in mask:
                yield item
            yield from item.iter(mask)

    @override
    def to_element(self) -> _Element:
        elem = Element("tmx", version=self.version)
        elem.append(self.header.to_element())
        body = Element("body")
        elem.append(body)
        for tu in self.tus:
            body.append(tu.to_element())
        return elem

    def export_to_file(self, file: str | bytes | PathLike | StringIO | BytesIO) -> None:
        ElementTree(self.to_element()).write(
            file,
            xml_declaration=True,
        )
