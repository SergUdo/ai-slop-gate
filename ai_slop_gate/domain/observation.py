from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Observation:
    """
    Raw signal produced by a provider or static analyzer.

    Stage 1 invariant:
    - NO verdict
    - NO severity
    - NO enforcement logic
    """

    code: str                 # e.g. "TODO_FOUND", "AI_SUSPECT_COMMENT"
    message: str              # human-readable description
    file: Optional[str] = None
    line: Optional[int] = None
    provider: Optional[str] = None
