"""Load the trusted package DTD and validate an element subtree."""

from functools import cache
from importlib.resources import files

from lxml import etree

from ..errors import TmxSpecError


@cache
def load_dtd() -> etree.DTD:
  resource = files("hypomnema").joinpath("resources", "tmx14.dtd")
  with resource.open("rb") as source:
    return etree.DTD(source)


def validate_fragment(element: etree._Element) -> None:
  """Validate this subtree, not its parent or its tail in that parent."""
  try:
    load_dtd().assertValid(element)
  except etree.DocumentInvalid as error:
    raise TmxSpecError(f"<{element.tag}> at line {element.sourceline}: {error}") from error
