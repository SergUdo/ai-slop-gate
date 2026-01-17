from ai_slop_gate.domain.policy_engine import PolicyRule


def test_policy_rule_contract():
    rule = PolicyRule(
        id="x",
        when={
            "category": "SECURITY",
            "signal": "BAD",
            "min_confidence": 0.5,
        },
        then={
            "action": "blocking",
            "message": "Nope",
        },
    )

    assert rule.when["category"] == "SECURITY"
    assert rule.when["signal"] == "BAD"
    assert rule.when["min_confidence"] == 0.5
    assert rule.then["action"] == "blocking"
    assert rule.then["message"] == "Nope"
