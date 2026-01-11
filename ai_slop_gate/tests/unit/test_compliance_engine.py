import pytest
from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.compliance.engine import evaluate_compliance_risks
from ai_slop_gate.domain.compliance.rules import LicenseRule


@pytest.fixture
def mock_rules():
    return [LicenseRule(id="LIC-GPL", forbidden_licenses={"GPL-3.0"}, message="Forbidden license detected")]

def test_detects_forbidden_license(mock_rules):
    obs = Observation(
        rule_id="L-SCAN",
        category="compliance",
        signal="license_violation",
        message="Found forbidden license: GPL-3.0",
        severity=Severity.HIGH,
        confidence=1.0,
        location=None
    )
    risks = evaluate_compliance_risks([obs], mock_rules, [])
    assert len(risks) == 1
    assert "GPL-3.0" in risks[0]

def test_detects_secret_violation():
    obs = Observation(
        rule_id="S-SCAN",
        category="compliance",
        signal="secret_exposed",
        message="Potential hardcoded secret found",
        severity=Severity.HIGH,
        confidence=0.8,
        location=None
    )
    risks = evaluate_compliance_risks([obs], [], [])
    assert len(risks) == 1
    assert "security-risk" in risks[0].lower()