from dataclasses import dataclass
from enum import Enum
from typing import Optional


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
    rule_id: str
    category: str
    signal: str
    message: str
    severity: Severity
    confidence: float
    location: Optional[Location] = None
