import functools
from logging import getLogger
from typing import Protocol

from lxml.etree import _Element

logger = getLogger("PythonTmx Logger")


class TmxElement(Protocol):
    def to_element(self) -> _Element: ...

    def to_string(self) -> str: ...

    def serialize_attributes(self) -> dict[str, str]: ...


def debug(func):
    """
    simple debug decorator that log the start and end of a function and
    the value of all its args and kwargs
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
