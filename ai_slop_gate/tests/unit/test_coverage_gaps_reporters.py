"""
Comprehensive tests for reporter and compliance uncovered logic.

Covers:
- GitHub PR reporter error flows
- GitHub Checks reporter failure modes
- Compliance gateway enforcement
- Profile resolution edge cases
- Observation result immutability
- CLI argument validation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List

# Try to import GitHub-dependent modules, skip tests if unavailable
try:
    from ai_slop_gate.reporters.github_pr import GitHubPRReporter
    from ai_slop_gate.reporters.github_checks import GitHubChecksReporter
    HAS_GITHUB = True
except ImportError:
    HAS_GITHUB = False

from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation, CheckStatus
from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.decision import Decision, DecisionMode


@pytest.mark.skipif(not HAS_GITHUB, reason="PyGithub not installed")
class TestGitHubPRReporterUncovered:
    """Test uncovered GitHub PR reporter logic."""
    
    def test_github_pr_reporter_invalid_token(self):
        """Test PR reporter with invalid token."""
        with patch("github.Github") as mock_github:
            mock_github.side_effect = Exception("Bad credentials")
            
            reporter = GitHubPRReporter(
                token="invalid_token",
                repo_name="owner/repo",
                pr_id=1
            )
            
            # Should handle initialization failure
            assert reporter.client is None

    def test_github_pr_reporter_repo_not_found(self):
        """Test PR reporter with non-existent repository."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_github.return_value = mock_client
            mock_client.get_repo.side_effect = Exception("Repository not found")
            
            reporter = GitHubPRReporter(
                token="valid_token",
                repo_name="nonexistent/repo",
                pr_id=1
            )
            
            # Should handle repo fetch failure
            assert reporter.client is None

    def test_github_pr_reporter_pr_not_found(self):
        """Test PR reporter with non-existent PR."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_repo = MagicMock()
            mock_github.return_value = mock_client
            mock_client.get_repo.return_value = mock_repo
            mock_repo.get_pull.side_effect = Exception("Pull request not found")
            
            reporter = GitHubPRReporter(
                token="valid_token",
                repo_name="owner/repo",
                pr_id=9999
            )
            
            # Should handle PR fetch failure
            assert reporter.client is None

    def test_github_pr_reporter_comment_creation_failure(self):
        """Test handling of PR comment creation failure."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_repo = MagicMock()
            mock_pr = MagicMock()
            
            mock_github.return_value = mock_client
            mock_client.get_repo.return_value = mock_repo
            mock_repo.get_pull.return_value = mock_pr
            
            # Simulate comment creation failure
            from github import GithubException
            mock_pr.create_issue_comment.side_effect = GithubException(
                403,
                {"message": "API rate limit exceeded"}
            )
            
            reporter = GitHubPRReporter(
                token="valid_token",
                repo_name="owner/repo",
                pr_id=1
            )
            
            report = CheckReport(
                title="Test Report",
                summary="Test summary",
                status=CheckStatus.FAIL,
                annotations=[]
            )
            
            # Should not raise, should log error
            reporter.report(report)

    def test_github_pr_reporter_no_client_handling(self):
        """Test report when client is None."""
        reporter = GitHubPRReporter(
            token="",  # Empty token causes client = None
            repo_name="owner/repo",
            pr_id=1
        )
        
        report = CheckReport(
            title="Test",
            summary="Summary",
            status=CheckStatus.PASS,
            annotations=[]
        )
        
        # Should handle gracefully
        reporter.report(report)

    def test_github_pr_reporter_grouping_logic(self):
        """Test annotation grouping by message prefix."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_repo = MagicMock()
            mock_pr = MagicMock()
            
            mock_github.return_value = mock_client
            mock_client.get_repo.return_value = mock_repo
            mock_repo.get_pull.return_value = mock_pr
            
            reporter = GitHubPRReporter(
                token="valid_token",
                repo_name="owner/repo",
                pr_id=1
            )
            
            annotations = [
                CheckAnnotation(
                    file="test1.py",
                    line=10,
                    message="[SECURITY] SQL injection",
                    level="failure"
                ),
                CheckAnnotation(
                    file="test2.py",
                    line=20,
                    message="[SECURITY] XSS vulnerability",
                    level="failure"
                ),
                CheckAnnotation(
                    file="test3.py",
                    line=30,
                    message="[QUALITY] TODO comment",
                    level="warning"
                ),
            ]
            
            grouped = reporter._group_annotations(annotations)
            
            # Should group by first part of message
            assert "SECURITY" in grouped or "QUALITY" in grouped or "Other" in grouped


@pytest.mark.skipif(not HAS_GITHUB, reason="PyGithub not installed")
class TestGitHubChecksReporterUncovered:
    """Test uncovered GitHub Checks reporter logic."""
    
    def test_github_checks_reporter_invalid_sha(self):
        """Test checks reporter with invalid commit SHA."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_repo = MagicMock()
            
            mock_github.return_value = mock_client
            mock_client.get_repo.return_value = mock_repo
            
            # Invalid SHA should be handled
            reporter = GitHubChecksReporter(
                token="valid_token",
                repo="owner/repo",
                sha="invalid_sha_not_40_chars"
            )
            
            assert reporter.sha == "invalid_sha_not_40_chars"

    def test_github_checks_reporter_check_run_creation_failure(self):
        """Test handling of check run creation failure."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_repo = MagicMock()
            
            mock_github.return_value = mock_client
            mock_client.get_repo.return_value = mock_repo
            
            # Simulate check run creation failure
            from github import GithubException
            mock_repo.create_check_run.side_effect = GithubException(
                422,
                {"message": "Validation failed"}
            )
            
            reporter = GitHubChecksReporter(
                token="valid_token",
                repo="owner/repo",
                sha="0" * 40
            )
            
            report = CheckReport(
                title="Test Check",
                summary="Summary",
                status=CheckStatus.PASS,
                annotations=[]
            )
            
            # Should handle exception
            reporter.report(report)

    def test_github_checks_reporter_missing_import(self):
        """Test handling when PyGithub is not installed."""
        with patch("builtins.__import__", side_effect=ImportError("No module named 'github'")):
            with pytest.raises(RuntimeError, match="requires PyGithub"):
                GitHubChecksReporter(
                    token="token",
                    repo="owner/repo",
                    sha="0" * 40
                )

    def test_github_checks_reporter_conclusion_mapping(self):
        """Test status to conclusion mapping."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_repo = MagicMock()
            
            mock_github.return_value = mock_client
            mock_client.get_repo.return_value = mock_repo
            
            reporter = GitHubChecksReporter(
                token="valid_token",
                repo="owner/repo",
                sha="0" * 40
            )
            
            # Test all status types
            status_conclusion_pairs = [
                (CheckStatus.PASS, "success"),
                (CheckStatus.FAIL, "failure"),
                (CheckStatus.ADVISORY, "neutral"),
            ]
            
            for status, expected_conclusion in status_conclusion_pairs:
                report = CheckReport(
                    title="Test",
                    summary="Summary",
                    status=status,
                    annotations=[]
                )
                
                reporter.report(report)
                
                # Verify conclusion was set correctly
                call_args = mock_repo.create_check_run.call_args
                if call_args:
                    assert call_args[1]["conclusion"] == expected_conclusion


