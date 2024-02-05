from typing import Literal
from xml.etree.ElementTree import Element
from datetime import datetime, UTC
from re import match


class tu:
    __slots__ = [
        "tuid",
        "oencoding",
        "datatype",
        "usagecount",
        "lastusagedate",
        "creationtool",
        "creationtoolversion",
        "creationdate",
        "creationid",
        "changedate",
        "segtype",
        "changeid",
        "otmf",
        "srclang",
        "notes",
        "props",
    ]

    def __init__(
        self,
        **kwargs,
    ) -> None:
        for attr in self.__slots__:
            if attr in kwargs.keys():
                self.__setattr__(attr, kwargs[attr])
            else:
                self.__setattr__(attr, None)

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
                        datetime.strptime(attr_value, "%Y%m%dT%H%M%SZ")
                    except ValueError:
                        raise ValueError(
                            f"""{attr_value} is not a correct value for {attr}.
{attr} should be an aware datetime object (with its timezone set to UTC) or a str in the format YYYMMDDTHHMMSSZ"""
                        )
            if attr.endswith("lang"):
                if match(r"^[a-z][a-z](-[a-z][a-z][a-z]?)?$", attr_value.lower()):
                    setattr(self, attr, attr_value.lower())
                    continue
                raise ValueError(
                    f"""{attr_value} is not a correct value for {attr}
{attr} should be in the format xx(-YY)
where xx is a 2 letter ISO country code and YY is an optional 2 or 3 letter ISO language code"""
                )

    def _CreateXmlElement(self) -> Element:
        self._ValidateAttributes()
        return Element(
            "header",
            {
                attr: getattr(self, attr)
                for attr in self.__slots__
                if getattr(self, attr) is not None
            },
        )
