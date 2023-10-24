"""Everything prop related"""

from typing import Any
from shared.base import StructuralElement


class prop(StructuralElement):
    """Property - used to define the various properties of its parent (or of the document when used in the header).\n
    These properties are not defined by the tmx spec.\n
    Attributes:
        - Required:
            - prop_type
            - value
        - Optional:
            - lang
            - encoding.
    """

    def __init__(
        self,
        prop_type: str,
        value: Any,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        self.prop_type: str = prop_type
        self.value: Any = value
        self.lang: str | None = lang
        self.encoding: str | None = encoding
        super().__init__()
