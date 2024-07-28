from csv import writer
from datetime import datetime
from os import PathLike
from typing import (
    Any,
    Generator,
    Iterable,
    Literal,
    MutableSequence,
    Optional,
    override,
)

from lxml.etree import Element, ElementTree, _Element, tostring

from .base import (
    ExtraTailError,
    ExtraTextError,
    TmxAttributes,
    TmxElement,
)
from .inline import Bpt, Ept, Hi, It, Ph, Sub, Ut

__all__ = ["Header", "Seg", "Tmx", "Tu", "Tuv", "Prop", "Note", "Map", "Ude"]


class Prop(TmxElement):
    """
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

    ## Required attributes:
    #### type: str
    The kind of data the element represents.
    ## text: str
    The actual contents of the element. The _content attribute should always be
    set to an empty list.

    ## Optional attributes:
    #### xmllang: str
    The locale of the element's content.
    A language code as described in the [RFC 3066].
    This declared value is considered to apply to all elements within
    the content of the element where it is specified, unless overridden
    with another instance of the xml:lang attribute.
    Unlike the other TMX attributes, the values for xml:lang are not
    case-sensitive.

    Note: PythonTmx currently DOES NOT checks that the value for xmllang is
    a correct language code, simply that the value is a str.
    ## oencoding str -- the original or preferred code set of the data

    Contents: None
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


class Note(TmxElement):
    """
    Note - The `Note` element is used for comments.

    ## Required attributes:
    ### text: str
    The actual contents of the element. The _content attribute should always be
    set to an empty list.

    ## Optional attributes:
    #### xmllang: str
    The locale of the element's content.
    A language code as described in the [RFC 3066].
    This declared value is considered to apply to all elements within
    the content of the element where it is specified, unless overridden
    with another instance of the xml:lang attribute.
    Unlike the other TMX attributes, the values for xml:lang are not
    case-sensitive.

    Note: PythonTmx currently DOES NOT checks that the value for xmllang is
    a correct language code, simply that the value is a str.
    ## oencoding str -- the original or preferred code set of the data

    Contents: None
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
        self.__dict__["_content"] = None
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


