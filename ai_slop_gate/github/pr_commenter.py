import os
import requests
from ai_slop_gate.domain.decision import Decision

def _get_pr_number() -> str | None:
    ref = os.getenv("GITHUB_REF", "")
    if ref.startswith("refs/pull/"):
        return ref.split("/")[2]
    return None

def publish_pr_comment(decision: Decision) -> None:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = _get_pr_number()

    if not token or not repo or not pr_number:
        return  # Skip if not in a PR context

    body = f"## 🤖 AI Slop Gate — **{decision.mode.upper()}**\n\n"

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
        response = requests.post(url, headers=headers, json={"body": body})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to post comment: {e}")
