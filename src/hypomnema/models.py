"""All Pydantic TMX models (recursive family, one module).

Structural pass: every attribute value is a plain ``str``. Proper value types
(integers, datetimes, language tags, enums) are layered in later via
``types.py``; this module fixes the node shapes, the mechanical field naming,
and the two inline content grammars.

Field naming is mechanical: the TMX attribute name with ``-`` and ``:``
replaced by ``_``, otherwise verbatim -- ``o_tmf``, ``xml_lang``, and plain
``type``, ``i``, ``x``. No translation table.

``lang`` is the deprecated attribute; ``xml_lang`` is the standard one.
The deprecated attribute still exists in TMX 1.4b and is modeled.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _as_tuple(value: object) -> object:
  """Accept a list or a tuple for a repeated field; store a tuple.

  Tuples close the mutation hole that ``validate_assignment`` cannot see:
  ``model.items.append(x)`` is invisible, ``model.items += (x,)`` rebinds and
  revalidates.
  """
  if isinstance(value, list):
    return tuple(value)
  return value


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
  o_encoding: str | None = None
  xml_lang: str | None = None
  # Deprecated by TMX 1.3: use xml_lang.
  lang: str | None = None
  text: str = ""


class Property(TmxModel):
  """``<prop>``: property name/value pair.

  DTD: ``<!ELEMENT prop (#PCDATA)>`` -- text only; ``type`` required.
  """

  element: Literal["prop"] = Field(default="prop", frozen=True)
  type: str
  xml_lang: str | None = None
  o_encoding: str | None = None
  # Deprecated by TMX 1.3: use xml_lang.
  lang: str | None = None
  text: str = ""


class Map(TmxModel):
  """``<map>``: character mapping inside a ``<ude>``.

  DTD: ``<!ELEMENT map EMPTY>`` -- no content; ``unicode`` required.
  """

  element: Literal["map"] = Field(default="map", frozen=True)
  unicode: str
  code: str | None = None
  ent: str | None = None
  subst: str | None = None


class Ude(TmxModel):
  """``<ude>``: user-defined encoding.

  DTD: ``<!ELEMENT ude (map+)>`` -- at least one map; ``name`` required.
  Cross-field rule enforced later: ``base`` is required when any ``<map>``
  carries ``code``.
  """

  element: Literal["ude"] = Field(default="ude", frozen=True)
  name: str
  base: str | None = None
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
  i: str
  x: str | None = None
  type: str | None = None
  content: ModelSequence[SubContentItem] = ()


class Ept(TmxModel):
  """``<ept>``: end of a paired inline tag.

  DTD: ``<!ELEMENT ept (#PCDATA|sub)*>`` -- text plus ``<sub>`` only;
  ``i`` required.
  """

  element: Literal["ept"] = Field(default="ept", frozen=True)
  i: str
  content: ModelSequence[SubContentItem] = ()


class It(TmxModel):
  """``<it>``: isolated inline tag.

  DTD: ``<!ELEMENT it (#PCDATA|sub)*>`` -- text plus ``<sub>`` only;
  ``pos`` required.
  """

  element: Literal["it"] = Field(default="it", frozen=True)
  pos: str
  x: str | None = None
  type: str | None = None
  content: ModelSequence[SubContentItem] = ()


class Ph(TmxModel):
  """``<ph>``: placeholder inline tag.

  DTD: ``<!ELEMENT ph (#PCDATA|sub)*>`` -- text plus ``<sub>`` only.
  """

  element: Literal["ph"] = Field(default="ph", frozen=True)
  x: str | None = None
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
  x: str | None = None
  type: str | None = None
  content: "ModelSequence[SegContentItem]" = ()


class Ut(TmxModel):
  """``<ut>``: unknown tag. Deprecated; modeled because TMX 1.4b allows it.

  DTD: ``<!ELEMENT ut (#PCDATA|sub)*>`` -- text plus ``<sub>`` only.
  """

  element: Literal["ut"] = Field(default="ut", frozen=True)
  x: str | None = None
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
  adminlang: str
  srclang: str
  datatype: str
  o_encoding: str | None = None
  creationdate: str | None = None
  creationid: str | None = None
  changedate: str | None = None
  changeid: str | None = None
  items: ModelSequence[HeaderChild] = ()


class TranslationUnitVariant(TmxModel):
  """``<tuv>``: one language variant inside a ``<tu>``.

  DTD: ``<!ELEMENT tuv ((note|prop)*, seg)>``. There is no ``Segment``
  model: ``<seg>`` has no attributes or identity, so its mixed inline
  content is carried directly as this node's ``content``.
  """

  element: Literal["tuv"] = Field(default="tuv", frozen=True)
  xml_lang: str
  o_encoding: str | None = None
  datatype: str | None = None
  usagecount: str | None = None
  lastusagedate: str | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | None = None
  creationid: str | None = None
  changedate: str | None = None
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
  tuid: str | None = None
  o_encoding: str | None = None
  datatype: str | None = None
  usagecount: str | None = None
  lastusagedate: str | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | None = None
  creationid: str | None = None
  changedate: str | None = None
  segtype: str | None = None
  changeid: str | None = None
  o_tmf: str | None = None
  srclang: str | None = None
  items: ModelSequence[TuChild] = ()


Sub.model_rebuild()
Hi.model_rebuild()