class Map(TmxElement):
    """
    Map - The `Map` element is used to specify a user-defined character and
    some of its properties.

    Note: at least one of the optional attributes should be specified.
    If the code attribute is specified, the parent `Ude` element must specify
    a base attribute.

    Note: This element is always empty.

    ## Required attributes:
    #### unicode: str
    Unicode character value of a `Map` element.
    Its value must be a valid Unicode value (including values in the Private
    Use areas) in hexadecimal format. For example: unicode="#xF8FF".

    ## Optional attributes:
    #### code: str
    The code-point value corresponding to the unicode character.
    A Hexadecimal value prefixed with "#x". For example: code="#x9F".
    #### ent: str
    The entity name of the character of a given `Map` element.
    #### subst: str
    An alternative string for the character.

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
        super().__init__(
            source_element=source_element,
            unicode=unicode,
            code=code,
            ent=ent,
            subst=subst,
        )
        self.__dict__["_content"] = None

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Map elements are empty elements and are not allowed to have content"
            )
        return super().__setattr__(name, value)


class Ude(TmxElement):
    """
    User-Defined Encoding - The `Ude` element is used to specify a set of
    user-defined characters and/or, optionally their mapping
    from Unicode to the user-defined encoding.

    Note: PythonTmx DOES NOT make use of the encoding defined in `Ude` and `Map`.
    These are purely for use by external Tools.

    ## Required attributes:
    #### name: str
    The name of a `Ude` element. Its value is not defined by the standard
    but tools providers should publish the values they use.
    #### maps: MutableSequence[Map]
    The actual contents of the element. The _content attribute should always be
    set to an empty list.


    ## Optional attributes:
    #### base: str
    The encoding upon which the re-mapping of the `Ude` element is based.

    Note: required if one or more of the `Map` elements contains a code attribute
    """

    maps: MutableSequence[Map]
    name: str
    base: Optional[str]
    _required_attributes = (TmxAttributes.name,)
    _optional_attributes = (TmxAttributes.base,)
    _allowed_content = tuple()

    def __init__(
        self,
        source_element: Optional[_Element] = None,
        maps: Optional[MutableSequence[Map]] = None,
        name: Optional[str] = None,
        base: Optional[str] = None,
    ) -> None:
        super().__init__(
            source_element=source_element,
            name=name,
            base=base,
        )
        self.maps = []
        self.__dict__["_content"]
        if source_element is not None:
            if source_element.text:
                raise ExtraTextError("ude", source_element.text)
            if source_element.tail:
                raise ExtraTailError("ude", source_element.tail)
            if len(source_element):
                for map_ in source_element:
                    self.maps.append(Map(map_))
            else:
                if maps is not None:
                    self.maps.extend(maps)

    def __iter__(self) -> Generator[Map, None, None]:
        yield from self.maps

    def add_map(
        self,
        unicode: str,
        code: Optional[str] = None,
        ent: Optional[str] = None,
        subst: Optional[str] = None,
    ) -> None:
        self.maps.append(Map(unicode=unicode, code=code, ent=ent, subst=subst))

    def insert_map(
        self,
        index: int,
        unicode: str,
        code: Optional[str] = None,
        ent: Optional[str] = None,
        subst: Optional[str] = None,
    ) -> None:
        self.maps.insert(index, Map(unicode=unicode, code=code, ent=ent, subst=subst))

    def append(self, map: Map) -> None:
        self.maps.append(map)

    def insert(self, index: int, map: Map) -> None:
        self.maps.insert(index, map)

    def remove(self, map: Map) -> None:
        self.maps.remove(map)


class Header(TmxElement):
    """
    File header - The `Header` element contains information pertaining
    to the whole document.

    ## Required attributes:
    #### creationtool: str
    The tool that created the TMX document.
    #### creationtoolversion: str
    The version of the tool that created the TMX document.
    #### segtype: "block" | "paragraph" | "sentence" | "phrase"
    The kind of segmentation used in the `Tu` element.
    #### otmf: str
    The format of the translation memory file from which the TMX documen
    or segment thereof have been generated.
    #### adminlang: str
    The default language for the administrative and informative elements
    `Note` and `Prop`.
    #### srclang: str
    The language of the source text.
    Can be set to "*all*" if any language inside a tu can be used a source.
    #### datatype: str
    The type of data

    ## Optional attributes:
    #### oencoding: str
    The original or preferred code set of the data
    #### creationdate: str | datetime
    The date of creation of the element.
    #### creationid: str
    The identifier of the user who created the element
    #### changedate: str | datetime
    The date of the last modification of
    #### changeid: str
    The identifier of the user who modified the element last
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
        self.notes, self.props, self.udes, self.__dict__["_content"] = [], [], [], None
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

    def __iter__(self) -> Generator[Ude, None, None]:
        yield from self.udes

    def add_prop(
        self,
        type: str,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.props.append(
            Prop(text=text, type=type, xmllang=xmllang, oencoding=oencoding)
        )

    def insert_prop(
        self,
        index: int,
        type: str,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.props.insert(
            index, Prop(text=text, type=type, xmllang=xmllang, oencoding=oencoding)
        )

    def remove_prop(self, prop: Prop) -> None:
        self.props.remove(prop)

    def add_note(
        self,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.notes.append(Note(text=text, xmllang=xmllang, oencoding=oencoding))

    def insert_note(
        self,
        index: int,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.notes.insert(index, Note(text=text, xmllang=xmllang, oencoding=oencoding))

    def remove_note(self, note: Note) -> None:
        self.notes.remove(note)

    def add_ude(
        self,
        name: str,
        base: Optional[str] = None,
        maps: Optional[MutableSequence[Map]] = None,
    ) -> None:
        self.udes.append(Ude(name=name, base=base, maps=maps))

    def insert_ude(
        self,
        index: int,
        name: str,
        base: Optional[str] = None,
        maps: Optional[MutableSequence[Map]] = None,
    ) -> None:
        self.udes.insert(index, Ude(name=name, base=base, maps=maps))

    def remove_ude(self, ude: Ude) -> None:
        self.udes.remove(ude)


class Seg(TmxElement):
    """
    Segment - The `Seg` element contains the text of the given segment.
    There is no length limitation to the content of a `Seg` element.
    All spacing and line-breaking characters are significant within a `Seg`
    element.

    Note: each `Bpt` element must have a subsequent corresponding `Ept` element.

    ## Required attributes:
    None
    ## Optional attributes:
    None
    """

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

    def append(self, value: str | Sub | Ut | Ph | It | Hi | Bpt | Ept) -> None:
        self._content.append(value)

    def insert(
        self, index: int, value: str | Sub | Ut | Ph | It | Hi | Bpt | Ept
    ) -> None:
        self._content.insert(index, value)


class Tuv(TmxElement):
    """
    Translation Unit Variant - The `Tuv` element specifies text
    in a given language.

    ## Required attributes
    ## segment: Seg
    The actual contents of the element. The _content attribute should always be
    set to an empty list.
    #### xmllang: str
    The locale of the element's content.
    A language code as described in the [RFC 3066].
    This declared value is considered to apply to all elements within
    the content of the element where it is specified, unless overridden
    with another instance of the xml:lang attribute.
    Unlike the other TMX attributes, the values for xml:lang are not
    case-sensitive.

    Note: PythonTmx currently DOES NOT checks that the value for xmllang is
    a correct language code, simply that the value is a str.

    ## Optional attributes:
    #### oencoding: str
    The original or preferred code set of the data
    #### datatype: str
    The type of data
    #### usagecount: int | str
    The number of times the element has been accessed in the original TM
    environment
    #### lastusagedate: str | datetime
    The last time the content of the element was used in the original
    translation memory environment.
    #### creationtool: str
    The tool that created the TMX document.
    #### creationtoolversion: str
    The version of the tool that created the TMX document.
    #### creationdate: str | datetime
    The date of creation of the element.
    #### creationid: str
    The identifier of the user who created the element
    #### changedate: str | datetime
    The date of the last modification of
    #### changeid: str
    The identifier of the user who modified the element last
    #### otmf: str
    The format of the translation memory file from which the TMX documen
    or segment thereof have been generated.
    """

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
        self.notes, self.props, self.__dict__["_content"] = [], [], None
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

    def __iter__(
        self,
    ) -> Generator[str | TmxElement, None, None]:
        yield from self.segment

    def add_prop(
        self,
        type: str,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.props.append(
            Prop(text=text, type=type, xmllang=xmllang, oencoding=oencoding)
        )

    def insert_prop(
        self,
        index: int,
        type: str,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.props.insert(
            index, Prop(text=text, type=type, xmllang=xmllang, oencoding=oencoding)
        )

    def remove_prop(self, prop: Prop) -> None:
        self.props.remove(prop)

    def add_note(
        self,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.notes.append(Note(text=text, xmllang=xmllang, oencoding=oencoding))

    def insert_note(
        self,
        index: int,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.notes.insert(index, Note(text=text, xmllang=xmllang, oencoding=oencoding))

    def remove_note(self, note: Note) -> None:
        self.notes.remove(note)


class Tu(TmxElement):
    """
    Translation unit - The `Tu` element contains the data for a given
    translation unit.

    ## Required attributes
    ## tuvs: MutableSequence[Tuv]
    The actual contents of the element. The _content attribute should always be
    set to an empty list.

    Note: PythonTmx currently DOES NOT checks that the value for xmllang is
    a correct language code, simply that the value is a str.

    ## Optional attributes:
    #### tuid: int | str:
    The identifier for the `Tu` element
    #### oencoding: str
    The original or preferred code set of the data
    #### datatype: str
    The type of data
    #### usagecount: int | str
    The number of times the element has been accessed in the original TM
    environment
    #### lastusagedate: str | datetime
    The last time the content of the element was used in the original
    translation memory environment.
    #### creationtool: str
    The tool that created the TMX document.
    #### creationtoolversion: str
    The version of the tool that created the TMX document.
    #### creationdate: str | datetime
    The date of creation of the element.
    #### creationid: str
    The identifier of the user who created the element
    #### changedate: str | datetime
    The date of the last modification of
    #### segtype: "block" | "paragraph" | "sentence" | "phrase"
    The kind of segmentation used in the `Tu` element.
    #### changeid: str
    The identifier of the user who modified the element last
    #### otmf: str
    The format of the translation memory file from which the TMX documen
    or segment thereof have been generated.
    #### srclang: str
    The language of the source text.lang: str
    """

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
        tuvs: Optional[Iterable[Tuv]] = None,
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
        self.notes, self.props, self.tuvs, self.__dict__["_content"] = [], [], [], None
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
                if tuvs is not None:
                    self.tuvs.extend(tuvs)
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

    def __iter__(self) -> Generator[Tuv, None, None]:
        yield from self.tuvs

    def add_prop(
        self,
        type: str,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.props.append(
            Prop(text=text, type=type, xmllang=xmllang, oencoding=oencoding)
        )

    def insert_prop(
        self,
        index: int,
        type: str,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.props.insert(
            index, Prop(text=text, type=type, xmllang=xmllang, oencoding=oencoding)
        )

    def remove_prop(self, prop: Prop) -> None:
        self.props.remove(prop)

    def add_note(
        self,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.notes.append(Note(text=text, xmllang=xmllang, oencoding=oencoding))

    def insert_note(
        self,
        index: int,
        text: str,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        self.notes.insert(index, Note(text=text, xmllang=xmllang, oencoding=oencoding))

    def remove_note(self, note: Note) -> None:
        self.notes.remove(note)


class Tmx(TmxElement):
    """
    Translation Memory Exchange - The Python object representation of a Tmx file.

    ## Required attributes:
    #### header: Header
    A `Header`element that has info over the whole file.
    #### tus: MutableSequence[Tu]
    The actual contents of the element. The _content attribute should always be
    set to an empty list.
    #### version: str = "1.4"
    The version of the TMX Standard the file follows. PythonTmx currently only
    support 1.4b

    ## Optional attributes:
    None
    """

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
        tus: Optional[Iterable[Tu]] = None,
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
            if tus is not None:
                self._content.extend(tus)
                if header is not None:
                    self.header = header
                else:
                    self.header = Header()

    def __iter__(self) -> Generator[Tu, None, None]:
        yield from self.tus

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_content":
            raise ValueError(
                "Tu elements are not allowed to have content. "
                "Please use the 'tuvs' property instead"
            )
        return super().__setattr__(name, value)

    @override
    def to_element(self) -> _Element:
        elem = Element("tmx", version=self.version)
        elem.append(self.header.to_element())
        body = Element("body")
        elem.append(body)
        for tu in self.tus:
            body.append(tu.to_element())
        return elem

    def to_tmx(self, file: str | bytes | PathLike) -> None:
        """
        Writes the element to a file using lxml.

        Arguments:
            file {str | bytes | PathLike | StringIO | BytesIO} -- A valid file
            path or file descriptor, or IO.
        """
        ElementTree(self.to_element()).write(
            file,
            xml_declaration=True,
        )

    def to_csv(self, file: str | bytes | PathLike) -> None:
        with open(file, "w", newline="") as f:
            csv_writer = writer(f)
            for tu in self:
                csv_writer.writerow(
                    [
                        tostring(tuv.segment.to_element())[5:-6].decode()
                        for tuv in tu.tuvs
                    ]
                )
