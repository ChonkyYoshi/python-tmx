from __future__ import annotations

from typing import ClassVar, Generator, Iterable, MutableSequence, Optional

from PythonTmx.helpers import xml_escape


class InlineElement:
    """
    Base class for all inline elements, i.e. anything inside a segment

    Acts as list-like for content related operation and dict-like for
    attribute related operations.

    Implements the extra methods:
    * iter() -- to iterate over the content with greater control
    * to_element() -- to serialize the object to an lxml `_Element`
    * to_string() -- to serialize the object directly to a string
    """

    _content: MutableSequence
    _allowed_attributes: ClassVar[tuple]
    _allowed_children: ClassVar[tuple]

    def __repr__(self) -> str:
        attr_dict = {key: getattr(self, key) for key in self._allowed_attributes}
        return (
            f"{self.__class__.__name__}({str(attr_dict)}, content={str(self._content)})"
        )

    def __len__(self):
        return len(self._content)

    def __iter__(self) -> Generator[str | InlineElement, None, None]:
        for item in self._content:
            yield item

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

    def clear(self) -> None:
        """clear's the object's content"""
        self._content = []

    def extend(self, value: Iterable) -> None:
        """extend the objetc's content from value"""
        self._content.extend(value)

    def append(self, value: str | InlineElement) -> None:
        """append valuee to the object's content"""
        self._content.append(value)

    def insert(self, index: int, value: InlineElement | str) -> None:
        """insert value at index in the object's content"""
        self._content.insert(index, value)

    def index(
        self,
        value: str | InlineElement,
        start: int = 0,
        stop: Optional[int] = None,
    ) -> int:
        """returns the first index of value from the object's content"""
        if stop is None:
            return self._content.index(value, start)
        return self._content.index(value, start, stop)

    def remove(self, value: str | InlineElement) -> None:
        """removes the element from the content at the given index without
        returning it"""
        self._content.remove(value)

    def pop(self, index: int) -> str | InlineElement:
        """removes the element from the content at the given index and returns it"""
        return self._content.pop(index)

    def reverse(self) -> None:
        """reverses the order of the content's elements"""
        self._content.reverse()

    def get(self, key: str) -> str | int | None:
        """retrive a attribute's value, equivalent to self.key.
        raises a KeyError if the attribute doesn't exist"""
        if key in self._allowed_attributes:
            return getattr(self, key)
        raise KeyError("attribute does not exist on this object")

    def set(self, key: str, value: str | int) -> None:
        """Set an attributes value, raises a KeyError if the attribute is not
        one that is allowed on the object"""
        if key not in self._allowed_attributes:
            raise KeyError("attribute is allowed on this object")
        setattr(self, key, value)

    def items(self) -> Generator[tuple[str, int | str], None, None]:
        """iterates over the object's attributes yielding a (key, value) tuple"""
        for key in self._allowed_attributes:
            yield key, getattr(self, key)

    def update(self, other: dict, **kwargs):
        """Updates the object's attributes from the dict/keywords arguments"""
        for key, val in other.items():
            self.set(key, val)
        for key, val in kwargs.items():
            self.set(key, val)

    def iter(
        self,
        recursive: bool = False,
        key: Optional[str | InlineElement | tuple[str | InlineElement]] = None,
    ) -> Generator[str | InlineElement, None, None]:
        """
        A Generator that yields every item in the object's content, in order.

        Keyword Arguments:
            recursive {bool} -- if true, yield all nested children in order
            (default: {False})
            key {Optional[str | InlineElement | tuple[str | InlineElement]]} --
            restricts the type of element to yield. if None yields every item
            (default: {None})

        """
        for item in self._content:
            if key is None:
                yield item
            else:
                if isinstance(item, type(key)):
                    yield item
            if isinstance(item, InlineElement) and recursive:
                yield from item.iter(recursive, key)

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
