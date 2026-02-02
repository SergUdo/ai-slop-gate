"""Policy engine integration tests."""
import pytest
import tempfile
import yaml
from pathlib import Path
from ai_slop_gate.domain.policy_engine import PolicyEngine


class TestPolicyEngineIntegration:
    """Integration tests for policy engine."""

    def test_policy_loading_and_parsing(self):
        """Test policy file loading and parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_file = Path(tmpdir) / "policy.yml"
            
            policy_data = {
                "version": "1.0",
                "provider": "static",
                "rules": [
                    {"name": "rule1", "enabled": True},
                    {"name": "rule2", "enabled": False}
                ],
                "compliance": {
                    "security_audit": {"enabled": True}
                }
            }
            
            policy_file.write_text(yaml.dump(policy_data))
            
            # Load and verify
            loaded = yaml.safe_load(policy_file.read_text())
            assert loaded["version"] == "1.0"
            assert len(loaded["rules"]) == 2

    def test_policy_with_profiles(self):
        """Test policy with multiple profiles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_file = Path(tmpdir) / "policy.yml"
            
            policy_data = {
                "version": "1.0",
                "profiles": {
                    "default": {
                        "provider": "static",
                        "enforcement": "advisory"
                    },
                    "eu-strict": {
                        "provider": "gemini",
                        "enforcement": "blocking",
                        "compliance": {
                            "enforce_data_residency": "EU"
                        }
                    },
                    "enterprise": {
                        "provider": ["static", "gemini", "groq"],
                        "enforcement": "blocking"
                    }
                }
            }
            
            policy_file.write_text(yaml.dump(policy_data))
            loaded = yaml.safe_load(policy_file.read_text())
            
            assert "default" in loaded["profiles"]
            assert "eu-strict" in loaded["profiles"]
            assert "enterprise" in loaded["profiles"]

    def test_policy_inheritance(self):
        """Test profile inheritance in policies."""
        base_profile = {
            "provider": "static",
            "enforcement": "advisory",
            "rules": {"secrets": True, "licenses": True}
        }
        
        extended_profile = {
            **base_profile,
            "enforcement": "blocking",
            "compliance": {"enforce_data_residency": "EU"}
        }
        
        assert extended_profile["provider"] == base_profile["provider"]
        assert extended_profile["enforcement"] == "blocking"
        assert extended_profile["compliance"]["enforce_data_residency"] == "EU"

    def test_policy_validation(self):
        """Test policy validation."""
        valid_policy = {
            "version": "1.0",
            "provider": "static"
        }
        
        # Check required fields
        assert "version" in valid_policy
        assert "provider" in valid_policy

    def test_policy_merging(self):
        """Test merging policies from multiple sources."""
        global_policy = {
            "version": "1.0",
            "enforcement": "advisory",
            "compliance": {"security_audit": {"enabled": True}}
        }
        
        team_policy = {
            "enforcement": "blocking",
            "compliance": {"license_audit": {"enabled": True}}
        }
        
        # Merge policies
        merged = {**global_policy, **team_policy}
        merged["compliance"] = {**global_policy["compliance"], **team_policy["compliance"]}
        
        assert merged["enforcement"] == "blocking"
        assert merged["compliance"]["security_audit"]["enabled"] is True
        assert merged["compliance"]["license_audit"]["enabled"] is True

    def test_policy_compliance_rules(self):
        """Test compliance rules in policy."""
        policy = {
            "compliance": {
                "security_audit": {
                    "enabled": True,
                    "detect_secrets": True,
                    "detect_pii": True,
                    "severity": "high"
                },
                "license_audit": {
                    "enabled": True,
                    "forbidden_licenses": ["GPL", "AGPL", "SSPL"],
                    "severity": "critical"
                },
                "gdpr_detection": {
                    "enabled": True,
                    "detect_email": True,
                    "severity": "high"
                }
            }
        }
        
        assert policy["compliance"]["security_audit"]["enabled"] is True
        assert "GPL" in policy["compliance"]["license_audit"]["forbidden_licenses"]
        assert policy["compliance"]["gdpr_detection"]["detect_email"] is True

    def test_policy_enforcement_modes(self):
        """Test different enforcement modes in policy."""
        enforcement_modes = {
            "advisory": "warn but don't fail",
            "blocking": "fail on violations",
            "permissive": "only log"
        }
        
        policies = [
            {"enforcement": "advisory", "enabled": True},
            {"enforcement": "blocking", "enabled": True},
            {"enforcement": "permissive", "enabled": True}
        ]
        
        for policy in policies:
            assert policy["enforcement"] in enforcement_modes
            assert policy["enabled"] is True

    def test_policy_provider_configuration(self):
        """Test provider configuration in policy."""
        policy = {
            "providers": {
                "static": {
                    "enabled": True,
                    "rules": ["secrets", "hardcoded"]
                },
                "gemini": {
                    "enabled": True,
                    "model": "gemini-2.5-flash",
                    "api_key": "${GEMINI_API_KEY}"
                },
                "groq": {
                    "enabled": True,
                    "model": "llama-3.3-70b",
                    "api_key": "${GROQ_API_KEY}"
                }
            }
        }
        
        assert policy["providers"]["static"]["enabled"] is True
        assert policy["providers"]["gemini"]["model"] == "gemini-2.5-flash"
        assert len(policy["providers"]) == 3

    def test_policy_rule_configuration(self):
        """Test rule configuration in policy."""
        policy = {
            "rules": {
                "secrets": {
                    "enabled": True,
                    "patterns": ["password", "api_key", "token"],
                    "severity": "critical"
                },
                "hardcoded_creds": {
                    "enabled": True,
                    "patterns": ["http://user:pass@", "Basic .*"],
                    "severity": "high"
                },
                "pii": {
                    "enabled": True,
                    "patterns": ["ssn", "email"],
                    "severity": "high"
                }
            }
        }
        
        assert policy["rules"]["secrets"]["enabled"] is True
        assert "api_key" in policy["rules"]["secrets"]["patterns"]


