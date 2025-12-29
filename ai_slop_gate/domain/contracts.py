from typing import List
from .observation import Observation
from .decision import Decision, DecisionMode
from .policy import PolicyRule


class Stage1ContractError(RuntimeError):
    pass


def evaluate_policy(
    observations: List[Observation],
    rules: List[PolicyRule],
) -> Decision:
    """
    Canonical Stage 1 policy evaluation.

    GUARANTEES:
    - No provider logic
    - No LLM calls
    - Deterministic output
    """

    reasons: List[str] = []
    mode = DecisionMode.ADVISORY

    for rule in rules:
        for obs in observations:
            if obs.code in rule.match:
                reasons.append(rule.message)

                if rule.decision == "blocking":
                    mode = DecisionMode.BLOCKING

    # HARD SAFETY: advisory-only repositories
    if mode == DecisionMode.BLOCKING and not reasons:
        raise Stage1ContractError(
            "Blocking decision without reasons is forbidden"
        )

    return Decision(
        mode=mode,
        reasons=reasons,
    )
