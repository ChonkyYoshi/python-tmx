"""Tests for the XML content readers and writers (src/hypomnema/xml/content.py).

Contract under test: ``None`` and the explicitly empty string are distinct
in-memory text slots; adjacent strings combine into one slot; whitespace is
never stripped; comments and PIs are discarded but their tails survive;
unresolved entities and XML-illegal text are rejected; readers never mutate
the tree. The helpers are not TMX grammar validators, so foreign elements
pass through untouched.
"""

from collections.abc import Callable

import pytest
from lxml import etree

from hypomnema.errors import TmxSpecError
from hypomnema.xml.content import (
  XmlContentItem,
  child_elements,
  read_mixed_content,
  read_text,
  write_mixed_content,
  write_text,
)

type ContentReader = Callable[[etree._Element], object]


def bare_element(tag: str = "seg") -> etree._Element:
  """A fresh in-memory element, never parsed, so text slots keep None versus ''."""
  return etree.Element(tag)


def parsed(xml: str) -> etree._Element:
  return etree.fromstring(xml)


def element_with_unresolved_entity() -> etree._Element:
  """An entity declared in the internal subset but left unexpanded.

  With ``resolve_entities=False`` the reference survives iteration as an
  ``_Entity`` node instead of being expanded or rejected by the parser.
  """
  parser = etree.XMLParser(resolve_entities=False)
  return etree.fromstring('<!DOCTYPE seg [<!ENTITY foo "expanded">]><seg>a&foo;b</seg>', parser)


# --- child_elements ---------------------------------------------------------


def test_child_elements_yields_structural_children_in_document_order() -> None:
  element = parsed("<seg><bpt i='1'/><!--skip--><ept i='1'/><?go skip?><hi/></seg>")
  assert [child.tag for child in child_elements(element)] == ["bpt", "ept", "hi"]


def test_child_elements_rejects_an_unresolved_entity() -> None:
  with pytest.raises(TmxSpecError, match="unresolved entity in content at line 1"):
    list(child_elements(element_with_unresolved_entity()))


# --- read_mixed_content -----------------------------------------------------


@pytest.mark.parametrize("xml", ["<seg/>", "<seg></seg>", "<seg><!--c--></seg>", "<seg><?p x?></seg>"])
def test_contentless_elements_yield_no_items(xml: str) -> None:
  assert list(read_mixed_content(parsed(xml))) == []


def test_items_are_yielded_in_document_order_with_exact_slots() -> None:
  element = parsed("<seg>pre<bpt i='1'/>mid<ept i='1'/>post</seg>")
  begin, end = element[0], element[1]
  assert list(read_mixed_content(element)) == ["pre", begin, "mid", end, "post"]


def test_mixed_content_whitespace_is_preserved_verbatim() -> None:
  element = parsed("<seg> a\n\t<bpt i='1'/> b\n </seg>")
  assert list(read_mixed_content(element)) == [" a\n\t", element[0], " b\n "]


def test_adjacent_text_around_discarded_nodes_combines() -> None:
  # Comments and PIs vanish, but the text on both sides survives and merges.
  assert list(read_mixed_content(parsed("<seg>a<!--c-->b<?p x?>c</seg>"))) == ["abc"]


def test_children_around_discarded_nodes_keep_their_order_without_text() -> None:
  element = parsed("<seg><bpt i='1'/><!--c--><ept i='1'/></seg>")
  items = list(read_mixed_content(element))
  elements = [item for item in items if isinstance(item, etree._Element)]
  assert len(elements) == len(items)
  assert [item.tag for item in elements] == ["bpt", "ept"]


def test_explicitly_empty_text_slot_survives_as_empty_string() -> None:
  element = bare_element()
  element.text = ""
  assert list(read_mixed_content(element)) == [""]


def test_unresolved_entity_is_rejected() -> None:
  with pytest.raises(TmxSpecError, match="unresolved entity in content at line 1"):
    list(read_mixed_content(element_with_unresolved_entity()))


# --- read_text --------------------------------------------------------------


@pytest.mark.parametrize("xml", ["<seg/>", "<seg></seg>", "<seg><!--c--></seg>", "<seg><?p x?></seg>"])
def test_contentless_elements_read_as_none(xml: str) -> None:
  assert read_text(parsed(xml)) is None


def test_explicitly_empty_text_slot_reads_as_empty_string_not_none() -> None:
  element = bare_element()
  element.text = ""
  assert read_text(element) == ""


def test_whitespace_only_text_is_returned_verbatim() -> None:
  assert read_text(parsed("<seg>  </seg>")) == "  "


