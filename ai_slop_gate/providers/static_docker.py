import os
import re
import logging
from pathlib import Path
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class StaticDockerProvider(BaseProvider):
    CHMOD_777_RE = re.compile(r"chmod\s+-R\s+777\s+/", re.IGNORECASE)

    def __init__(self, model: str = "docker-slop-v1"):
        self.name = "static-docker"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        target_dir = Path(base_path).absolute()
        
        docker_files = [p for p in target_dir.rglob("*") if p.is_file() and (p.name == "Dockerfile" or p.suffix == ".dockerfile")]

        for file_path in docker_files:
            rel_path = os.path.relpath(file_path, target_dir)
            try:
                text = file_path.read_text(errors="ignore")
                for i, line in enumerate(text.splitlines(), start=1):
                    if self.CHMOD_777_RE.search(line):
                        observations.append(make_observation(
                            provider=self.name, category="security", signal="extreme_privilege",
                            confidence=1.0, message="Recursive chmod 777 detected in Dockerfile.",
                            severity="critical", evidence={"file": rel_path, "line": i}
                        ))
            except Exception as e:
                logger.error(f"Error reading {rel_path}: {e}")

        return ProviderObservation(self.name, self.model, observations, "Docker Scan Complete")

    def analyze(self, code: str, input_file: str = "inline") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "")