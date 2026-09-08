"""Error hierarchy."""


class TmxError(Exception):
  """Base class for errors concerning TMX data."""


class TmxSpecError(TmxError):
  """Data violates the TMX contract."""


class TmxWarning(UserWarning):
  """Soft advisory that does not violate the TMX contract.

  Emitted for spec recommendations we deliberately do not enforce; consumers
  can filter, escalate, or ignore via the standard ``warnings`` machinery.
  """
