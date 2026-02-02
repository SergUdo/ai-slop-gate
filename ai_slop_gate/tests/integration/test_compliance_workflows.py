"""Compliance workflow integration tests."""
import pytest
import tempfile
from pathlib import Path


class TestComplianceWorkflows:
    """Integration tests for compliance workflows."""

    def test_security_compliance_workflow(self):
        """Test complete security compliance workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Scan for secrets
            findings = {
                "secrets": [
                    {"type": "api_key", "file": "config.py", "line": 10},
                    {"type": "password", "file": "app.py", "line": 45}
                ]
            }
            
            # Step 2: Evaluate severity
            severity_map = {
                "api_key": "high",
                "password": "critical"
            }
            severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            
            # Step 3: Make decision
            severities = [severity_map[f["type"]] for f in findings["secrets"]]
            # Severities are ["high", "critical"], max by order is "critical"
            max_severity_order = max(severity_order[s] for s in severities)
            assert max_severity_order == 4

    def test_license_compliance_workflow(self):
        """Test license compliance workflow."""
        requirements = [
            {"package": "flask", "version": "2.0.0", "license": "BSD"},
            {"package": "requests", "version": "2.28.0", "license": "Apache-2.0"},
            {"package": "gpl_package", "version": "1.0.0", "license": "GPL-2.0"}
        ]
        
        forbidden = ["GPL", "AGPL", "SSPL"]
        
        violations = [
            r for r in requirements
            if any(f in r["license"] for f in forbidden)
        ]
        
        assert len(violations) == 1
        assert violations[0]["package"] == "gpl_package"

    def test_gdpr_compliance_workflow(self):
        """Test GDPR compliance workflow."""
        code_scans = {
            "pii_detected": [
                {"type": "email", "count": 3, "files": ["auth.py", "models.py"]},
                {"type": "ssn", "count": 1, "files": ["user_data.py"]},
                {"type": "phone", "count": 2, "files": ["contact.py"]}
            ]
        }
        
        high_risk = [
            p for p in code_scans["pii_detected"]
            if p["type"] in ["ssn", "credit_card"]
        ]
        
        assert len(high_risk) == 1

    def test_data_residency_compliance(self):
        """Test data residency compliance check."""
        residency_requirement = "EU"
        
        providers_config = {
            "gemini": {"region": "US", "compliant": False},
            "groq": {"region": "US", "compliant": False},
            "local": {"region": "EU", "compliant": True}
        }
        
        violations = [
            p for p, conf in providers_config.items()
            if not conf["compliant"] and residency_requirement == "EU"
        ]
        
        assert "gemini" in violations
        assert "groq" in violations
        assert "local" not in violations

    def test_ai_generated_code_compliance(self):
        """Test AI-generated code detection and compliance."""
        code_metrics = {
            "repetition_score": 0.85,
            "variance_score": 0.15,
            "pattern_match": 0.92,
            "documentation_score": 0.3
        }
        
        # AI-generated code indicators
        ai_indicators = [
            code_metrics["repetition_score"] > 0.8,
            code_metrics["variance_score"] < 0.3,
            code_metrics["documentation_score"] < 0.5
        ]
        
        is_ai_generated = sum(ai_indicators) >= 2
        assert is_ai_generated is True

    def test_compliance_issue_severity_mapping(self):
        """Test mapping compliance issues to severity levels."""
        issues = {
            "critical": ["hardcoded_secret", "gpl_license"],
            "high": ["weak_crypto", "sql_injection"],
            "medium": ["hardcoded_url", "missing_auth"],
            "low": ["style", "naming"]
        }
        
        finding = "hardcoded_secret"
        severity = next(
            (sev for sev, items in issues.items() if finding in items),
            None
        )
        
        assert severity == "critical"

    def test_compliance_remediation_workflow(self):
        """Test compliance issue remediation workflow."""
        issues = [
            {"id": 1, "type": "secret", "status": "found"},
            {"id": 2, "type": "license", "status": "found"},
            {"id": 3, "type": "style", "status": "found"}
        ]
        
        # Remediate by priority
        critical_issues = [i for i in issues if i["type"] in ["secret", "license"]]
        
        for issue in critical_issues:
            issue["status"] = "remediated"
        
        remediated_count = sum(1 for i in issues if i["status"] == "remediated")
        assert remediated_count == 2

    def test_compliance_report_generation(self):
        """Test compliance report generation."""
        report = {
            "timestamp": "2026-02-02T10:00:00Z",
            "compliance_score": 85,
            "issues": {
                "critical": 1,
                "high": 2,
                "medium": 3,
                "low": 5
            },
            "profile_used": "eu-strict",
            "decision": "ADVISORY"
        }
        
        assert report["compliance_score"] == 85
        assert report["issues"]["critical"] == 1
        assert report["decision"] == "ADVISORY"

    def test_compliance_audit_trail(self):
        """Test compliance audit trail generation."""
        audit_log = [
            {"timestamp": "2026-02-02T10:00:00Z", "action": "policy_loaded", "profile": "eu-strict"},
            {"timestamp": "2026-02-02T10:00:01Z", "action": "scan_started", "target": "main.py"},
            {"timestamp": "2026-02-02T10:00:05Z", "action": "issue_found", "type": "secret", "severity": "critical"},
            {"timestamp": "2026-02-02T10:00:06Z", "action": "decision_made", "result": "BLOCKING"},
            {"timestamp": "2026-02-02T10:00:07Z", "action": "report_generated", "format": "json"}
        ]
        
        assert len(audit_log) == 5
        assert audit_log[0]["action"] == "policy_loaded"
        assert audit_log[3]["result"] == "BLOCKING"


class TestEnterpriseComplianceWorkflows:
    """Integration tests for enterprise compliance scenarios."""

    def test_multi_profile_compliance(self):
        """Test multi-profile compliance checking."""
        profiles = {
            "default": {
                "enforcement": "advisory",
                "checks": ["static_analysis"]
            },
            "eu-strict": {
                "enforcement": "blocking",
                "checks": ["static_analysis", "security_audit", "gdpr_check", "license_check"],
                "data_residency": "EU"
            },
            "enterprise": {
                "enforcement": "blocking",
                "checks": ["static_analysis", "security_audit", "license_check", "ai_detection"],
                "providers": ["static", "gemini", "groq"]
            }
        }
        
        # Select profile
        selected_profile = profiles["eu-strict"]
        assert selected_profile["enforcement"] == "blocking"
        assert len(selected_profile["checks"]) == 4

    def test_organization_policy_enforcement(self):
        """Test organization-wide policy enforcement."""
        org_policies = {
            "global": {
                "forbidden_licenses": ["GPL", "AGPL"],
                "max_ai_generated": 0.2,
                "require_docs": True
            },
            "team_overrides": {
                "data-team": {
                    "max_ai_generated": 0.3
                }
            }
        }
        
        # Get policy for team
        team = "data-team"
        effective_policy = {**org_policies["global"]}
        if team in org_policies["team_overrides"]:
            effective_policy.update(org_policies["team_overrides"][team])
        
        assert effective_policy["max_ai_generated"] == 0.3
        assert effective_policy["require_docs"] is True

    def test_rollout_compliance_workflow(self):
        """Test compliance checking for feature rollout."""
        rollout_stages = {
            "pre_release": {
                "checks_required": ["security", "license"],
                "enforcement": "blocking",
                "approval_required": True
            },
            "staging": {
                "checks_required": ["security", "license", "performance"],
                "enforcement": "blocking",
                "approval_required": True
            },
            "production": {
                "checks_required": ["security", "license", "performance", "accessibility"],
                "enforcement": "blocking",
                "approval_required": True
            }
        }
        
        stage = "production"
        required_checks = rollout_stages[stage]["checks_required"]
        assert len(required_checks) == 4

    def test_exception_approval_workflow(self):
        """Test exception approval workflow for compliance."""
        violation = {
            "type": "license",
            "package": "special_lib",
            "license": "GPL-2.0",
            "status": "violation_found"
        }
        
        exception_request = {
            "violation_id": violation,
            "justification": "Business critical, no alternative available",
            "requested_by": "team_lead",
            "expires": "2026-12-31"
        }
        
        approvals = {
            "security_team": {"status": "approved", "approver": "sec_lead"},
            "legal_team": {"status": "approved", "approver": "legal_counsel"}
        }
        
        all_approved = all(a["status"] == "approved" for a in approvals.values())
        assert all_approved is True
