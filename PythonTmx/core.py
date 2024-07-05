from __future__ import annotations

from typing import ClassVar, Generator, Iterable, MutableSequence, Optional, Self

from PythonTmx.helpers import xml_escape


class InlineElement:
    """All the operations on a read-write sequence.

    Concrete subclasses must provide __new__ or __init__,
    __getitem__, __setitem__, __delitem__, __len__, and insert().
    """

    _content: MutableSequence[str | InlineElement]
    _allowed_attributes: ClassVar[tuple[str, ...]]
    _allowed_children: ClassVar[tuple[InlineElement, ...]]

    def __len__(self):
        return len(self._content)

    def __iter__(self) -> Generator[str | InlineElement, None, None]:
        for item in self._content:
            yield item

    def __getitem__(
        self, key: int | slice
    ) -> str | InlineElement | MutableSequence[str | InlineElement]:
        return self._content[key]

    def __setitem__(self, key: int, value: str | Self) -> None:
        self._content[key] = value

    def __delitem__(self, key: int | slice) -> None:
        del self._content[key]

    def __eq__(self, other: object) -> bool:
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

    def __contain__(self, item: str | InlineElement) -> bool:
        for _item in self.iter(key=item):
            if item == _item:
                return True
        return False

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

    def extend(self, value: Iterable):
        for item in value:
            self._content.append(item)

    def append(self, value: str | InlineElement):
        self._content.append(value)

    def to_string(self) -> str:
        """
        Serializes the object to a string directly.

        Raises:
            TmxInvalidContentError: raised if any item inside self.content is
            not tmx compliant, or if content is not a non-empty Sequence.

        Returns:
            str -- a string representation of the object
        """
        string: str = "<hi "
        for attribute in self._allowed_attributes:
            value = self.__getattribute__(attribute)
            if value is None:
                continue
            string += f'{xml_escape(attribute)}="{xml_escape(value)} '
        if not len(self):
            return string + "/>"
        string += ">"
        for item in self:
            match item:
                case None:
                    pass
                case str():
                    string += item
                case InlineElement() if item in self._allowed_children:
                    string += self.to_string()
                case InlineElement():
                    raise TypeError(
                        f"'{type(item).__name__}' is not allowed inside this object"
                    )
                case _:
                    raise TypeError(
                        "Unexpected item encountered. Expected"
                        f"a str or TmxElement but got '{type(item).__name__}'"
                    )
        return string + "</hi>"
