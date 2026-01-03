# python -m scripts.test_pr_formatter

from ai_slop_gate.domain.observation import Observation, Severity, Location
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.reporters.formatter import format_pr_comment

observations = [
    Observation(
        rule_id="R001",
        category="CODE_QUALITY",
        signal="todo",
        message="Remove TODO before merge",
        severity=Severity.MEDIUM,
        confidence=0.91,
        location=Location(file="app/main.py", line=42),
    )
]

decision = Decision(
    mode=DecisionMode.ADVISORY,
    reasons=["Remove TODOs before merge"],
)

print(format_pr_comment(decision, observations))
