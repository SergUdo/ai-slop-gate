from collections import defaultdict
from typing import List
import requests

from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.decision import Decision


class GitHubPRReporter:
    def __init__(self, repo: str, pr_number: int, token: str):
        self.repo = repo
        self.pr_number = pr_number
        self.token = token

    def report(self, decision: Decision, observations: List[Observation]) -> None:
        body = self._format_comment(decision, observations)
        self._post_comment(body)

    def _format_comment(
        self, decision: Decision, observations: List[Observation]
    ) -> str:
        deduped = self._deduplicate(observations)
        grouped = self._group_by_category(deduped)

        lines = []
        lines.append("## 🤖 AI Slop Gate Report\n")
        lines.append(f"**Decision:** `{decision.mode.value.upper()}`\n")

        for category, items in grouped.items():
            lines.append(f"### {category}")
            for obs in items:
                lines.append(
                    f"- **{obs.signal}** ({obs.confidence:.2f}): {obs.message}"
                )
            lines.append("")

        return "\n".join(lines)

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

    def _post_comment(self, body: str) -> None:
        url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

        response = requests.post(url, headers=headers, json={"body": body})
        response.raise_for_status()