from dataclasses import dataclass
from typing import List, Optional

from .decision import Decision, DecisionMode, Annotation
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
    Evaluates a set of observations against a list of policy rules
    and returns a Decision object.
    """
    reasons_set = set()
    annotations: list[Annotation] = []
    mode = DecisionMode.ADVISORY

    for obs in observations:
        for rule in rules:
            if (
                obs.category == rule.category
                and obs.signal == rule.signal
                and getattr(obs, "confidence", 1.0) >= getattr(rule, "min_confidence", 0.0)
            ):
                reasons_set.add(rule.message)

                if hasattr(obs, 'evidence') and obs.evidence and "file" in obs.evidence:
                    annotations.append(
                        Annotation(
                            file=obs.evidence["file"],
                            line=obs.evidence.get("line", 1),
                            message=rule.message,
                            level="error" if rule.action == "blocking" else "warning"
                        )
                    )

                if rule.action == "blocking":
                    mode = DecisionMode.BLOCKING

    return Decision(
        mode=mode,
        reasons=sorted(reasons_set),
        annotations=annotations
    )


# --- Stub class for backward compatibility with tests / CLI ---
class PolicyEngine:
    """
    Wrapper class to maintain backward compatibility with tests and CLI.
    Calls evaluate_policy internally.
    """
    def __init__(self, rules: Optional[List[PolicyRule]] = None):
        self.rules = rules or []

    def evaluate(self, observations: List[Observation]) -> Decision:
        return evaluate_policy(observations, self.rules)