def test_text_around_discarded_nodes_is_joined() -> None:
  assert read_text(parsed("<note>a<!--c-->b<?p x?>c</note>")) == "abc"


@pytest.mark.parametrize("xml", ["<seg><bpt i='1'/></seg>", "<seg>a<bpt i='1'/>b</seg>"])
def test_child_elements_are_rejected_by_the_plain_text_reader(xml: str) -> None:
  with pytest.raises(TmxSpecError, match="expected text only inside <seg> at line 1"):
    read_text(parsed(xml))


def test_unresolved_entity_is_rejected_by_the_plain_text_reader() -> None:
  with pytest.raises(TmxSpecError, match="unresolved entity in content"):
    read_text(element_with_unresolved_entity())


# --- read nonmutation -------------------------------------------------------


@pytest.mark.parametrize(
  "reader",
  [lambda element: list(child_elements(element)), lambda element: list(read_mixed_content(element))],
  ids=["child_elements", "read_mixed_content"],
)
def test_readers_do_not_mutate_the_tree(reader: ContentReader) -> None:
  element = parsed("<seg>a<!--c-->b<bpt i='1'/>c</seg>")
  snapshot = etree.tostring(element)
  reader(element)
  assert etree.tostring(element) == snapshot


# --- write_text -------------------------------------------------------------


def test_writing_none_sets_an_absent_text_slot() -> None:
  element = bare_element()
  write_text(element, None)
  assert element.text is None


def test_writing_empty_string_sets_an_explicitly_empty_text_slot() -> None:
  element = bare_element()
  write_text(element, "")
  assert element.text is not None
  assert element.text == ""


def test_written_text_is_stored_verbatim() -> None:
  element = bare_element()
  write_text(element, " padded\ttext ")
  assert element.text == " padded\ttext "


@pytest.mark.parametrize("text", ["\x00", "a\x0cb"])
def test_xml_illegal_text_is_rejected(text: str) -> None:
  element = bare_element()
  with pytest.raises(TmxSpecError, match="XML-illegal text inside <seg>"):
    write_text(element, text)


def test_none_and_empty_slots_are_indistinguishable_after_a_parse_roundtrip() -> None:
  # The distinction lives in the in-memory slot only: once serialized and
  # re-parsed, an explicitly empty element reads back as None.
  absent = bare_element()
  write_text(absent, None)
  explicit = bare_element()
  write_text(explicit, "")
  for serialized in (etree.tostring(absent), etree.tostring(explicit)):
    assert read_text(etree.fromstring(serialized)) is None


# --- write_mixed_content ----------------------------------------------------


def test_no_items_leaves_a_fresh_element_untouched() -> None:
  element = bare_element()
  write_mixed_content(element, [])
  assert element.text is None
  assert len(element) == 0


def test_consecutive_strings_fold_into_one_text_slot() -> None:
  element = bare_element()
  write_mixed_content(element, ["a", "", "b", "", "c"])
  assert element.text == "abc"
  assert len(element) == 0


def test_items_land_in_exact_text_child_and_tail_slots() -> None:
  element = bare_element()
  begin, end = etree.Element("bpt"), etree.Element("ept")
  write_mixed_content(element, ["pre", begin, "mid", end, "post"])
  assert element.text == "pre"
  assert list(element) == [begin, end]
  assert begin.tail == "mid"
  assert end.tail == "post"


def test_strings_after_a_child_fold_into_its_tail() -> None:
  element = bare_element()
  only = etree.Element("ph")
  write_mixed_content(element, [only, "a", "b"])
  assert element.text is None
  assert only.tail == "ab"


def test_leading_strings_go_to_text_not_a_tail() -> None:
  element = bare_element()
  only = etree.Element("ph")
  write_mixed_content(element, ["a", "b", only])
  assert element.text == "ab"
  assert only.tail is None


@pytest.mark.parametrize("items", [["bad\x0c"], [etree.Element("x"), "bad\x0c"]])
def test_xml_illegal_text_is_rejected_in_text_and_tail_slots(items: list[XmlContentItem]) -> None:
  element = bare_element()
  with pytest.raises(TmxSpecError, match="XML-illegal text inside <seg>"):
    write_mixed_content(element, items)


def test_content_helpers_are_not_tmx_grammar_validators() -> None:
  # A foreign element is written and read back as-is; grammar is not checked.
  element = bare_element()
  foreign = etree.Element("div")
  write_mixed_content(element, ["before", foreign])
  assert list(read_mixed_content(element)) == ["before", foreign]
