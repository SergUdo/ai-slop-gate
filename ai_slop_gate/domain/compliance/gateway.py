from typing import List
from pathlib import Path

from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.compliance.config import ComplianceConfig

class ComplianceGateway:
    def __init__(self, config: ComplianceConfig):
        self.config = config

    def analyze(self, artifacts_path: str) -> List[Observation]:
        if not self.config.enabled:
            return []

        observations: List[Observation] = []
        artifacts_path = Path(artifacts_path)

        req = artifacts_path / "requirements.txt"
        if not req.exists():
            return observations

        for line_no, line in enumerate(req.read_text().splitlines(), 1):
            for lic in self.config.forbid_licenses or []:
                if lic in line:
                    observations.append(
                        Observation(
                            category="COMPLIANCE",
                            signal="FORBIDDEN_LICENSE",
                            confidence=1.0,
                            message=f"Forbidden license {lic}",
                            evidence={"file": "requirements.txt", "line": line_no},
                        )
                    )

        return observations
