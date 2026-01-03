from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.checks import (
    CheckReport,
    CheckStatus,
    CheckAnnotation,
)

def decision_to_check(decision: Decision) -> CheckReport:
    """
    Maps a Policy Decision to a GitHub-compatible CheckReport with Suggestions support.
    """
    if decision.mode == DecisionMode.BLOCKING:
        status = CheckStatus.FAIL
        summary_prefix = "🚨 Blocking"
    elif decision.reasons:
        status = CheckStatus.ADVISORY
        summary_prefix = "⚠️ Advisory"
    else:
        status = CheckStatus.PASS
        summary_prefix = "✅ Clean"

    summary_text = (
        f"{summary_prefix}: {len(decision.reasons)} issue(s) detected.\n\n"
        + "\n".join([f"- {reason}" for reason in decision.reasons])
        if decision.reasons
        else "No AI slop or quality issues detected. Code is clean."
    )

    annotations = []
    decision_annotations = getattr(decision, "annotations", [])
    
    for a in decision_annotations:
        # Building the message with a GitHub Suggestion block if suggested_code exists
        msg = a.message
        
        # Check if the annotation has a 'suggested_code' attribute
        suggested_code = getattr(a, "suggested_code", None)
        if suggested_code:
            msg += f"\n\n```suggestion\n{suggested_code}\n```"

        annotations.append(
            CheckAnnotation(
                file=a.file,
                line=a.line,
                message=msg,
                level="failure" if getattr(a, "level", "warning") == "error" else "warning",
            )
        )

    return CheckReport(
        title="AI Slop Gate Analysis",
        summary=summary_text,
        status=status,
        annotations=annotations if annotations else None,
    )
