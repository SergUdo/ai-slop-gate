from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DecisionMode(str, Enum):
    ALLOW = "allow"
    ADVISORY = "advisory"
    BLOCKING = "blocking"


@dataclass(frozen=True)
class Annotation:
    file: str
    line: int
    message: str
    level: str  # "warning" | "error"


@dataclass(frozen=True)
class Decision:
    """
    Result of policy evaluation.

    Domain invariant:
    - Produced ONLY by policy evaluation
    - Never mutated downstream
    """
    mode: DecisionMode
    reasons: List[str]
    annotations: Optional[List[Annotation]] = None
