from abc import ABC, abstractmethod
from typing import List
from ai_slop_gate.domain.observation import Observation


class Provider(ABC):
    """
    Provider extracts raw signals from a source and converts them into
    domain-level Observations.

    Providers must not:
    - apply policy
    - make decisions
    - know about enforcement mode
    """

    @abstractmethod
    def collect(self) -> List[Observation]:
        """Return a list of Observations."""
        raise NotImplementedError
