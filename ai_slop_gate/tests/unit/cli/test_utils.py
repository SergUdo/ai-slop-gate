import pytest
import yaml
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock, mock_open
from ai_slop_gate.cli.utils import load_policy


class TestLoadPolicy:
    """Test suite for load_policy function."""

    @pytest.fixture
    def minimal_policy_yaml(self):
        """Minimal valid policy YAML content."""
        return {
            "enforcement": "advisory",
            "rules": []
        }

    @pytest.fixture
    def complete_policy_yaml(self):
        """Complete policy YAML with all sections."""
        return {
            "enforcement": "strict",
            "ai_provider": {
                "provider": "gemini",
                "model": "gemini-2.0"
            },
            "compliance": {
                "enabled": True,
                "data_residency_mode": "enforce",
                "license_audit": {
                    "enabled": True,
                    "forbidden_licenses": ["GPL-3.0"],
                    "severity": "high",
                    "tags": ["license"]
                },
                "security_audit": {
                    "enabled": True,
                    "detect_secrets": True,
                    "detect_pii": True,
                    "detect_suspicious_todos": True,
                    "detect_non_eu_endpoints": True,
                    "enforce_data_residency": "EU",
                    "severity": "critical",
                    "tags": ["security"]
                },
                "gdpr_detection": {
                    "enabled": True,
                    "severity_email": "high",
                    "severity_ssn": "critical",
                    "severity_todo": "medium",
                    "severity_non_eu_endpoint": "high"
                }
            },
            "code_quality": {
                "enabled": True
            },
            "infrastructure_security": {
                "enabled": True
            },
            "ai_slop": {
                "enabled": True
            },
            "rules": [
                {
                    "id": "rule1",
                    "when": {"type": "check"},
                    "then": {"action": "alert"}
                }
            ]
        }

    def test_load_minimal_policy(self, minimal_policy_yaml):
        """Test loading a minimal policy file."""
        policy_str = yaml.dump(minimal_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, rules = load_policy("policy.yml")
            
            assert policy_config is not None
            assert rules == []
            assert policy_config.enforcement == "advisory"

    def test_load_complete_policy(self, complete_policy_yaml):
        """Test loading a complete policy file."""
        policy_str = yaml.dump(complete_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, rules = load_policy("policy.yml")
            
            assert policy_config is not None
            assert len(rules) == 1
            assert rules[0].id == "rule1"
            assert policy_config.enforcement == "strict"
            assert policy_config.compliance.enabled is True

    def test_load_policy_with_rules(self, complete_policy_yaml):
        """Test that load_policy returns rules."""
        policy_str = yaml.dump(complete_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, rules = load_policy("policy.yml")
            
            assert isinstance(rules, list)
            assert len(rules) == 1
            assert rules[0].id == "rule1"

    def test_load_policy_compliance_disabled_defaults(self, minimal_policy_yaml):
        """Test that compliance has correct defaults when disabled."""
        policy_str = yaml.dump(minimal_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.compliance.enabled is False
            assert policy_config.compliance.license_audit.enabled is False
            assert policy_config.compliance.security_audit.enabled is False
            assert policy_config.compliance.gdpr_detection.enabled is False

    def test_load_policy_license_audit_config(self, complete_policy_yaml):
        """Test license audit configuration is loaded correctly."""
        policy_str = yaml.dump(complete_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.compliance.license_audit.enabled is True
            assert "GPL-3.0" in policy_config.compliance.license_audit.forbidden_licenses
            assert policy_config.compliance.license_audit.severity == "high"

    def test_load_policy_security_audit_config(self, complete_policy_yaml):
        """Test security audit configuration is loaded correctly."""
        policy_str = yaml.dump(complete_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            sec_cfg = policy_config.compliance.security_audit
            assert sec_cfg.enabled is True
            assert sec_cfg.detect_secrets is True
            assert sec_cfg.detect_pii is True
            assert sec_cfg.detect_suspicious_todos is True
            assert sec_cfg.detect_non_eu_endpoints is True
            assert sec_cfg.enforce_data_residency == "EU"

    def test_load_policy_gdpr_config(self, complete_policy_yaml):
        """Test GDPR detection configuration is loaded correctly."""
        policy_str = yaml.dump(complete_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            gdpr_cfg = policy_config.compliance.gdpr_detection
            assert gdpr_cfg.enabled is True
            assert gdpr_cfg.severity_email == "high"
            assert gdpr_cfg.severity_ssn == "critical"
            assert gdpr_cfg.severity_todo == "medium"
            assert gdpr_cfg.severity_non_eu_endpoint == "high"

    def test_load_policy_default_enforcement(self, minimal_policy_yaml):
        """Test default enforcement mode when not specified."""
        minimal_yaml = {}
        policy_str = yaml.dump(minimal_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.enforcement == "advisory"

    def test_load_policy_default_data_residency(self, minimal_policy_yaml):
        """Test default data residency mode."""
        policy_str = yaml.dump(minimal_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.compliance.data_residency_mode == "advisory"

    def test_load_policy_default_license_severity(self):
        """Test default severity for license audit."""
        policy_yaml = {
            "compliance": {
                "license_audit": {
                    "enabled": True
                }
            }
        }
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.compliance.license_audit.severity == "high"

    def test_load_policy_default_security_severity(self):
        """Test default severity for security audit."""
        policy_yaml = {
            "compliance": {
                "security_audit": {
                    "enabled": True
                }
            }
        }
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.compliance.security_audit.severity == "critical"

    def test_load_policy_returns_policy_config_object(self, minimal_policy_yaml):
        """Test that load_policy returns a PolicyConfig object."""
        policy_str = yaml.dump(minimal_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config is not None
            assert hasattr(policy_config, 'enforcement')
            assert hasattr(policy_config, 'compliance')

    def test_load_policy_returns_rules_list(self, complete_policy_yaml):
        """Test that load_policy returns a list of rules."""
        policy_str = yaml.dump(complete_policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            _, rules = load_policy("policy.yml")
            
            assert isinstance(rules, list)
            # Check that rules have required PolicyRule fields
            for rule in rules:
                assert hasattr(rule, 'id')
                assert hasattr(rule, 'when')
                assert hasattr(rule, 'then')

    def test_load_policy_custom_path(self, minimal_policy_yaml):
        """Test loading policy from custom path."""
        policy_str = yaml.dump(minimal_policy_yaml)
        custom_path = "/custom/path/to/policy.yml"
        
        with patch("builtins.open", mock_open(read_data=policy_str)) as mock_file:
            load_policy(custom_path)
            
            mock_file.assert_called_once_with(custom_path, "r", encoding="utf-8")

    def test_load_policy_empty_rules(self):
        """Test loading policy with empty rules."""
        policy_yaml = {"rules": []}
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, rules = load_policy("policy.yml")
            
            assert len(rules) == 0

    def test_load_policy_multiple_rules(self):
        """Test loading policy with multiple rules."""
        policy_yaml = {
            "rules": [
                {"id": "rule1", "when": {"type": "check1"}, "then": {"action": "alert"}},
                {"id": "rule2", "when": {"type": "check2"}, "then": {"action": "block"}},
                {"id": "rule3", "when": {"type": "check3"}, "then": {"action": "warn"}}
            ]
        }
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, rules = load_policy("policy.yml")
            
            assert len(rules) == 3
            assert rules[0].id == "rule1"
            assert rules[1].id == "rule2"
            assert rules[2].id == "rule3"

    def test_load_policy_ai_provider_config(self):
        """Test ai_provider configuration is loaded."""
        policy_yaml = {
            "ai_provider": {
                "provider": "gemini",
                "model": "gemini-pro"
            }
        }
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.ai_provider == policy_yaml["ai_provider"]

    def test_load_policy_code_quality_config(self):
        """Test code_quality configuration is loaded."""
        policy_yaml = {
            "code_quality": {
                "enabled": True,
                "rules": []
            }
        }
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.code_quality == policy_yaml["code_quality"]

    def test_load_policy_infrastructure_security_config(self):
        """Test infrastructure_security configuration is loaded."""
        policy_yaml = {
            "infrastructure_security": {
                "enabled": True
            }
        }
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.infrastructure_security == policy_yaml["infrastructure_security"]

    def test_load_policy_ai_slop_config(self):
        """Test ai_slop configuration is loaded."""
        policy_yaml = {
            "ai_slop": {
                "enabled": True,
                "threshold": 0.5
            }
        }
        policy_str = yaml.dump(policy_yaml)
        
        with patch("builtins.open", mock_open(read_data=policy_str)):
            policy_config, _ = load_policy("policy.yml")
            
            assert policy_config.ai_slop == policy_yaml["ai_slop"]
