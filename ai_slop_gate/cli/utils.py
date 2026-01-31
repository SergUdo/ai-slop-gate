import yaml
from ai_slop_gate.domain.compliance.config import (
    ComplianceConfig,
    LicenseAuditConfig,
    SecurityAuditConfig,
    GDPRDetectionConfig,
)
from ai_slop_gate.domain.config import PolicyConfig
from ai_slop_gate.domain.policy import PolicyRule


def load_policy(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    compliance_data = data.get("compliance", {})

    # LICENSE AUDIT
    license_cfg = LicenseAuditConfig(
        enabled=compliance_data.get("license_audit", {}).get("enabled", False),
        forbidden_licenses=compliance_data.get("license_audit", {}).get("forbidden_licenses", []),
        severity=compliance_data.get("license_audit", {}).get("severity", "high"),
        tags=compliance_data.get("license_audit", {}).get("tags", []),
    )

    # SECURITY AUDIT
    sec = compliance_data.get("security_audit", {})

    security_cfg = SecurityAuditConfig(
        enabled=sec.get("enabled", False),
        detect_secrets=sec.get("detect_secrets", False),
        detect_pii=sec.get("detect_pii", False),
        detect_suspicious_todos=sec.get("detect_suspicious_todos", False),
        detect_non_eu_endpoints=sec.get("detect_non_eu_endpoints", False),
        enforce_data_residency=sec.get("enforce_data_residency"),
        severity=sec.get("severity", "critical"),
        tags=sec.get("tags", []),
    )

    # GDPR DETECTION
    gdpr = compliance_data.get("gdpr_detection", {})

    gdpr_cfg = GDPRDetectionConfig(
        enabled=gdpr.get("enabled", False),
        severity_email=gdpr.get("severity_email", "medium"),
        severity_ssn=gdpr.get("severity_ssn", "high"),
        severity_todo=gdpr.get("severity_todo", "medium"),
        severity_non_eu_endpoint=gdpr.get("severity_non_eu_endpoint", "medium"),
    )

    # COMPLIANCE ROOT
    compliance_cfg = ComplianceConfig(
        enabled=compliance_data.get("enabled", False),
        data_residency_mode=compliance_data.get("data_residency_mode", "advisory"),
        license_audit=license_cfg,
        security_audit=security_cfg,
        gdpr_detection=gdpr_cfg,
    )

    # RULES
    rules_raw = data.get("rules", [])
    rules = [PolicyRule(**rule) for rule in rules_raw]

    # FULL POLICY CONFIG
    policy_config = PolicyConfig(
        enforcement=data.get("enforcement", "advisory"),
        ai_provider=data.get("ai_provider", {}),
        compliance=compliance_cfg,
        code_quality=data.get("code_quality", {}),
        infrastructure_security=data.get("infrastructure_security", {}),
        ai_slop=data.get("ai_slop", {}),
        rules=rules,
    )

    return policy_config, rules
