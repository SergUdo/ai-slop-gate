from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class ComplianceProfile:
    name: str
    forbid_licenses: List[str] = None
    data_regions: List[str] = None
    extends: Optional[str] = None


BASE_PROFILE = ComplianceProfile(
    name="base",
)

OSS_CLEAN_PROFILE = ComplianceProfile(
    name="oss-clean",
    forbid_licenses=["GPL-3.0", "AGPL-3.0", "SSPL"],
    extends="base",
)

EU_PROFILE = ComplianceProfile(
    name="eu",
    data_regions=["EU"],
    extends="oss-clean",
)

EU_STRICT_PROFILE = ComplianceProfile(
    name="eu-strict",
    forbid_licenses=["LGPL-3.0"],
    extends="eu",
)

PROFILE_REGISTRY = {
    "base": BASE_PROFILE,
    "oss-clean": OSS_CLEAN_PROFILE,
    "eu": EU_PROFILE,
    "eu-strict": EU_STRICT_PROFILE,
}
