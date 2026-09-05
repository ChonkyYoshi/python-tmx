"""Enums, Annotated value aliases, parse/format functions.

Value aliases are public Pydantic functional metadata so a value is honestly
its Python type: a ``TMXDatetime`` is a ``datetime``. The markers make XML
parsing and output formatting -- and JSON, which shares one formatter per
type -- flow through the same functions.

Aliases are bare until the converter pass wires their
``BeforeValidator``/``PlainSerializer`` markers; models already reference the
names.
"""

import re
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, PlainSerializer


# Value aliases. Bare for now: the markers that parse XML strings and format
# canonical output land with the converter pass.
type TMXInteger = Annotated[int, ...]
type TMXDatetime = Annotated[datetime, ...]
type TMXLanguageTag = Annotated[str, ...]
type TMXIdentifier = Annotated[str, ...]
type TMXSourceLanguage = Annotated[str, ...]
"""A ``TMXLanguageTag`` or the special value ``*all*``; not case-sensitive."""


_HEX_CODE_POINT = re.compile(r"#x[0-9A-Fa-f]+")


def parse_hex_integer(value: object) -> int:
  """Parse a ``#x``-prefixed hexadecimal integer, e.g. ``#xF8FF``.

  The format the TMX spec prescribes for ``<map unicode>`` and
  ``<map code>``. Strictly ``#x`` plus hexadecimal digits: no ``0x``, no
  sign, no whitespace, no ``int()`` conveniences such as underscores.
  Already-integer values pass through so Python and JSON-python inputs
  work.
  """
  if isinstance(value, int):
    return value
  if not isinstance(value, str) or not _HEX_CODE_POINT.fullmatch(value):
    raise ValueError("expected '#x' followed by hexadecimal digits, e.g. '#xF8FF'")
  return int(value[2:], 16)


def format_hex_integer(value: int) -> str:
  """Format a hexadecimal integer the way the spec's examples spell it."""
  return f"#x{value:X}"


def validate_unicode_scalar(value: int) -> int:
  """Check a code point is a valid Unicode scalar value.

  0 to 0x10FFFF, surrogates excluded; Private Use areas allowed per spec.
  """
  if not 0 <= value <= 0x10FFFF or 0xD800 <= value <= 0xDFFF:
    raise ValueError("not a valid Unicode scalar value")
  return value


def validate_ascii(value: str) -> str:
  """Check text is ASCII, as the spec requires for ``ent`` and ``subst``."""
  if not value.isascii():
    raise ValueError("must be ASCII")
  return value


type TMXHexInteger = Annotated[
  int, BeforeValidator(parse_hex_integer), PlainSerializer(format_hex_integer, return_type=str)
]
type TMXUnicodeCodePoint = Annotated[TMXHexInteger, AfterValidator(validate_unicode_scalar)]
type TMXAsciiText = Annotated[str, AfterValidator(validate_ascii)]
