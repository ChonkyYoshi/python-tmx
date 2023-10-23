import python_tmx as tmx
import pathlib as pl
import lxml.etree as et


def main(file: str):
    file_object: pl.Path = pl.Path(file)
    if not file_object.is_file():
        raise ValueError("File doesn't exist idiot")
    tree: et._ElementTree = et.parse(file_object, et.XMLParser(remove_blank_text=True))
    root: et._Element = tree.getroot()
    for seg in root.iter("seg"):
        seg: et._Element
        seg_object: tmx.segment.segment = tmx.segment.segment(xml=seg)
        seg_object.content.append(tmx.segment.text_run(text=seg.text))
        for elem in seg.iterdescendants("*"):
            elem: et._Element
            match elem.tag:
                case "bpt":
                    seg_object.content.append(
                        tmx.segment.bpt_run(
                            i=elem.get("i", 0),
                            tagged_text=elem.text,
                            x=elem.get("x", None),
                            data_type=elem.get("type", None),
                        )
                    )
                    seg_object.content.append(tmx.segment.text_run(text=elem.tail))
                case "ept":
                    seg_object.content.append(
                        tmx.segment.ept_run(
                            i=elem.get("i", 0),
                            tagged_text=elem.text,
                        )
                    )
                    seg_object.content.append(tmx.segment.text_run(text=elem.tail))
                case "ph"
    1 + 1


if __name__ == "__main__":
    main("sample.tmx")
