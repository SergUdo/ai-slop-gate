from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any, Optional

@dataclass(frozen=True)
class ProviderObservation:
    """
    Standard container for results from any provider.
    Observations is a list of objects created by make_observation.
    """
    provider: str
    model: str
    observations: List[Any]
    raw_text: str

class BaseProvider(ABC):
    """
    Base contract for all Analysis Providers.
    Supports both local filesystem collection and remote snippet analysis.
    """
    name: str
    kind: str  # "llm" or "static" or "infra"

    @abstractmethod
    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Analyzes a specific string of code or a single file content.
        Used primarily by LLMs for PR diffs or specialized snippet scans.
        """
        pass

    @abstractmethod
    def collect(self, base_path: str = ".") -> ProviderObservation:
        """
        Scans a directory or gathers data from the environment.
        Used by static analysis tools (ESLint, AST, etc.) to audit a codebase.
        """
        pass

    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        """
        Optional implementation for providers that interface directly with GitHub.
        Typically implemented only by LLM providers.
        """
        raise NotImplementedError(
            f"Provider '{self.name}' (kind: {self.kind}) does not support direct PR analysis mode. "
            "Use local collection instead."
        )