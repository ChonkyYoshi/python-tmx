from io import BytesIO, StringIO
from os import PathLike

from lxml.etree import XMLParser, parse

from PythonTmx.classes import Tmx


def read_from_file(file: str | bytes | PathLike | StringIO | BytesIO) -> Tmx:
    root = parse(
        file, XMLParser(remove_blank_text=True, resolve_entities=False)
    ).getroot()
    if root.tag != "tmx":
        raise ValueError(f"Expected root tag to be <tmx> but got {root.tag}")
    return Tmx(source_element=root)


read_from_file("test.tmx").export_to_file("new.tmx")
