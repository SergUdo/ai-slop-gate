import pytest
from ai_slop_gate.domain.observation import Observation, Location, Severity


class TestLocation:
    """Test suite for Location dataclass."""

    def test_location_creation_with_file_only(self):
        """Test creating Location with just file path."""
        loc = Location(file="test.py")
        
        assert loc.file == "test.py"
        assert loc.line is None

    def test_location_creation_with_file_and_line(self):
        """Test creating Location with file and line number."""
        loc = Location(file="test.py", line=42)
        
        assert loc.file == "test.py"
        assert loc.line == 42

    def test_location_immutable(self):
        """Test that Location is immutable (frozen)."""
        loc = Location(file="test.py")
        
        with pytest.raises(AttributeError):
            loc.file = "other.py"

    def test_location_with_absolute_path(self):
        """Test Location with absolute file path."""
        loc = Location(file="/home/user/project/test.py")
        
        assert loc.file == "/home/user/project/test.py"

    def test_location_with_relative_path(self):
        """Test Location with relative file path."""
        loc = Location(file="src/module/test.py")
        
        assert loc.file == "src/module/test.py"


class TestSeverity:
    """Test suite for Severity enum."""

    def test_severity_low(self):
        """Test LOW severity value."""
        assert Severity.LOW == "low"

    def test_severity_medium(self):
        """Test MEDIUM severity value."""
        assert Severity.MEDIUM == "medium"

    def test_severity_high(self):
        """Test HIGH severity value."""
        assert Severity.HIGH == "high"

    def test_severity_string_comparison(self):
        """Test comparing severity with string."""
        sev = Severity.HIGH
        assert sev == "high"

    def test_severity_is_enum(self):
        """Test that Severity is an enum."""
        assert isinstance(Severity.LOW, Severity)
        assert isinstance(Severity.MEDIUM, Severity)
        assert isinstance(Severity.HIGH, Severity)


class TestObservation:
    """Test suite for Observation dataclass."""

    def test_observation_minimal(self):
        """Test creating Observation with minimal required fields."""
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected"
        )
        
        assert obs.category == "security"
        assert obs.signal == "sql_injection"
        assert obs.confidence == 0.9
        assert obs.message == "SQL injection detected"
        assert obs.severity is None
        assert obs.evidence is None
        assert obs.rule_id is None
        assert obs.location is None

    def test_observation_with_severity(self):
        """Test creating Observation with severity."""
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            severity="high"
        )
        
        assert obs.severity == "high"

    def test_observation_with_severity_enum(self):
        """Test creating Observation with Severity enum."""
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            severity=Severity.HIGH
        )
        
        assert obs.severity == Severity.HIGH

    def test_observation_with_evidence(self):
        """Test creating Observation with evidence dict."""
        evidence = {"file": "app.py", "line": 42}
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            evidence=evidence
        )
        
        assert obs.evidence == evidence
        assert obs.evidence["file"] == "app.py"
        assert obs.evidence["line"] == 42

    def test_observation_with_rule_id(self):
        """Test creating Observation with rule_id."""
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            rule_id="rule-001"
        )
        
        assert obs.rule_id == "rule-001"

    def test_observation_with_location(self):
        """Test creating Observation with Location."""
        loc = Location(file="app.py", line=42)
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            location=loc
        )
        
        assert obs.location == loc
        assert obs.location.file == "app.py"
        assert obs.location.line == 42

    def test_observation_all_fields(self):
        """Test creating Observation with all fields."""
        loc = Location(file="app.py", line=42)
        evidence = {"context": "user input"}
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.95,
            message="SQL injection detected",
            severity=Severity.HIGH,
            evidence=evidence,
            rule_id="rule-001",
            location=loc
        )
        
        assert obs.category == "security"
        assert obs.signal == "sql_injection"
        assert obs.confidence == 0.95
        assert obs.message == "SQL injection detected"
        assert obs.severity == Severity.HIGH
        assert obs.evidence == evidence
        assert obs.rule_id == "rule-001"
        assert obs.location == loc

    def test_observation_immutable(self):
        """Test that Observation is immutable (frozen)."""
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected"
        )
        
        with pytest.raises(AttributeError):
            obs.category = "other"

    def test_observation_confidence_range(self):
        """Test Observation with different confidence values."""
        obs_low = Observation(
            category="security",
            signal="issue",
            confidence=0.1,
            message="Low confidence issue"
        )
        
        obs_high = Observation(
            category="security",
            signal="issue",
            confidence=0.99,
            message="High confidence issue"
        )
        
        assert obs_low.confidence == 0.1
        assert obs_high.confidence == 0.99

    def test_observation_multiple_evidence_keys(self):
        """Test Observation with multiple evidence entries."""
        evidence = {
            "file": "app.py",
            "line": 42,
            "function": "process_data",
            "snippet": "query = f'SELECT * FROM users WHERE id = {user_id}'"
        }
        obs = Observation(
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            evidence=evidence
        )
        
        assert len(obs.evidence) == 4
        assert obs.evidence["function"] == "process_data"

    def test_observation_empty_message(self):
        """Test Observation with empty message."""
        obs = Observation(
            category="security",
            signal="issue",
            confidence=0.5,
            message=""
        )
        
        assert obs.message == ""

    def test_observation_category_types(self):
        """Test Observation with different category values."""
        categories = ["security", "performance", "maintainability", "compliance"]
        
        for cat in categories:
            obs = Observation(
                category=cat,
                signal="test_signal",
                confidence=0.5,
                message="Test message"
            )
            assert obs.category == cat

    def test_observation_confidence_zero(self):
        """Test Observation with zero confidence."""
        obs = Observation(
            category="security",
            signal="issue",
            confidence=0.0,
            message="No confidence"
        )
        
        assert obs.confidence == 0.0

    def test_observation_confidence_one(self):
        """Test Observation with full confidence."""
        obs = Observation(
            category="security",
            signal="issue",
            confidence=1.0,
            message="Full confidence"
        )
        
        assert obs.confidence == 1.0

    def test_observation_severity_none(self):
        """Test Observation explicitly with None severity."""
        obs = Observation(
            category="security",
            signal="issue",
            confidence=0.5,
            message="Test",
            severity=None
        )
        
        assert obs.severity is None

    def test_observation_legacy_location_field(self):
        """Test backward compatibility with legacy location field."""
        loc = Location(file="legacy.py", line=10)
        obs = Observation(
            category="security",
            signal="issue",
            confidence=0.5,
            message="Legacy format",
            location=loc
        )
        
        # Should support legacy location access
        assert obs.location.file == "legacy.py"
        assert obs.location.line == 10
