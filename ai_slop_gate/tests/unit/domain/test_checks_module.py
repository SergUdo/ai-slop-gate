"""Unit tests for domain/checks module."""
import pytest
from ai_slop_gate.domain.checks import CheckStatus, CheckAnnotation, CheckReport


class TestCheckStatus:
    """Test suite for CheckStatus enum."""

    def test_check_status_pass(self):
        """Test CheckStatus.PASS value."""
        assert CheckStatus.PASS.value == "pass"

    def test_check_status_advisory(self):
        """Test CheckStatus.ADVISORY value."""
        assert CheckStatus.ADVISORY.value == "advisory"

    def test_check_status_fail(self):
        """Test CheckStatus.FAIL value."""
        assert CheckStatus.FAIL.value == "fail"

    def test_check_status_string_comparison(self):
        """Test CheckStatus can be compared as strings."""
        assert CheckStatus.PASS == "pass"
        assert CheckStatus.ADVISORY == "advisory"
        assert CheckStatus.FAIL == "fail"

    def test_check_status_members(self):
        """Test CheckStatus has all expected members."""
        statuses = [member.name for member in CheckStatus]
        assert "PASS" in statuses
        assert "ADVISORY" in statuses
        assert "FAIL" in statuses

    def test_check_status_all_values(self):
        """Test all CheckStatus values."""
        all_values = [status.value for status in CheckStatus]
        assert "pass" in all_values
        assert "advisory" in all_values
        assert "fail" in all_values


class TestCheckAnnotation:
    """Test suite for CheckAnnotation dataclass."""

    def test_check_annotation_basic(self):
        """Test basic CheckAnnotation creation."""
        annotation = CheckAnnotation(
            file="test.py",
            line=10,
            message="Issue found",
            level="warning"
        )
        assert annotation.file == "test.py"
        assert annotation.line == 10
        assert annotation.message == "Issue found"
        assert annotation.level == "warning"

    def test_check_annotation_with_failure_level(self):
        """Test CheckAnnotation with failure level."""
        annotation = CheckAnnotation(
            file="main.py",
            line=42,
            message="Critical error",
            level="failure"
        )
        assert annotation.level == "failure"
        assert annotation.message == "Critical error"

    def test_check_annotation_with_none_file(self):
        """Test CheckAnnotation with None file."""
        annotation = CheckAnnotation(
            file=None,
            line=5,
            message="Global issue",
            level="warning"
        )
        assert annotation.file is None
        assert annotation.line == 5

    def test_check_annotation_with_none_line(self):
        """Test CheckAnnotation with None line."""
        annotation = CheckAnnotation(
            file="script.js",
            line=None,
            message="File-level issue",
            level="warning"
        )
        assert annotation.line is None
        assert annotation.file == "script.js"

    def test_check_annotation_is_frozen(self):
        """Test that CheckAnnotation is frozen."""
        annotation = CheckAnnotation(
            file="test.py",
            line=1,
            message="Test",
            level="warning"
        )
        with pytest.raises(AttributeError):
            annotation.file = "changed.py"

    def test_check_annotation_with_path(self):
        """Test CheckAnnotation with full file path."""
        annotation = CheckAnnotation(
            file="/home/user/project/src/main.py",
            line=100,
            message="Found issue",
            level="failure"
        )
        assert annotation.file == "/home/user/project/src/main.py"

    def test_check_annotation_multiline_message(self):
        """Test CheckAnnotation with multiline message."""
        msg = "Line 1\nLine 2\nLine 3"
        annotation = CheckAnnotation(
            file="test.py",
            line=1,
            message=msg,
            level="warning"
        )
        assert annotation.message == msg

    def test_check_annotation_empty_message(self):
        """Test CheckAnnotation with empty message."""
        annotation = CheckAnnotation(
            file="test.py",
            line=1,
            message="",
            level="warning"
        )
        assert annotation.message == ""

    def test_check_annotation_special_characters(self):
        """Test CheckAnnotation with special characters."""
        annotation = CheckAnnotation(
            file="test_file-2024.py",
            line=42,
            message="Issue: $VAR not defined",
            level="warning"
        )
        assert "$VAR" in annotation.message


class TestCheckReport:
    """Test suite for CheckReport dataclass."""

    def test_check_report_basic(self):
        """Test basic CheckReport creation."""
        report = CheckReport(
            title="Test Report",
            summary="All checks passed",
            status=CheckStatus.PASS,
            annotations=[]
        )
        assert report.title == "Test Report"
        assert report.summary == "All checks passed"
        assert report.status == CheckStatus.PASS
        assert len(report.annotations) == 0

    def test_check_report_with_fail_status(self):
        """Test CheckReport with FAIL status."""
        report = CheckReport(
            title="Failed Analysis",
            summary="Found critical issues",
            status=CheckStatus.FAIL,
            annotations=[]
        )
        assert report.status == CheckStatus.FAIL

    def test_check_report_with_advisory_status(self):
        """Test CheckReport with ADVISORY status."""
        report = CheckReport(
            title="Advisory Report",
            summary="Non-blocking issues detected",
            status=CheckStatus.ADVISORY,
            annotations=[]
        )
        assert report.status == CheckStatus.ADVISORY

    def test_check_report_with_annotations(self):
        """Test CheckReport with annotations."""
        annotations = [
            CheckAnnotation(file="test.py", line=10, message="Issue 1", level="warning"),
            CheckAnnotation(file="test.py", line=20, message="Issue 2", level="failure")
        ]
        report = CheckReport(
            title="Report with Issues",
            summary="2 issues found",
            status=CheckStatus.ADVISORY,
            annotations=annotations
        )
        assert len(report.annotations) == 2
        assert report.annotations[0].message == "Issue 1"

    def test_check_report_with_reasons(self):
        """Test CheckReport with reasons."""
        reasons = ["Reason 1", "Reason 2", "Reason 3"]
        report = CheckReport(
            title="Test",
            summary="Test",
            status=CheckStatus.ADVISORY,
            annotations=[],
            reasons=reasons
        )
        assert report.reasons == reasons
        assert len(report.reasons) == 3

    def test_check_report_without_reasons(self):
        """Test CheckReport without reasons (default None)."""
        report = CheckReport(
            title="Test",
            summary="Test",
            status=CheckStatus.PASS,
            annotations=[]
        )
        assert report.reasons is None

    def test_check_report_empty_annotations(self):
        """Test CheckReport with empty annotations list."""
        report = CheckReport(
            title="Clean Report",
            summary="No issues",
            status=CheckStatus.PASS,
            annotations=[]
        )
        assert len(report.annotations) == 0

    def test_check_report_multiline_summary(self):
        """Test CheckReport with multiline summary."""
        summary = "Line 1\nLine 2\nLine 3"
        report = CheckReport(
            title="Test",
            summary=summary,
            status=CheckStatus.PASS,
            annotations=[]
        )
        assert report.summary == summary

    def test_check_report_is_frozen(self):
        """Test that CheckReport is frozen."""
        report = CheckReport(
            title="Test",
            summary="Test",
            status=CheckStatus.PASS,
            annotations=[]
        )
        with pytest.raises(AttributeError):
            report.title = "Changed"

    def test_check_report_multiple_annotations(self):
        """Test CheckReport with multiple annotations."""
        annotations = [
            CheckAnnotation(f"file{i}.py", i*10, f"Message {i}", "warning")
            for i in range(5)
        ]
        report = CheckReport(
            title="Multiple Issues",
            summary="5 issues",
            status=CheckStatus.ADVISORY,
            annotations=annotations
        )
        assert len(report.annotations) == 5
