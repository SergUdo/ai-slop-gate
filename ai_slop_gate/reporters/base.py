# ai_slop_gate/reporters/base.py
from abc import ABC, abstractmethod
from ai_slop_gate.domain.checks import CheckReport

class Reporter(ABC):
    @abstractmethod
    def report(self, report: CheckReport) -> None:
        """
        Sends a CheckReport to a specific destination.
        :param report: The unified domain object containing check results.
        """
        pass
