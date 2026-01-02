import json
import subprocess
from pathlib import Path
from typing import List

from ai_slop_gate.providers.base import Provider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation


class ESLintProvider(Provider):
    name = "eslint"

    def collect(self) -> ProviderObservation:
        observations = self.run(Path.cwd())
        return ProviderObservation(
            provider=self.name,
            model="eslint-v1",
            observations=observations,
            raw_text="",
        )

    def run(self, repo_path: Path) -> List:
        observations = []

        try:
            result = subprocess.run(
                ["npx", "eslint", ".", "--format", "json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return observations

        if not result.stdout.strip():
            return observations

        reports = json.loads(result.stdout)

        for file_report in reports:
            file_path = file_report.get("filePath")
            for msg in file_report.get("messages", []):
                observations.append(
                    make_observation(
                        provider="eslint",
                        category=self._map_category(msg.get("ruleId")),
                        signal="eslint_violation",
                        confidence=0.9 if msg.get("severity") == 2 else 0.6,
                        message=f"{msg.get('message')} (eslint: {msg.get('ruleId')})",
                        evidence={
                            "file": file_path,
                            "line": msg.get("line"),
                            "tool": "eslint",
                        },
                        rule=msg.get("ruleId"),
                    )
                )

        return observations

    def _map_category(self, rule_id: str | None) -> str:
        if not rule_id:
            return "code_quality"
        if "no-secrets" in rule_id:
            return "security"
        if rule_id.startswith("security/"):
            return "security"
        if rule_id == "no-console":
            return "dev_in_prod"
        if rule_id == "no-undef":
            return "missing_required"
        return "code_quality"
