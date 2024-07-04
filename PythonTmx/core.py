import functools
from enum import StrEnum, auto
from logging import getLogger
from typing import Protocol

from lxml.etree import _Element

logger = getLogger("PythonTmx Logger")


class TmxElements(StrEnum):
    tmx = auto()
    header = auto()
    prop = auto()
    note = auto()
    ude = auto()
    map = auto()
    body = auto()
    tu = auto()
    tuv = auto()
    seg = auto()
    hi = auto()
    it = auto()
    ph = auto()
    bpt = auto()
    ept = auto()
    ut = auto()
    sub = auto()


class TmxElement(Protocol):
    def serialize_attributes(self) -> dict[str, str]:
        """
        Validates and converts the attributes to a xml serializable dict

        Raises:
            TmxInvalidAttributeError: raised if any attribute is of the wrong
            type or its value is incorrect.
            TmxInvalidContentError: raised if content is None, not a Sequence,
            or if any item inside content is not one of the allowed types.

        Returns:
            dict[str, str] -- A tmx compliant and
            xml serializable dict of the object's attributes
        """

    def to_element(self) -> _Element:
        """
        Serializes the object to a lxml `_Element`

        Raises:
            TmxInvalidContentError: raised if any item inside self.content is
            not tmx compliant, or if content is not a non-empty Sequence.

        Returns:
            _Element -- the lxml `_Element` representing the object
        """

    def to_string(self) -> str:
        """
        Serializes the object to a string directly.

        Raises:
            TmxInvalidContentError: raised if any item inside self.content is
            not tmx compliant, or if content is not a non-empty Sequence.

        Returns:
            str -- a string representation of the object
        """


def debug(func):
    """
    simple debug decorator that log the start and end of a function and
    the value of all its args and kwargs.

    used during dev
    """

    @functools.wraps(func)
    def debug_logger(*args, **kwargs):
        logger.debug(
            f"starting execution of function {func.__name__}\nargs: {args}\nkwargs: {kwargs}"
        )
        value = func(*args, **kwargs)
        logger.debug(f"execution of function {func.__name__} finished")
        return value

    return debug_logger
