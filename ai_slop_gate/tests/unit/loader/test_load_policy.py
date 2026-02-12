from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.contracts import PolicyRule
from ai_slop_gate.domain.config import PolicyConfig
from pathlib import Path


def test_load_policy_empty(tmp_path: Path):
    p = tmp_path / "policy.yml"
    p.write_text("rules: []")

    cfg, rules = load_policy(str(p))

    assert isinstance(cfg, PolicyConfig)
    assert rules == []


def test_load_policy_rules_parsed(tmp_path: Path):
    p = tmp_path / "policy.yml"
    p.write_text("""
rules:
  - id: r1
    when:
      category: TEST
      signal: X
      min_confidence: 0.0
    then:
      action: advisory
      message: "Hello"
""")

    cfg, rules = load_policy(str(p))

    assert len(rules) == 1
    assert isinstance(rules[0], PolicyRule)

    # Stage 0.7: fields live inside when/then
    assert rules[0].when["category"] == "TEST"
    assert rules[0].when["signal"] == "X"
    assert rules[0].when["min_confidence"] == 0.0

    assert rules[0].then["action"] == "advisory"
    assert rules[0].then["message"] == "Hello"
