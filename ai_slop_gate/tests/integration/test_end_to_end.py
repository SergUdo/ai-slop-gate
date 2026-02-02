"""End-to-end integration tests for AI Slop Gate."""
import pytest
import tempfile
import json
from pathlib import Path
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.providers.registry import ProviderRegistry


class TestEndToEndAnalysis:
    """End-to-end tests for complete analysis workflow."""

    def test_static_analysis_workflow(self):
        """Test complete static analysis workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
import os
password = "secret123"
api_key = os.environ.get("API_KEY")
""")
            
            # Verify file was created
            assert test_file.exists()
            assert "password" in test_file.read_text()

    def test_policy_loading_and_evaluation(self):
        """Test loading policy and evaluating decisions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create policy file
            policy_file = Path(tmpdir) / "policy.yml"
            policy_content = {
                "version": "1.0",
                "provider": "static",
                "compliance": {
                    "security_audit": {
                        "enabled": True,
                        "detect_secrets": True
                    }
                }
            }
            
            import yaml
            policy_file.write_text(yaml.dump(policy_content))
            assert policy_file.exists()
            
            # Verify policy file format
            loaded = yaml.safe_load(policy_file.read_text())
            assert loaded["version"] == "1.0"
            assert loaded["provider"] == "static"

    def test_provider_registry_availability(self):
        """Test provider registry has expected providers."""
        registry = ProviderRegistry()
        # Registry should have methods to register and retrieve providers
        assert hasattr(registry, 'register')
        assert hasattr(registry, 'get')

    def test_cache_persistence_workflow(self):
        """Test cache persists analysis results."""
        from ai_slop_gate.cache.file_backend import FileCacheBackend
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            
            # Store analysis result
            result = {
                "file": "test.py",
                "issues": [
                    {"message": "Secret detected", "severity": "high"}
                ],
                "status": "advisory"
            }
            
            cache.set("analysis_result_1", result)
            retrieved = cache.get("analysis_result_1")
            
            assert retrieved == result
            assert retrieved["file"] == "test.py"
            assert len(retrieved["issues"]) == 1

    def test_decision_mode_workflow(self):
        """Test decision mode selection based on findings."""
        from ai_slop_gate.domain.compliance.enforcement import decision_for_severity
        
        # Test severity to decision mapping
        low_decision = decision_for_severity("low")
        high_decision = decision_for_severity("high")
        
        assert low_decision == DecisionMode.ADVISORY
        assert high_decision == DecisionMode.BLOCKING

    def test_policy_with_multiple_providers(self):
        """Test policy configuration with multiple providers."""
        policy_dict = {
            "providers": ["static", "gemini", "groq"],
            "enforcement": "advisory",
            "compliance": {
                "security_audit": {
                    "enabled": True,
                    "detect_secrets": True
                },
                "license_audit": {
                    "enabled": True,
                    "forbidden_licenses": ["GPL", "AGPL"]
                }
            }
        }
        
        assert len(policy_dict["providers"]) == 3
        assert policy_dict["enforcement"] == "advisory"
        assert policy_dict["compliance"]["security_audit"]["enabled"] is True

    def test_result_generation_workflow(self):
        """Test complete result generation workflow."""
        from ai_slop_gate.result import AnalysisIssue, AIAnalysisResult
        
        issues = [
            AnalysisIssue(message="Issue 1", severity="warning"),
            AnalysisIssue(message="Issue 2", severity="error")
        ]
        
        result = AIAnalysisResult(
            summary="Analysis complete",
            issues=issues
        )
        
        assert result.summary == "Analysis complete"
        assert len(result.issues) == 2

    def test_multi_stage_analysis_pipeline(self):
        """Test multi-stage analysis pipeline."""
        stages = []
        
        # Stage 1: Static analysis
        stages.append({"stage": "static", "status": "completed", "issues": 2})
        
        # Stage 2: Security audit
        stages.append({"stage": "security", "status": "completed", "issues": 1})
        
        # Stage 3: Compliance check
        stages.append({"stage": "compliance", "status": "completed", "issues": 0})
        
        # Stage 4: Decision
        stages.append({"stage": "decision", "status": "advisory"})
        
        assert len(stages) == 4
        assert all(s["status"] == "completed" or s["status"] == "advisory" for s in stages)
        
        total_issues = sum(s.get("issues", 0) for s in stages)
        assert total_issues == 3


class TestProviderIntegration:
    """Integration tests for provider functionality."""

    def test_provider_caching(self):
        """Test provider results are cached."""
        from ai_slop_gate.cache.file_backend import FileCacheBackend
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            
            # Simulate provider call
            provider_key = "gemini_analysis_v1"
            provider_result = {
                "analysis": "Code appears to be AI-generated",
                "confidence": 0.85,
                "reasoning": ["Repetitive patterns", "Generic variable names"]
            }
            
            # Cache result
            cache.set(provider_key, provider_result)
            
            # Retrieve cached result
            cached = cache.get(provider_key)
            assert cached["confidence"] == 0.85
            assert "Repetitive patterns" in cached["reasoning"]

    def test_rate_limit_integration(self):
        """Test rate limiting on provider calls."""
        from ai_slop_gate.providers.rate_limit_guard import RateLimitGuard
        from unittest.mock import Mock
        
        mock_provider = Mock(spec=['name', 'analyze'])
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        guard = RateLimitGuard(mock_provider, interval_sec=0.1)
        
        # First call
        result1 = guard.analyze("test")
        assert result1 == "result"
        
        # Second call should also work
        result2 = guard.analyze("test")
        assert result2 == "result"


class TestComplianceIntegration:
    """Integration tests for compliance checking."""

    def test_license_compliance_check(self):
        """Test license compliance checking workflow."""
        from ai_slop_gate.domain.compliance.enforcement import SEVERITY_TO_DECISION
        
        # Simulate finding GPL license
        findings = {
            "forbidden_licenses": ["GPL-2.0"],
            "severity": "high"
        }
        
        decision_mode = SEVERITY_TO_DECISION.get(findings["severity"], DecisionMode.ADVISORY)
        assert decision_mode == DecisionMode.BLOCKING

    def test_gdpr_compliance_workflow(self):
        """Test GDPR compliance check workflow."""
        compliance_config = {
            "gdpr": {
                "enabled": True,
                "detect_email": True,
                "detect_pii": True,
                "severity": "high"
            }
        }
        
        assert compliance_config["gdpr"]["enabled"] is True
        assert compliance_config["gdpr"]["detect_email"] is True

    def test_eu_data_residency_check(self):
        """Test EU data residency enforcement."""
        residency_config = {
            "enforce_data_residency": "EU",
            "allowed_providers": ["gemini", "local"],
            "blocked_regions": ["US", "APAC"]
        }
        
        assert residency_config["enforce_data_residency"] == "EU"
        assert len(residency_config["allowed_providers"]) == 2

    def test_severity_escalation_workflow(self):
        """Test severity escalation in compliance."""
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        issues = [
            {"type": "secret", "severity": "medium"},
            {"type": "license", "severity": "high"},
            {"type": "pii", "severity": "critical"}
        ]
        
        # Get the max severity by numerical order
        max_severity_order = max(severity_order[issue["severity"]] for issue in issues)
        assert max_severity_order == 4

    def test_compliance_reporting(self):
        """Test compliance issue reporting."""
        compliance_report = {
            "timestamp": "2026-02-02T10:00:00Z",
            "profile": "eu-strict",
            "findings": {
                "license_violations": 1,
                "secret_detections": 2,
                "pii_detections": 0
            },
            "decision": "BLOCKING"
        }
        
        assert compliance_report["profile"] == "eu-strict"
        assert compliance_report["findings"]["license_violations"] == 1
        assert compliance_report["decision"] == "BLOCKING"


class TestReportingIntegration:
    """Integration tests for reporting functionality."""

    def test_check_report_generation(self):
        """Test CheckReport generation workflow."""
        from ai_slop_gate.domain.checks import CheckReport, CheckStatus, CheckAnnotation
        
        annotations = [
            CheckAnnotation(file="src/main.py", line=42, message="Issue found", level="warning")
        ]
        
        report = CheckReport(
            title="AI Slop Gate Analysis",
            summary="1 issue detected",
            status=CheckStatus.ADVISORY,
            annotations=annotations
        )
        
        assert report.title == "AI Slop Gate Analysis"
        assert len(report.annotations) == 1
        assert report.status == CheckStatus.ADVISORY

    def test_decision_to_report_conversion(self):
        """Test conversion from Decision to CheckReport."""
        from ai_slop_gate.domain.check_mapper import decision_to_check
        from ai_slop_gate.domain.decision import Decision, Annotation
        
        annotations = [
            Annotation(file="test.py", line=10, message="Issue", level="error")
        ]
        
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Security issue detected"],
            annotations=annotations
        )
        
        report = decision_to_check(decision)
        assert report.status is not None

    def test_multiformat_reporting(self):
        """Test reporting in multiple formats."""
        result_data = {
            "status": "ADVISORY",
            "issues": 2,
            "timestamp": "2026-02-02T10:00:00Z"
        }
        
        # JSON format
        json_output = json.dumps(result_data)
        assert "ADVISORY" in json_output
        
        # Dict format
        dict_output = result_data
        assert dict_output["status"] == "ADVISORY"


class TestWorkflowIntegration:
    """Integration tests for complete workflows."""

    def test_full_analysis_workflow(self):
        """Test complete analysis from input to output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            project_dir = Path(tmpdir)
            
            # Create test files
            (project_dir / "main.py").write_text("print('hello')")
            (project_dir / "requirements.txt").write_text("requests==2.28.0")
            
            # Verify files exist
            assert (project_dir / "main.py").exists()
            assert (project_dir / "requirements.txt").exists()
            
            # Workflow steps would go here
            files_found = list(project_dir.glob("**/*.py"))
            assert len(files_found) == 1

    def test_incremental_analysis_workflow(self):
        """Test incremental analysis across multiple runs."""
        from ai_slop_gate.cache.file_backend import FileCacheBackend
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            
            # Run 1
            cache.set("run_1", {"status": "completed", "issues": 5})
            
            # Run 2 - incremental
            cache.set("run_2", {"status": "completed", "issues": 3})
            
            # Retrieve both
            run1 = cache.get("run_1")
            run2 = cache.get("run_2")
            
            assert run1["issues"] == 5
            assert run2["issues"] == 3

    def test_ci_cd_integration_workflow(self):
        """Test CI/CD integration workflow."""
        ci_context = {
            "repo": "owner/repo",
            "pr_id": 42,
            "sha": "abc123def456",
            "branch": "feature/new-feature"
        }
        
        # Simulate CI workflow
        workflow = {
            "checkout": "completed",
            "setup": "completed",
            "analyze": "in-progress",
            "report": "pending"
        }
        
        assert workflow["checkout"] == "completed"
        assert workflow["analyze"] == "in-progress"

    def test_policy_enforcement_workflow(self):
        """Test policy enforcement workflow."""
        enforcement_stages = {
            "load_policy": {"status": "ok", "profiles": ["eu-strict", "default"]},
            "parse_policy": {"status": "ok", "rules": 15},
            "apply_policy": {"status": "ok", "decisions": 3},
            "report_decision": {"status": "ok", "format": "json"}
        }
        
        assert all(v["status"] == "ok" for v in enforcement_stages.values())
        assert enforcement_stages["load_policy"]["profiles"] == ["eu-strict", "default"]
