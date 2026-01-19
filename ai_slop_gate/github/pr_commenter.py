import requests
from ai_slop_gate.domain.decision import Decision


COMMENT_MARKER = "<!-- ai-slop-gate -->"


def build_comment_body(decision: Decision) -> str:
    body = f"""{COMMENT_MARKER}
## 🤖 AI Slop Gate

**Decision:** `{decision.mode.name}`

"""

    if decision.reasons:
        body += "### Reasons\n"
        for r in decision.reasons:
            body += f"- {r}\n"

    if decision.annotations:
        body += "\n### Findings\n"
        for a in decision.annotations:
            body += f"- `{a.file}:{a.line}` — {a.message}\n"

    return body.strip()


def publish_pr_comment(
    *,
    decision: Decision,
    repo: str,
    pr_id: int,
    token: str,
) -> None:
    body = build_comment_body(decision)

    url = f"https://api.github.com/repos/{repo}/issues/{pr_id}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.post(url, headers=headers, json={"body": body})
    response.raise_for_status()
