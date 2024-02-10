from typing import Literal


class note:
    __slots__ = ["text", "xmllang", "oencoding"]

    def __init__(self, text: str, **kwargs) -> None:
        self.text = text
        self.xmllang = kwargs.get("xmllang", None)
        self.oencoding = kwargs.get("oencoding", None)


class prop:
    __slots__ = ["text", "_type", "xmllang", "oencoding"]

    def __init__(self, text: str, _type: str, **kwargs) -> None:
        self.text = text
        self._type = _type
        self.xmllang = kwargs.get("xmllang", None)
        self.oencoding = kwargs.get("oencoding", None)


class header:
    __slots__ = [
        "creationtool",
        "creationtoolversion",
        "segtype",
        "otmf",
        "adminlang",
        "srclang",
        "datatype",
        "segtype",
        "oencoding",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
        "notes",
        "props",
    ]

    def __init__(
        self,
        creationtool: str,
        creationtoolversion: str,
        segtype: Literal["block", "paragraph", "sentence", "phrase"],
        otmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        **kwargs,
    ) -> None:
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.segtype = segtype
        self.otmf = otmf
        self.adminlang = adminlang
        self.srclang = srclang
        self.datatype = datatype
        self.oencoding = kwargs.get("oencoding", None)
        self.creationdate = kwargs.get("creationdate", None)
        self.creationid = kwargs.get("creationid", None)
        self.changedate = kwargs.get("changedate", None)
        self.changeid = kwargs.get("changeid", None)
        self.notes = kwargs.get("notes", None)
        self.props = kwargs.get("props", None)


class run:
    __slots__ = ["tagtype", "text"]

    def __init__(
        self, tagtype: Literal["ph", "it", "hi", "bpt", "ept"] | None, text: str
    ) -> None:
        self.tagtype = tagtype
        self.text = text


class ph(run):
    __slots__ = ["x", "_type", "assoc"]

    def __init__(self, text, **kwargs) -> None:
        self.x = kwargs.get("x", None)
        self._type = kwargs.get("_type", None)
        self.assoc = kwargs.get("assoc", None)
        super().__init__("ph", text)


class it(run):
    __slots__ = ["pos", "x", "_type"]

    def __init__(self, text: str, pos: str, **kwargs) -> None:
        self.pos = pos
        self.x = kwargs.get("x", None)
        self._type = kwargs.get("_type", None)
        super().__init__("it", text)


class hi(run):
    __slots__ = ["x", "_type"]

    def __init__(self, text: str, **kwargs) -> None:
        self.x = kwargs.get("x", None)
        self._type = kwargs.get("_type", None)
        super().__init__("hi", text)


class bpt(run):
    __slots__ = ["i", "x", "_type"]

    def __init__(self, text: str, i: int | str, **kwargs) -> None:
        self.i = i
        self.x = kwargs.get("x", None)
        self._type = kwargs.get("_type", None)
        super().__init__("bpt", text)


class ept(run):
    __slots__ = ["i"]

    def __init__(self, text: str, i: int | str) -> None:
        self.i = i
        super().__init__("ept", text)


class seg:
    __slots__ = ["content"]

    def __init__(self, content: list[run]) -> None:
        self.content = content
