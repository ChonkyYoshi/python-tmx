from csv import reader
from io import BytesIO, StringIO
from os import PathLike
from typing import Optional

from lxml.etree import XMLParser, fromstring, parse

from .inline import Bpt, Ept, Hi, It, Ph, Sub, Ut
from .structural import Header, Map, Note, Prop, Seg, Tmx, Tu, Tuv, Ude


def from_tmx(file: str | bytes | PathLike) -> Tmx:
    return Tmx(parse(file, XMLParser(remove_blank_text=True)).getroot())


def from_csv(
    file: str | bytes | PathLike,
    source_col: int,
    source_lang: str,
    target_col: int,
    target_lang: str,
    header: Optional[Header] = None,
) -> Tmx:
    tmx = Tmx()
    if header is None:
        tmx.header = Header(
            creationtool="PythonTmx",
            creationtoolversion="0.2",
            segtype="paragraph",
            otmf="csv",
            adminlang="en-US",
            srclang=source_lang,
            datatype="unknown",
        )
    else:
        tmx.header = header
    with open(file, "r") as f:
        for row in reader(f):
            tmx.tus.append(
                Tu(
                    tuvs=[
                        Tuv(
                            xmllang=source_lang,
                            segment=Seg(
                                source_element=fromstring(
                                    f"<seg>{row[source_col]}</seg>"
                                )
                            ),
                        ),
                        Tuv(
                            xmllang=target_lang,
                            segment=Seg(
                                source_element=fromstring(
                                    f"<seg>{row[target_col]}</seg>"
                                )
                            ),
                        ),
                    ]
                )
            )
    return tmx
