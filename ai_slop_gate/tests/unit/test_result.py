"""Unit tests for result module."""
import pytest
from ai_slop_gate.result import AnalysisInput, AnalysisIssue, AIAnalysisResult


class TestAnalysisInput:
    """Test suite for AnalysisInput dataclass."""

    def test_analysis_input_creation(self):
        """Test creating AnalysisInput."""
        input_obj = AnalysisInput(text="print('hello')", filename="test.py")
        assert input_obj.text == "print('hello')"
        assert input_obj.filename == "test.py"

    def test_analysis_input_with_multiline_text(self):
        """Test AnalysisInput with multiline text."""
        code = "def hello():\n    print('hello')\n"
        input_obj = AnalysisInput(text=code, filename="module.py")
        assert input_obj.text == code
        assert input_obj.filename == "module.py"

    def test_analysis_input_with_javascript(self):
        """Test AnalysisInput with JavaScript code."""
        js_code = "console.log('test');"
        input_obj = AnalysisInput(text=js_code, filename="script.js")
        assert input_obj.text == js_code
        assert input_obj.filename == "script.js"

    def test_analysis_input_empty_text(self):
        """Test AnalysisInput with empty text."""
        input_obj = AnalysisInput(text="", filename="empty.py")
        assert input_obj.text == ""
        assert input_obj.filename == "empty.py"

    def test_analysis_input_special_characters_in_filename(self):
        """Test AnalysisInput with special characters in filename."""
        input_obj = AnalysisInput(text="code", filename="/path/to/my-file_test.py")
        assert input_obj.filename == "/path/to/my-file_test.py"


class TestAnalysisIssue:
    """Test suite for AnalysisIssue dataclass."""

    def test_analysis_issue_info(self):
        """Test creating AnalysisIssue with info severity."""
        issue = AnalysisIssue(message="Information message", severity="info")
        assert issue.message == "Information message"
        assert issue.severity == "info"

    def test_analysis_issue_warning(self):
        """Test creating AnalysisIssue with warning severity."""
        issue = AnalysisIssue(message="Warning message", severity="warning")
        assert issue.message == "Warning message"
        assert issue.severity == "warning"

    def test_analysis_issue_error(self):
        """Test creating AnalysisIssue with error severity."""
        issue = AnalysisIssue(message="Error message", severity="error")
        assert issue.message == "Error message"
        assert issue.severity == "error"

    def test_analysis_issue_multiline_message(self):
        """Test AnalysisIssue with multiline message."""
        msg = "Line 1\nLine 2\nLine 3"
        issue = AnalysisIssue(message=msg, severity="warning")
        assert issue.message == msg

    def test_analysis_issue_with_special_characters(self):
        """Test AnalysisIssue with special characters in message."""
        msg = "Found issue: $VAR not defined @ line 42"
        issue = AnalysisIssue(message=msg, severity="error")
        assert issue.message == msg

    def test_analysis_issue_empty_message(self):
        """Test AnalysisIssue with empty message."""
        issue = AnalysisIssue(message="", severity="info")
        assert issue.message == ""
        assert issue.severity == "info"


class TestAIAnalysisResult:
    """Test suite for AIAnalysisResult dataclass."""

    def test_analysis_result_creation(self):
        """Test creating AIAnalysisResult with summary and issues."""
        issues = [
            AnalysisIssue(message="Issue 1", severity="warning"),
            AnalysisIssue(message="Issue 2", severity="error")
        ]
        result = AIAnalysisResult(summary="Found 2 issues", issues=issues)
        assert result.summary == "Found 2 issues"
        assert len(result.issues) == 2

    def test_analysis_result_empty_issues(self):
        """Test AIAnalysisResult with no issues."""
        result = AIAnalysisResult(summary="Code looks good", issues=[])
        assert result.summary == "Code looks good"
        assert len(result.issues) == 0

    def test_analysis_result_single_issue(self):
        """Test AIAnalysisResult with single issue."""
        issue = AnalysisIssue(message="Single problem", severity="info")
        result = AIAnalysisResult(summary="Found 1 issue", issues=[issue])
        assert len(result.issues) == 1
        assert result.issues[0].message == "Single problem"

    def test_analysis_result_multiple_issues(self):
        """Test AIAnalysisResult with multiple issues of different severities."""
        issues = [
            AnalysisIssue(message="Info message", severity="info"),
            AnalysisIssue(message="Warning message", severity="warning"),
            AnalysisIssue(message="Error message", severity="error")
        ]
        result = AIAnalysisResult(summary="Analysis complete", issues=issues)
        assert len(result.issues) == 3
        assert result.issues[0].severity == "info"
        assert result.issues[1].severity == "warning"
        assert result.issues[2].severity == "error"

    def test_analysis_result_access_issues(self):
        """Test accessing individual issues in result."""
        issues = [
            AnalysisIssue(message="First", severity="error"),
            AnalysisIssue(message="Second", severity="warning")
        ]
        result = AIAnalysisResult(summary="Test", issues=issues)
        assert result.issues[0].message == "First"
        assert result.issues[1].message == "Second"

    def test_analysis_result_with_empty_summary(self):
        """Test AIAnalysisResult with empty summary."""
        result = AIAnalysisResult(summary="", issues=[])
        assert result.summary == ""

    def test_analysis_result_issue_count(self):
        """Test counting issues in result."""
        issues = [AnalysisIssue(message=f"Issue {i}", severity="info") for i in range(5)]
        result = AIAnalysisResult(summary="5 issues found", issues=issues)
        assert len(result.issues) == 5

    def test_analysis_result_filter_error_issues(self):
        """Test filtering error issues from result."""
        issues = [
            AnalysisIssue(message="Info", severity="info"),
            AnalysisIssue(message="Error 1", severity="error"),
            AnalysisIssue(message="Warning", severity="warning"),
            AnalysisIssue(message="Error 2", severity="error")
        ]
        result = AIAnalysisResult(summary="Test", issues=issues)
        error_issues = [i for i in result.issues if i.severity == "error"]
        assert len(error_issues) == 2

    def test_analysis_result_filter_warning_issues(self):
        """Test filtering warning issues from result."""
        issues = [
            AnalysisIssue(message="Info", severity="info"),
            AnalysisIssue(message="Warning 1", severity="warning"),
            AnalysisIssue(message="Warning 2", severity="warning"),
            AnalysisIssue(message="Error", severity="error")
        ]
        result = AIAnalysisResult(summary="Test", issues=issues)
        warning_issues = [i for i in result.issues if i.severity == "warning"]
        assert len(warning_issues) == 2