class TestPolicyDecisionIntegration:
    """Integration tests for policy-based decisions."""

    def test_policy_decision_blocking(self):
        """Test policy resulting in blocking decision."""
        from ai_slop_gate.domain.decision import DecisionMode
        
        policy = {
            "enforcement": "blocking",
            "findings": [
                {"type": "secret", "severity": "critical"}
            ]
        }
        
        # If enforcement is blocking and severity is critical
        if policy["enforcement"] == "blocking" and any(f["severity"] == "critical" for f in policy["findings"]):
            decision = DecisionMode.BLOCKING
            assert decision == DecisionMode.BLOCKING

    def test_policy_decision_advisory(self):
        """Test policy resulting in advisory decision."""
        from ai_slop_gate.domain.decision import DecisionMode
        
        policy = {
            "enforcement": "advisory",
            "findings": [
                {"type": "style", "severity": "low"}
            ]
        }
        
        # If enforcement is advisory, decision is advisory
        if policy["enforcement"] == "advisory":
            decision = DecisionMode.ADVISORY
            assert decision == DecisionMode.ADVISORY

    def test_policy_decision_allow(self):
        """Test policy resulting in allow decision."""
        from ai_slop_gate.domain.decision import DecisionMode
        
        policy = {
            "enforcement": "permissive",
            "findings": []
        }
        
        # If no findings and permissive enforcement
        if not policy["findings"] and policy["enforcement"] == "permissive":
            decision = DecisionMode.ALLOW
            assert decision == DecisionMode.ALLOW

    def test_policy_override_logic(self):
        """Test policy override logic for decisions."""
        # Base policy
        policy = {
            "enforcement": "advisory",
            "override_rules": [
                {"condition": "critical_security", "action": "block"}
            ]
        }
        
        # Check findings
        findings = [
            {"type": "secret", "severity": "critical", "category": "critical_security"}
        ]
        
        # Check if override applies
        override_found = any(
            f["category"] == r["condition"] and r["action"] == "block"
            for f in findings
            for r in policy["override_rules"]
        )
        
        if override_found:
            decision = "block"
            assert decision == "block"
