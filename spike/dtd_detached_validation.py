"""Spike 1: can lxml's DTD validate detached <header> and <tu> fragments?

The reader/writer design depends on:
1. Loading the bundled DTD from a file object (importlib.resources, zip-safe).
2. Validating elements that are NOT part of a complete <tmx> document --
   mid-stream in the reader, pre-commit in the writer.
3. Usable error messages on failure (element/line context for TmxSpecError).
"""

import io

from lxml import etree

DTD_TEXT = open("src/hypomnema/resources/tmx14.dtd", "rb").read()


def load_dtd_from_bytes() -> etree.DTD:
  return etree.DTD(io.BytesIO(DTD_TEXT))


def load_dtd_from_fileobj() -> etree.DTD:
  import importlib.resources

  resource = importlib.resources.files("hypomnema.resources").joinpath("tmx14.dtd")
  with resource.open("rb") as f:
    return etree.DTD(f)


VALID_HEADER = """
<header creationtool="ct" creationtoolversion="1.0" segtype="sentence"
        o-tmf="tmf" adminlang="en" srclang="en" datatype="plaintext">
  <note>hello</note>
</header>
"""

VALID_TU = """
<tu tuid="1">
  <prop type="x">y</prop>
  <tuv xml:lang="en"><seg>Hello <bpt i="1">{"</bpt>world<ept i="1">"}"</ept></seg></tuv>
  <tuv xml:lang="de"><seg>Hallo <hi>Welt</hi></seg></tuv>
</tu>
"""

CASES = [
  ("valid header", VALID_HEADER, True),
  ("valid tu", VALID_TU, True),
  (
    "header missing required srclang",
    '<header creationtool="c" creationtoolversion="1" segtype="sentence" o-tmf="t" adminlang="en" datatype="plaintext"/>',
    False,
  ),
  ("tu missing required tuv", "<tu><prop>p</prop></tu>", False),
  ("tu with unknown child element", "<tu><bogus/></tu>", False),
  ("tu with undeclared attribute", '<tu tuid="1" vendorjunk="x"><tuv xml:lang="en"><seg>hi</seg></tuv></tu>', False),
  (
    "tu with interleaved note/prop (DTD-legal)",
    '<tu><note>n1</note><prop type="x">p</prop><note>n2</note><tuv xml:lang="en"><seg>s</seg></tuv></tu>',
    True,
  ),
  ("tu with note AFTER tuv (illegal order)", '<tu><tuv xml:lang="en"><seg>s</seg></tuv><note>n</note></tu>', False),
  ("tuv missing xml:lang", "<tu><tuv><seg>s</seg></tuv></tu>", False),
  (
    "seg with illegal nesting (bpt inside ph)",
    '<tu><tuv xml:lang="en"><seg><ph x="1">a<bpt i="1">t</bpt></ph></seg></tuv></tu>',
    False,
  ),
  (
    "header with bad segtype enum value",
    '<header creationtool="c" creationtoolversion="1" segtype="banana" o-tmf="t" adminlang="en" srclang="en" datatype="plaintext"/>',
    False,
  ),
]


def main() -> None:
  dtd = load_dtd_from_bytes()
  load_dtd_from_fileobj()
  print("DTD loaded from bytes and from file object: both ok\n")

  for name, xml, expected in CASES:
    element = etree.fromstring(xml)
    ok = dtd.validate(element)
    status = "OK " if ok == expected else "MISMATCH"
    print(f"[{status}] {name}: valid={ok}")
    if not ok:
      for error in dtd.error_log:
        print(f"         {error.line}:{error.column} {error.message}")
  print()

  # Where do line numbers point on detached fragments?
  element = etree.fromstring("<tu>\n  <bogus/>\n</tu>")
  dtd.validate(element)
  print(f"detached fragment error lines: {[e.line for e in dtd.error_log]}")

  # Element vs ElementTree argument: do both work?
  tree = etree.ElementTree(etree.fromstring(VALID_HEADER))
  print(f"validate(Element)={dtd.validate(etree.fromstring(VALID_HEADER))}, validate(ElementTree)={dtd.validate(tree)}")

  # Does validate mutate/touch the fragment? (reader reuses the element tree)
  element = etree.fromstring(VALID_TU)
  before = etree.tostring(element)
  dtd.validate(element)
  print(f"validate mutated the fragment: {etree.tostring(element) != before}")


if __name__ == "__main__":
  main()
