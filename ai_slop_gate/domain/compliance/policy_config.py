from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class ComplianceConfig:
    enabled: bool = False
    profiles: List[str] = None
    forbid_licenses: List[str] = None
    allow_licenses: List[str] = None
    enforcement: str = "advisory"


@dataclass(frozen=True)
class PolicyConfig:
    compliance: Optional[ComplianceConfig] = None
