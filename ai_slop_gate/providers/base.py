# ai_slop_gate/providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from ai_slop_gate.domain.observation import Observation


@dataclass(frozen=True)
class ProviderObservation:
    provider: str
    model: str
    observations: List[Observation]
    raw_text: str


class Provider(ABC):
    """
    Stage 2+ contract.
    Providers are sensors.
    """

    @abstractmethod
    def collect(self) -> ProviderObservation:
        raise NotImplementedError
    
class BaseProvider:
    name: str
    kind: str  # scm | infra | llm

    def analyze(self, input_data):
        raise NotImplementedError

    def cache_key(self, input_data):
        return None

    def rate_limit_key(self):
        return self.name

