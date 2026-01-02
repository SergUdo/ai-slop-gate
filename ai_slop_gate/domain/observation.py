from dataclasses import dataclass
from typing import Literal, Dict, Optional

@dataclass(frozen=True)
class Observation:
    category: str
    signal: str
    message: str
    confidence: float = 1.0
    source: Optional[str] = None
