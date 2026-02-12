import logging
from collections import defaultdict
from typing import List
from dataclasses import replace
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation

# import all static analysis providers
from ai_slop_gate.providers.static.static import StaticProvider
from ai_slop_gate.providers.static.eslint import ESLintProvider
from ai_slop_gate.providers.static.static_python import StaticPythonProvider
from ai_slop_gate.providers.static.static_ts_js import StaticTSJSProvider
from ai_slop_gate.providers.static.static_docker import StaticDockerProvider
from ai_slop_gate.providers.static.supply_chain import SupplyChainProvider
from .trivy import TrivyProvider
from .sbom import SBOMProvider

logger = logging.getLogger(__name__)


class StaticPipelineProvider(BaseProvider):
    """
    SteticPipelineProvider - the main provider for static analysis. It runs a series of static analysis tools and aggregates their results. The collect() method is the main entry point, which executes each provider in the pipeline and then smartly aggregates the observations, filtering out noise and grouping similar issues together.
    """

    EXCLUDE_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        ".slop",
        ".idea",
        ".pytest_cache",
        "site-packages",
        "ai_slop_gate", 
        "htmlcov",
    }

    def __init__(self, model: str = "static-pipeline-v1"):
        self.name = "static_pipeline"
        self.kind = "static"
        self.model = model
        self.pipeline = [
            StaticProvider(),
            ESLintProvider(),
            StaticPythonProvider(),
            StaticTSJSProvider(),
            StaticDockerProvider(),
            SupplyChainProvider(),
            TrivyProvider(),
            SBOMProvider(),
        ]

    # -------------------------------------------------------------------------
    # Main collect method → runs all providers and aggregates results
    # -------------------------------------------------------------------------
    def collect(self, base_path: str = ".") -> ProviderObservation:
        """
        Runs all providers in the pipeline and aggregates their results.
        """
        all_obs = []

        for provider in self.pipeline:
            try:
                res = provider.collect(base_path=base_path)
                if res and res.observations:
                    all_obs.extend(res.observations)
            except Exception as e:
                logger.exception(f"Failed to run provider {provider.name}")

        return self._smart_aggregate(all_obs)

    # -------------------------------------------------------------------------
    # Smart aggregation method → filters noise and groups similar issues
    # -------------------------------------------------------------------------
    def _smart_aggregate(self, observations: List) -> ProviderObservation:
        clean_list = []

        for obs in observations:
            f = "unknown"

            if hasattr(obs, "location") and obs.location:
                f = getattr(obs.location, "file", "unknown")
            elif isinstance(obs.evidence, dict):
                f = obs.evidence.get("file", "unknown")

            # Normalize path for consistent exclusion checks
            parts = f.replace("\\", "/").split("/")

            # Filter out noise based on file paths. This helps reduce false positives from dependencies, build artifacts, or our own code.
            if any(p in self.EXCLUDE_DIRS for p in parts):
                continue

            clean_list.append(obs)

        if not clean_list:
            return ProviderObservation(self.name, self.model, [], "No issues found")

        # Group similar issues together by signal and file. If there are many similar issues in the same file, we keep a few examples and then add a summary observation to indicate that this is a common pattern. This helps focus attention on unique issues while still acknowledging widespread problems.
        grouped = defaultdict(list)
        for obs in clean_list:
            f_key = obs.location.file if (hasattr(obs, "location") and obs.location) else "unknown"
            grouped[(obs.signal, f_key)].append(obs)

        final_results = []

        for (sig, f_path), items in grouped.items():
            if len(items) > 5:
                final_results.extend(items[:3])
                summary = replace(items[0], message=f"Found {len(items)} instances of [{sig}] in this file.")
                if hasattr(summary, "location") and summary.location:
                    summary = replace(summary, location=replace(summary.location, line=None))
                final_results.append(summary)
            else:
                final_results.extend(items)

        return ProviderObservation(self.name, self.model, final_results, "Done")

    # -------------------------------------------------------------------------
    # analyze() → runs the collect() method
    # -------------------------------------------------------------------------
    def analyze(self, code: str, input_file: str = "", base_path: str = ".") -> ProviderObservation:
        return self.collect(base_path=base_path)
