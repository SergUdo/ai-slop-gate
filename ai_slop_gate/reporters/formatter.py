from collections import defaultdict
from typing import List
from ai_slop_gate.domain.decision import Decision
from ai_slop_gate.domain.observation import Observation

MARKER = "<!-- AI_SLOP_GATE_REPORT -->"


def format_pr_comment(
    decision: Decision,
    observations: List[Observation],
) -> str:
    grouped = defaultdict(list)
    for obs in observations:
        grouped[obs.category].append(obs)

    lines: list[str] = []
    lines.append(MARKER)

    if decision.mode.value == "blocking":
        lines.append("## 🚨 AI Slop Gate — BLOCKING")
    elif decision.mode.value == "advisory":
        lines.append("## ⚠️ AI Slop Gate — Advisory")
    else:
        lines.append("## ✅ AI Slop Gate — Pass")

    lines.append("")

    for reason in decision.reasons:
        lines.append(f"- **{reason}**")

    lines.append("\n---\n")

    for category, items in grouped.items():
        lines.append(f"### `{category}`")
        for obs in items:
            location = ""
            if obs.location:
                location = f" ({obs.location.file}:{obs.location.line})"
            lines.append(
                f"- {obs.message} "
                f"[{obs.severity.value}, {obs.confidence:.2f}]{location}"
            )
        lines.append("")

    return "\n".join(lines)
