from typing import List, Optional

from ai_slop_gate.domain.compliance.config import ComplianceConfig
from ai_slop_gate.domain.compliance.observation import ComplianceObservation
from pathlib import Path


class ComplianceGateway:
    """
    Deterministic compliance gateway.
    """

    def __init__(self, config: Optional[ComplianceConfig] = None):
        self.config = config or ComplianceConfig()

    def analyze(self, artifacts_path: str) -> List[ComplianceObservation]:
        if not self.config.enabled:
            return []

        observations = []
        artifacts_path = Path(artifacts_path)

        req_path = artifacts_path / "requirements.txt"
        if req_path.exists():
            with open(req_path, "r") as f:
                for line_number, line in enumerate(f, 1):
                    if "# GPL-3.0" in line:
                        observations.append(
                            ComplianceObservation(
                                license="GPL-3.0",
                                severity="high",
                                message="License GPL-3.0 is forbidden by compliance policy",
                                evidence={"file": "requirements.txt", "line": line_number},
                            )
                        )

        return observations

