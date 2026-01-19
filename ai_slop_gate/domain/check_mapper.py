from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.checks import (
    CheckReport,
    CheckStatus,
    CheckAnnotation,
)


def decision_to_check(decision: Decision) -> CheckReport:
    if decision.mode == DecisionMode.BLOCKING:
        status = CheckStatus.FAIL
        prefix = "🚨 Blocking"
    elif decision.reasons:
        status = CheckStatus.ADVISORY
        prefix = "⚠️ Advisory"
    else:
        status = CheckStatus.PASS
        prefix = "✅ Clean"

    summary = (
        f"{prefix}: {len(decision.reasons)} issue(s) detected.\n\n"
        + "\n".join(f"- {r}" for r in decision.reasons)
        if decision.reasons
        else "No compliance or quality issues detected."
    )

    annotations = None
    if decision.annotations:
        annotations = [
            CheckAnnotation(
                file=a.file,
                line=a.line,
                message=a.message,
                level="failure" if a.level == "error" else "warning",
            )
            for a in decision.annotations
        ]

    return CheckReport(
        title="AI Slop Gate Analysis",
        summary=summary,
        status=status,
        annotations=annotations,
    )
