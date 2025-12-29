from dataclasses import dataclass
from enum import Enum
from typing import List


class DecisionMode(str, Enum):
    ADVISORY = "advisory"
    BLOCKING = "blocking"


@dataclass(frozen=True)
class Decision:
    """
    Result of policy evaluation.

    Stage 1 invariant:
    - Decision is derived ONLY from policy + observations
    """

    mode: DecisionMode
    reasons: List[str]
