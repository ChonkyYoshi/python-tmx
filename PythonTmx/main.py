from functools import partial
from xml.etree.ElementTree import Element, XMLPullParser

from structural import Header, Tmx, Tu


def load_tmx_file(file: str) -> Tmx:
    event: str
    elem: Element
    tmx = Tmx(tus=[])
    parser = XMLPullParser()
    with open(file, "rb") as f:
        for block in iter(partial(f.read, 64), b""):
            parser.feed(block)
            for event, elem in parser.read_events():
                if elem.tag == "header":
                    tmx.header = Header(elem)
                    f.flush()
                if elem.tag == "tu":
                    tmx.tus.append(Tu(elem))
                    f.flush()
    return tmx
