import os
import logging
from pathlib import Path
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class StaticProvider(BaseProvider):
    # Папки, які ми НІКОЛИ не хочемо аналізувати
    EXCLUDE_DIRS = {".venv", "venv", "node_modules", "ai_slop_gate", "scripts", "htmlcov", ".git"}

    def __init__(self, model: str = "generic-static-v1"):
        self.name = "static"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        target_dir = Path(base_path).resolve()
        
        for path in target_dir.rglob("*"):
            # ПЕРЕВІРКА ШЛЯХУ: Якщо хоча б одна частина шляху в списку ігнорування - пропускаємо
            if any(part in self.EXCLUDE_DIRS for part in path.parts):
                continue
                
            if path.is_file() and path.suffix in [".js", ".ts", ".py", ".sh", ".env"]:
                rel_path = os.path.relpath(path, target_dir)
                try:
                    text = path.read_text(errors="ignore")
                    # Простий пошук TODO
                    for i, line in enumerate(text.splitlines(), start=1):
                        if "TODO" in line.upper():
                            observations.append(make_observation(
                                provider=self.name, category="quality", signal="todo_found",
                                confidence=0.9, message="Unresolved TODO found in code.",
                                severity="low", evidence={"file": rel_path, "line": i}
                            ))
                except Exception as e:
                    logger.error(f"Error reading {rel_path}: {e}")

        return ProviderObservation(self.name, self.model, observations, "Scan Complete")

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "")