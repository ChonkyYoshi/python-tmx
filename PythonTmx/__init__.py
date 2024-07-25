from io import BytesIO, StringIO
from os import PathLike

from lxml.etree import XMLParser, XMLPullParser, _Element, _ElementTree, parse, iterparse

from PythonTmx.core import Tmx


def read_from_file(file: str | bytes | PathLike | StringIO | BytesIO, use_pull: bool) -> Tmx:
    if not use_pull:
        tree: _ElementTree = parse(file, XMLParser(remove_blank_text=True))
        root: _Element = tree.getroot()
        if root.tag != "tmx":
            raise ValueError(f"Expected root tag to be <tmx> but got {root.tag}")
        return Tmx(source_element=root)
    else:
        for event, elem in iterparse(file):
            