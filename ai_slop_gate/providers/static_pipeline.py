import logging
from collections import defaultdict
from typing import List
from dataclasses import replace
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation

# Імпорт під-провайдерів
from .static import StaticProvider
from .eslint import ESLintProvider
from .static_python import StaticPythonProvider
from .static_ts_js import StaticTSJSProvider
from .static_docker import StaticDockerProvider
from .supply_chain import SupplyChainProvider

logger = logging.getLogger(__name__)

class StaticPipelineProvider(BaseProvider):
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
            SupplyChainProvider()
        ]

    def collect(self, base_path: str = ".") -> ProviderObservation:
        all_obs = []
        for provider in self.pipeline:
            try:
                res = provider.collect(base_path=base_path)
                if res and res.observations:
                    all_obs.extend(res.observations)
            except Exception as e:
                logger.error(f"Failed to run provider {provider.name}: {e}")

        return self._smart_aggregate(all_obs)

    def _smart_aggregate(self, observations: List) -> ProviderObservation:
        # 1. Фільтрація сміття (venv, ai_slop_gate і т.д.)
        BLACKLIST = {".venv", "venv", "node_modules", "ai_slop_gate", "htmlcov"}
        clean_list = []
        
        for obs in observations:
            # Дістаємо файл з будь-якого доступного поля
            f = "unknown"
            if hasattr(obs, 'location') and obs.location:
                f = getattr(obs.location, 'file', "unknown")
            elif isinstance(obs.evidence, dict):
                f = obs.evidence.get("file", "unknown")
            
            # Перевірка: чи є в шляху файлу заборонена папка
            is_bad = False
            for part in f.replace("\\", "/").split("/"):
                if part in BLACKLIST:
                    is_bad = True
                    break
            
            if not is_bad:
                clean_list.append(obs)

        if not clean_list:
            return ProviderObservation(self.name, self.model, [], "No issues found")

        # 2. Групування та схлопування
        grouped = defaultdict(list)
        for obs in clean_list:
            f_key = obs.location.file if (hasattr(obs, 'location') and obs.location) else "unknown"
            grouped[(obs.signal, f_key)].append(obs)

        final_results = []
        for (sig, f_path), items in grouped.items():
            if len(items) > 5:
                final_results.extend(items[:3])
                summary = replace(items[0], message=f"Found {len(items)} instances of [{sig}] in this file.")
                if hasattr(summary, 'location') and summary.location:
                    summary = replace(summary, location=replace(summary.location, line=None))
                final_results.append(summary)
            else:
                final_results.extend(items)

        return ProviderObservation(self.name, self.model, final_results, "Done")

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        return self.collect()