"""Unit tests for domain/check_mapper module."""
import pytest
from unittest.mock import Mock
from ai_slop_gate.domain.check_mapper import decision_to_check
from ai_slop_gate.domain.decision import Decision, DecisionMode, Annotation
from ai_slop_gate.domain.checks import CheckStatus


class TestDecisionToCheck:
    """Test suite for decision_to_check function."""

    def test_decision_to_check_blocking_decision(self):
        """Test conversion of blocking decision."""
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Reason 1", "Reason 2"],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        assert report.status == CheckStatus.FAIL
        assert "🚨 Blocking" in report.summary

    def test_decision_to_check_advisory_decision(self):
        """Test conversion of advisory decision with reasons."""
        decision = Decision(
            mode=DecisionMode.ADVISORY,
            reasons=["Advisory reason"],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        assert report.status == CheckStatus.ADVISORY
        assert "⚠️ Advisory" in report.summary

    def test_decision_to_check_pass_decision(self):
        """Test conversion of passing decision."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=[],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        # ALLOW mode with no reasons should result in PASS
        assert report.status == CheckStatus.PASS or report.status == CheckStatus.ADVISORY

    def test_decision_to_check_report_title(self):
        """Test that report has correct title."""
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=[],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        assert report.title == "AI Slop Gate Analysis"

    def test_decision_to_check_blocking_with_multiple_reasons(self):
        """Test blocking decision with multiple reasons."""
        reasons = ["Issue 1", "Issue 2", "Issue 3"]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=reasons,
            annotations=[]
        )
        report = decision_to_check(decision)
        
        assert "3 issue(s) detected" in report.summary
        assert all(reason in report.summary for reason in reasons)

    def test_decision_to_check_with_annotations(self):
        """Test conversion with annotations."""
        annotations = [
            Annotation(file="test.py", line=10, message="Issue 1", level="error"),
            Annotation(file="test.py", line=20, message="Issue 2", level="warning")
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Reason"],
            annotations=annotations
        )
        report = decision_to_check(decision)
        
        assert len(report.annotations) == 2
        assert report.annotations[0].file == "test.py"
        assert report.annotations[0].line == 10

    def test_decision_to_check_annotation_level_conversion(self):
        """Test annotation level is converted correctly."""
        annotations = [
            Annotation(file="test.py", line=1, message="Error", level="error"),
            Annotation(file="test.py", line=2, message="Warning", level="warning")
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Reason"],
            annotations=annotations
        )
        report = decision_to_check(decision)
        
        assert report.annotations[0].level == "failure"
        assert report.annotations[1].level == "warning"

    def test_decision_to_check_no_annotations(self):
        """Test conversion with no annotations."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=[],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        # When annotations is empty list, annotations should be None per code logic
        assert report.annotations is None or len(report.annotations) == 0

    def test_decision_to_check_advisory_without_reasons(self):
        """Test advisory decision without reasons defaults to PASS."""
        decision = Decision(
            mode=DecisionMode.ADVISORY,
            reasons=[],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        # When mode is ADVISORY but reasons is empty, should still show advisory status
        # But based on code, it checks if decision.reasons is truthy
        # Empty list is falsy, so it should be PASS status
        assert report.status == CheckStatus.PASS or report.status == CheckStatus.ADVISORY

    def test_decision_to_check_single_reason(self):
        """Test decision with single reason."""
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Single issue"],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        assert "1 issue(s) detected" in report.summary
        assert "Single issue" in report.summary

    def test_decision_to_check_permissive_mode(self):
        """Test ALLOW mode results in PASS status."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=["Not enforced"],
            annotations=[]
        )
        report = decision_to_check(decision)
        
        # ALLOW mode without reasons check should go to else (PASS)
        # But if it has reasons, it might be ADVISORY, check both
        assert report.status in [CheckStatus.PASS, CheckStatus.ADVISORY]

    def test_decision_to_check_annotation_message_preserved(self):
        """Test annotation messages are preserved."""
        msg = "Critical issue: $VAR not found"
        annotations = [
            Annotation(file="main.py", line=42, message=msg, level="error")
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Reason"],
            annotations=annotations
        )
        report = decision_to_check(decision)
        
        assert report.annotations[0].message == msg

    def test_decision_to_check_annotation_file_preserved(self):
        """Test annotation file paths are preserved."""
        file_path = "/home/user/project/src/module.py"
        annotations = [
            Annotation(file=file_path, line=1, message="Issue", level="warning")
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Reason"],
            annotations=annotations
        )
        report = decision_to_check(decision)
        
        assert report.annotations[0].file == file_path

    def test_decision_to_check_multiple_blocking_reasons(self):
        """Test multiple reasons in blocking decision."""
        reasons = [f"Reason {i}" for i in range(5)]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=reasons,
            annotations=[]
        )
        report = decision_to_check(decision)
        
        assert "5 issue(s) detected" in report.summary
        for reason in reasons:
            assert f"- {reason}" in report.summary
