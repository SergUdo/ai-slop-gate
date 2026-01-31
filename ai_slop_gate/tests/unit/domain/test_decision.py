import pytest
from ai_slop_gate.domain.decision import Decision, DecisionMode, Annotation


class TestDecisionMode:
    """Test suite for DecisionMode enum."""

    def test_decision_mode_allow(self):
        """Test ALLOW mode value."""
        assert DecisionMode.ALLOW == "allow"

    def test_decision_mode_advisory(self):
        """Test ADVISORY mode value."""
        assert DecisionMode.ADVISORY == "advisory"

    def test_decision_mode_blocking(self):
        """Test BLOCKING mode value."""
        assert DecisionMode.BLOCKING == "blocking"

    def test_decision_mode_string_comparison(self):
        """Test comparing mode with string."""
        mode = DecisionMode.BLOCKING
        assert mode == "blocking"

    def test_decision_mode_is_enum(self):
        """Test that DecisionMode is an enum."""
        assert isinstance(DecisionMode.ALLOW, DecisionMode)
        assert isinstance(DecisionMode.ADVISORY, DecisionMode)
        assert isinstance(DecisionMode.BLOCKING, DecisionMode)


class TestAnnotation:
    """Test suite for Annotation dataclass."""

    def test_annotation_creation(self):
        """Test creating Annotation with all required fields."""
        ann = Annotation(
            file="app.py",
            line=42,
            message="Issue found",
            level="error"
        )
        
        assert ann.file == "app.py"
        assert ann.line == 42
        assert ann.message == "Issue found"
        assert ann.level == "error"

    def test_annotation_warning_level(self):
        """Test Annotation with warning level."""
        ann = Annotation(
            file="app.py",
            line=10,
            message="Warning",
            level="warning"
        )
        
        assert ann.level == "warning"

    def test_annotation_immutable(self):
        """Test that Annotation is immutable (frozen)."""
        ann = Annotation(
            file="app.py",
            line=42,
            message="Issue",
            level="error"
        )
        
        with pytest.raises(AttributeError):
            ann.file = "other.py"

    def test_annotation_with_absolute_path(self):
        """Test Annotation with absolute file path."""
        ann = Annotation(
            file="/home/user/project/app.py",
            line=42,
            message="Issue",
            level="error"
        )
        
        assert ann.file == "/home/user/project/app.py"

    def test_annotation_with_relative_path(self):
        """Test Annotation with relative file path."""
        ann = Annotation(
            file="src/app.py",
            line=42,
            message="Issue",
            level="error"
        )
        
        assert ann.file == "src/app.py"

    def test_annotation_line_numbers(self):
        """Test Annotation with different line numbers."""
        lines = [1, 10, 100, 1000]
        
        for line_num in lines:
            ann = Annotation(
                file="app.py",
                line=line_num,
                message="Issue",
                level="error"
            )
            assert ann.line == line_num

    def test_annotation_empty_message(self):
        """Test Annotation with empty message."""
        ann = Annotation(
            file="app.py",
            line=42,
            message="",
            level="warning"
        )
        
        assert ann.message == ""


