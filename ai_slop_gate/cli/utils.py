from pathlib import Path
import yaml

from ai_slop_gate.domain.policy_engine import PolicyRule
from ai_slop_gate.domain.policy_config import (
    PolicyConfig,
    ComplianceConfig,
)

def load_policy(path: str):
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    # --- Compliance section (optional)
    compliance_raw = raw.get("compliance")
    compliance = None

    if compliance_raw:
        compliance = ComplianceConfig(
            enabled=compliance_raw.get("enabled", False),
            profiles=compliance_raw.get("profiles", []),
            forbid_licenses=compliance_raw.get("license", {}).get("forbid", []),
            allow_licenses=compliance_raw.get("license", {}).get("allow", []),
            enforcement=compliance_raw.get("enforcement", "advisory"),
        )

    # --- Rules
    rules = []
    for rule in raw.get("rules", []):
        rules.append(
            PolicyRule(
                id=rule["id"],
                category=rule["when"].get("category"),
                signal=rule["when"].get("signal"),
                source=rule["when"].get("source"),
                license=rule["when"].get("license"),
                min_confidence=rule["when"].get("min_confidence", 0.0),
                action=rule["then"]["decision"],
                message=rule["then"]["reason"],
            )
        )

    return PolicyConfig(compliance=compliance), rules
