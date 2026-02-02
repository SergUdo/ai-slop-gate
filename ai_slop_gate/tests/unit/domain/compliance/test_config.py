"""Unit tests for domain/compliance modules."""
import pytest
from unittest.mock import Mock, patch
from ai_slop_gate.domain.compliance.config import (
    LicenseAuditConfig,
    SecurityAuditConfig,
    GDPRDetectionConfig
)
from ai_slop_gate.domain.compliance.enforcement import decision_for_severity, SEVERITY_TO_DECISION
from ai_slop_gate.domain.decision import DecisionMode


class TestLicenseAuditConfig:
    """Test suite for LicenseAuditConfig."""

    def test_license_audit_config_disabled(self):
        """Test LicenseAuditConfig disabled by default."""
        config = LicenseAuditConfig()
        assert config.enabled is False
        assert config.forbidden_licenses is None
        assert config.severity == "high"

    def test_license_audit_config_enabled(self):
        """Test LicenseAuditConfig enabled."""
        config = LicenseAuditConfig(
            enabled=True,
            forbidden_licenses=["GPL", "AGPL"],
            severity="critical"
        )
        assert config.enabled is True
        assert config.forbidden_licenses == ["GPL", "AGPL"]
        assert config.severity == "critical"

    def test_license_audit_config_with_tags(self):
        """Test LicenseAuditConfig with tags."""
        config = LicenseAuditConfig(
            enabled=True,
            tags=["security", "legal"]
        )
        assert config.tags == ["security", "legal"]


class TestSecurityAuditConfig:
    """Test suite for SecurityAuditConfig."""

    def test_security_audit_config_defaults(self):
        """Test SecurityAuditConfig default values."""
        config = SecurityAuditConfig()
        assert config.enabled is False
        assert config.detect_secrets is False
        assert config.detect_pii is False
        assert config.enforce_data_residency is None
        assert config.severity == "critical"

    def test_security_audit_config_enabled(self):
        """Test SecurityAuditConfig with features enabled."""
        config = SecurityAuditConfig(
            enabled=True,
            detect_secrets=True,
            detect_pii=True,
            enforce_data_residency="EU"
        )
        assert config.enabled is True
        assert config.detect_secrets is True
        assert config.detect_pii is True
        assert config.enforce_data_residency == "EU"

    def test_security_audit_config_partial(self):
        """Test SecurityAuditConfig with partial enablement."""
        config = SecurityAuditConfig(
            enabled=True,
            detect_secrets=True,
            detect_suspicious_todos=True
        )
        assert config.enabled is True
        assert config.detect_secrets is True
        assert config.detect_pii is False
        assert config.detect_suspicious_todos is True


class TestGDPRDetectionConfig:
    """Test suite for GDPRDetectionConfig."""

    def test_gdpr_detection_config_disabled(self):
        """Test GDPRDetectionConfig disabled by default."""
        config = GDPRDetectionConfig()
        assert config.enabled is False

    def test_gdpr_detection_config_enabled(self):
        """Test GDPRDetectionConfig enabled."""
        config = GDPRDetectionConfig(enabled=True)
        assert config.enabled is True
        assert config.severity_email == "medium"
        assert config.severity_ssn == "high"

    def test_gdpr_detection_config_custom_severities(self):
        """Test GDPRDetectionConfig with custom severities."""
        config = GDPRDetectionConfig(
            enabled=True,
            severity_email="high",
            severity_ssn="critical",
            severity_todo="low"
        )
        assert config.severity_email == "high"
        assert config.severity_ssn == "critical"
        assert config.severity_todo == "low"


class TestSeverityMapping:
    """Test suite for severity to decision mapping."""

    def test_severity_to_decision_low(self):
        """Test low severity maps to ADVISORY."""
        result = decision_for_severity("low")
        assert result == DecisionMode.ADVISORY

    def test_severity_to_decision_medium(self):
        """Test medium severity maps to ADVISORY."""
        result = decision_for_severity("medium")
        assert result == DecisionMode.ADVISORY

    def test_severity_to_decision_high(self):
        """Test high severity maps to BLOCKING."""
        result = decision_for_severity("high")
        assert result == DecisionMode.BLOCKING

    def test_severity_to_decision_unknown(self):
        """Test unknown severity defaults to ADVISORY."""
        result = decision_for_severity("unknown")
        assert result == DecisionMode.ADVISORY

    def test_severity_mapping_dict(self):
        """Test SEVERITY_TO_DECISION dictionary."""
        assert "low" in SEVERITY_TO_DECISION
        assert "medium" in SEVERITY_TO_DECISION
        assert "high" in SEVERITY_TO_DECISION
        assert SEVERITY_TO_DECISION["low"] == DecisionMode.ADVISORY
        assert SEVERITY_TO_DECISION["high"] == DecisionMode.BLOCKING
