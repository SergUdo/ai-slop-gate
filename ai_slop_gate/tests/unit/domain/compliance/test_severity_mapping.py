from ai_slop_gate.domain.compliance.enforcement import decision_for_severity
from ai_slop_gate.domain.decision import DecisionMode

def test_high_severity_blocks():
    assert decision_for_severity("high") == DecisionMode.BLOCKING
