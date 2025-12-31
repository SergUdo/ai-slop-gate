from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class DecisionMode(str, Enum):
    ADVISORY = "advisory"
    BLOCKING = "blocking"

@dataclass(frozen=True)
class Annotation:
    file: str
    line: int
    message: str
    level: str  # "warning" or "error"

@dataclass(frozen=True)
class Decision:
    """
    Result of policy evaluation.

    Stage 1 invariant:
    - Decision is derived ONLY from policy + observations
    """
    mode: DecisionMode
    reasons: List[str]
    annotations: Optional[List[Annotation]] = None

from .observation import Observation
from .contracts import PolicyRule

def evaluate_policy(
    observations: List[Observation],
    rules: List[PolicyRule],
) -> Decision:
    """
    Pure domain function.

    Evaluates observations against policy rules
    and produces a Decision.

    Stage 2.1 invariant:
    - No IO
    - No providers
    - No reporters
    """
    reasons: List[str] = []
    annotations: List[Annotation] = []
    mode = DecisionMode.ADVISORY

    for obs in observations:
        for rule in rules:
            if (
                obs.category == rule.category
                and obs.signal == rule.signal
                and obs.confidence >= rule.min_confidence
            ):
                reasons.append(rule.message)

                if obs.evidence and "file" in obs.evidence:
                    annotations.append(
                        Annotation(
                            file=obs.evidence["file"],
                            line=obs.evidence.get("line", 1),
                            message=rule.message,
                            level="error" if rule.decision == DecisionMode.BLOCKING else "warning"
                        )
                    )

                if rule.decision == DecisionMode.BLOCKING:
                    mode = DecisionMode.BLOCKING

    return Decision(
        mode=mode,
        reasons=reasons,
        annotations=annotations if annotations else None
    )
