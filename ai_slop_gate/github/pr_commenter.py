import os
import requests

from ai_slop_gate.domain.decision import Decision


def _get_pr_number() -> str | None:
    """
    Extract PR number from GITHUB_REF.
    Expected formats:
      - refs/pull/<number>/merge
      - refs/pull/<number>/head
    """
    ref = os.getenv("GITHUB_REF", "")
    parts = ref.split("/")

    if len(parts) >= 4 and parts[0] == "refs" and parts[1] == "pull":
        return parts[2]

    return None


def publish_pr_comment(decision: Decision) -> None:
    token = os.getenv("AI_SLOP_GATE_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = _get_pr_number()

    # Not running in PR context or missing credentials
    if not token or not repo or not pr_number:
        return

    mode = (
        decision.mode.value.upper()
        if hasattr(decision.mode, "value")
        else str(decision.mode).upper()
    )

    body = f"## 🤖 AI Slop Gate — **{mode}**\n\n"

    if decision.reasons:
        body += "### Reasons\n"
        for reason in decision.reasons:
            body += f"- {reason}\n"

    if decision.annotations:
        body += "\n### Findings\n"
        for a in decision.annotations:
            body += f"- `{a.file}:{a.line}` — {a.message}\n"

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"body": body},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[ai-slop-gate] Failed to post PR comment: {exc}")
