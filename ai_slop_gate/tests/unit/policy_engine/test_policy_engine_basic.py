from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.contracts import PolicyRule
from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.decision import DecisionMode


def test_policy_engine_no_rules_returns_allow():
    engine = PolicyEngine(rules=[])
    decision = engine.evaluate([])

    assert decision.mode == DecisionMode.ALLOW
    assert decision.reasons == []
    assert decision.annotations == []


def test_policy_engine_advisory_rule():
    rule = PolicyRule(
        id="adv",
        when={
            "category": "TEST",
            "signal": "X",
            "min_confidence": 0.0,
        },
        then={
            "action": "advisory",
            "message": "Advisory triggered",
        },
    )

    obs = Observation(
        category="TEST",
        signal="X",
        confidence=1.0,
        message="test"
    )

    engine = PolicyEngine([rule])
    decision = engine.evaluate([obs])

    assert decision.mode == DecisionMode.ADVISORY
    assert "Advisory triggered" in decision.reasons


def test_policy_engine_blocking_rule():
    rule = PolicyRule(
        id="block",
        when={
            "category": "TEST",
            "signal": "X",
            "min_confidence": 0.0,
        },
        then={
            "action": "blocking",
            "message": "Blocking triggered",
        },
    )

    obs = Observation(
        category="TEST",
        signal="X",
        confidence=1.0,
        message="test"
    )

    engine = PolicyEngine([rule])
    decision = engine.evaluate([obs])

    assert decision.mode == DecisionMode.BLOCKING
    assert "Blocking triggered" in decision.reasons
