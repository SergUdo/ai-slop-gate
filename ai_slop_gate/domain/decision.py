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
    mode = DecisionMode.ADVISORY

    for rule in rules:
        for obs in observations:
            if obs.code in rule.match:
                reasons.append(rule.message)
                if rule.decision == DecisionMode.BLOCKING.value:
                    mode = DecisionMode.BLOCKING
                break

    return Decision(
        mode=mode,
        reasons=reasons,
    )
