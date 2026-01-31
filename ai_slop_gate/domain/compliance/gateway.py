from pathlib import Path
from typing import List

from ai_slop_gate.domain.observation import Observation
from .detector import ComplianceDetector
from .profiles import ComplianceProfile


class ComplianceGateway:
    """
    Executes deterministic compliance checks based on resolved ComplianceProfile.
    """

    def __init__(self, config: ComplianceProfile | None):
        self.config = config

    def analyze(self, artifacts_path: str) -> List[Observation]:
        if not self.config:
            return []

        observations: List[Observation] = []

        # License audit
        if self.config.forbid_licenses:
            detector = ComplianceDetector(self.config.forbid_licenses)

            licenses = self._load_license_artifacts(artifacts_path)

            observations.extend(detector.detect(licenses))

        return observations

    def _load_license_artifacts(self, artifacts_path: str):
        """
        Temporary adapter.
        Expected format: List[(file, license)]
        """
        return []
