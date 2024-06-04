import datetime
from csv import reader
from io import TextIOWrapper
from xml.etree.ElementTree import ElementTree, parse

from classes import Header, Seg, Tmx, Tu, Tuv

__all__ = ["load_tmx_file", "load_csv_file", "write_to_tmx_file"]


def load_tmx_file(file: TextIOWrapper) -> Tmx:
    if not isinstance(file, TextIOWrapper):
        raise TypeError(f"Expected a TextIOWrapper but got {type(file)}")
    return Tmx(parse(file).getroot())


def load_csv_file(
    csvfile: TextIOWrapper,
    source_lang: str,
    target_lang: str,
    source_col: int,
    target_col: int,
    header: Header | None = None,
    skip_first: bool = True,
) -> Tmx:
    if not isinstance(csvfile, TextIOWrapper):
        raise TypeError(f"Expected a TextIOWrapper but got {type(csvfile)}")
    csv_reader = reader(csvfile)
    return Tmx(
        header=Header(
            creationtool="Python Tmx Library",
            creationtoolversion="0.5",
            segtype="paragraph",
            o_tmf="csv",
            adminlang="en-US",
            srclang=source_lang,
            datatype="plaintext",
            creationdate=datetime.datetime.now(datetime.UTC),
            creationid="Python Tmx Library",
        ),
        tus=[
            Tu(
                tuvs=[
                    Tuv(lang=source_lang, segment=Seg(content=row[source_col])),
                    Tuv(lang=target_lang, segment=Seg(content=row[target_col])),
                ],
            )
            for index, row in enumerate(csv_reader)
            if index != 0
        ],
    )


def write_to_tmx_file(tmx: Tmx, target: TextIOWrapper) -> None:
    if not isinstance(target, TextIOWrapper):
        raise TypeError(f"Expected a TextIOWrapper but got {type(target)}")
    if not isinstance(tmx, Tmx):
        raise TypeError(f"Expected a Tmx but got {type(tmx)}")
    ElementTree(tmx.export()).write(target, encoding="utf-8", xml_declaration=True)
