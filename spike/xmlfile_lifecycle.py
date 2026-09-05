"""Spike 2: lxml xmlfile lifecycle -- validate-before-commit and failure modes.

The writer design depends on:
1. Writing the declaration, optional DOCTYPE, root, header, then streaming
   <tu> elements committed one complete element per xmlfile.write() call.
2. Knowing exactly when bytes hit the destination (plan: __enter__ validates
   the whole header before the destination sees a byte).
3. Knowing what a mid-stream failure does: which exceptions surface, whether
   the output stays well-formed, whether the writer can recover (plan: it
   fails and stays failed).
"""

from lxml import etree

DTD = etree.DTD(open("src/hypomnema/resources/tmx14.dtd", "rb"))


class Probe:
  """File-like object that logs every write with a running offset."""

  def __init__(self) -> None:
    self.chunks: list[str] = []
    self.closed = False
    self.fail = False

  def write(self, data: str | bytes) -> int:
    if self.fail:
      raise OSError("disk full / stream closed")
    text = data.decode("utf-8") if isinstance(data, bytes) else data
    self.chunks.append(text)
    return len(text)

  def flush(self) -> None:
    pass

  @property
  def content(self) -> str:
    return "".join(self.chunks)


def valid_tu(text: str, lang: str = "en") -> etree._Element:
  tu = etree.fromstring(f'<tu><tuv xml:lang="{lang}"><seg>{text}</seg></tuv></tu>')
  assert DTD.validate(tu), DTD.error_log
  return tu


def happy_path() -> None:
  print("=== happy path: byte timing and structure ===")
  probe = Probe()
  header = etree.fromstring(
    '<header creationtool="ct" creationtoolversion="1" segtype="sentence"'
    ' o-tmf="t" adminlang="en" srclang="en" datatype="plaintext"/>'
  )
  assert DTD.validate(header)

  with etree.xmlfile(probe, encoding="UTF-8", close=False) as xf:
    print(f"  after xmlfile():  bytes so far = {len(probe.content)!r:>5} -> {probe.content!r}")
    xf.write_declaration()
    print(f"  after declaration: {probe.content!r}")
    try:
      xf.write_doctype('<!DOCTYPE tmx SYSTEM "tmx14.dtd">')
      print(f"  after doctype:     {probe.content!r}")
    except Exception as error:  # noqa: BLE001
      print(f"  write_doctype failed: {type(error).__name__}: {error}")
    with xf.element("tmx", version="1.4"):
      xf.write(header)
      with xf.element("body"):
        xf.write(valid_tu("one"))
        xf.write(valid_tu("two"))
  print(f"  final:\n{probe.content}\n")


def failure_closed_stream() -> None:
  print("=== failure: underlying stream closed mid-stream ===")
  probe = Probe()
  with etree.xmlfile(probe, encoding="UTF-8", close=False) as xf:
    with xf.element("tmx"):
      with xf.element("body"):
        xf.write(valid_tu("one"))
        probe.closed = True
        probe.fail = True
        try:
          xf.write(valid_tu("two"))
          print("  write succeeded?!")
        except BaseException as error:  # noqa: BLE002
          print(f"  write raised: {type(error).__name__}: {error}")
        try:
          xf.write(valid_tu("three"))
          print("  second write succeeded?!")
        except BaseException as error:  # noqa: BLE002
          print(f"  second write raised: {type(error).__name__}: {error}")
  print(f"  output after failure:\n{probe.content}\n")


def failure_broken_element_context() -> None:
  print("=== failure: exception raised inside an element context ===")
  probe = Probe()
  try:
    with etree.xmlfile(probe, encoding="UTF-8", close=False) as xf:
      with xf.element("tmx"):
        with xf.element("body"):
          xf.write(valid_tu("one"))
          raise RuntimeError("consumer bug mid-stream")
  except RuntimeError as error:
    print(f"  propagated: {type(error).__name__}: {error}")
  print(f"  output after failure:\n{probe.content}\n")


def misuse_after_context_exit() -> None:
  print("=== misuse: write after root element context exited ===")
  probe = Probe()
  with etree.xmlfile(probe, encoding="UTF-8", close=False) as xf:
    with xf.element("tmx"):
      pass
    try:
      xf.write(valid_tu("late"))
      print("  write succeeded?!")
    except BaseException as error:  # noqa: BLE002
      print(f"  write raised: {type(error).__name__}: {error}")
  print(f"  output:\n{probe.content}\n")


def detached_element_with_tail() -> None:
  print("=== does write() emit a detached element's tail text? ===")
  probe = Probe()
  tu = valid_tu("one")
  tu.tail = "STRAY TAIL TEXT"
  with etree.xmlfile(probe, encoding="UTF-8", close=False) as xf:
    with xf.element("tmx"):
      with xf.element("body"):
        xf.write(tu)
  print(f"  output:\n{probe.content!r}\n")


if __name__ == "__main__":
  happy_path()
  failure_closed_stream()
  failure_broken_element_context()
  misuse_after_context_exit()
  detached_element_with_tail()
