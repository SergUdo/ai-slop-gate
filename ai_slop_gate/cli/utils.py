import yaml
from typing import Tuple, List, Dict, Optional

from ai_slop_gate.domain.config import PolicyConfig
from ai_slop_gate.domain.compliance.config import ComplianceConfig
from ai_slop_gate.domain.compliance.profiles import (
    load_profiles,
    resolve_profile_chain,
)
from ai_slop_gate.domain.policy_engine import PolicyRule
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.domain.compliance.profiles import ComplianceProfile


def load_policy(path: str) -> Tuple[PolicyConfig, List[PolicyRule]]:
    with open(path, "r") as f:
        raw = yaml.safe_load(f) or {}

    compliance_raw = raw.get("compliance", {})
    compliance_cfg = None

    raw_profiles = compliance_raw.get("profiles", [])
    profiles = {}
    if raw_profiles:
        if isinstance(raw_profiles[0], str):
            for profile_name in raw_profiles:
                profiles[profile_name] = ComplianceProfile(name=profile_name, forbid_licenses=[])
        else:
            profiles = load_profiles(raw_profiles)

    active_profile_name = compliance_raw.get("active_profile")
    active_profile = resolve_profile_chain(active_profile_name, profiles) if active_profile_name else None

    forbid_licenses = []
    if active_profile:
        forbid_licenses.extend(active_profile.forbid_licenses or [])
    if compliance_raw.get("forbid_licenses"):
        forbid_licenses.extend(compliance_raw["forbid_licenses"])

    compliance_cfg = ComplianceConfig(
        enabled=bool(compliance_raw.get("enabled", False)),
        profiles=[active_profile_name] if active_profile_name else None,
        forbid_licenses=forbid_licenses or None,
    )

    rules_raw = raw.get("rules", [])
    rules = [PolicyRule(id=r["id"], when=r.get("when", {}), then=r.get("then", {})) for r in rules_raw]

    return PolicyConfig(compliance=compliance_cfg), rules

