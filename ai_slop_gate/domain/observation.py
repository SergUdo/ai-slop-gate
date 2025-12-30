from dataclasses import dataclass
from typing import Literal, Dict, Optional

@dataclass(frozen=True)
class Observation:
    """
    Stage 2.2 contract.
    Structured observation from a provider.
    """
    category: Literal["quality", "style", "hallucination"]
    signal: Literal["positive", "neutral", "negative"]
    confidence: float        # 0.0 – 1.0
    message: str
    evidence: Dict[str, Optional[int | str]]
