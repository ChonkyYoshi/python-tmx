from os import PathLike

from lxml.etree import _Element, iterparse, parse
from structural import Tmx

type FileDescriptorOrPath = int | str | bytes | PathLike[str] | PathLike[bytes]


def load_tmx_file(file: FileDescriptorOrPath) -> Tmx:
    return Tmx(parse(file).getroot())


def validate_tmx(tmx: FileDescriptorOrPath) -> bool:
    ctx = iterparse(tmx, remove_blank_text=True)
    elem: _Element
    for _, elem in ctx:
        match elem.tag:
            case "header":
                if elem.getparent().tag != "tmx":
                    return False
                if elem.text or elem.tail:
                    return False
                elem.clear()
            case "ude":
                if elem.getparent().tag != "header":
                    return False
                if elem.text or elem.tail:
                    return False
                elem.clear()
            case "map":
                if elem.getparent().tag != "ude":
                    return False
                if elem.text or elem.tail:
                    return False
                elem.clear()
            case "prop" | "note":
                if elem.getparent().tag not in {"header", "tu", "tuv"}:
                    return False
                if len(elem):
                    return False
                elem.clear()
            case "tu":
                if elem.getparent().tag != "body":
                    return False
                if elem.text or elem.tail:
                    return False
            case "tuv":
                if elem.getparent().tag != "tu":
                    return False
                if elem.text or elem.tail:
                    return False
                elem.clear()
            case "seg":
                if elem.getparent().tag != "tuv":
                    return False
                elem.clear()
            case "sub":
                if elem.getparent().tag not in {
                    "bpt",
                    "ept",
                    "hi",
                    "it",
                    "ph",
                    "ut",
                    "seg",
                }:
                    return False
            case "bpt" | "ept" | "it" | "hi" | "ph":
                if elem.getparent().tag not in {"seg", "sub", "hi", "ut"}:
                    return False
            case "ut":
                if elem.getparent().tag not in {"sub", "hi", "seg"}:
                    return False
            case "body" | "tmx":
                pass
            case _:
                return False
    if ctx.root.tag != "tmx":
        return False
    return True
