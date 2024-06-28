from typing import (
    Callable,
    Optional,
    Protocol,
    TypeAlias,
)
from xml.etree.ElementTree import Element

from lxml.etree import _Element

_XmlElement: TypeAlias = Element | _Element


class TmxElement(Protocol):
    def __init__(
        self, XmlElement: Optional[_XmlElement] = None, strict: bool = True, **attribs
    ) -> None: ...
    def to_element(self, factory: Callable) -> _XmlElement: ...
    def to_string(self) -> str: ...
    @property
    def attrib(self) -> dict[str, str]: ...