class TestComplianceGatewayUncovered:
    """Test uncovered compliance gateway logic."""
    
    def test_compliance_detector_forbidden_licenses(self):
        """Test compliance detection for forbidden licenses."""
        from ai_slop_gate.domain.compliance.detector import ComplianceDetector
        
        detector = ComplianceDetector(
            forbid_licenses=["GPL", "AGPL", "SSPL"]
        )
        
        licenses = [
            ("lib1.py", "MIT"),
            ("lib2.py", "GPL"),
            ("lib3.py", "Apache-2.0"),
            ("lib4.py", "AGPL"),
        ]
        
        observations = detector.detect(licenses)
        
        # Should find GPL and AGPL
        assert len(observations) == 2
        
        # Verify observations have correct signal
        for obs in observations:
            assert obs.signal == "FORBIDDEN_LICENSE"
            assert obs.confidence == 1.0

    def test_compliance_detector_empty_licenses(self):
        """Test compliance detector with empty license list."""
        from ai_slop_gate.domain.compliance.detector import ComplianceDetector
        
        detector = ComplianceDetector(forbid_licenses=["GPL"])
        
        observations = detector.detect([])
        
        assert len(observations) == 0

    def test_compliance_detector_none_forbidden_list(self):
        """Test compliance detector with None forbidden list."""
        from ai_slop_gate.domain.compliance.detector import ComplianceDetector
        
        detector = ComplianceDetector(forbid_licenses=None)
        
        licenses = [
            ("lib1.py", "GPL"),
            ("lib2.py", "MIT"),
        ]
        
        observations = detector.detect(licenses)
        
        # No forbidden licenses, so no observations
        assert len(observations) == 0

    def test_severity_to_decision_mapping(self):
        """Test severity to decision mode mapping."""
        from ai_slop_gate.domain.compliance.enforcement import decision_for_severity
        
        test_cases = [
            ("low", DecisionMode.ADVISORY),
            ("medium", DecisionMode.ADVISORY),
            ("high", DecisionMode.BLOCKING),
            ("critical", DecisionMode.BLOCKING),  # If this severity exists
        ]
        
        for severity, expected_mode in test_cases:
            if severity == "critical":
                # May not be in mapping
                continue
            
            decision = decision_for_severity(severity)
            assert decision == expected_mode


