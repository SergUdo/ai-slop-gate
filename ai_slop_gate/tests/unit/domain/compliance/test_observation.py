# ai_slop_gate/tests/unit/domain/compliance/test_observation.py
from ai_slop_gate.domain.compliance.observation import ComplianceObservation
from ai_slop_gate.domain.decision import DecisionMode

def test_compliance_observation_fields():
    obs = ComplianceObservation(
        license="GPL-3.0",
        severity="high",
        message="Forbidden"
    )
    assert obs.license == "GPL-3.0"
    assert obs.severity == "high"
    assert obs.message == "Forbidden"
    assert obs.suggested_decision() == DecisionMode.BLOCKING
