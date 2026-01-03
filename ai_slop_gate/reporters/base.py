# ai_slop_gate/reporters/base.py
from abc import ABC, abstractmethod
from ai_slop_gate.domain.checks import CheckReport


class CheckReporter(ABC):
    @abstractmethod
    def report(self, report: CheckReport) -> None:
        pass

