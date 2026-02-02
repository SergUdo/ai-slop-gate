import pytest

from ai_slop_gate.reporters.formatter import format_pr_comment, MARKER
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.observation import Observation, Severity


def test_format_pr_comment_basic():
    decision = Decision(mode=DecisionMode.BLOCKING, reasons=["reason-1"])
    obs = [
        Observation(category="security", signal="s1", confidence=0.9, message="Found issue", severity=Severity.HIGH),
    ]

    out = format_pr_comment(decision, obs)
    assert MARKER in out
    assert "BLOCKING" in out
    assert "Found issue" in out
