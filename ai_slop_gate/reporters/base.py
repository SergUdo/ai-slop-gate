# ai_slop_gate/reporters/base.py
from abc import ABC, abstractmethod
from typing import List
from ai_slop_gate.domain.decision import Decision
from ai_slop_gate.domain.observation import Observation


class Reporter(ABC):
    @abstractmethod
    def report(
        self,
        decision: Decision,
        observations: List[Observation],
    ) -> None:
        """
        Report the decision and observations.

        Stage 2.4 invariant:
        - No decisions
        - No policy logic
        - No provider logic
        """
        pass
