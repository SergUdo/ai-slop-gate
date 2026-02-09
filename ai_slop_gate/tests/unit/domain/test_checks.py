import pytest
from ai_slop_gate.domain.checks import CheckStatus, CheckAnnotation, CheckReport


class TestCheckStatus:
    """Test suite for CheckStatus enum."""

    def test_check_status_pass(self):
        """Test PASS status value."""
        assert CheckStatus.PASS == "pass"

    def test_check_status_advisory(self):
        """Test ADVISORY status value."""
        assert CheckStatus.ADVISORY == "advisory"

    def test_check_status_fail(self):
        """Test FAIL status value."""
        assert CheckStatus.FAIL == "fail"

    def test_check_status_string_comparison(self):
        """Test comparing status with string."""
        status = CheckStatus.FAIL
        assert status == "fail"

    def test_check_status_is_enum(self):
        """Test that CheckStatus is an enum."""
        assert isinstance(CheckStatus.PASS, CheckStatus)
        assert isinstance(CheckStatus.ADVISORY, CheckStatus)
        assert isinstance(CheckStatus.FAIL, CheckStatus)


class TestCheckAnnotation:
    """Test suite for CheckAnnotation dataclass."""

    def test_annotation_with_file_and_line(self):
        """Test creating CheckAnnotation with file and line."""
        ann = CheckAnnotation(
            file="app.py",
            line=42,
            message="Issue found",
            level="warning"
        )
        
        assert ann.file == "app.py"
        assert ann.line == 42
        assert ann.message == "Issue found"
        assert ann.level == "warning"

    def test_annotation_with_none_file(self):
        """Test creating CheckAnnotation with None file."""
        ann = CheckAnnotation(
            file=None,
            line=None,
            message="General issue",
            level="warning"
        )
        
        assert ann.file is None
        assert ann.line is None
        assert ann.message == "General issue"

    def test_annotation_with_failure_level(self):
        """Test CheckAnnotation with failure level."""
        ann = CheckAnnotation(
            file="app.py",
            line=42,
            message="Critical issue",
            level="failure"
        )
        
        assert ann.level == "failure"

    def test_annotation_immutable(self):
        """Test that CheckAnnotation is immutable (frozen)."""
        ann = CheckAnnotation(
            file="app.py",
            line=42,
            message="Issue",
            level="warning"
        )
        
        with pytest.raises(AttributeError):
            ann.file = "other.py"

    def test_annotation_absolute_path(self):
        """Test CheckAnnotation with absolute path."""
        ann = CheckAnnotation(
            file="/home/user/project/app.py",
            line=42,
            message="Issue",
            level="warning"
        )
        
        assert ann.file == "/home/user/project/app.py"

    def test_annotation_relative_path(self):
        """Test CheckAnnotation with relative path."""
        ann = CheckAnnotation(
            file="src/app.py",
            line=42,
            message="Issue",
            level="warning"
        )
        
        assert ann.file == "src/app.py"

    def test_annotation_empty_message(self):
        """Test CheckAnnotation with empty message."""
        ann = CheckAnnotation(
            file="app.py",
            line=42,
            message="",
            level="warning"
        )
        
        assert ann.message == ""

    def test_annotation_line_zero(self):
        """Test CheckAnnotation with line 0."""
        ann = CheckAnnotation(
            file="app.py",
            line=0,
            message="Issue",
            level="warning"
        )
        
        assert ann.line == 0

    def test_annotation_line_large_number(self):
        """Test CheckAnnotation with large line number."""
        ann = CheckAnnotation(
            file="app.py",
            line=999999,
            message="Issue",
            level="warning"
        )
        
        assert ann.line == 999999


