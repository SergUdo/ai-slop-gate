"""Unit tests for reporter modules."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from ai_slop_gate.reporters.base import Reporter, BaseReporter


class TestReporter:
    """Test suite for abstract Reporter class."""

    def test_reporter_is_abstract(self):
        """Test that Reporter is an abstract class."""
        with pytest.raises(TypeError):
            Reporter()

    def test_reporter_requires_report_method(self):
        """Test that Reporter requires report method implementation."""
        class IncompleteReporter(Reporter):
            pass
        
        with pytest.raises(TypeError):
            IncompleteReporter()

    def test_reporter_can_be_subclassed(self):
        """Test that Reporter can be properly subclassed."""
        class CustomReporter(Reporter):
            def report(self, report):
                pass
        
        reporter = CustomReporter()
        assert isinstance(reporter, Reporter)

    def test_reporter_report_method_signature(self):
        """Test that report method has correct signature."""
        class TestReporter(Reporter):
            def report(self, report):
                self.last_report = report
        
        reporter = TestReporter()
        mock_report = Mock()
        reporter.report(mock_report)
        assert reporter.last_report == mock_report


class TestBaseReporter:
    """Test suite for BaseReporter class."""

    def test_base_reporter_initialization(self):
        """Test BaseReporter can be instantiated."""
        reporter = BaseReporter()
        assert reporter is not None

    def test_base_reporter_report_not_implemented(self):
        """Test BaseReporter.report raises NotImplementedError."""
        reporter = BaseReporter()
        with pytest.raises(NotImplementedError):
            reporter.report(Mock())

    def test_base_reporter_report_with_none(self):
        """Test BaseReporter.report with None input."""
        reporter = BaseReporter()
        with pytest.raises(NotImplementedError):
            reporter.report(None)

    def test_base_reporter_subclass_can_override(self):
        """Test that BaseReporter can be subclassed with override."""
        class CustomReporter(BaseReporter):
            def report(self, report):
                self.reported = report
        
        reporter = CustomReporter()
        mock_report = Mock()
        reporter.report(mock_report)
        assert reporter.reported == mock_report

    def test_base_reporter_multiple_instances(self):
        """Test multiple BaseReporter instances are independent."""
        reporter1 = BaseReporter()
        reporter2 = BaseReporter()
        assert reporter1 is not reporter2

    def test_base_reporter_has_report_method(self):
        """Test BaseReporter has report method."""
        reporter = BaseReporter()
        assert hasattr(reporter, 'report')
        assert callable(reporter.report)
