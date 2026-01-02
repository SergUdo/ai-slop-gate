import json
import subprocess
from pathlib import Path
from typing import List

from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.providers.base import Provider


class ESLintProvider(Provider):
    name = "eslint"

    def run(self, repo_path: Path) -> List[Observation]:
        observations: List[Observation] = []

        eslint_config = repo_path / ".eslintrc.json"
        if not eslint_config.exists():
            return observations  # eslint optional

        try:
            result = subprocess.run(
                [
                    "npx",
                    "eslint",
                    ".",
                    "--format",
                    "json",
                ],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            # eslint / npx not installed — fail silently
            return observations

        if not result.stdout.strip():
            return observations

        try:
            reports = json.loads(result.stdout)
        except json.JSONDecodeError:
            return observations

        for file_report in reports:
            file_path = file_report.get("filePath", "")
            for msg in file_report.get("messages", []):
                observations.append(
                    self._message_to_observation(file_path, msg)
                )

        return observations

    def _message_to_observation(self, file_path: str, msg: dict) -> Observation:
        rule_id = msg.get("ruleId", "unknown")
        message = msg.get("message", "")
        line = msg.get("line")
        severity = msg.get("severity", 1)

        category = self._map_category(rule_id)
        confidence = 0.9 if severity == 2 else 0.6

        return Observation(
            category=category,
            signal="negative",
            confidence=confidence,
            message=f"{message} (eslint: {rule_id})",
            evidence={
                "file": file_path,
                "line": line,
                "tool": "eslint",
            },
        )

    def _map_category(self, rule_id: str) -> str:
        if "no-secrets" in rule_id:
            return "security"
        if rule_id.startswith("security/"):
            return "security"
        if rule_id in ("no-console",):
            return "dev_in_prod"
        if rule_id in ("no-undef",):
            return "missing_required"
        return "code_quality"
