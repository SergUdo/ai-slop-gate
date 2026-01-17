from ai_slop_gate.domain.compliance.observation import ComplianceObservation
from ai_slop_gate.domain.config import ComplianceConfig

class ComplianceGateway:
    def __init__(self, config: ComplianceConfig):
        self.config = config

    def analyze(self, artifacts_path: str):
        if not self.config or not self.config.enabled:
            return []

        # Stage 0 stub
        detected_licenses = ["GPL-3.0"]

        observations = []

        for lic in detected_licenses:
            if lic in (self.config.forbid_licenses or []):
                observations.append(
                    ComplianceObservation(
                        license=lic,
                        severity="high",
                        message=f"License {lic} is forbidden by compliance policy",
                    )
                )

        return observations