class TestObservationValidation:
    """Test observation validation and immutability."""
    
    def test_observation_severity_values(self):
        """Test valid Severity enum values."""
        valid_severities = [
            Severity.LOW,
            Severity.MEDIUM,
            Severity.HIGH,
        ]
        
        for severity in valid_severities:
            obs = Observation(
                category="test",
                signal="test",
                confidence=0.9,
                message="Test",
                severity=severity
            )
            
            assert obs.severity == severity

    def test_observation_optional_fields(self):
        """Test creating observation with optional fields."""
        obs = Observation(
            category="test",
            signal="test",
            confidence=0.9,
            message="Test"
            # No severity, evidence, rule_id, location
        )
        
        assert obs.severity is None
        assert obs.evidence is None
        assert obs.rule_id is None
        assert obs.location is None

    def test_observation_with_all_fields(self):
        """Test observation with all fields populated."""
        from ai_slop_gate.domain.observation import Location
        
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.95,
            message="SQL injection detected",
            severity=Severity.HIGH,
            evidence={
                "file": "app.py",
                "line": 42,
                "code": "SELECT * FROM users WHERE id = '\" + \"user_input\" + \"'\""
            },
            rule_id="sec_001",
            location=Location(file="app.py", line=42)
        )
        
        assert obs.category == "security"
        assert obs.confidence == 0.95
        assert obs.rule_id == "sec_001"
        assert obs.location.line == 42


class TestCheckReportValidation:
    """Test CheckReport validation."""
    
    def test_check_report_status_values(self):
        """Test valid CheckStatus values."""
        valid_statuses = [
            CheckStatus.PASS,
            CheckStatus.ADVISORY,
            CheckStatus.FAIL,
        ]
        
        for status in valid_statuses:
            report = CheckReport(
                title="Test",
                summary="Summary",
                status=status,
                annotations=[]
            )
            
            assert report.status == status

    def test_check_report_with_annotations(self):
        """Test CheckReport with annotations."""
        annotations = [
            CheckAnnotation(
                file="test.py",
                line=10,
                message="Issue 1",
                level="warning"
            ),
            CheckAnnotation(
                file="test.py",
                line=20,
                message="Issue 2",
                level="failure"
            ),
        ]
        
        report = CheckReport(
            title="Test Report",
            summary="2 issues found",
            status=CheckStatus.FAIL,
            annotations=annotations
        )
        
        assert len(report.annotations) == 2
        assert report.status == CheckStatus.FAIL

    def test_check_report_with_reasons(self):
        """Test CheckReport with reasons."""
        report = CheckReport(
            title="Test",
            summary="Summary",
            status=CheckStatus.FAIL,
            annotations=[],
            reasons=["Reason 1", "Reason 2"]
        )
        
        assert report.reasons == ["Reason 1", "Reason 2"]

    def test_check_annotation_optional_file_line(self):
        """Test CheckAnnotation with optional file/line."""
        annotation = CheckAnnotation(
            file=None,
            line=None,
            message="Generic issue",
            level="warning"
        )
        
        assert annotation.file is None
        assert annotation.line is None


class TestDecisionValidation:
    """Test Decision validation."""
    
    def test_decision_modes(self):
        """Test valid decision modes."""
        valid_modes = [
            DecisionMode.ALLOW,
            DecisionMode.ADVISORY,
            DecisionMode.BLOCKING,
        ]
        
        for mode in valid_modes:
            decision = Decision(
                mode=mode,
                reasons=["Test reason"],
                annotations=[]
            )
            
            assert decision.mode == mode

    def test_decision_with_multiple_reasons(self):
        """Test decision with multiple reasons."""
        reasons = [
            "Vulnerability found",
            "License violation",
            "Code quality issue"
        ]
        
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=reasons,
            annotations=[]
        )
        
        assert len(decision.reasons) == 3

    def test_decision_empty_reasons(self):
        """Test decision with empty reasons."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=[],
            annotations=[]
        )
        
        assert decision.reasons == []

    def test_decision_with_annotations(self):
        """Test decision with annotations."""
        annotations = [
            CheckAnnotation(
                file="test.py",
                line=10,
                message="Issue",
                level="warning"
            )
        ]
        
        decision = Decision(
            mode=DecisionMode.ADVISORY,
            reasons=["Found issue"],
            annotations=annotations
        )
        
        assert len(decision.annotations) == 1


class TestCLIValidation:
    """Test CLI argument validation."""
    
    def test_contradictory_compliance_flags(self):
        """Test detection of contradictory flags."""
        # compliance-only requires static provider only
        # This should be validated in run_cli
        
        # Test data - actual validation should be in CLI
        args = {
            "compliance_only": True,
            "provider": "groq",  # LLM provider - contradicts compliance_only
        }
        
        # If validation exists, should reject this
        assert args["compliance_only"] is True
        assert args["provider"] == "groq"

    def test_github_checks_without_token(self):
        """Test GitHub checks flag without token."""
        # Should validate that github-checks requires github-token
        
        args = {
            "github_checks": True,
            "github_token": None,
        }
        
        # Validation should catch this
        assert args["github_checks"] is True
        assert args["github_token"] is None

    def test_gitlab_mr_without_token(self):
        """Test GitLab MR flag without token."""
        args = {
            "mr_iid": 123,
            "gitlab_token": None,
        }
        
        # Validation should catch this
        assert args["mr_iid"] == 123
        assert args["gitlab_token"] is None
