from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Observation:
    # Identity
    rule_id: str

    # Policy matching
    category: str
    signal: str
    confidence: float

    # Human-readable
    severity: str
    message: str
    location: str

    # Context / proof
    evidence: Dict[str, Any] | None = None
