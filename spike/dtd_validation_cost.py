"""Spike 3: per-TU DTD validation cost.

Question: the plan validates every <tu> against the DTD before converting it
(reader) and before committing it (writer). Is per-unit validation affordable,
or does it dominate streaming throughput?

Measured per element: DTD.validate(), parse (fromstring), and tostring, on a
realistic size ladder, plus the full pipeline the reader will actually run
(parse + validate) so the overhead shows up in context.
"""

import time

from lxml import etree

DTD = etree.DTD(open("src/hypomnema/resources/tmx14.dtd", "rb"))

HEADER_ATTRS = (
  'creationtool="ct" creationtoolversion="1.0" segtype="sentence"'
  ' o-tmf="tmf" adminlang="en" srclang="en" datatype="plaintext"'
)

SMALL = """
<tu tuid="1"><tuv xml:lang="en"><seg>Hello world</seg></tuv></tu>
"""

MEDIUM = """
<tu tuid="2" datatype="plaintext">
  <note>a translation memory note</note>
  <prop type="origin">machine</prop>
  <tuv xml:lang="en" creationdate="20260905T120000Z"><seg>The <ph x="1">[skip]</ph> quick
  brown fox jumps over the lazy dog near the <bpt i="1">[</bpt>river<ept i="1">]</ept> bank.</seg></tuv>
  <tuv xml:lang="de" creationdate="20260905T120000Z"><seg>Der <ph x="1">[skip]</ph> schnelle
  braune Fuchs springt ueber den faulen Hund nahe dem <bpt i="1">[</bpt>Fluss<ept i="1">]</ept> Ufer.</seg></tuv>
</tu>
"""


def large() -> str:
  segs = []
  for index in range(20):
    segs.append(
      f'<tuv xml:lang="l{index % 40:02d}"><seg>Sentence number {index} with '
      f'<bpt i="{index}">&lt;</bpt>inline content<ept i="{index}">&gt;</ept> and '
      f"<hi>emphasis</hi> plus a decent amount of surrounding plain text to make the "
      f"unit realistically large, around this size, repeating filler words.</seg></tuv>"
    )
  return '<tu tuid="large">' + "".join(segs) + "</tu>"


def timed(fn, elements: list[etree._Element], rounds: int = 5) -> float:
  """Median seconds per call across rounds."""
  samples = []
  for _ in range(rounds):
    start = time.perf_counter()
    for element in elements:
      fn(element)
    samples.append((time.perf_counter() - start) / len(elements))
  return sorted(samples)[len(samples) // 2]


def measure(name: str, xml: str, count: int = 2000) -> None:
  elements = [etree.fromstring(xml) for _ in range(count)]
  size = len(xml)
  validate_time = timed(lambda element: DTD.validate(element), elements)
  parse_time = timed(lambda element: etree.fromstring(etree.tostring(element)), elements)
  serialize_time = timed(etree.tostring, elements)
  pipeline_time = timed(lambda element: DTD.validate(etree.fromstring(etree.tostring(element))), elements)

  def format_results(label: str, seconds: float) -> str:
    return f"  {label:<38} {seconds * 1e6:8.1f} us/elem  ({1 / seconds:>12,.0f} /s)"

  print(f"{name}  ({size:,} bytes per fragment)")
  print(format_results("DTD.validate()", validate_time))
  print(format_results("parse (tostring+fromstring)", parse_time))
  print(format_results("tostring()", serialize_time))
  print(format_results("reader pipeline (parse+validate)", pipeline_time))
  overhead = validate_time / (parse_time + validate_time)
  print(f"  validation share of reader pipeline: {overhead:.1%}\n")


def main() -> None:
  header = etree.fromstring(f"<header {HEADER_ATTRS}/>")
  # warm-up so first-touch costs (libxml2 dict, allocator) don't pollute round 1
  for _ in range(500):
    DTD.validate(header)
    etree.fromstring(SMALL)
  print()
  measure("small tu (1 tuv, plain seg)", SMALL)
  measure("medium tu (2 tuvs, note, prop, inline)", MEDIUM)
  measure("large tu (20 tuvs, heavy inline)", large(), count=200)


if __name__ == "__main__":
  main()
