"""tmx-lvel related functions"""
from pathlib import Path
from shared.classes import tmx
import lxml.etree as et

xml_parser: et.XMLParser = et.XMLParser(
    encoding="utf-8", no_network=True, remove_blank_text=True, resolve_entities=False
)


def parse_tmx(source: Path) -> tmx:
    """parses a tmx file and returns a tmx object representing its content"""
    tmx_tree: et._ElementTree = et.parse(source, xml_parser)
