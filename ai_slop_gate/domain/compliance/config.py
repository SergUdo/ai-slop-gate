from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ComplianceConfig:
    """
    Canonical compliance configuration.
    Single source of truth for compliance settings.
    """

    enabled: bool = False
    profiles: Optional[List[str]] = None
    forbid_licenses: Optional[List[str]] = None
    allow_licenses: Optional[List[str]] = None
    enforcement: str = "advisory"


@dataclass(frozen=True)
class PolicyConfig:
    compliance: Optional[ComplianceConfig] = None
