"""Enums, Annotated value aliases, parse/format functions.

Value aliases are public Pydantic functional metadata so a value is honestly
its Python type: a ``TMXDatetime`` is a ``datetime``. The markers make XML
parsing and output formatting -- and JSON, which shares one formatter per
type -- flow through the same functions.
"""

import codecs
import warnings
from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, PlainSerializer

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
      f"encoding {value!r} is not recognized by Python's codecs;"
      " the spec recommends IANA charset identifiers",
      TmxWarning,
    )
  return value


type TMXEncodingName = Annotated[str, AfterValidator(warn_unknown_encoding)]


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


type TMXInteger = Annotated[
  int, BeforeValidator(parse_integer), PlainSerializer(format_integer, return_type=str)
]


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

  ``YYYYMMDDTHHMMSSZ`` in UTC; a naive datetime is taken as UTC.
  """
  if value.tzinfo is None:
    value = value.replace(tzinfo=UTC)
  else:
    value = value.astimezone(UTC)
  return (
    f"{value.year:04d}{value.month:02d}{value.day:02d}"
    f"T{value.hour:02d}{value.minute:02d}{value.second:02d}Z"
  )


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


# Grandfathered tags from the IANA registry: the one BCP 47 grammar path a
# structural walk cannot decide. Fixed data, lowercased here.
_GRANDFATHERED_TAGS = frozenset({
  "en-gb-oed",
  "i-ami", "i-bnn", "i-default", "i-enochian", "i-hak", "i-klingon", "i-lux",
  "i-mingo", "i-navajo", "i-pwn", "i-tao", "i-tay", "i-tsu",
  "sgn-be-fr", "sgn-be-nl", "sgn-de", "sgn-dk", "sgn-es", "sgn-fr", "sgn-gb",
  "sgn-gr", "sgn-it", "sgn-jp", "sgn-kr", "sgn-nl", "sgn-pt", "sgn-se",
  "sgn-th", "sgn-tw", "sgn-us", "sgn-za",
  "zh-min", "zh-min-nan",
  "art-lojban", "cel-gaulish", "no-bok", "no-nyn", "zh-guoyu", "zh-hakka",
  "zh-min", "zh-xiang", "zh-yue",
})


def _is_ascii_alpha(text: str) -> bool:
  return text.isascii() and text.isalpha()


def _is_ascii_alnum(text: str) -> bool:
  return text.isascii() and text.isalnum()


def _is_alnum_subtag(text: str, minimum: int, maximum: int) -> bool:
  return minimum <= len(text) <= maximum and _is_ascii_alnum(text)


def validate_language_tag(value: str) -> str:
  """Check a well-formed BCP 47 language tag -- grammar, not registry.

  ``xml:lang``, ``lang``, and ``adminlang``. The full ``langtag`` grammar
  (language, extlangs, script, region, variants, extensions, private use)
  plus the grandfathered registered tags, which a structural walk cannot
  decide. Case is preserved: tags are case-insensitive, spelling is not.
  """
  lowered = value.lower()
  if lowered in _GRANDFATHERED_TAGS:
    return value
  subtags = value.split("-")
  if subtags[0].lower() == "x":
    if len(subtags) < 2 or not all(
      _is_alnum_subtag(subtag, 1, 8) for subtag in subtags[1:]
    ):
      raise ValueError(f"malformed private-use language tag: {value!r}")
    return value
  if not (
    (len(subtags[0]) in (2, 3) and _is_ascii_alpha(subtags[0]))
    or (len(subtags[0]) == 4 and _is_ascii_alpha(subtags[0]))
    or _is_alnum_subtag(subtags[0], 5, 8)
  ):
    raise ValueError(f"malformed language subtag {subtags[0]!r}: {value!r}")
  index = 1
  extlang_count = 0
  while (
    extlang_count < 3
    and index < len(subtags)
    and len(subtags[index]) == 3
    and _is_ascii_alpha(subtags[index])
  ):
    extlang_count += 1
    index += 1
  if index < len(subtags) and len(subtags[index]) == 4 and _is_ascii_alpha(subtags[index]):
    index += 1  # script
  if index < len(subtags) and (
    len(subtags[index]) == 3 and subtags[index].isdigit() and subtags[index].isascii()
  ):
    index += 1  # numeric region
  elif index < len(subtags) and len(subtags[index]) == 2 and _is_ascii_alpha(subtags[index]):
    index += 1  # alpha region
  while index < len(subtags) and (
    _is_alnum_subtag(subtags[index], 5, 8)
    or (
      len(subtags[index]) == 4
      and subtags[index][0].isdigit()
      and _is_ascii_alnum(subtags[index][1:])
    )
  ):
    index += 1  # variants
  singletons: set[str] = set()
  while index < len(subtags):
    subtag = subtags[index].lower()
    if len(subtag) != 1 or not _is_ascii_alnum(subtag):
      raise ValueError(f"malformed subtag {subtags[index]!r}: {value!r}")
    if subtag in singletons:
      raise ValueError(f"duplicate singleton {subtag!r}: {value!r}")
    singletons.add(subtag)
    index += 1
    if index == len(subtags):
      raise ValueError(f"singleton {subtag!r} without subtags: {value!r}")
    if subtag == "x":
      # private use terminates the tag; its subtags may be a single character
      while index < len(subtags):
        if not _is_alnum_subtag(subtags[index], 1, 8):
          raise ValueError(f"malformed private-use subtag {subtags[index]!r}: {value!r}")
        index += 1
    else:
      body_count = 0
      while index < len(subtags) and len(subtags[index]) != 1:
        if not _is_alnum_subtag(subtags[index], 2, 8):
          raise ValueError(f"malformed extension subtag {subtags[index]!r}: {value!r}")
        body_count += 1
        index += 1
      if body_count == 0:
        raise ValueError(f"extension {subtag!r} without subtags: {value!r}")
  return value


type TMXLanguageTag = Annotated[str, AfterValidator(validate_language_tag)]


def validate_source_language(value: str) -> str:
  """Check a ``srclang`` value: a language tag or ``*all*``.

  The spec makes ``srclang`` values case-insensitive, so ``*ALL*`` is
  normalized to the canonical ``*all*``; language tags keep their
  spelling.
  """
  if value.lower() == "*all*":
    return "*all*"
  return validate_language_tag(value)


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
