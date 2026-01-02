from collections import defaultdict
from typing import List
import requests

from ai_slop_gate.domain.decision import Decision
from ai_slop_gate.domain.observation import Observation


class GitHubPRReporter:
    """
    Stage 2.4.1 — PR Comment Reporter

    Responsibilities:
    - format Decision + Observations into markdown
    - deduplicate observations
    - post a single PR comment

    Forbidden:
    - no decisions
    - no policy logic
    - no provider logic
    """

    def __init__(self, token: str, repo: str, pr_id: int):
        self.token = token
        self.repo = repo
        self.pr_id = pr_id

    def report(self, decision: Decision, observations: List[Observation]) -> None:
        body = self._format_comment(decision, observations)
        self._post_comment(body)

    # ---------- formatting ----------

    def _format_comment(
        self, decision: Decision, observations: List[Observation]
    ) -> str:
        icon = "🚫" if decision.mode.value == "blocking" else "⚠️"

        lines = [
            f"## {icon} AI Slop Gate",
            "",
            f"**Decision:** `{decision.mode.value.upper()}`",
            "",
        ]

        deduped = self._deduplicate(observations)
        grouped = self._group_by_category(deduped)

        for category, items in grouped.items():
            lines.append(f"### {category}")
            for obs in items:
                lines.append(
                    f"- **{obs.signal}** ({obs.confidence:.2f}): {obs.message}"
                )
            lines.append("")

        return "\n".join(lines)

    # ---------- helpers ----------

    def _deduplicate(self, observations: List[Observation]) -> List[Observation]:
        seen = set()
        result = []

        for obs in observations:
            key = (obs.category, obs.signal, obs.message)
            if key not in seen:
                seen.add(key)
                result.append(obs)

        return result

    def _group_by_category(
        self, observations: List[Observation]
    ) -> dict[str, list[Observation]]:
        grouped = defaultdict(list)
        for obs in observations:
            grouped[obs.category].append(obs)
        return grouped

    # ---------- transport ----------

    def _post_comment(self, body: str) -> None:
        url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_id}/comments"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
            },
            json={"body": body},
            timeout=10,
        )

        response.raise_for_status()
