from ai_slop_gate.domain.compliance.observation import ComplianceObservation
from ai_slop_gate.domain.compliance.profile_resolver import ComplianceProfileResolver
from ai_slop_gate.domain.compliance.effective_policy import EffectiveCompliancePolicy

class ComplianceGateway:
    def __init__(self, config):
        self.config = config
        self.resolver = ComplianceProfileResolver()

    def analyze(self, artifacts_path: str):
        if not self.config or not self.config.enabled:
            return []

        profiles = self.resolver.resolve(self.config.profiles or [])
        effective_policy = EffectiveCompliancePolicy(profiles)

        # stub detector
        detected_licenses = ["GPL-3.0"]

        observations = []
        for lic in detected_licenses:
            if lic in effective_policy.forbid_licenses:
                observations.append(
                    ComplianceObservation(
                        license=lic,
                        severity="high",
                        message=f"License {lic} forbidden by compliance profile",
                    )
                )

        return observations
