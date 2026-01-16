from ai_slop_gate.domain.policy_engine import PolicyRule

def test_policy_rule_contract():
    rule = PolicyRule(
        id="x",
        category="SECURITY",
        signal="BAD",
        min_confidence=0.5,
        action="blocking",
        message="Nope",
    )

    assert rule.category == "SECURITY"
