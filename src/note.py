"""Everything note related"""

from shared.base import StructuralElement


class prop(StructuralElement):
    """Note - used for comments.\n
    Attributes:
        - Required:
            - value
        - Optional:
            - lang
            - encoding
    """

    def __init__(
        self,
        value: str,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        self.value: str = value
        self.lang: str | None = lang
        self.encoding: str | None = encoding
        super().__init__()
