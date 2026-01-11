from dataclasses import dataclass, field
from typing import Set, List

@dataclass(frozen=True)
class LicenseRule:
    id: str
    forbidden_licenses: Set[str]
    message: str = "Legal risk: forbidden license detected"
    action: str = "blocking"

@dataclass(frozen=True)
class SecretRule:
    id: str
    message: str = "Security risk: hardcoded secret detected"
    action: str = "blocking"