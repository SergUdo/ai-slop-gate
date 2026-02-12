from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.contracts import PolicyRule
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.decision import DecisionMode


def test_policy_blocks_on_compliance_observation():
    # Stage 0.7: PolicyRule uses when/then contract
    rules = [
        PolicyRule(
            id="forbidden-license",
            when={
                "category": "COMPLIANCE",
                "signal": "FORBIDDEN_LICENSE",
                "min_confidence": 0.5,
            },
            then={
                "action": "blocking",
                "message": "Forbidden license detected",
            },
        )
    ]

    # Stage 0.7: Observation uses new contract
    obs = [
        Observation(
            category="COMPLIANCE",
            signal="FORBIDDEN_LICENSE",
            confidence=1.0,
            message="License GPL-3.0 is forbidden by compliance policy",
            severity=Severity.HIGH,
            evidence={"license": "GPL-3.0"},
            rule_id="L-SCAN",
        )
    ]

    engine = PolicyEngine(rules)
    decision = engine.evaluate(obs)

    assert decision.mode == DecisionMode.BLOCKING
    assert "Forbidden license detected" in decision.reasons
