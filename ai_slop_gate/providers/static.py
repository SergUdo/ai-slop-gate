from typing import List, Set
from pathlib import Path
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

class StaticProvider(BaseProvider):
    IGNORE_DIRS: Set[str] = {
        ".git", ".venv", "venv", "node_modules", "__pycache__",
        ".pytest_cache", ".tmp-cache", ".ai-slop-cache",
        "dist", "build", ".mypy_cache", ".vscode", ".idea"
    }

    IGNORE_FILE_EXTENSIONS: Set[str] = {
        ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".map", ".min.js"
    }

    def __init__(self, model: str = "static-v1", findings: List[str] | None = None):
        self.name = "static"
        self.kind = "scm"
        self.model = model
        self.findings = findings or []

    def analyze(self, input_data: str = "") -> ProviderObservation:
        observations = []

        if not input_data:
            for path in Path(".").rglob("*"):
                if self._should_ignore(path):
                    continue
                try:
                    if path.is_file():
                        text = path.read_text(errors="ignore")
                        observations.extend(self._scan_file(text, path))
                except Exception as e:
                    print(f"Error reading file {path}: {e}")

        return ProviderObservation(
            provider=self.name,
            model=self.model,
            observations=observations,
            raw_text="Static analysis complete.",
        )

    def _should_ignore(self, path: Path) -> bool:
        if path.is_dir():
            return any(ignore_dir in str(path) for ignore_dir in self.IGNORE_DIRS)

        if path.suffix in self.IGNORE_FILE_EXTENSIONS:
            return True

        return any(ignore_dir in path.parts for ignore_dir in self.IGNORE_DIRS)

    def _scan_file(self, text: str, path: Path) -> List:
        observations = []
        for i, line in enumerate(text.splitlines(), start=1):
            if "TODO" in line:
                observations.append(
                    make_observation(
                        provider=self.name,
                        category="quality",
                        signal="todo_found",
                        confidence=0.9,
                        message=f"TODO found in {path}:{i}",
                        severity="low",
                        evidence={"file": str(path), "line": i},
                    )
                )
            if "FIXME" in line:
                observations.append(
                    make_observation(
                        provider=self.name,
                        category="quality",
                        signal="fixme_found",
                        confidence=0.95,
                        message=f"FIXME found in {path}:{i}",
                        severity="high",
                        evidence={"file": str(path), "line": i},
                    )
                )
        return observations

    def collect(self) -> ProviderObservation:
        return self.analyze()
