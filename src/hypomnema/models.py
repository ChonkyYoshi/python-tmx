"""All Pydantic TMX models (recursive family, one module).

Node shapes, the mechanical field naming, and the two inline content
grammars. Value typing and conversion live in ``types.py``; this module only
references the aliases.

Field naming is mechanical: the TMX attribute name with ``-`` and ``:``
replaced by ``_``, otherwise verbatim -- ``o_tmf``, ``xml_lang``, and plain
``type``, ``i``, ``x``. No translation table.

``lang`` is the deprecated attribute; ``xml_lang`` is the standard one.
The deprecated attribute still exists in TMX 1.4b and is modeled.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from .types import (
  TMXAsciiText,
  TMXEncodingName,
  TMXDatetime,
  TMXHexInteger,
  TMXIdentifier,
  TMXInteger,
  TMXLanguageTag,
  TMXSourceLanguage,
  TMXUnicodeCodePoint,
)


def _as_tuple[T](value: list[T] | tuple[T, ...]) -> tuple[T, ...]:
  """Accept a list or a tuple for a repeated field; store a tuple.

  Tuples close the mutation hole that ``validate_assignment`` cannot see:
  ``model.items.append(x)`` is invisible, ``model.items += (x,)`` rebinds and
  revalidates. Values of any other type pass through untouched so the strict
  tuple check rejects them with a proper Pydantic error.
  """
  return tuple(value) if isinstance(value, list) else value


type ModelSequence[T] = Annotated[tuple[T, ...], BeforeValidator(_as_tuple)]


# Union slots, named for the content shape they carry. Lazy PEP 695 aliases,
# resolved on first use once every model below exists.
type HeaderChild = Note | Property | Ude
type TuChild = Note | Property | TranslationUnitVariant
type TuvChild = Note | Property
type SegContentItem = str | Bpt | Ept | Ph | It | Hi | Ut
type SubContentItem = str | Sub


class TmxModel(BaseModel):
  model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True)


class Note(TmxModel):
  """``<note>``: free-form comment.

  DTD: ``<!ELEMENT note (#PCDATA)>`` -- text only.
  """

  element: Literal["note"] = Field(default="note", frozen=True)
  o_encoding: TMXEncodingName | None = None
  xml_lang: TMXLanguageTag | None = None
  # Deprecated by TMX 1.3: use xml_lang.
  lang: TMXLanguageTag | None = None
  text: str | None = None


class Property(TmxModel):
  """``<prop>``: property name/value pair.

  DTD: ``<!ELEMENT prop (#PCDATA)>`` -- text only; ``type`` required.
  """

  element: Literal["prop"] = Field(default="prop", frozen=True)
  type: str
  xml_lang: TMXLanguageTag | None = None
  o_encoding: TMXEncodingName | None = None
  # Deprecated by TMX 1.3: use xml_lang.
  lang: TMXLanguageTag | None = None
  text: str | None = None


class Map(TmxModel):
  """``<map>``: character mapping inside a ``<ude>``.

  DTD: ``<!ELEMENT map EMPTY>`` -- no content; ``unicode`` required.
  The spec types the values beyond what the DTD can express: ``unicode``
  and ``code`` are ``#x``-prefixed hexadecimal integers, ``ent`` and
  ``subst`` must be ASCII text.
  """

  element: Literal["map"] = Field(default="map", frozen=True)
  unicode: TMXUnicodeCodePoint
  code: TMXHexInteger | None = None
  ent: TMXAsciiText | None = None
  subst: TMXAsciiText | None = None


class Ude(TmxModel):
  """``<ude>``: user-defined encoding.

  DTD: ``<!ELEMENT ude (map+)>`` -- at least one map; ``name`` required.
  Cross-field rule enforced later: ``base`` is required when any ``<map>``
  carries ``code``.
  """

  element: Literal["ude"] = Field(default="ude", frozen=True)
  name: str
  base: TMXEncodingName | None = None
  maps: ModelSequence[Map] = ()


class Sub(TmxModel):
  """``<sub>``: inline code content of a content element.

  DTD: ``<!ELEMENT sub (#PCDATA|bpt|ept|it|ph|hi|ut)*>`` -- the general
  inline grammar, same as ``<seg>``.
  """

  element: Literal["sub"] = Field(default="sub", frozen=True)
  datatype: str | None = None
  type: str | None = None
  content: "ModelSequence[SegContentItem]" = ()


class Bpt(TmxModel):
  """``<bpt>``: beginning of a paired inline tag.

  DTD: ``<!ELEMENT bpt (#PCDATA|sub)*>`` -- text plus ``<sub>`` only;
  ``i`` required.
  """

  element: Literal["bpt"] = Field(default="bpt", frozen=True)
  i: TMXInteger
  x: TMXInteger | None = None
  type: str | None = None
  content: ModelSequence[SubContentItem] = ()


class Ept(TmxModel):
  """``<ept>``: end of a paired inline tag.

  DTD: ``<!ELEMENT ept (#PCDATA|sub)*>`` -- text plus ``<sub>`` only;
  ``i`` required.
  """

  element: Literal["ept"] = Field(default="ept", frozen=True)
  i: TMXInteger
  content: ModelSequence[SubContentItem] = ()


class It(TmxModel):
  """``<it>``: isolated inline tag.

  DTD: ``<!ELEMENT it (#PCDATA|sub)*>`` -- text plus ``<sub>`` only;
  ``pos`` required.
  """

  element: Literal["it"] = Field(default="it", frozen=True)
  pos: str
  x: TMXInteger | None = None
  type: str | None = None
  content: ModelSequence[SubContentItem] = ()


class Ph(TmxModel):
  """``<ph>``: placeholder inline tag.

  DTD: ``<!ELEMENT ph (#PCDATA|sub)*>`` -- text plus ``<sub>`` only.
  """

  element: Literal["ph"] = Field(default="ph", frozen=True)
  x: TMXInteger | None = None
  # Prose enum: "p", "f", or "b".
  assoc: str | None = None
  type: str | None = None
  content: ModelSequence[SubContentItem] = ()


class Hi(TmxModel):
  """``<hi>``: highlight, user-defined emphasis.

  DTD: ``<!ELEMENT hi (#PCDATA|bpt|ept|it|ph|hi|ut)*>`` -- the general
  inline grammar, recursively containing ``<hi>``.
  """

  element: Literal["hi"] = Field(default="hi", frozen=True)
  x: TMXInteger | None = None
  type: str | None = None
  content: "ModelSequence[SegContentItem]" = ()


class Ut(TmxModel):
  """``<ut>``: unknown tag. Deprecated; modeled because TMX 1.4b allows it.

  DTD: ``<!ELEMENT ut (#PCDATA|sub)*>`` -- text plus ``<sub>`` only.
  """

  element: Literal["ut"] = Field(default="ut", frozen=True)
  x: TMXInteger | None = None
  content: ModelSequence[SubContentItem] = ()


class Header(TmxModel):
  """``<header>``: TMX file header.

  DTD: ``<!ELEMENT header (note|prop|ude)*>`` -- interleaved children in
  document order, not grouped by kind. All seven core attributes required.
  """

  element: Literal["header"] = Field(default="header", frozen=True)
  creationtool: str
  creationtoolversion: str
  segtype: str
  o_tmf: str
  adminlang: TMXLanguageTag
  srclang: TMXSourceLanguage
  datatype: str
  o_encoding: TMXEncodingName | None = None
  creationdate: TMXDatetime | None = None
  creationid: str | None = None
  changedate: TMXDatetime | None = None
  changeid: str | None = None
  items: ModelSequence[HeaderChild] = ()


class TranslationUnitVariant(TmxModel):
  """``<tuv>``: one language variant inside a ``<tu>``.

  DTD: ``<!ELEMENT tuv ((note|prop)*, seg)>``. There is no ``Segment``
  model: ``<seg>`` has no attributes or identity, so its mixed inline
  content is carried directly as this node's ``content``.
  """

  element: Literal["tuv"] = Field(default="tuv", frozen=True)
  xml_lang: TMXLanguageTag
  o_encoding: TMXEncodingName | None = None
  datatype: str | None = None
  usagecount: TMXInteger | None = None
  lastusagedate: TMXDatetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: TMXDatetime | None = None
  creationid: str | None = None
  changedate: TMXDatetime | None = None
  o_tmf: str | None = None
  changeid: str | None = None
  # Deprecated by TMX 1.3: use xml_lang.
  lang: str | None = None
  items: ModelSequence[TuvChild] = ()
  content: ModelSequence[SegContentItem] = ()


class TranslationUnit(TmxModel):
  """``<tu>``: one translation unit.

  DTD: ``<!ELEMENT tu ((note|prop)*, tuv+)>`` -- interleaved children in
  document order, at least one variant. No attributes are required; the
  header supplies the defaults.
  """

  element: Literal["tu"] = Field(default="tu", frozen=True)
  tuid: TMXIdentifier | None = None
  o_encoding: TMXEncodingName | None = None
  datatype: str | None = None
  usagecount: TMXInteger | None = None
  lastusagedate: TMXDatetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: TMXDatetime | None = None
  creationid: str | None = None
  changedate: TMXDatetime | None = None
  segtype: str | None = None
  changeid: str | None = None
  o_tmf: str | None = None
  srclang: TMXSourceLanguage | None = None
  items: ModelSequence[TuChild] = ()


