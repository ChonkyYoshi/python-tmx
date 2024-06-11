from csv import reader
from datetime import UTC, datetime
from typing import Iterable, Tuple
from xml.etree.ElementTree import Element, XMLPullParser, parse

from errors import TmxParseError
from structural import Header, Map, Note, Prop, Seg, Tmx, Tu, Tuv, Ude


def load_huge_tmx_file(file: str) -> Tmx:
    event: str
    elem: Element
    tmx = Tmx(tus=[])
    parser = XMLPullParser(events=["start", "end"])
    with open(file, "rb") as f:
        ctx = iter(lambda: f.read(4096), b"")
        for chunk in ctx:
            parser.feed(chunk)
            for event, elem in parser.read_events():
                match event, elem.tag:
                    case "start", "header":
                        header = Header(elem)
                        parent = header
                    case "end", "header":
                        tmx.header = header
                        header = None
                        parser.flush()
                    case "end", "note":
                        parent.notes.append(Note(elem))
                        parser.flush()
                    case "end", "prop":
                        parent.props.append(Prop(elem))
                        parser.flush()
                    case "start", "ude":
                        ude = Ude(elem)
                        parent = ude
                    case "end", "ude":
                        header.udes.append(ude)
                        ude = None
                        parser.flush()
                    case "end", "map" if not isinstance(parent, Ude):
                        raise TmxParseError("map outside a ude")
                        parser.flush()
                    case "end", "map":
                        parent.maps.append(Map(elem))
                        parser.flush()
                    case "start", "tu":
                        tu = Tu(elem)
                        parent = tu
                    case "end", "tu":
                        tmx.tus.append(tu)
                        parser.flush()
                    case "start", "tuv" if tu is None:
                        raise TmxParseError("found tuv outside if tu")
                    case "start", "tuv":
                        tuv = Tuv(elem)
                        parent = tuv
                    case "end", "tuv":
                        tu.tuvs.append(tuv)
                        parent = tu
                        parser.flush()
                    case "start", "seg" if not isinstance(parent, Tuv):
                        raise TmxParseError("found seg outside tuv")
                    case "end", "seg":
                        parent.segment = Seg(elem)
                        parser.flush()
    return tmx


def load_tmx_file(file: str) -> Tmx:
    return Tmx(parse(file).getroot())


def load_csv_file(
    file: str,
    source: Tuple[int, str],
    target: Tuple[int, str] | Iterable[Tuple[int, str]],
    skip_csv_header: bool = True,
    encoding: str | None = "utf-8",
    header: Header | None = None,
    csv_options: dict[str | str] | None = None,
) -> Tmx:
    default_header = Header(
        creationtool="PythonTMX",
        creationtoolversion="0.4",
        segtype="paragraph",
        o_tmf="csv",
        adminlang="en-us",
        srclang="en-us",
        datatype="Plain text",
        creationdate=datetime.now(UTC),
        creationid="PythonTmx",
        o_encoding="utf-8",
    )
    tmx = Tmx(header=header) if header is not None else Tmx(header=default_header)
    with open(file, "r", encoding=encoding) as f:
        if csv_options is not None:
            csv_reader = reader(f, **csv_options)
        else:
            csv_reader = reader(f)
        if skip_csv_header:
            csv_reader.__next__()
        tmx.tus.extend(
            [
                Tu(
                    srclang=source[1],
                    tuvs=[
                        Tuv(lang=source[1], segment=Seg(content=row[source[0]])),
                        *[
                            Tuv(
                                lang=child_target[1],
                                segment=Seg(content=row[child_target[0]]),
                            )
                            for child_target in target
                        ],
                    ],
                )
                for row in csv_reader
            ]
        )
    return tmx
