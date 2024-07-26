from io import BytesIO, StringIO
from os import PathLike

from lxml.etree import XMLParser, _Element, _ElementTree, iterparse, parse

from PythonTmx.inline import Bpt, Ept, Hi, It, Ph, Sub, Ut
from PythonTmx.structural import Header, Map, Note, Prop, Seg, Tmx, Tu, Tuv, Ude


def read_from_file(file: str | bytes | PathLike | StringIO | BytesIO) -> Tmx:
    return Tmx(parse(file, XMLParser(remove_blank_text=True)).getroot())
