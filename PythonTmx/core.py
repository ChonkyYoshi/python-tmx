from __future__ import annotations

from pprint import pformat
from typing import ClassVar, Generator, Iterable, Literal, MutableSequence, Optional
from xml.etree.ElementTree import Element

from lxml.etree import _Element


class InlineElement:
    _content: MutableSequence
    _allowed_attributes: ClassVar[tuple]

    def __repr__(self):
        attr_dict = {key: getattr(self, key, None) for key in self._allowed_attributes}
        return f"{self.__class__.__name__}:{pformat(attr_dict)}"

    def __len__(self):
        return len(self._content)

    def __iter__(self):
        return iter(self._content)

    def __getitem__(self, key):
        return self._content[key]

    def __setitem__(self, key, value):
        self._content[key] = value

    def __delitem__(self, key):
        del self._content[key]

    def __reversed__(self):
        self._content.reverse()

    def __contain__(self, item):
        return self._content.__contains__(item)

    def __eq__(self, other):
        if not isinstance(other, InlineElement):
            return False
        for attribute in self._allowed_attributes:
            if getattr(self, attribute) != getattr(other, attribute):
                return False
        if len(self) != len(other):
            return False
        if not len(self):
            return True
        for i in range(len(self._content)):
            if self._content[i] != other._content[i]:
                return False
        return True

    def clear(self) -> None:
        self._content = []

    def extend(self, value: Iterable) -> None:
        self._content.extend(value)

    def append(self, value: str | InlineElement) -> None:
        self._content.append(value)

    def insert(self, index: int, value: InlineElement | str) -> None:
        self._content.insert(index, value)

    def index(
        self,
        value: str | InlineElement,
        start: int = 0,
        stop: Optional[int] = None,
    ) -> int:
        if stop is None:
            return self._content.index(value, start)
        return self._content.index(value, start, stop)

    def remove(self, value: str | InlineElement) -> None:
        self._content.remove(value)

    def pop(self, index: int) -> str | InlineElement:
        return self._content.pop(index)

    def reverse(self) -> None:
        self._content.reverse()

    def get(self, key: str) -> str | int | None:
        if key in self._allowed_attributes:
            return getattr(self, key)
        raise KeyError("attribute does not exist on this object")

    def __setattr__(self, key, value) -> None:
        if key not in self._allowed_attributes:
            raise KeyError("attribute is allowed on this object")
        self.__dict__[key] = value

    def set(self, key: str, value: str | int) -> None:
        if key not in self._allowed_attributes:
            raise KeyError("attribute is allowed on this object")
        setattr(self, key, value)

    def items(self) -> Generator[tuple[str, int | str], None, None]:
        for key in self._allowed_attributes:
            yield key, getattr(self, key)

    def update(self, other: dict, **kwargs):
        for key, val in other.items():
            self.set(key, val)
        for key, val in kwargs.items():
            self.set(key, val)

    def iter(
        self,
        recursive: bool = False,
        key: Optional[str | InlineElement | tuple[str | InlineElement]] = None,
    ) -> Generator[str | InlineElement, None, None]:
        for item in self._content:
            if key is None:
                yield item
            else:
                if isinstance(item, type(key)):
                    yield item
            if isinstance(item, InlineElement) and recursive:
                yield from item.iter(recursive, key)

    def serialize(
        self, method: Literal["str", "byte", "lxml", "ElementTree"]
    ) -> str | bytes | _Element | Element: ...
