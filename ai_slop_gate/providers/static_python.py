import ast
from pathlib import Path
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

class StaticPythonProvider(BaseProvider):
    def __init__(self, model: str = "py-ast-slop-v1"):
        self.name = "static-python"
        self.kind = "scm"
        self.model = model

    def analyze(self, input_data: str = "") -> ProviderObservation:
        observations = []

        if not input_data:
            files = list(Path(".").rglob("*.py"))
            for file_path in files:
                if any(ignore in str(file_path) for ignore in ["node_modules", ".venv", "__pycache__"]):
                    continue
                code = file_path.read_text(errors="ignore")
                observations.extend(self._analyze_code(code, str(file_path)))
        else:
            observations.extend(self._analyze_code(input_data, "inline_content"))

        return ProviderObservation(self.name, self.model, observations, "Analyzed Python code.")

    def _analyze_code(self, code: str, filename: str) -> List:
        obs = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            obs.append(
                make_observation(
                    provider=self.name,
                    category="quality",
                    signal="syntax_error",
                    confidence=1.0,
                    message=str(e),
                    evidence={"file": filename},
                )
            )
            return obs

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in ["eval", "exec", "system"]:
                    obs.append(
                        make_observation(
                            provider=self.name,
                            category="security",
                            signal="dangerous_function",
                            confidence=1.0,
                            message=f"Dangerous function '{func_name}' detected. Risk of arbitrary code execution.",
                            evidence={"file": filename, "line": node.lineno},
                        )
                    )

            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict)):
                        obs.append(
                            make_observation(
                                provider=self.name,
                                category="quality",
                                signal="mutable_default_argument",
                                confidence=0.9,
                                message=f"Mutable default argument in function '{node.name}'. Can lead to shared state bugs.",
                                evidence={"file": filename, "line": node.lineno},
                            )
                        )

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(k in name_lower for k in ["api_key", "password", "secret", "token"]):
                            obs.append(
                                make_observation(
                                    provider=self.name,
                                    category="security",
                                    signal="hardcoded_secret",
                                    confidence=0.8,
                                    message=f"Potential secret found in variable '{target.id}'.",
                                    evidence={"file": filename, "line": node.lineno},
                                )
                            )

            if isinstance(node, ast.JoinedStr):
                if "SELECT" in ast.dump(node) or "INSERT" in ast.dump(node) or "UPDATE" in ast.dump(node) or "DELETE" in ast.dump(node):
                    obs.append(
                        make_observation(
                            provider=self.name,
                            category="security",
                            signal="sql_injection_risk",
                            confidence=0.7,
                            message="F-string detected in SQL-like string. Use parameterized queries instead.",
                            evidence={"file": filename, "line": node.lineno},
                        )
                    )

        return obs

    def collect(self) -> ProviderObservation:
        return self.analyze()
