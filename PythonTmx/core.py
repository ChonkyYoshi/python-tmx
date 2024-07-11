from __future__ import annotations

from datetime import datetime
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


class TmxElement:
    _content: MutableSequence
    _allowed_attributes: ClassVar[tuple[str, ...]]
    _allowed_children: ClassVar[tuple[str, ...]]

    def __init__(
        self,
        xml_element: Optional[ElementLike] = None,
        **kwargs,
    ) -> None:
        if xml_element is None:
            for attr in self._allowed_attributes:
                setattr(self, attr, kwargs.get(attr, None))
        else:
            for attr in self._allowed_attributes:
                if attr.startswith("o"):
                    setattr(
                        self,
                        attr,
                        kwargs.get(attr, xml_element.get("o-" + attr[1:], None)),
                    )
                else:
                    setattr(self, attr, kwargs.get(attr, xml_element.get(attr, None)))
        if "x" in self._allowed_attributes:
            try:
                self.x = int(self.x)  # type:ignore
            except (ValueError, TypeError):
                pass
        if "i" in self._allowed_attributes:
            try:
                self.i = int(self.i)  # type:ignore
            except (ValueError, TypeError):
                pass
        if "usagecount" in self._allowed_attributes:
            try:
                self.usagecount = int(self.usagecount)  # type:ignore
            except (ValueError, TypeError):
                pass
        if "creationdate" in self._allowed_attributes:
            try:
                self.creationdate = datetime.strptime(
                    self.creationdate,  # type:ignore
                    r"%Y%m%dT%H%M%SZ",
                )
            except (ValueError, TypeError):
                pass
        if "changedate" in self._allowed_attributes:
            try:
                self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")  # type:ignore
            except (ValueError, TypeError):
                pass
        if "lastusagedate" in self._allowed_attributes:
            try:
                self.lastusagedate = datetime.strptime(
                    self.lastusagedate,  # type:ignore
                    r"%Y%m%dT%H%M%SZ",
                )
            except (ValueError, TypeError):
                pass

    def __repr__(self):
        attr_dict = {key: getattr(self, key, None) for key in self._allowed_attributes}
        return f"{self.__class__.__name__}:{pformat(attr_dict)}"

    def __len__(self):
        if hasattr(self, "_content"):
            return len(self._content)
        raise AttributeError("Element does not have content, cannot get length")

    def __iter__(self):
        if hasattr(self, "_content"):
            return len(self._content)
        raise AttributeError("Element does not have content, cannot iterate over it")

    def __getitem__(self, key):
        if hasattr(self, "_content"):
            return self._content[key]
        raise AttributeError(
            f"Element does not have content, cannot get element at index {key}"
        )

    def __setitem__(self, key, value):
        if hasattr(self, "_content"):
            self._content[key] = value
        else:
            raise AttributeError(
                f"Element does not have content, cannot set element at index {key}"
            )

    def __delitem__(self, key):
        if hasattr(self, "_content"):
            del self._content[key]
        else:
            raise AttributeError(
                f"Element does not have content, cannot delete element at index {key}"
            )

    def __reversed__(self):
        if hasattr(self, "_content"):
            yield from self._content.__reversed__()
        else:
            raise AttributeError(
                "Element does not have content, cannot iterate in reverse"
            )

    def __contain__(self, item):
        if hasattr(self, "_content"):
            return item in self._content
        return False

    def __eq__(self, other):
        if not isinstance(other, TmxElement):
            return False
        for attribute in self._allowed_attributes:
            if getattr(self, attribute) != getattr(other, attribute):
                return False
        if hasattr(self, "_content"):
            if not hasattr(other, "_content"):
                return False
            if len(self) != len(other):
                return False
            if not len(self):
                return True
            for i in range(len(self._content)):
                if self._content[i] != other._content[i]:
                    return False
        else:
            if not hasattr(other, "_content"):
                return True
            return False

    def clear(self) -> None:
        if hasattr(self, "_content"):
            self._content = []
        else:
            raise AttributeError("Element does not have content, cannot clear")

    def extend(self, value: Iterable) -> None:
        if hasattr(self, "_content"):
            self._content.extend(value)
        else:
            raise AttributeError("Element does not have content, cannot extend")

    def append(self, value: str | TmxElement) -> None:
        if hasattr(self, "_content"):
            self._content.append(value)
        else:
            raise AttributeError("Element does not have content, cannot append")

    def insert(self, index: int, value: TmxElement | str) -> None:
        if hasattr(self, "_content"):
            self._content.insert(index, value)
        else:
            raise AttributeError("Element does not have content, cannot insert")

    def index(
        self,
        value: str | TmxElement,
        start: int = 0,
        stop: Optional[int] = None,
    ) -> int:
        if hasattr(self, "_content"):
            if stop is None:
                return self._content.index(value, start)
            return self._content.index(value, start, stop)
        else:
            raise AttributeError(
                f"Element does not have content, cannot get index of value {value}"
            )

    def remove(self, value: str | TmxElement) -> None:
        if hasattr(self, "_content"):
            self._content.remove(value)
        raise AttributeError(
            f"Element does not have content, cannot remove value {value}"
        )

    def pop(self, index: int) -> str | TmxElement:
        if hasattr(self, "_content"):
            return self._content.pop(index)
        raise AttributeError(
            f"Element does not have content, cannot pop value at index {index}"
        )

    def reverse(self) -> None:
        if hasattr(self, "_content"):
            return self._content.reverse()
        raise AttributeError("Element does not have content, cannot reverse")

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
        key: Optional[str | TmxElement | tuple[str | TmxElement]] = None,
    ) -> Iterator[str | TmxElement]:
        if hasattr(self, "_content"):
            for item in self._content:
                if key is None:
                    yield item
                else:
                    if isinstance(item, type(key)):
                        yield item
                if isinstance(item, TmxElement) and recursive:
                    yield from item.iter(recursive, key)
        else:
            raise AttributeError("Element does not have content, cannot iterate")

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
            if not hasattr(self, "_content"):
                return elem + " />"
            elem += ">"
            if len(self._content):
                bpt_count, ept_count = 0, 0
                for item in self._content:
                    match item:
                        case str():
                            elem += item
                        case TmxElement() if item.__class__.__name__ in self._allowed_children:  # type: ignore
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
                        raise ValueError(
                            "One bpt element is missing its ept counterpart"
                        )
                    case n if n > 1:
                        raise ValueError(
                            f"{n} bpt elements are missing their ept counterpart"
                        )
                    case -1:
                        raise ValueError(
                            "One ept element is missing its bpt counterpart"
                        )
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
            if not hasattr(self, "_content"):
                return elem
            if len(self._content):
                bpt_count, ept_count = 0, 0
                for item in self._content:
                    match item:
                        case str() if not len(elem):
                            elem.text += item
                        case str():
                            elem[-1].tail += item
                        case TmxElement() if item.__class__.__name__ in self._allowed_children:  # type: ignore
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
                        raise ValueError(
                            "One bpt element is missing its ept counterpart"
                        )
                    case n if n > 1:
                        raise ValueError(
                            f"{n} bpt elements are missing their ept counterpart"
                        )
                    case -1:
                        raise ValueError(
                            "One ept element is missing its bpt counterpart"
                        )
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
