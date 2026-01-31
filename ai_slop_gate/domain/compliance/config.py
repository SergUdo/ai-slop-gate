from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LicenseAuditConfig:
    enabled: bool = False
    forbidden_licenses: Optional[List[str]] = None
    severity: str = "high"
    tags: Optional[List[str]] = None


@dataclass
class SecurityAuditConfig:
    enabled: bool = False

    detect_secrets: bool = False
    detect_pii: bool = False
    detect_suspicious_todos: bool = False
    detect_non_eu_endpoints: bool = False

    enforce_data_residency: Optional[str] = None
    severity: str = "critical"
    tags: Optional[List[str]] = None


@dataclass
class GDPRDetectionConfig:
    enabled: bool = False
    severity_email: str = "medium"
    severity_ssn: str = "high"
    severity_todo: str = "medium"
    severity_non_eu_endpoint: str = "medium"


@dataclass
class ComplianceConfig:
    enabled: bool = False
    data_residency_mode: str = "advisory"

    license_audit: LicenseAuditConfig = field(default_factory=LicenseAuditConfig)
    security_audit: SecurityAuditConfig = field(default_factory=SecurityAuditConfig)
    gdpr_detection: GDPRDetectionConfig = field(default_factory=GDPRDetectionConfig)
