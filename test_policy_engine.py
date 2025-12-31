from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.policy_engine import PolicyRule, evaluate_policy
from ai_slop_gate.domain.decision import DecisionMode

observations = [
    Observation(
        category="quality",
        signal="negative",
        confidence=0.8,
        message="TODO detected",
        evidence={"file": None, "line": None},
    )
]

rules = [
    PolicyRule(
        id="no-todo",
        category="quality",
        signal="negative",
        min_confidence=0.7,
        action="advisory",
        message="Remove TODOs before merge",
    )
]

decision = evaluate_policy(observations, rules)

print(decision)
assert decision.mode == DecisionMode.ADVISORY
assert "Remove TODOs before merge" in decision.reasons
