import ast
from pathlib import Path
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

class StaticPythonProvider(BaseProvider):
    # List of variable names that are considered safe and should not trigger secret detection
    SAFE_TOKEN_NAMES = {
        "page_token", "next_page_token", "token_name", "token_re", 
        "token_number", "token_count", "tokens_start", "token_type",
        "access_token_refresh_threshold", "is_page_token"
    }

    def __init__(self, model: str = "py-ast-slop-v1"):
        self.name = "static-python"
        self.kind = "scm"
        self.model = model

    def analyze(self, input_data: str = "") -> ProviderObservation:
        observations = []

        if not input_data:
            files = list(Path(".").rglob("*.py"))
            for file_path in files:
                # Ignore common virtual environment and cache directories
                if any(ignore in str(file_path) for ignore in ["node_modules", ".venv", "__pycache__", "venv", "env"]):
                    continue
                try:
                    code = file_path.read_text(errors="ignore")
                    observations.extend(self._analyze_code(code, str(file_path)))
                except Exception:
                    continue
        else:
            observations.extend(self._analyze_code(input_data, "inline_content"))

        return ProviderObservation(
            provider=self.name, 
            model=self.model, 
            observations=observations, 
            raw_text=f"Analyzed Python code. Found {len(observations)} issues."
        )

    def _analyze_code(self, code: str, filename: str) -> List:
        obs = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            obs.append(make_observation(
                provider=self.name,
                category="quality",
                signal="syntax_error",
                confidence=1.0,
                severity="high",
                message=f"Syntax error: {e}",
                evidence={"file": filename}
            ))
            return obs

        for node in ast.walk(tree):
            # 1. Dangerous function usage
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in ["eval", "exec", "system"]:
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="dangerous_function",
                        confidence=1.0,
                        severity="critical",
                        message=f"Dangerous function '{func_name}' detected. Risk of arbitrary code execution.",
                        evidence={"file": filename, "line": getattr(node, 'lineno', 0)}
                    ))

            # 2. Mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict)):
                        obs.append(make_observation(
                            provider=self.name,
                            category="quality",
                            signal="mutable_default_argument",
                            confidence=0.9,
                            severity="medium",
                            message=f"Mutable default argument in function '{node.name}'. Can lead to shared state bugs.",
                            evidence={"file": filename, "line": getattr(node, 'lineno', 0)}
                        ))

            # 3. Potential hardcoded secrets
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(k in name_lower for k in ["api_key", "password", "secret", "token"]):
                            # Filter out safe token names
                            if not any(safe in name_lower for safe in self.SAFE_TOKEN_NAMES):
                                obs.append(make_observation(
                                    provider=self.name,
                                    category="security",
                                    signal="hardcoded_secret",
                                    confidence=0.8,
                                    severity="high",
                                    message=f"Potential secret found in variable '{target.id}'.",
                                    evidence={"file": filename, "line": getattr(node, 'lineno', 0)}
                                ))

            # 4 SQL injection risk
            if isinstance(node, ast.JoinedStr):
                dump = ast.dump(node).upper()
                if any(kw in dump for kw in ["SELECT ", "INSERT ", "UPDATE ", "DELETE "]):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="sql_injection_risk",
                        confidence=0.7,
                        severity="high",
                        message="F-string detected in SQL-like string. Use parameterized queries instead.",
                        evidence={"file": filename, "line": getattr(node, 'lineno', 0)}
                    ))

        return obs

    def collect(self) -> ProviderObservation:
        return self.analyze()