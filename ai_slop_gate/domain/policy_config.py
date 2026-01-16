from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class ComplianceConfig:
    enabled: bool = False
    profiles: List[str] = None
    enforcement: str = "advisory"


@dataclass(frozen=True)
class PolicyConfig:
    compliance: Optional[ComplianceConfig] = None
