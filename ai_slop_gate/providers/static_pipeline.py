from typing import List

from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.providers.base import Provider, ProviderObservation
from ai_slop_gate.providers.static import StaticProvider
from ai_slop_gate.providers.static_js import StaticJSProvider
from ai_slop_gate.providers.eslint import ESLintProvider


class StaticPipelineProvider(Provider):
    """
    Aggregates all deterministic static analyzers.
    """

    def collect(self) -> ProviderObservation:
        observations: List[Observation] = []

        providers = [
            StaticProvider(),      # config / TODO / FIXME
            StaticJSProvider(),    # JS security analysis
            ESLintProvider(),      # ESLint rulesets (secrets, prod safety, base)
        ]

        for provider in providers:
            result = provider.collect()
            observations.extend(result.observations)

        return ProviderObservation(
            provider="static-pipeline",
            model="static-v1",
            observations=observations,
            raw_text="",
        )
