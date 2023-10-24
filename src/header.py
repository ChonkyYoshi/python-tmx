"""everything header related"""

from shared.base import StructuralElement
from typing import Any, Literal


class header(StructuralElement):
    """File header - contains information pertaining to the whole document.\n
    Attributes:
        - Required:
            - creationtool
            - creationtoolversion
            - segtype
            - tmf
            - adminlang
            - srclang
            - datatype.
        - Optional attributes:
            - encoding
            - creationdate
            - creationid
            - changedate
            - changeid.\n
    """

    def __init__(
        self,
        creationtool: str,
        creationtoolversion: str,
        segtype: Literal["block", "paragraph", "sentence", "phrase"],
        tmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        encoding: str | None = None,
        creationdate: str | None = None,
        creationid: str | None = None,
        changedate: str | None = None,
        changeid: str | None = None,
    ) -> None:
        self.creationtool: str = creationtool
        self.creationtoolversion: str = creationtoolversion
        self.segtype: Literal["block", "paragraph", "sentence", "phrase"] = segtype
        self.tmf: str = tmf
        self.adminlang: str = adminlang
        self.srclang: str = srclang
        self.datatype: str = datatype
        self.encoding: str | None = encoding
        self.creationdate: str | None = creationdate
        self.creationid: str | None = creationid
        self.changedate: str | None = changedate
        self.changeid: str | None = changeid
        super().__init__()

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "segtype" and __value not in [
            "block",
            "paragraph",
            "sentence",
            "phrase",
        ]:
            raise ValueError
        return super().__setattr__(__name, __value)


h = header("", "", "", "", "", "", "")
1
