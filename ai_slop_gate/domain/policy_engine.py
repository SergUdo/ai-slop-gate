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

    - observations: list of Observation objects from providers
    - rules: list of PolicyRule objects defining checks
    """
    # --- Initialize variables to avoid UnboundLocalError
    reasons_set = set()
    annotations: list[Annotation] = []
    mode = DecisionMode.ADVISORY

    for obs in observations:
        for rule in rules:
            # --- Check if observation matches the rule criteria
            if (
                obs.category == rule.category
                and obs.signal == rule.signal
                and obs.confidence >= rule.min_confidence
            ):
                # Add the rule message to reasons
                reasons_set.add(rule.message)

                # --- Optionally create an annotation if evidence is provided
                if hasattr(obs, 'evidence') and obs.evidence and "file" in obs.evidence:
                    annotations.append(
                        Annotation(
                            file=obs.evidence["file"],
                            line=obs.evidence.get("line", 1),
                            message=rule.message,
                            level="error" if rule.action == "blocking" else "warning"
                        )
                    )

                # --- Escalate decision mode if any blocking rule is triggered
                if rule.action == "blocking":
                    mode = DecisionMode.BLOCKING

    # --- Return the final Decision object
    return Decision(
        mode=mode,
        reasons=sorted(reasons_set),
        annotations=annotations
    )
