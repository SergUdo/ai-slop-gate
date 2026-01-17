import pytest
from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.policy_engine import PolicyRule

def test_load_policy_rules(tmp_path):
    """
    Loading policy should parse rules and compliance config correctly.
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
      reason: "GPL forbidden by EU compliance"
""")

    config, rules = load_policy(str(policy_file))

    assert config.compliance.enabled is True
    assert "eu" in config.compliance.profiles
    assert "GPL-3.0" in config.compliance.forbid_licenses
    assert isinstance(rules[0], PolicyRule)
    assert rules[0].source == "compliance"
