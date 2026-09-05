"""Spike 2b: xmlfile with buffered=False -- the mode the writer actually needs."""

from lxml import etree

DTD = etree.DTD(open("src/hypomnema/resources/tmx14.dtd", "rb"))


class Probe:
  def __init__(self) -> None:
    self.chunks: list[str] = []
    self.fail = False
    self.fail_once = False
    self._failed = False

  def write(self, data: str | bytes) -> int:
    if self.fail or (self.fail_once and not self._failed):
      self._failed = True
      raise OSError("disk full")
    text = data.decode("utf-8") if isinstance(data, bytes) else data
    self.chunks.append(text)
    return len(text)

  def flush(self) -> None:
    pass

  @property
  def content(self) -> str:
    return "".join(self.chunks)


def valid_tu(text: str) -> etree._Element:
  tu = etree.fromstring(f'<tu><tuv xml:lang="en"><seg>{text}</seg></tuv></tu>')
  assert DTD.validate(tu), DTD.error_log
  return tu


def timing() -> None:
  print("=== buffered=False: incremental byte arrival ===")
  probe = Probe()
  header = etree.fromstring(
    '<header creationtool="ct" creationtoolversion="1" segtype="sentence"'
    ' o-tmf="t" adminlang="en" srclang="en" datatype="plaintext"/>'
  )
  with etree.xmlfile(probe, encoding="UTF-8", close=False, buffered=False) as xf:
    print(f"  after xmlfile():  {probe.content!r}")
    xf.write_declaration()
    print(f"  after declaration: {probe.content!r}")
    with xf.element("tmx", version="1.4"):
      print(f"  after opening root: {probe.content!r}")
      xf.write(header)
      print(f"  after header:       {probe.content[-60:]!r}")
      with xf.element("body"):
        print(f"  after opening body: {probe.content[-20:]!r}")
        xf.write(valid_tu("one"))
        print(f"  after tu one:       {probe.content[-80:]!r}")
  print(f"  after exit:         {probe.content[-30:]!r}\n")


def failure_mid_stream() -> None:
  print("=== buffered=False: underlying write fails mid-stream ===")
  probe = Probe()
  try:
    with etree.xmlfile(probe, encoding="UTF-8", close=False, buffered=False) as xf:
      with xf.element("tmx"):
        with xf.element("body"):
          xf.write(valid_tu("one"))
          probe.fail = True
          xf.write(valid_tu("two"))
  except BaseException as error:  # noqa: BLE002
    print(f"  raised: {type(error).__name__}: {error}")
  print(f"  output ({len(probe.content)} chars):\n{probe.content!r}\n")


def failure_recovery_attempt() -> None:
  print("=== buffered=False: write() after a failed write() ===")
  probe = Probe()
  probe.fail_once = True
  try:
    with etree.xmlfile(probe, encoding="UTF-8", close=False, buffered=False) as xf:
      with xf.element("tmx"):
        with xf.element("body"):
          try:
            xf.write(valid_tu("one"))
          except OSError as error:
            print(f"  first write raised: {type(error).__name__}: {error}")
          try:
            xf.write(valid_tu("two"))
            print("  retry succeeded (stream usable)")
          except BaseException as error:  # noqa: BLE002
            print(f"  retry raised: {type(error).__name__}: {error}")
  except BaseException as error:  # noqa: BLE002
    print(f"  at exit: {type(error).__name__}: {error}")
  print(f"  output ({len(probe.content)} chars):\n{probe.content!r}\n")


if __name__ == "__main__":
  timing()
  failure_mid_stream()
  failure_recovery_attempt()
