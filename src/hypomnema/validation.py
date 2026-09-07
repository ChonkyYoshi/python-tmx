"""Explicit, user-invocable validation for rules spanning several nodes.

GAPS decision 11: cheap local constraints run automatically in the models;
these cross-node correctness checks never run automatically. A user calls
them at their own runtime cost, and the writer (once it exists) always
calls them before converting a model to XML -- successfully completed
output must be spec-compliant. Rejections are Pydantic ``ValidationError``
with the offending node's location; the writer will wrap them into
``TmxSpecError``.

Current checks (GAPS decisions 12-13):

- ``validate_translation_unit_variant``: ``bpt``/``ept`` pairing and
  ``bpt.i`` uniqueness per flow scope. Flows are the variant's segment
  content and each ``<sub>``'s content (the embedded segment's own flow);
  ``<hi>`` is transparent, so its inline elements join the enclosing
  flow. Matching is per-``i`` with ordering, deliberately not stack
  nesting: the spec permits overlapping native code pairs.
- ``validate_translation_unit``: the variant check for every variant,
  plus one ``TmxWarning`` when sibling variants disagree on their ``x``
  values -- the spec's cross-variant matching mechanism, advisory per
  decision 13.
"""

from warnings import warn

from pydantic import ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from .errors import TmxWarning
from .models import (
  Bpt,
  Ept,
  Hi,
  It,
  Ph,
  SegContentItem,
  Sub,
  SubContentItem,
  TranslationUnit,
  TranslationUnitVariant,
  Ut,
)

_PAIRING_ERROR_TYPE = "inline_tag_pairing"


def _pairing_error(loc: tuple[str | int, ...], message: str, node: object) -> InitErrorDetails:
  return {
    "type": PydanticCustomError(_PAIRING_ERROR_TYPE, "{message}", {"message": message}),
    "loc": loc,
    "input": node,
  }


def _walk_segment(
  items: tuple[SegContentItem, ...], loc: tuple[str | int, ...], errors: list[InitErrorDetails]
) -> None:
  """Walk one flow: fresh ``i`` namespaces, unmatched-bpt check at the end."""
  bpt_locations: dict[int, tuple[tuple[str | int, ...], Bpt]] = {}
  ept_seen: set[int] = set()
  _walk_items(items, loc, errors, bpt_locations, ept_seen)
  for i, (bpt_loc, bpt) in bpt_locations.items():
    if i not in ept_seen:
      errors.append(_pairing_error(bpt_loc, f"<bpt> i={i} has no subsequent corresponding <ept> within this flow", bpt))


def _walk_items(
  items: tuple[SegContentItem, ...],
  loc: tuple[str | int, ...],
  errors: list[InitErrorDetails],
  bpt_locations: dict[int, tuple[tuple[str | int, ...], Bpt]],
  ept_seen: set[int],
) -> None:
  """Walk one flow's items in document order, sharing the flow's state.

  ``<hi>`` recursion shares the caller's state (it is transparent);
  paired and placeholder tags open fresh flows for their ``<sub>``
  contents.
  """
  for index, node in enumerate(items):
    child_loc = (*loc, index, "content")
    if isinstance(node, Bpt):
      if node.i in bpt_locations:
        errors.append(
          _pairing_error(
            (*loc, index), f"duplicate <bpt> i={node.i} within one flow; i must be unique among <bpt> elements", node
          )
        )
      else:
        bpt_locations[node.i] = ((*loc, index), node)
      _walk_sub_flows(node.content, child_loc, errors)
    elif isinstance(node, Ept):
      if node.i in ept_seen:
        errors.append(
          _pairing_error(
            (*loc, index), f"duplicate <ept> i={node.i} within one flow; i must be unique among <ept> elements", node
          )
        )
      ept_seen.add(node.i)
      if node.i not in bpt_locations:
        errors.append(
          _pairing_error((*loc, index), f"<ept> i={node.i} has no corresponding <bpt> earlier in this flow", node)
        )
      _walk_sub_flows(node.content, child_loc, errors)
    elif isinstance(node, It | Ph | Ut):
      _walk_sub_flows(node.content, child_loc, errors)
    elif isinstance(node, Hi):
      _walk_items(node.content, child_loc, errors, bpt_locations, ept_seen)


def _walk_sub_flows(
  items: tuple[SubContentItem, ...], loc: tuple[str | int, ...], errors: list[InitErrorDetails]
) -> None:
  """Walk the content of a paired or placeholder tag: text plus ``<sub>``
  nodes, each ``<sub>`` its own flow."""
  for index, node in enumerate(items):
    if isinstance(node, Sub):
      _walk_segment(node.content, (*loc, index, "content"), errors)


def validate_translation_unit_variant(tuv: TranslationUnitVariant) -> None:
  """Check ``bpt``/``ept`` pairing and ``i`` uniqueness in every flow.

  Per GAPS decision 12: every ``bpt`` needs a subsequent corresponding
  ``ept`` and every ``ept`` a preceding ``bpt``, within one flow; ``i``
  is unique among ``bpt`` elements and among ``ept`` elements of a flow.
  Raises ``ValidationError`` with the offending node's location.
  """
  errors: list[InitErrorDetails] = []
  _walk_segment(tuv.content, ("content",), errors)
  if errors:
    raise ValidationError.from_exception_data("TranslationUnitVariant", errors)


def _collect_x_values(node: SegContentItem | SubContentItem, into: set[int]) -> None:
  """Collect the ``x`` values of the inline elements the spec matches
  across variants (``bpt``, ``it``, ``ph``, ``hi``), including nested
  content."""
  if isinstance(node, str):
    return
  if isinstance(node, Bpt | It | Ph | Hi) and node.x is not None:
    into.add(node.x)
  for child in node.content:
    _collect_x_values(child, into)


def validate_translation_unit(tu: TranslationUnit) -> None:
  """Validate the whole translation unit.

  Runs ``validate_translation_unit_variant`` on every variant (raising on
  the first batch of structural errors), then emits one ``TmxWarning`` if
  the variants disagree on their inline ``x`` values (GAPS decision 13).
  """
  errors: list[InitErrorDetails] = []
  for index, tuv in enumerate(tu.variants):
    variant_errors: list[InitErrorDetails] = []
    _walk_segment(tuv.content, ("content",), variant_errors)
    for error in variant_errors:
      error["loc"] = ("variants", index, *error["loc"])
    errors.extend(variant_errors)
  if errors:
    raise ValidationError.from_exception_data("TranslationUnit", errors)
  x_sets = []
  for tuv in tu.variants:
    values: set[int] = set()
    for node in tuv.content:
      _collect_x_values(node, values)
    x_sets.append(frozenset(values))
  if len(set(x_sets)) > 1:
    all_values = sorted(set().union(*x_sets))
    warn(
      f"the variants of this <tu> use different inline x values {all_values};"
      " the x attribute matches inline tags between variants",
      TmxWarning,
    )
