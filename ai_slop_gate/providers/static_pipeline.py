from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.providers.static import StaticProvider
from ai_slop_gate.providers.static_js import StaticJSProvider
from ai_slop_gate.providers.eslint import ESLintProvider
from ai_slop_gate.providers.static_ts_js import StaticTSJSProvider
from ai_slop_gate.providers.static_python import StaticPythonProvider
from ai_slop_gate.providers.static_docker import StaticDockerProvider

class StaticPipelineProvider(BaseProvider):
    def __init__(self, model: str = "static-pipeline-v1"):
        self.name = "static-pipeline"
        self.kind = "scm"
        self.model = model

    def analyze(self, input_data: str = "") -> ProviderObservation:
        observations: List = []

        providers = [
            StaticProvider(),
            StaticJSProvider(),
            ESLintProvider(),
            StaticTSJSProvider(),
            StaticPythonProvider(),
            StaticDockerProvider(),
        ]

        for provider in providers:
            try:
                if hasattr(provider, 'name'):
                    provider_name = provider.name
                else:
                    provider_name = provider.__class__.__name__

                if hasattr(provider, 'analyze'):
                    result = provider.analyze(input_data)
                else:
                    result = provider.collect()

                observations.extend(result.observations)
            except Exception as e:
                print(f"Error running {provider_name}: {e}")

        return ProviderObservation(
            provider=self.name,
            model=self.model,
            observations=observations,
            raw_text="",
        )

    def collect(self) -> ProviderObservation:
        return self.analyze()
