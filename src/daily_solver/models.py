from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Problem:
    title: str
    url: str
    statement: str
    examples: list[dict[str, Any]] = field(default_factory=list)
    source: str = "configured"


@dataclass(frozen=True)
class Solution:
    title: str
    url: str
    explanation: str
    time_complexity: str
    space_complexity: str
    implementation: str
    tests: str = ""