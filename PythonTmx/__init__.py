from io import BytesIO, StringIO
from os import PathLike

from lxml.etree import XMLParser, _Element, _ElementTree, parse

from PythonTmx.core import Tmx


def read_from_file(file: str | bytes | PathLike | StringIO | BytesIO) -> Tmx:
    tree: _ElementTree = parse(
        file, XMLParser(remove_blank_text=True, resolve_entities=False)
    )
    root: _Element = tree.getroot()
    if root.tag != "tmx":
        raise ValueError(f"Expected root tag to be <tmx> but got {root.tag}")
    return Tmx(source_element=root)
