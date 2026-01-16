from ai_slop_gate.cli.utils import load_policy_rules

def test_load_policy_rules(tmp_path):
    policy = tmp_path / "policy.yml"
    policy.write_text("""
rules:
  - id: test
    when:
      category: CODE_QUALITY
      signal: TODO
    then:
      action: advisory
      message: Remove TODO
""")

    rules = load_policy_rules(str(policy))
    assert len(rules) == 1
    assert rules[0].id == "test"
