from dataclasses import dataclass
from typing import List
from ai_slop_gate.domain.observation import Observation

@dataclass(frozen=True)
class ProviderObservation:
    """
    Stage 2.2 contract.
    Providers are sensors.
    They emit observations, never decisions.
    """
    provider: str           # e.g. "gemini", "local-llama"
    model: str              # model identifier
    observations: List[Observation]
    raw_text: str           # raw LLM output (for debugging / audit)
