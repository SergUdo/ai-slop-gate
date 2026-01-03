from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.checks import (
    CheckReport,
    CheckStatus,
    CheckAnnotation,
)

def decision_to_check(decision: Decision) -> CheckReport:
    if decision.mode == DecisionMode.BLOCKING:
        status = CheckStatus.FAIL
        summary_prefix = "🚨 Blocking"
    elif decision.reasons:
        status = CheckStatus.ADVISORY
        summary_prefix = "⚠️ Advisory"
    else:
        status = CheckStatus.PASS
        summary_prefix = "✅ Clean"

    summary = (
        f"{summary_prefix}: {len(decision.reasons)} issue(s) detected"
        if decision.reasons
        else "No issues detected"
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
        title="AI Slop Gate",
        summary=summary,
        status=status,
        annotations=annotations,
    )
