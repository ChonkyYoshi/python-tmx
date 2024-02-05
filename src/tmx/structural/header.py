from typing import Literal
from xml.etree.ElementTree import Element
from datetime import datetime, UTC
from re import match


class header:
    __slots__ = [
        "creationtool",
        "creationtoolversion",
        "segtype",
        "otmf",
        "adminlang",
        "srclang",
        "datatype",
        "segtype",
        "oencoding",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
        "notes",
        "props",
    ]

    def __init__(
        self,
        creationtool: str,
        creationtoolversion: str,
        segtype: Literal["block", "paragraph", "sentence", "phrase"],
        otmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        **kwargs,
    ) -> None:
        for attr in self.__slots__:
            if attr in kwargs.keys():
                self.__setattr__(attr, kwargs[attr])
            else:
                self.__setattr__(attr, None)
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.segtype = segtype
        self.otmf = otmf
        self.adminlang = adminlang
        self.srclang = srclang
        self.datatype = datatype
        self._ValidateAttributes()

    def _ValidateAttributes(self) -> None:
        for attr in self.__slots__:
            attr_value = getattr(self, attr)
            if attr_value is None:
                continue
            if attr.endswith("date"):
                if type(attr_value) == datetime:
                    if (
                        attr_value.tzinfo is None
                        or attr_value.tzinfo.utcoffset(attr_value) is None
                    ):
                        attr_value = attr_value.astimezone(tz=UTC)
                    else:
                        attr_value = datetime.astimezone(attr_value, UTC)
                    setattr(self, attr, attr_value.strftime("%Y%m%dT%H%M%SZ"))
                    continue
                else:
                    try:
                        datetime.strptime(str(attr_value), "%Y%m%dT%H%M%SZ")
                    except ValueError:
                        raise ValueError(
                            f"""{attr_value} is not a correct value for {attr}.
{attr} should be an aware datetime object (with its timezone set to UTC) or a str in the format YYYYMMDDTHHMMSSZ"""
                        )
            if attr.endswith("lang"):
                if not match(r"^[a-z][a-z](-[a-z][a-z][a-z]?)?$", attr_value.lower()):
                    raise ValueError(
                        f"""{attr_value} is not a correct value for {attr}
{attr} should be in the format xx(-YY)
where xx is a 2 letter ISO country code and YY is an optional 2 or 3 letter ISO language code"""
                    )
                setattr(self, attr, attr_value.lower())
                continue

    def _XmlElement(self) -> Element:
        self._ValidateAttributes()
        return Element(
            "header",
            {
                attr: getattr(self, attr)
                for attr in self.__slots__
                if getattr(self, attr) is not None
            },
        )


a = header("1", "1", "block", "1", "en", "en", "1", creationdate=13)
