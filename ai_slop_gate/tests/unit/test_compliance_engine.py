import pytest
from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.compliance.engine import evaluate_compliance_risks

def test_detects_secret_violation():
    obs = Observation(
        rule_id="S-SCAN",
        category="COMPLIANCE",
        signal="SECRET_EXPOSED",
        message="Potential hardcoded secret found",
        severity=Severity.HIGH,
        confidence=0.8,
        evidence={"secret": True}
    )

    risks = evaluate_compliance_risks([obs], [], [])

    assert len(risks) == 1
    assert "security-risk" in risks[0]

