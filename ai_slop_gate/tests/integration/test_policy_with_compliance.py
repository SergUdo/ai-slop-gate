from ai_slop_gate.domain.policy_engine import evaluate_policy
from ai_slop_gate.domain.compliance.observation import ComplianceObservation

def test_policy_blocks_on_compliance_observation():
    observations = [
        ComplianceObservation(
            license="GPL-3.0",
            severity="high",
            message="GPL detected",
        )
    ]

    rules = [
        {
            "id": "forbid-gpl",
            "when": {
                "source": "compliance",
                "license": "GPL-3.0",
            },
            "then": {
                "decision": "block",
                "reason": "GPL not allowed",
            },
        }
    ]

    decision = evaluate_policy(observations, rules)

    assert decision.mode.value == "blocking"
