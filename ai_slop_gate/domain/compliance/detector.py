from typing import List
from ai_slop_gate.domain.observation import Observation

class ComplianceDetector:
    def __init__(self, forbid_licenses: list[str]):
        self.forbid_licenses = set(forbid_licenses or [])

    def detect(self, licenses: list[tuple[str, str]]) -> List[Observation]:
        observations = []

        for file, license_name in licenses:
            if license_name in self.forbid_licenses:
                observations.append(
                    Observation(
                        category="COMPLIANCE",
                        signal="FORBIDDEN_LICENSE",
                        confidence=1.0,
                        message=f"Forbidden license detected: {license_name}",
                        evidence={
                            "file": file,
                            "license": license_name,
                        },
                    )
                )

        return observations
