"""Direct element-to-model projection for the first tuv/ph slice.

Accepts already-parsed lxml elements, not bytes. This is not a hardened
XML reader; parser configuration and document-level checks remain I/O work.
"""

from lxml import etree
from pydantic import ValidationError

from ..errors import TmxSpecError
from ..models import Ph, TmxModel, TranslationUnitVariant
from .content import child_elements, read_mixed_content
from .dtd import validate_fragment


def from_element(element: etree._Element) -> TmxModel:
  """DTD-check a fragment, then project it without modifying its tree.

  Valid TMX outside the implemented slice raises NotImplementedError,
  rather than silently losing unsupported content.
  """
  validate_fragment(element)
  return _from_element(element)


def _from_element(element: etree._Element) -> TmxModel:
  if not isinstance(element.tag, str) or element.tag.startswith("{"):
    raise TmxSpecError(f"expected a namespace-free TMX element, got {element.tag!r}")
  try:
    match element.tag:
      case "tuv":
        children = tuple(child_elements(element))
        if any(child.tag != "seg" for child in children):
          raise NotImplementedError("variant metadata projection is not implemented yet")
        # The DTD has already checked seg presence, attributes and cardinality.
        return TranslationUnitVariant.model_validate(
          {
            "xml_lang": element.get("{http://www.w3.org/XML/1998/namespace}lang"),
            "o_encoding": element.get("o-encoding"),
            "datatype": element.get("datatype"),
            "usagecount": element.get("usagecount"),
            "lastusagedate": element.get("lastusagedate"),
            "creationtool": element.get("creationtool"),
            "creationtoolversion": element.get("creationtoolversion"),
            "creationdate": element.get("creationdate"),
            "creationid": element.get("creationid"),
            "changedate": element.get("changedate"),
            "o_tmf": element.get("o-tmf"),
            "changeid": element.get("changeid"),
            "lang": element.get("lang"),
            "content": _parse_content(children[0]),
          }
        )
      case "ph":
        return Ph.model_validate(
          {
            "x": element.get("x"),
            "assoc": element.get("assoc"),
            "type": element.get("type"),
            "content": _parse_content(element),
          }
        )
      case _:
        raise NotImplementedError(f"projection of <{element.tag}> is not implemented yet")
  except ValidationError as error:
    raise TmxSpecError(f"<{element.tag}> at line {element.sourceline}: {error}") from error


def _parse_content(element: etree._Element) -> tuple[str | TmxModel, ...]:
  return tuple(item if isinstance(item, str) else _from_element(item) for item in read_mixed_content(element))
