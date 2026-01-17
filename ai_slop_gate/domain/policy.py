from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class PolicyRule:
    """
    Stage 0.7 declarative policy rule.

    Structure:
    - id: rule identifier
    - when: matching conditions (category, signal, min_confidence)
    - then: action block (action, message)
    """

    id: str
    when: Dict[str, Any]
    then: Dict[str, Any]

