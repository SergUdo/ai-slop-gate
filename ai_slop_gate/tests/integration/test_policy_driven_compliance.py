import pytest
from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.compliance.observation import ComplianceObservation

def test_forbidden_license_emits_observation(tmp_path):
    """
    Policy engine should produce an observation for forbidden license.
    """
    policy_file = tmp_path / "policy.yml"
    policy_file.write_text("""
version: "v1"
project_name: "ai_slop_gate"
compliance:
  enabled: true
  profiles: [eu]
  license:
    forbid: [GPL-3.0]
    allow: [MIT]
rules:
  - id: forbid-gpl
    when:
      source: compliance
      license: GPL-3.0
    then:
      decision: block
      reason: "GPL is forbidden by EU compliance"
""")

    policy_config, rules = load_policy(str(policy_file))

    obs = ComplianceObservation(license="GPL-3.0", severity="high", message="GPL is forbidden")
    assert obs.license == "GPL-3.0"
    assert obs.severity == "high"
