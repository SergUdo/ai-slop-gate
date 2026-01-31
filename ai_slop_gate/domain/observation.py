from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Location:
    file: str
    line: Optional[int] = None


@dataclass(frozen=True)
class Observation:
    """
    Stage 0.7 observation contract.

    Supports:
    - New format: category, signal, confidence, message, severity, evidence, rule_id
    - Legacy field: location (used by older providers/tests)
    """

    category: str
    signal: str
    confidence: float
    message: str

    severity: Optional[Severity] = None
    evidence: Optional[Dict[str, Any]] = None
    rule_id: Optional[str] = None

    # Legacy compatibility
    location: Optional[Location] = None
    