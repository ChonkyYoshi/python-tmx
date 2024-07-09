from __future__ import annotations

from pprint import pformat
from typing import (
    Callable,
    ClassVar,
    Iterable,
    Iterator,
    Literal,
    MutableSequence,
    Optional,
    Protocol,
)


class ElementLike(Protocol):
    text: Optional[str]
    tail: Optional[str]

    def __iter__(self): ...
    def get(self, key, default): ...
    def set(self, key, value): ...
    def append(self, value): ...
    def __len__(self): ...
    def __getitem__(self, key): ...
    def __setitem__(self, key, value): ...


class InlineElement:
    _content: MutableSequence
    _allowed_attributes: ClassVar[tuple[str, ...]]
    _allowed_children = ClassVar[tuple[str, ...]]

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
        if key not in self._allowed_attributes and key != "_content":
            raise KeyError(f"attribute {key} is not allowed on this object")
        self.__dict__[key] = value

    def set(self, key: str, value: str | int) -> None:
        if key not in self._allowed_attributes and key != "_content":
            raise KeyError(f"attribute {key} is not allowed on this object")
        setattr(self, key, value)

    def items(self) -> Iterator[tuple[str, int | str]]:
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
    ) -> Iterator[str | InlineElement]:
        for item in self._content:
            if key is None:
                yield item
            else:
                if isinstance(item, type(key)):
                    yield item
            if isinstance(item, InlineElement) and recursive:
                yield from item.iter(recursive, key)

    def serialize_attrs(self) -> dict[str, str]:
        raise NotImplementedError

    def serialize(
        self,
        factory: Literal["str", "bytes"] | Callable[[str], ElementLike],
    ) -> str | bytes | ElementLike:
        def _to_string() -> str:
            elem = f"<{self.__class__.__name__.lower()} "
            elem += " ".join(
                f'{key}="{val}"' for key, val in self.serialize_attrs().items()
            )
            elem += ">"
            if len(self._content):
                bpt_count, ept_count = 0, 0
                for item in self._content:
                    match item:
                        case str():
                            elem += item
                        case InlineElement() if item.__class__.__name__ in self._allowed_children:  # type: ignore
                            if item.__class__.__name__ == "Bpt":
                                bpt_count += 1
                            if item.__class__.__name__ == "Ept":
                                ept_count += 1
                            elem += item.serialize(factory="str")  # type: ignore
                        case _:
                            raise TypeError(
                                f"{type(item).__name__} is not allowed in a hi element"
                            )
            match bpt_count - ept_count:
                case 0:
                    pass
                case 1:
                    raise ValueError("One bpt element is missing its ept counterpart")
                case n if n > 1:
                    raise ValueError(
                        f"{n} bpt elements are missing their ept counterpart"
                    )
                case -1:
                    raise ValueError("One ept element is missing its bpt counterpart")
                case n if n < 1:
                    raise ValueError(
                        f"{n} ept elements are missing their bpt counterpart"
                    )
            elem += f"</{self.__class__.__name__.lower()}>"
            return elem

        def _to_element(factory: Callable[[str], ElementLike]) -> ElementLike:
            elem = factory(self.__class__.__name__.lower())
            elem.text, elem.tail = "", ""
            for key, val in self.serialize_attrs().items():
                elem.set(key, val)
            if len(self._content):
                bpt_count, ept_count = 0, 0
                for item in self._content:
                    match item:
                        case str() if not len(elem):
                            elem.text += item
                        case str():
                            elem[-1].tail += item
                        case InlineElement() if item.__class__.__name__ in self._allowed_children:  # type: ignore
                            if item.__class__.__name__ == "Bpt":
                                bpt_count += 1
                            if item.__class__.__name__ == "Ept":
                                ept_count += 1
                            elem.append(item.serialize(factory))
                        case _:
                            raise TypeError(
                                f"{type(item).__name__} is not allowed in a hi element"
                            )
            match bpt_count - ept_count:
                case 1:
                    raise ValueError("One bpt element is missing its ept counterpart")
                case n if n > 1:
                    raise ValueError(
                        f"{n} bpt elements are missing their ept counterpart"
                    )
                case -1:
                    raise ValueError("One ept element is missing its bpt counterpart")
                case n if n < 1:
                    raise ValueError(
                        f"{n} ept elements are missing their bpt counterpart"
                    )
            return elem

        match factory:
            case "str":
                return _to_string()
            case "bytes":
                return _to_string().encode()
            case func if callable(func):
                return _to_element(factory=func)
