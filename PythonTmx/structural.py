from datetime import datetime
from enum import StrEnum, auto
from re import match
from typing import Any, Iterable, Iterator, Optional, Protocol, Self


class _XmlElement(Protocol):
    tag: str
    attrib: dict[str, str]
    text: str | None
    tail: str | None
    _children: Iterable[Self]

    def get(self, item: str) -> str | None:
        raise NotImplementedError

    def iter(self) -> Iterator[Self]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Self]:
        pass


class Segtype(StrEnum):
    block = auto()
    paragraph = auto()
    sentence = auto()
    phrase = auto()


class Header:
    creationtool: str
    creationtoolversion: str
    segtype: Segtype
    otmf: str
    adminlang: str
    srclang: str
    datatype: str
    oencoding: str
    creationdate: str | datetime
    creationid: str
    changedate: str | datetime
    changeid: str

    def __init__(
        self,
        XmlElement: Optional[_XmlElement],
        **attribs,
    ) -> None:
        def _parse_attributes(attrib: dict[str, Any], strict: bool = True) -> None:
            for key, val in attrib.items():
                match key, val:
                    case (
                        "creationtool"
                        | "creationtoolversion"
                        | "o-tmf"
                        | "adminlang"
                        | "srclang"
                        | "datatype"
                        | "o-encoding"
                        | "creationid"
                        | "changeid",
                        str(),
                    ):
                        setattr(self, key.replace("-", ""), val)
                    case "segtype", "block":
                        self.segtype = Segtype.block
                    case "segtype", "paragraph":
                        self.segtype = Segtype.paragraph
                    case "segtype", "sentence":
                        self.segtype = Segtype.sentence
                    case "segtype", "phrase":
                        self.segtype = Segtype.phrase
                    case "segtype", _:
                        if strict:
                            raise ValueError(
                                f"Value for segtype is incorrect, expected one of block, paragraph, sentence or phrase but found {val}"
                            )
                        self.segtype = val
                    case "creationdate" | "changedate", str():
                        if not match(r"^\d{8}T\d{6}Z$", val):
                            if strict:
                                raise ValueError(
                                    f"Value for {key} is not of the correct format"
                                )
                            setattr(self, key, val)
                        else:
                            setattr(
                                self, key, datetime.strptime(val, r"%Y%m%dT%H%M%SZ")
                            )
                    case "creationdate" | "changedate", datetime():
                        setattr(self, key, val)
                    case (
                        "creationtool"
                        | "creationtoolversion"
                        | "segtype"
                        | "o-tmf"
                        | "adminlang"
                        | "srclang"
                        | "datatype"
                        | "o-encoding"
                        | "creationdate"
                        | "creationid"
                        | "changedate"
                        | "changeid",
                        _,
                    ):
                        if strict:
                            raise TypeError(
                                f"attribute {key} does not supports values of type {type(val)}"
                            )
                        setattr(self, key, val)
                    case _:
                        raise AttributeError(f"Unknown attribute found: '{key}'")

        if XmlElement is not None:
            if len(attribs):
                attrs = XmlElement.attrib | attribs
                _parse_attributes(attrs)
            else:
                _parse_attributes(XmlElement.attrib)
        else:
            _parse_attributes(attribs)
