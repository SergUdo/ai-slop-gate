import pytest
from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.compliance.engine import evaluate_compliance_risks

def test_forbidden_license_emits_observation(tmp_path):
    policy_file = tmp_path / "policy.yml"
    policy_file.write_text("""
version: "v1"
compliance:
  enabled: true
  forbid_licenses: ["GPL-3.0"]
rules: []
""")

    policy_config, _ = load_policy(str(policy_file))

    obs = Observation(
        category="COMPLIANCE",
        signal="FORBIDDEN_LICENSE",
        confidence=1.0,
        message="GPL is forbidden",
        severity=Severity.HIGH,
        evidence={"license": "GPL-3.0"},
        rule_id="L-SCAN"
    )

    risks = evaluate_compliance_risks([obs], [], [])

    assert len(risks) == 1

