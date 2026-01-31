from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class PolicyRule:
    id: str
    when: Dict[str, Any]
    then: Dict[str, Any]
