import yaml
from ai_slop_gate.domain.policy_engine import PolicyRule
from ai_slop_gate.domain.config import PolicyConfig, ComplianceConfig

def load_policy(path: str):
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    compliance = None
    comp_raw = raw.get("compliance")

    if comp_raw:
        license_cfg = comp_raw.get("license", {})
        compliance = ComplianceConfig(
            enabled=comp_raw.get("enabled", False),
            profiles=comp_raw.get("profiles", []),
            forbid_licenses=license_cfg.get("forbid", []),
            allow_licenses=license_cfg.get("allow", []),
            enforcement=comp_raw.get("enforcement", "advisory"),
        )

    rules = []

    for rule in raw.get("rules", []):
        then = rule["then"]
        action = then.get("decision") or then.get("action")

        rules.append(
            PolicyRule(
                id=rule["id"],
                category=rule["when"].get("category"),
                signal=rule["when"].get("signal"),
                source=rule["when"].get("source"),
                license=rule["when"].get("license"),
                min_confidence=rule["when"].get("min_confidence", 0.0),
                action=action,
                message=then.get("reason") or then.get("message"),
            )
        )

    return PolicyConfig(compliance=compliance), rules
