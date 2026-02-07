import ast
import os
import logging
from pathlib import Path
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class StaticPythonProvider(BaseProvider):
    EXCLUDE_DIRS = {
        ".venv", "venv", "__pycache__", "node_modules", "dist",
        "build", "htmlcov", "site-packages", "ai_slop_gate"
    }

    def __init__(self, model: str = "py-ast-v1"):
        self.name = "static-python"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        base = os.path.abspath(base_path)

        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for f in files:
                if not f.endswith(".py"):
                    continue

                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base)

                try:
                    code = open(full_path, "r", errors="ignore").read()
                    observations.extend(self._analyze_code(code, rel_path))
                except Exception as e:
                    logger.error(f"Failed to read {rel_path}: {e}")

        return ProviderObservation(self.name, self.model, observations, "Python AST Scan Complete")

    def _analyze_code(self, code: str, filename: str) -> List:
        obs = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            obs.append(make_observation(
                provider=self.name, category="quality", signal="syntax_error",
                confidence=1.0, message=f"Syntax error: {str(e)}",
                severity="high", evidence={"file": filename, "line": e.lineno}
            ))
            return obs

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr

                if name in ["eval", "exec", "system"]:
                    obs.append(make_observation(
                        provider=self.name, category="security", signal="dangerous_function",
                        confidence=1.0, message=f"Dangerous function '{name}' detected.",
                        severity="high", evidence={"file": filename, "line": node.lineno}
                    ))

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and any(
                        k in target.id.lower() for k in ["api_key", "secret", "token", "password"]
                    ):
                        obs.append(make_observation(
                            provider=self.name, category="security", signal="hardcoded_secret",
                            confidence=0.8, message=f"Potential secret in variable '{target.id}'.",
                            severity="high", evidence={"file": filename, "line": node.lineno}
                        ))

        return obs

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, self._analyze_code(code, input_file), "")
