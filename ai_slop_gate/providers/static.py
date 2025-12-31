from typing import List
from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation import Observation



class StaticProvider:
    def __init__(self, findings: list[str] | None = None):
        self.findings = findings or []

    def observe(self) -> ProviderObservation:
        observations = [
            Observation(
                kind="static",
                message=msg,
                severity="warning"
            )
            for msg in self.findings
        ]

        return ProviderObservation(
            provider="static",
            model="static",
            observations=observations,
            raw_text=""
        )
