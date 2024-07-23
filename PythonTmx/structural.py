from typing import Optional

from lxml.etree import _Element

from PythonTmx.core import BaseElement


class Prop(BaseElement):
    content: str
    type: str
    xmllang: Optional[str]
    oencoding: Optional[str]

    def __init__(
        self,
        *,
        lxml_element: Optional[_Element] = None,
        content: Optional[str] = None,
        type: Optional[str] = None,
        xmllang: Optional[str] = None,
        oencoding: Optional[str] = None,
    ) -> None:
        match lxml_element:
            case _Element():
                self.content = (
                    lxml_element.text
                    if lxml_element.text is not None
                    else content
                    if content is not None
                    else ""
                )
                self.type = lxml_element.get("type", type if type is not None else "")
                self.xmllang = lxml_element.get("xml:lang", xmllang)
                self.oencoding = lxml_element.get("o-encoding", oencoding)
            case None:
                self.content = content if content is not None else ""
                self.type = type if type is not None else ""
                self.xmllang = xmllang
                self.oencoding = oencoding
            case _:
                raise TypeError(
                    f"Expected an lxml '_Element' object but got '{lxml_element.__class__.__name__}'"
                )

    def __len__(self) -> int:
        return len(self.content)

    def validate(self) -> None:
        for attribute in ("content", "xmllang", "oencoding", "type"):
            value = getattr(self, attribute)
            match attribute, value:
                case "type", None:
                    raise AttributeError("required attribute missing")
                case "content", None:
                    raise AttributeError("content missing")
                case _, None:
                    continue
                case _:
                    raise TypeError
