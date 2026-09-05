"""Enums, Annotated value aliases, parse/format functions.

Value aliases are public Pydantic functional metadata so a value is honestly
its Python type: a ``TMXDatetime`` is a ``datetime``. The markers make XML
parsing and output formatting -- and JSON, which shares one formatter per
type -- flow through the same functions.

Language-tag validation lives in ``bcp47.py`` (grammar-only, RFC 5646) and is
used here through its ``validate_language_tag``.
"""

import codecs
import warnings
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BeforeValidator, PlainSerializer

from .bcp47 import validate_language_tag
from .errors import TmxWarning


def warn_unknown_encoding(value: str) -> str:
  """Nudge when an encoding name is unknown to Python's codecs.

  The spec recommends IANA charset identifiers for ``o-encoding`` and
  ``<ude base>`` but only as a soft "if possible" -- not enforceable, so
  this warns and keeps the value instead of rejecting it.
  """
  try:
    codecs.lookup(value)
  except LookupError:
    warnings.warn(
      f"encoding {value!r} is not recognized by Python's codecs; the spec recommends IANA charset identifiers",
      TmxWarning,
    )
  return value


type TMXEncodingName = Annotated[str, AfterValidator(warn_unknown_encoding)]


type TMXSegType = Literal["block", "paragraph", "sentence", "phrase"]
"""The ``%segtypes;`` entity the DTD enumerates: the segment's granularity."""

type TMXPos = Literal["begin", "end"]
"""``<it pos>``: whether the isolated tag opens or closes markup."""

type TMXAssoc = Literal["p", "f", "b"]
"""``<ph assoc>``: whether the placeholder belongs to preceding, following,
or both-sides text (spec prose, not the DTD)."""


_DECIMAL_DIGITS = "0123456789"


def parse_integer(value: object) -> int:
  """Parse a decimal integer, e.g. ``usagecount``, ``i``, ``x``.

  Strict ASCII digits: no sign, no whitespace, no ``int()`` conveniences
  such as underscores. SGML ``NUMBER`` admits digits only, so negatives
  are rejected. Already-integer values pass through; strict mode rejects
  ``bool`` downstream.
  """
  if isinstance(value, int):
    return value
  if not isinstance(value, str):
    raise TypeError(f"expected a string, got {type(value)!r}")
  if not value or any(digit not in _DECIMAL_DIGITS for digit in value):
    raise ValueError("expected decimal digits, e.g. '42'")
  return int(value)


def format_integer(value: int) -> str:
  """Format an integer as canonical decimal digits."""
  return str(value)


type TMXInteger = Annotated[int, BeforeValidator(parse_integer), PlainSerializer(format_integer, return_type=str)]


def parse_datetime(value: object) -> datetime:
  """Parse an ISO 8601 instant, e.g. ``creationdate``.

  The spec requires ISO 8601 and only recommends ``YYYYMMDDTHHMMSSZ``, so
  any ISO 8601 instant is accepted: basic or extended, with or without an
  offset. A naive value means UTC. Date-only forms are rejected. The
  result is truncated to whole seconds so ``datetime.now(UTC)`` just
  works. Already-datetime values take the same path.
  """
  if not isinstance(value, datetime):
    if not isinstance(value, str):
      raise TypeError(f"expected a string or datetime, got {type(value)!r}")
    if "t" not in value.lower():
      raise ValueError("expected an instant with date and time, not a date-only value")
    try:
      value = datetime.fromisoformat(value)
    except ValueError:
      raise ValueError(f"not an ISO 8601 instant: {value!r}") from None
  if value.tzinfo is None:
    value = value.replace(tzinfo=UTC)
  return value.replace(microsecond=0)


def format_datetime(value: datetime) -> str:
  """Format an instant in the spec's canonical basic form.

  ``YYYYMMDDTHHMMSSZ`` in UTC; a naive datetime is taken as UTC. Manual
  formatting because ``strftime``'s ``%Y`` zero-padding for years below
  1000 is platform-dependent.
  """
  if value.tzinfo is None:
    value = value.replace(tzinfo=UTC)
  else:
    value = value.astimezone(UTC)
  return f"{value.year:04d}{value.month:02d}{value.day:02d}T{value.hour:02d}{value.minute:02d}{value.second:02d}Z"


type TMXDatetime = Annotated[
  datetime, BeforeValidator(parse_datetime), PlainSerializer(format_datetime, return_type=str)
]


def validate_identifier(value: str) -> str:
  """Check an identifier contains no whitespace, as the spec requires
  for ``tuid``."""
  if any(character.isspace() for character in value):
    raise ValueError("must not contain whitespace")
  return value


type TMXIdentifier = Annotated[str, AfterValidator(validate_identifier)]


def validate_source_language(value: str) -> str:
  """Check a ``srclang`` value: a language tag or ``*all*``.

  The spec makes ``srclang`` values case-insensitive, so ``*ALL*`` is
  normalized to the canonical ``*all*``; language tags keep their
  spelling.
  """
  if value.lower() == "*all*":
    return "*all*"
  return validate_language_tag(value)


type TMXLanguageTag = Annotated[str, AfterValidator(validate_language_tag)]
type TMXSourceLanguage = Annotated[str, AfterValidator(validate_source_language)]


_HEX_DIGITS = "0123456789abcdefABCDEF"


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
  if not isinstance(value, str):
    raise TypeError(f"expected a string, got {type(value)!r}")
  if not value.startswith("#x"):
    raise ValueError("expected a '#x' prefix, e.g. '#xF8FF'")
  digits = value[2:]
  if not digits:
    raise ValueError("missing digits after '#x'")
  for digit in digits:
    if digit not in _HEX_DIGITS:
      raise ValueError(f"invalid hexadecimal digit {digit!r}")
  return int(digits, 16)


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