class TestCheckReport:
    """Test suite for CheckReport dataclass."""

    def test_report_pass_status(self):
        """Test CheckReport with PASS status."""
        report = CheckReport(
            title="Security Check",
            summary="All security checks passed",
            status=CheckStatus.PASS,
            annotations=[]
        )
        
        assert report.title == "Security Check"
        assert report.summary == "All security checks passed"
        assert report.status == CheckStatus.PASS
        assert report.annotations == []

    def test_report_advisory_status(self):
        """Test CheckReport with ADVISORY status."""
        ann = CheckAnnotation(
            file="app.py",
            line=42,
            message="Warning",
            level="warning"
        )
        report = CheckReport(
            title="Code Quality Check",
            summary="Some warnings found",
            status=CheckStatus.ADVISORY,
            annotations=[ann]
        )
        
        assert report.status == CheckStatus.ADVISORY
        assert len(report.annotations) == 1

    def test_report_fail_status(self):
        """Test CheckReport with FAIL status."""
        report = CheckReport(
            title="Security Check",
            summary="Critical issues found",
            status=CheckStatus.FAIL,
            annotations=[]
        )
        
        assert report.status == CheckStatus.FAIL

    def test_report_with_single_annotation(self):
        """Test CheckReport with single annotation."""
        ann = CheckAnnotation(
            file="app.py",
            line=42,
            message="Issue",
            level="failure"
        )
        report = CheckReport(
            title="Check",
            summary="Issue found",
            status=CheckStatus.FAIL,
            annotations=[ann]
        )
        
        assert len(report.annotations) == 1
        assert report.annotations[0] == ann

    def test_report_with_multiple_annotations(self):
        """Test CheckReport with multiple annotations."""
        anns = [
            CheckAnnotation(file="app.py", line=42, message="Issue 1", level="failure"),
            CheckAnnotation(file="api.py", line=10, message="Issue 2", level="warning"),
            CheckAnnotation(file=None, line=None, message="General issue", level="failure")
        ]
        report = CheckReport(
            title="Check",
            summary="Multiple issues",
            status=CheckStatus.FAIL,
            annotations=anns
        )
        
        assert len(report.annotations) == 3
        assert report.annotations == anns

    def test_report_with_reasons(self):
        """Test CheckReport with reasons."""
        reasons = ["Reason 1", "Reason 2", "Reason 3"]
        report = CheckReport(
            title="Check",
            summary="Issues found",
            status=CheckStatus.FAIL,
            annotations=[],
            reasons=reasons
        )
        
        assert report.reasons == reasons
        assert len(report.reasons) == 3

    def test_report_with_none_reasons(self):
        """Test CheckReport with None reasons."""
        report = CheckReport(
            title="Check",
            summary="No issues",
            status=CheckStatus.PASS,
            annotations=[],
            reasons=None
        )
        
        assert report.reasons is None

    def test_report_with_empty_reasons(self):
        """Test CheckReport with empty reasons list."""
        report = CheckReport(
            title="Check",
            summary="No reasons",
            status=CheckStatus.PASS,
            annotations=[],
            reasons=[]
        )
        
        assert report.reasons == []

    def test_report_immutable(self):
        """Test that CheckReport is immutable (frozen)."""
        report = CheckReport(
            title="Check",
            summary="Summary",
            status=CheckStatus.PASS,
            annotations=[]
        )
        
        with pytest.raises(AttributeError):
            report.title = "New Title"

    def test_report_long_title(self):
        """Test CheckReport with long title."""
        title = "Security Check for Database Connection and Authentication Layer"
        report = CheckReport(
            title=title,
            summary="Check performed",
            status=CheckStatus.PASS,
            annotations=[]
        )
        
        assert report.title == title

    def test_report_long_summary(self):
        """Test CheckReport with long summary."""
        summary = "This is a comprehensive summary explaining all the security checks that were performed, their results, and any potential risks identified during the analysis process."
        report = CheckReport(
            title="Security Check",
            summary=summary,
            status=CheckStatus.PASS,
            annotations=[]
        )
        
        assert report.summary == summary

    def test_report_empty_annotations_list(self):
        """Test CheckReport with empty annotations list."""
        report = CheckReport(
            title="Check",
            summary="No annotations",
            status=CheckStatus.PASS,
            annotations=[]
        )
        
        assert report.annotations == []
        assert len(report.annotations) == 0

    def test_report_various_status_and_annotations_combinations(self):
        """Test different combinations of status and annotations."""
        cases = [
            (CheckStatus.PASS, []),
            (CheckStatus.ADVISORY, [
                CheckAnnotation(file="app.py", line=1, message="Warning", level="warning")
            ]),
            (CheckStatus.FAIL, [
                CheckAnnotation(file="app.py", line=1, message="Error 1", level="failure"),
                CheckAnnotation(file="api.py", line=2, message="Error 2", level="failure")
            ])
        ]
        
        for status, annotations in cases:
            report = CheckReport(
                title="Test",
                summary="Test summary",
                status=status,
                annotations=annotations
            )
            assert report.status == status
            assert report.annotations == annotations

    def test_report_with_special_characters_in_summary(self):
        """Test CheckReport with special characters."""
        summary = "Check failed: config error in 'app.py' - <tag> not allowed, issue at line 42:15"
        report = CheckReport(
            title="Check",
            summary=summary,
            status=CheckStatus.FAIL,
            annotations=[]
        )
        
        assert report.summary == summary

    def test_report_annotation_with_unicode_message(self):
        """Test CheckReport with unicode in annotation messages."""
        ann = CheckAnnotation(
            file="app.py",
            line=42,
            message="Error: Success is not guaranteed",
            level="failure"
        )
        report = CheckReport(
            title="Check",
            summary="Unicode test",
            status=CheckStatus.FAIL,
            annotations=[ann]
        )
        
        assert report.annotations[0].message == "Error: Success is not guaranteed"
