import pytest
from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.policy_engine import PolicyRule

def test_load_policy_rules(tmp_path):
    policy_file = tmp_path / "policy.yml"
    policy_file.write_text("""
version: "v1"
project_name: "ai_slop_gate"
compliance:
  enabled: true
  forbid_licenses:
    - GPL-3.0
rules:
  - id: forbid-gpl
    when:
      category: COMPLIANCE
      signal: FORBIDDEN_LICENSE
      min_confidence: 0.0
    then:
      action: blocking
      message: "GPL forbidden by EU compliance"
""")

    config, rules = load_policy(str(policy_file))

    assert config.compliance.enabled is True
    assert "GPL-3.0" in config.compliance.forbid_licenses

    assert isinstance(rules[0], PolicyRule)
    assert rules[0].when["category"] == "COMPLIANCE"
    assert rules[0].when["signal"] == "FORBIDDEN_LICENSE"
    assert rules[0].then["action"] == "blocking"
    assert rules[0].then["message"] == "GPL forbidden by EU compliance"
