from datetime import datetime
from email.header import Header
from os import PathLike
from xml.etree.ElementTree import Element as std_Element

from errors import InvalidTmxError
from inline import Bpt, Ept, Hi, It, Ph, Sub, Ut
from lxml.etree import Element as lxml_Element_Factory
from lxml.etree import _Element as lxml_Element_type
from lxml.etree import iterparse
from structural import (
    Map,
    Note,
    Prop,
    Tmx,
    TmxElement,
    Tu,
    Tuv,
    Ude,
)

type FileDescriptorOrPath = int | str | bytes | PathLike[str] | PathLike[bytes]
type XmlElement = lxml_Element_type | std_Element


def _validate_object_required_attributes(obj: TmxElement) -> dict[str, str]:
    validated_attrs: dict[str, str] = {}
    for attr, type_ in obj.REQ_ATTRIBUTES:
        attr = attr.replace("-", "_")
        val = getattr(obj, attr)
        match attr, val:
            case _, None:
                raise AttributeError(
                    f"{type(obj).__name__} "
                    "object is missing required attribute {attr}"
                )
            case _, x if not isinstance(x, type_):
                raise TypeError(
                    f"Attribute {attr} of object {type(obj).__name__} is of the"
                    " wrong type, expected {type_} but got {type(val)}"
                )
            case "segtype", str() if val not in (
                "block",
                "paragraph",
                "sentence",
                "phrase",
            ):
                raise ValueError(
                    f"Attribute segtype of object {type(obj).__name__}"
                    " is of the wrong value, expected one of "
                    "'block', 'paragraph', 'sentence' or 'phrase'"
                    " but got '{val}'"
                )
            case _, str():
                validated_attrs[attr] = val
            case _, datetime():
                validated_attrs[attr] = val.strftime(r"%Y%m%dT%H%M%SZ")
            case _, int():
                validated_attrs[attr] = str(val)
    return validated_attrs


def _validate_object_optional_attributes(obj: TmxElement) -> dict[str, str]:
    validated_attrs: dict[str, str] = {}
    for attr, type_ in obj.OPT_ATTRIBUTES:
        attr = attr.replace("-", "_")
        val = getattr(obj, attr)
        match attr, val:
            case _, None:
                pass
            case _, x if not isinstance(x, type_):
                raise TypeError(
                    f"Attribute {attr} of object {type(obj).__name__} is of the"
                    " wrong type, expected {type_} but got {type(val)}"
                )
            case "segtype", str() if val not in (
                "block",
                "paragraph",
                "sentence",
                "phrase",
            ):
                raise ValueError(
                    f"Attribute segtype of object {type(obj).__name__}"
                    " is of the wrong value, expected one of "
                    "'block', 'paragraph', 'sentence' or 'phrase'"
                    " but got '{val}'"
                )
            case _, str():
                validated_attrs[attr] = val
            case _, datetime():
                validated_attrs[attr] = val.strftime(r"%Y%m%dT%H%M%SZ")
            case _, int():
                validated_attrs[attr] = str(val)
    return validated_attrs


def validate_attributes(obj: TmxElement | XmlElement) -> dict[str, str]:
    if isinstance(obj, TmxElement):
        return _validate_object_required_attributes(
            obj
        ) | _validate_object_optional_attributes(obj)
    elif isinstance(obj, (lxml_Element_type, std_Element)):
        match obj.tag:
            case "header":
                obj = Header(lxml_Element_Factory(obj.tag, obj.attrib))
            case "prop":
                obj = Prop(lxml_Element_Factory(obj.tag, obj.attrib))
            case "note":
                obj = Note(lxml_Element_Factory(obj.tag, obj.attrib))
            case "tu":
                obj = Tu(lxml_Element_Factory(obj.tag, obj.attrib))
            case "tuv":
                obj = Tuv(lxml_Element_Factory(obj.tag, obj.attrib))
            case "ph":
                obj = Ph(lxml_Element_Factory(obj.tag, obj.attrib))
            case "hi":
                obj = Hi(lxml_Element_Factory(obj.tag, obj.attrib))
            case "it":
                obj = It(lxml_Element_Factory(obj.tag, obj.attrib))
            case "ept":
                obj = Ept(lxml_Element_Factory(obj.tag, obj.attrib))
            case "bpt":
                obj = Bpt(lxml_Element_Factory(obj.tag, obj.attrib))
            case "sub":
                obj = Sub(lxml_Element_Factory(obj.tag, obj.attrib))
            case "ut":
                obj = Ut(lxml_Element_Factory(obj.tag, obj.attrib))
            case "ude":
                obj = Ude(lxml_Element_Factory(obj.tag, obj.attrib))
            case "map":
                obj = Map(lxml_Element_Factory(obj.tag, obj.attrib))
        return _validate_object_required_attributes(
            obj
        ) | _validate_object_optional_attributes(obj)


def validate_tmx_object(tmx: Tmx) -> None:
    validate_attributes(tmx.header)
    for tu in tmx.tus:
        validate_attributes(tu)
        for tuv in tu.tuvs:
            validate_attributes(tuv)
            for child in tuv.segment:
                if not isinstance(child, str):
                    validate_attributes(child)


def validate_tmx_file(TmxFile: FileDescriptorOrPath) -> None:
    ctx = iterparse(TmxFile, remove_blank_text=True, events=("start", "end"))
    for event, elem in ctx:
        match event, elem.tag:
            case "start", "header":
                validate_attributes(Header(elem))
            case "start", "prop":
                validate_attributes(Prop(elem))
            case "start", "note":
                validate_attributes(Note(elem))
            case "start", "tu":
                validate_attributes(Tu(elem))
            case "start", "tuv":
                validate_attributes(Tuv(elem))
            case "start", "ph":
                validate_attributes(Ph(elem))
            case "start", "hi":
                validate_attributes(Hi(elem))
            case "start", "it":
                validate_attributes(It(elem))
            case "start", "ept":
                validate_attributes(Ept(elem))
            case "start", "bpt":
                validate_attributes(Bpt(elem))
            case "start", "sub":
                validate_attributes(Sub(elem))
            case "start", "ut":
                validate_attributes(Ut(elem))
            case "start", "ude":
                validate_attributes(Ude(elem))
            case "start", "map":
                validate_attributes(Map(elem))
            case "start", "tmx":
                if not elem.get("version"):
                    raise AttributeError(
                        f'Requried attribute version is incorrect. expected 1.4 but got {elem.get("version")}'
                    )
                pass
            case _, _:
                raise InvalidTmxError(f"encountered unexpected {elem.tag} element")
    if ctx.root != "tmx":
        raise InvalidTmxError(f"root element is not tmx but {elem.tag}")


validate_tmx_file("test.tmx")
