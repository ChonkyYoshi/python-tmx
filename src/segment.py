"""segment object definition"""
from dataclasses import dataclass, field
from run import run


@dataclass(kw_only=True, slots=True)
class segment:
    runs: list[run] = field(default_factory=list)
