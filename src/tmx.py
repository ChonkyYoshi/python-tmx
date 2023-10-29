"""tmx object definition"""

from dataclasses import dataclass

from header import header
from tu import tu


@dataclass(kw_only=True, slots=True)
class tmx:
    header: header
    tus: list[tu]
