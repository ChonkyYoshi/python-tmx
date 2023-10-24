"""everything header related"""

from shared.base import StructuralElement


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
        segtype: str,
        otmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        oencoding: str | None = None,
        creationdate: str | None = None,
        creationid: str | None = None,
        changedate: str | None = None,
        changeid: str | None = None,
    ) -> None:
        self.creationtool: str = creationtool
        self.creationtoolversion: str = creationtoolversion
        self.segtype: str = segtype
        self.otmf: str = otmf
        self.adminlang: str = adminlang
        self.srclang: str = srclang
        self.datatype: str = datatype
        self.oencoding: str | None = oencoding
        self.creationdate: str | None = creationdate
        self.creationid: str | None = creationid
        self.changedate: str | None = changedate
        self.changeid: str | None = changeid
        super().__init__()
