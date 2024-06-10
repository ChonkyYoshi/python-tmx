from time import perf_counter
from xml.etree.ElementTree import Element, XMLPullParser, parse, tostring

from errors import TmxParseError
from structural import Header, Map, Note, Prop, Seg, Tmx, Tu, Tuv, Ude


def load_tmx_file(file: str) -> Tmx:
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


def make_big_file(name: str) -> None:
    b = tostring(
        Tu(
            tuvs=[
                Tuv(lang="en-us", segment=Seg(content="en content")),
                Tuv(lang="fr-fr", segment=Seg(content="fr content")),
            ],
            srclang="en-us",
        ).export(),
        encoding="unicode",
    )
    with open(name, "a", encoding="utf-8") as f:
        f.write(
            """<?xml version="1.0"?><tmx version="1.4"><header creationtool="XYZTool" creationtoolversion="1.01-023" datatype="PlainText" segtype="sentence" adminlang="en-us" srclang="EN" o-tmf="ABCTransMem" creationdate="20020101T163812Z" creationid="ThomasJ" changedate="20020413T023401Z" changeid="Amity" o-encoding="iso-8859-1"></header><body>"""
        )
        for i in range(1_000_000):
            f.write(b)
            f.flush()
        f.write("</body></tmx>")
    print("done creating big file")


# make_big_file("b.tmx")
e = perf_counter()
a = load_tmx_file("b.tmx")
print(perf_counter() - e)
e = perf_counter()
a = Tmx(parse("b.tmx").getroot())
print(perf_counter() - e)
