from ai_slop_gate.domain.compliance.observation import ComplianceObservation

def test_compliance_observation_fields():
    obs = ComplianceObservation(
        license="MIT",
        severity="low",
        message="MIT detected",
    )

    assert obs.source == "compliance"
    assert obs.license == "MIT"
