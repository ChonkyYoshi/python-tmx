"""Direct model-to-element projection for the first tuv/ph slice."""

from datetime import datetime

from lxml import etree

from ..errors import TmxSpecError
from ..models import Ph, TmxModel, TranslationUnitVariant
from ..validators import format_datetime, format_integer
from .content import write_mixed_content


def to_element(model: TmxModel) -> etree._Element:
  """Build a detached element, without indentation or model_dump().

  This is projection, not whole-tree revalidation. The caller owns domain
  checks and DTD validation of the result. Unsupported nodes/metadata fail
  explicitly. Expanded empty-tag spelling belongs to the future writer.
  """
  match model:
    case TranslationUnitVariant():
      if model.metadata:
        raise NotImplementedError("variant metadata projection is not implemented yet")
      element = etree.Element("tuv")
      _write_attributes(element, model)
      segment = etree.SubElement(element, "seg")
      _build_content(segment, model.content)
      return element
    case Ph():
      element = etree.Element("ph")
      _write_attributes(element, model)
      _build_content(element, model.content)
      return element
    case _:
      raise NotImplementedError(f"projection of {type(model).__name__} is not implemented yet")


def _write_attributes(element: etree._Element, model: Ph | TranslationUnitVariant) -> None:
  """Walk native fields, excluding the discriminator and explicit child slots."""
  for field_name in type(model).model_fields:
    if field_name in {"element", "metadata", "content"}:
      continue
    value: object = getattr(model, field_name)
    if value is None:
      continue

    match value:
      case str():
        formatted = value
      case datetime():
        formatted = format_datetime(value)
      case int():
        formatted = format_integer(value)
      case _:
        raise TypeError(f"unsupported attribute value for {type(model).__name__}.{field_name}")

    xml_name = (
      f"{{http://www.w3.org/XML/1998/namespace}}{field_name[4:]}"
      if field_name.startswith("xml_")
      else field_name.replace("_", "-")
    )
    try:
      element.set(xml_name, formatted)
    except ValueError as error:
      raise TmxSpecError(f"XML-illegal attribute {xml_name!r} on <{element.tag}>: {error}") from error


def _build_content(element: etree._Element, items: tuple[str | TmxModel, ...]) -> None:
  write_mixed_content(element, (item if isinstance(item, str) else to_element(item) for item in items))
