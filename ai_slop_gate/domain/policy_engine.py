from dataclasses import dataclass
from typing import List

from .decision import Decision, DecisionMode
from .observation import Observation


@dataclass(frozen=True)
class PolicyRule:
    id: str
    category: str
    signal: str
    min_confidence: float
    action: str          # "advisory" | "blocking"
    message: str


def evaluate_policy(
    observations: List[Observation],
    rules: List[PolicyRule],
) -> Decision:
    """
    Stage 2.3 invariant:
    - Policy evaluates ONLY structured observations
    - Deterministic
    - No provider / LLM knowledge
    """

    reasons: list[str] = []
    mode = DecisionMode.ADVISORY

    for rule in rules:
        for obs in observations:
            if (
                obs.category == rule.category
                and obs.signal == rule.signal
                and obs.confidence >= rule.min_confidence
            ):
                reasons.append(rule.message)

                if rule.action == "blocking":
                    mode = DecisionMode.BLOCKING

    return Decision(mode=mode, reasons=reasons)
