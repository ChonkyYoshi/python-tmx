from typing import Literal
from datetime import datetime
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
        _validate: bool = True,
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
        if _validate:
            self._ValidateAttributes()

    def _ValidateAttributes(self) -> None:
        for attr in self.__slots__:
            attr_value = getattr(self, attr)
            match attr_value:
                case None:
                    continue
                case datetime():
                    if not attr.endswith("date"):
                        raise TypeError(
                            f"datetime objects cannot be used for attribute {attr}"
                        )
                    continue
                case str():
                    if attr.endswith("lang"):
                        if not match(
                            r"^[a-z][a-z](-[a-z][a-z][a-z]?)?$", attr_value.lower()
                        ):
                            raise ValueError(
                                f"""{attr_value} is not a correct value for {attr}
{attr} should be in the format xx(-YY)
where xx is a 2 letter ISO country code and YY is an optional 2 or 3 letter ISO language code"""
                            )
                        continue
                    if attr == "segtype" and attr_value not in [
                        "block",
                        "paragraph",
                        "sentence",
                        "phrase",
                    ]:
                        raise ValueError(
                            f"""{attr_value} is not a correct value for segtype.
segtype should be one of block, paragraph, sentence or phrase."""
                        )
                    if attr.endswith("date"):
                        datetime.strptime(attr_value, "%Y%m%dT%H%M%SZ")
                        continue
                case _:
                    raise TypeError(
                        f"only strings (and datetime objects for creationdate and changedate) can be used as values for header attribute not {type(attr_value)}"
                    )
