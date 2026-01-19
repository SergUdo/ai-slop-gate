from typing import List

from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.policy import PolicyRule


class PolicyContractError(RuntimeError):
    pass


def evaluate_policy(
    observations: List[Observation],
    rules: List[PolicyRule],
) -> Decision:
    """
    Canonical policy evaluation.

    GUARANTEES:
    - Deterministic
    - No IO
    - No providers
    """

    reasons: List[str] = []
    mode = DecisionMode.ALLOW

    for rule in rules:
        for obs in observations:
            if _matches(rule, obs):
                reasons.append(rule.then["message"])

                if rule.then.get("decision") == "blocking":
                    mode = DecisionMode.BLOCKING
                elif mode != DecisionMode.BLOCKING:
                    mode = DecisionMode.ADVISORY

    if mode == DecisionMode.BLOCKING and not reasons:
        raise PolicyContractError("Blocking decision without reasons")

    return Decision(
        mode=mode,
        reasons=reasons,
    )


def _matches(rule: PolicyRule, obs: Observation) -> bool:
    when = rule.when

    return (
        obs.category == when.get("category")
        and obs.signal == when.get("signal")
        and obs.confidence >= when.get("min_confidence", 0.0)
    )
