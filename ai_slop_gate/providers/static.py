from typing import List
from ai_slop_gate.providers.base import Provider, ProviderObservation
from ai_slop_gate.domain.observation import Observation

class StaticProvider:
    def __init__(self, findings: list[str] | None = None):
        self.findings = findings or []

    def observe(self) -> ProviderObservation:
        observations = [
            Observation(
                category="quality",
                signal="negative", 
                confidence=0.9,
                message=msg,
                evidence={}
            )
            for msg in self.findings
        ]

        return ProviderObservation(
            provider="static",
            model="static",
            observations=observations,
            raw_text=""
        )

    def collect(self) -> ProviderObservation:
        return ProviderObservation(
            provider="static",
            model="static-fixture",
            raw_text="static test data",
            observations=[
                Observation(
                    category="quality",
                    signal="negative",
                    confidence=0.9,
                    message="TODO found",
                    evidence={"file": "example.js", "line": 1}
                )
            ]
        )
