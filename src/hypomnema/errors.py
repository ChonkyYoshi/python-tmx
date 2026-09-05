"""Error hierarchy."""


class TmxWarning(UserWarning):
  """Soft advisory that does not violate the TMX contract.

  Emitted for spec recommendations we deliberately do not enforce; consumers
  can filter, escalate, or ignore via the standard ``warnings`` machinery.
  """
