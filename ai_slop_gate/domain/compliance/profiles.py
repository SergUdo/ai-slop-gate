from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass(frozen=True)
class ComplianceProfile:
    """
    A single compliance profile definition loaded from policy.yml.
    Profiles may extend each other and override fields.
    """
    name: str
    forbid_licenses: Optional[List[str]] = None
    data_regions: Optional[List[str]] = None
    extends: Optional[str] = None


def load_profiles(raw_profiles: List[Dict]) -> Dict[str, ComplianceProfile]:
    profiles = {}
    for p in raw_profiles:
        if isinstance(p, str):
            profiles[p] = ComplianceProfile(name=p, forbid_licenses=[])
        else:
            profiles[p["name"]] = ComplianceProfile(
                name=p["name"],
                forbid_licenses=p.get("forbid_licenses") or [],
                data_regions=p.get("data_regions") or [],
                extends=p.get("extends"),
            )
    return profiles



def resolve_profile_chain(name: str, profiles: Dict[str, ComplianceProfile]) -> ComplianceProfile:
    """
    Resolve a profile including all inherited fields via 'extends'.
    Merge order: base → child.
    """
    chain = []
    current = name

    # Build inheritance chain
    while current:
        if current not in profiles:
            raise ValueError(f"Unknown compliance profile: {current}")
        chain.append(profiles[current])
        current = profiles[current].extends

    # Merge from base → leaf
    merged_forbid = []
    merged_regions = []

    for p in reversed(chain):
        if p.forbid_licenses:
            merged_forbid.extend(p.forbid_licenses)
        if p.data_regions:
            merged_regions.extend(p.data_regions)

    return ComplianceProfile(
        name=name,
        forbid_licenses=merged_forbid,
        data_regions=merged_regions,
        extends=None,
    )
