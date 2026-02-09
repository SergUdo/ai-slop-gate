import json
import subprocess
import os
import logging
from pathlib import Path
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class ESLintProvider(BaseProvider):
    def __init__(self, model: str = "eslint-v8"):
        self.name = "eslint"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        target = Path(base_path).absolute()
        
        try:
            # Run ESLint with JSON output. We use npx to ensure we run the local version if available. The "htmlcov" formatter is used to avoid color codes in the output, and we ignore the .venv directory.
            result = subprocess.run(
                ["npx", "eslint", ".", "--format", "json", "htmlcov", ".venv"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False
            )
            
            if not result.stdout.strip():
                return ProviderObservation(self.name, self.model, [], "No eslint output")

            reports = json.loads(result.stdout)
            for file_report in reports:
                abs_path = file_report.get("filePath")
                # Get the relative path for better readability in observations, but fall back to absolute if it fails (e.g., if the file is outside the target directory).
                try:
                    rel_path = os.path.relpath(abs_path, target)
                except ValueError:
                    rel_path = abs_path

                for msg in file_report.get("messages", []):
                    rule_id = msg.get("ruleId", "unknown")
                    observations.append(make_observation(
                        provider=self.name,
                        category="quality",
                        signal=rule_id,
                        confidence=1.0,
                        message=msg.get("message"),
                        severity="high" if msg.get("severity") == 2 else "low",
                        evidence={
                            "file": rel_path, 
                            "line": msg.get("line"),
                            "tool": "eslint"
                        }
                    ))
        except Exception as e:
            logger.error(f"ESLint execution failed: {e}")
            
        return ProviderObservation(self.name, self.model, observations, "ESLint scan complete")

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "Snippet analysis via ESLint is not implemented")