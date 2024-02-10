from datetime import datetime
from re import match
from objects import note, prop


def ValidateAttributes(
    obj, force_string: bool
) -> dict[str, str | datetime | int] | dict[str, str]:
    attribs: dict = {}
    for attr in obj.__slots__:
        attr_value = getattr(obj, attr)
        match attr_value:
            case None:
                continue
            case datetime():
                if not attr.endswith("date"):
                    raise TypeError(
                        f"datetime objects cannot be used for attribute {attr}"
                    )
                attribs[attr] = (
                    datetime.strftime(attr_value, "%Y%m%dT%H%M%SZ")
                    if force_string
                    else attr_value
                )
            case str():
                match attr:
                    case "srclang" | "adminlang":
                        if not match(
                            r"^[a-z][a-z](-[a-z][a-z][a-z]?)?$", attr_value.lower()
                        ):
                            raise ValueError(
                                f"{attr} should be in the format xx(-YY) where xx is a 2 letter ISO country code and YY is an optional 2 or 3 letter ISO language code"
                            )
                        attribs[attr] = attr_value
                    case "xmllang":
                        if not match(
                            r"^[a-z][a-z](-[a-z][a-z][a-z]?)?$", attr_value.lower()
                        ):
                            raise ValueError(
                                f"{attr} should be in the format xx(-YY) where xx is a 2 letter ISO country code and YY is an optional 2 or 3 letter ISO language code"
                            )
                        attribs["{http://www.w3.org/XML/1998/namespace}lang"] = (
                            attr_value
                        )
                    case "segtype":
                        if attr_value not in [
                            "block",
                            "paragraph",
                            "sentence",
                            "phrase",
                        ]:
                            raise ValueError(
                                f"{attr_value} is not a correct value for segtype. segtype should be one of block, paragraph, sentence or phrase."
                            )
                        attribs[attr] = attr_value
                    case "changedate" | "creationdate" | "lastusagedate":
                        datetime.strptime(attr_value, "%Y%m%dT%H%M%SZ")
                        attribs[attr] = attr_value
                    case "_type":
                        attribs["type"] = attr_value
                    case "otmf":
                        attribs["o-tmf"] = attr_value
                    case "oencoding":
                        attribs["o-encoding"] = attr_value
                    case (
                        "creationtool"
                        | "creationtoolversion"
                        | "datatype"
                        | "creationid"
                        | "changeid"
                    ):
                        attribs[attr] = attr_value
            case int():
                if attr not in ["i", "x", "tuid", "usagecount"]:
                    raise TypeError(f"{attr} does not accept int value")
                attribs[attr] = str(attr_value) if force_string else attr_value
            case list():
                match attr:
                    case "notes":
                        for index, _note in enumerate(attr_value):
                            if _note is not note:
                                raise TypeError(
                                    f"note {index}  is of type {type(_note)} not note"
                                )
                    case "props":
                        for index, _prop in enumerate(attr_value):
                            if _prop is not prop:
                                raise TypeError(
                                    f"prop {index} is of type {type(_prop)} not prop"
                                )
                    case "seg":
                        raise NotImplementedError
            case _:
                raise TypeError(f"{type(attr_value)} are not allowed")
    return attribs
