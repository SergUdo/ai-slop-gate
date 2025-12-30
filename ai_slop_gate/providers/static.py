from typing import List
from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.providers.base import Provider


class StaticProvider(Provider):
    """
    Static provider returns predefined observations.
    Used for testing, CI, and contract validation.
    """

    def __init__(self, observations: List[Observation]):
        self._observations = observations

    def collect(self) -> List[Observation]:
        return list(self._observations)