class TestDecision:
    """Test suite for Decision dataclass."""

    def test_decision_minimal(self):
        """Test creating Decision with minimal required fields."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=["All checks passed"]
        )
        
        assert decision.mode == DecisionMode.ALLOW
        assert decision.reasons == ["All checks passed"]
        assert decision.annotations is None

    def test_decision_advisory_mode(self):
        """Test Decision with advisory mode."""
        decision = Decision(
            mode=DecisionMode.ADVISORY,
            reasons=["Some warnings found"]
        )
        
        assert decision.mode == DecisionMode.ADVISORY

    def test_decision_blocking_mode(self):
        """Test Decision with blocking mode."""
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Critical issue found"]
        )
        
        assert decision.mode == DecisionMode.BLOCKING

    def test_decision_with_single_reason(self):
        """Test Decision with single reason."""
        decision = Decision(
            mode=DecisionMode.ADVISORY,
            reasons=["Single reason"]
        )
        
        assert len(decision.reasons) == 1
        assert decision.reasons[0] == "Single reason"

    def test_decision_with_multiple_reasons(self):
        """Test Decision with multiple reasons."""
        reasons = [
            "Missing security headers",
            "Weak password policy",
            "Unencrypted data transmission"
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=reasons
        )
        
        assert len(decision.reasons) == 3
        assert decision.reasons == reasons

    def test_decision_with_empty_reasons_list(self):
        """Test Decision with empty reasons list."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=[]
        )
        
        assert decision.reasons == []

    def test_decision_with_single_annotation(self):
        """Test Decision with single annotation."""
        ann = Annotation(
            file="app.py",
            line=42,
            message="Issue found",
            level="error"
        )
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Issue found"],
            annotations=[ann]
        )
        
        assert len(decision.annotations) == 1
        assert decision.annotations[0] == ann

    def test_decision_with_multiple_annotations(self):
        """Test Decision with multiple annotations."""
        anns = [
            Annotation(file="app.py", line=42, message="Issue 1", level="error"),
            Annotation(file="api.py", line=10, message="Issue 2", level="warning"),
            Annotation(file="utils.py", line=55, message="Issue 3", level="error")
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=["Multiple issues found"],
            annotations=anns
        )
        
        assert len(decision.annotations) == 3
        assert decision.annotations == anns

    def test_decision_immutable(self):
        """Test that Decision is immutable (frozen)."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=["OK"]
        )
        
        with pytest.raises(AttributeError):
            decision.mode = DecisionMode.BLOCKING

    def test_decision_annotations_none(self):
        """Test Decision with explicitly None annotations."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=["OK"],
            annotations=None
        )
        
        assert decision.annotations is None

    def test_decision_annotations_empty_list(self):
        """Test Decision with empty annotations list."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=["OK"],
            annotations=[]
        )
        
        assert decision.annotations == []
        assert len(decision.annotations) == 0

    def test_decision_all_modes(self):
        """Test creating Decision with each mode."""
        modes_and_reasons = [
            (DecisionMode.ALLOW, ["All checks passed"]),
            (DecisionMode.ADVISORY, ["Some warnings found"]),
            (DecisionMode.BLOCKING, ["Critical issue found"])
        ]
        
        for mode, reasons in modes_and_reasons:
            decision = Decision(mode=mode, reasons=reasons)
            assert decision.mode == mode
            assert decision.reasons == reasons

    def test_decision_with_detailed_annotations(self):
        """Test Decision with fully populated annotations."""
        anns = [
            Annotation(
                file="src/auth/login.py",
                line=89,
                message="SQL injection vulnerability: unsanitized user input",
                level="error"
            ),
            Annotation(
                file="src/config.py",
                line=15,
                message="Hardcoded API key detected",
                level="error"
            )
        ]
        reasons = [
            "SQL injection vulnerability found",
            "Hardcoded credentials detected"
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=reasons,
            annotations=anns
        )
        
        assert decision.mode == DecisionMode.BLOCKING
        assert len(decision.reasons) == 2
        assert len(decision.annotations) == 2
        assert decision.annotations[0].line == 89
        assert decision.annotations[1].message == "Hardcoded API key detected"

    def test_decision_long_reason_messages(self):
        """Test Decision with long reason messages."""
        long_reason = "This is a very long reason explaining in detail what the issue is and why it was detected as a security concern that requires immediate attention."
        decision = Decision(
            mode=DecisionMode.ADVISORY,
            reasons=[long_reason]
        )
        
        assert decision.reasons[0] == long_reason

    def test_decision_reason_messages_with_special_chars(self):
        """Test Decision with special characters in reasons."""
        reasons = [
            "Issue: 'SQL injection' in user@example.com",
            "Config error: path = /etc/passwd (should be /var/...)",
            "Warning: <script> tags detected"
        ]
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=reasons
        )
        
        assert decision.reasons == reasons
