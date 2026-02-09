import pytest
from ai_slop_gate.domain.observation_factory import make_observation
from ai_slop_gate.domain.observation import Observation, Location


class TestMakeObservation:
    """Test suite for make_observation factory function."""

    def test_make_observation_minimal(self):
        """Test make_observation with minimal required parameters."""
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected"
        )
        
        assert isinstance(obs, Observation)
        # rule_id contains provider, category, and signal
        assert "static" in obs.rule_id
        assert obs.category == "security"
        assert obs.signal == "sql_injection"
        assert obs.confidence == 0.9
        assert obs.message == "SQL injection detected"

    def test_make_observation_with_evidence(self):
        """Test make_observation with evidence."""
        evidence = {"file": "app.py", "line": 42}
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            evidence=evidence
        )
        
        assert obs.evidence == evidence
        assert obs.location is not None
        assert obs.location.file == "app.py"
        assert obs.location.line == 42

    def test_make_observation_with_evidence_no_location(self):
        """Test make_observation with evidence but no file."""
        evidence = {"detail": "some detail"}
        obs = make_observation(
            provider="static",
            category="security",
            signal="issue",
            confidence=0.5,
            message="Issue found",
            evidence=evidence
        )
        
        assert obs.evidence == evidence
        assert obs.location is None

    def test_make_observation_with_rule(self):
        """Test make_observation with custom rule."""
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            rule="custom-rule-001"
        )
        
        assert obs.rule_id == "custom-rule-001"

    def test_make_observation_without_rule(self):
        """Test make_observation generates rule_id from provider/category/signal."""
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected"
        )
        
        # Should auto-generate rule_id
        assert obs.rule_id is not None
        assert "static" in obs.rule_id
        assert "security" in obs.rule_id
        assert "sql_injection" in obs.rule_id

    def test_make_observation_with_severity(self):
        """Test make_observation with custom severity."""
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected",
            severity="high"
        )
        
        assert obs.severity == "high"

    def test_make_observation_without_severity(self):
        """Test make_observation defaults to medium severity."""
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection detected"
        )
        
        assert obs.severity == "medium"

    def test_make_observation_all_parameters(self):
        """Test make_observation with all parameters."""
        evidence = {"file": "app.py", "line": 42, "context": "user input"}
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.95,
            message="SQL injection detected in login form",
            evidence=evidence,
            rule="rule-sql-injection",
            severity="critical"
        )
        
        assert obs.category == "security"
        assert obs.signal == "sql_injection"
        assert obs.confidence == 0.95
        assert obs.message == "SQL injection detected in login form"
        assert obs.evidence == evidence
        assert obs.rule_id == "rule-sql-injection"
        assert obs.severity == "critical"
        assert obs.location.file == "app.py"
        assert obs.location.line == 42

    def test_make_observation_location_creation(self):
        """Test that location is properly created from evidence."""
        evidence = {"file": "/path/to/file.py", "line": 100}
        obs = make_observation(
            provider="test",
            category="test",
            signal="test",
            confidence=0.5,
            message="test",
            evidence=evidence
        )
        
        assert isinstance(obs.location, Location)
        assert obs.location.file == "/path/to/file.py"
        assert obs.location.line == 100

    def test_make_observation_line_defaults_to_1(self):
        """Test that line defaults to 1 when not in evidence."""
        evidence = {"file": "app.py"}
        obs = make_observation(
            provider="static",
            category="security",
            signal="issue",
            confidence=0.5,
            message="Issue found",
            evidence=evidence
        )
        
        assert obs.location.line == 1

    def test_make_observation_empty_evidence(self):
        """Test make_observation with empty evidence dict."""
        obs = make_observation(
            provider="static",
            category="security",
            signal="issue",
            confidence=0.5,
            message="Issue found",
            evidence={}
        )
        
        assert obs.evidence == {}
        assert obs.location is None

    def test_make_observation_none_evidence(self):
        """Test make_observation with None evidence."""
        obs = make_observation(
            provider="static",
            category="security",
            signal="issue",
            confidence=0.5,
            message="Issue found",
            evidence=None
        )
        
        assert obs.evidence == {}
        assert obs.location is None

    def test_make_observation_various_categories(self):
        """Test make_observation with different categories."""
        categories = ["security", "performance", "maintainability", "compliance"]
        
        for category in categories:
            obs = make_observation(
                provider="static",
                category=category,
                signal="test_signal",
                confidence=0.5,
                message="Test message"
            )
            assert obs.category == category

    def test_make_observation_various_severities(self):
        """Test make_observation with different severity levels."""
        severities = ["low", "medium", "high", "critical"]
        
        for severity in severities:
            obs = make_observation(
                provider="static",
                category="security",
                signal="issue",
                confidence=0.5,
                message="Test",
                severity=severity
            )
            assert obs.severity == severity

    def test_make_observation_confidence_values(self):
        """Test make_observation with various confidence values."""
        confidences = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for conf in confidences:
            obs = make_observation(
                provider="static",
                category="security",
                signal="issue",
                confidence=conf,
                message="Test"
            )
            assert obs.confidence == conf

    def test_make_observation_long_message(self):
        """Test make_observation with long message."""
        message = "This is a very long message explaining in detail what the issue is, why it was detected, and what the recommended fix is. It contains comprehensive information for the developer to understand and resolve the issue."
        obs = make_observation(
            provider="static",
            category="security",
            signal="issue",
            confidence=0.5,
            message=message
        )
        
        assert obs.message == message

    def test_make_observation_special_characters_in_message(self):
        """Test make_observation with special characters."""
        message = "SQL injection: user input '<script>' in query 'SELECT * WHERE id = {input}'"
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message=message
        )
        
        assert obs.message == message

    def test_make_observation_complex_evidence(self):
        """Test make_observation with complex evidence structure."""
        evidence = {
            "file": "app.py",
            "line": 42,
            "function": "process_user_data",
            "snippet": "query = f'SELECT * FROM users WHERE id = {user_id}'",
            "context": {
                "user_input": True,
                "sanitized": False
            }
        }
        obs = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.95,
            message="SQL injection detected",
            evidence=evidence,
            severity="critical"
        )
        
        assert obs.evidence == evidence
        assert obs.location.file == "app.py"
        assert obs.location.line == 42

    def test_make_observation_unicode_in_message(self):
        message = "SQL injection detected: user input 'DROP TABLE users;' in query 'SELECT * FROM users WHERE id = {input}'"
        obs = make_observation(
            provider="static",
            category="security",
            signal="issue",
            confidence=0.8,
            message=message
        )
        
        assert obs.message == message

    def test_make_observation_returns_observation_instance(self):
        """Test that make_observation always returns Observation instance."""
        obs = make_observation(
            provider="test",
            category="test",
            signal="test",
            confidence=0.5,
            message="test"
        )
        
        assert isinstance(obs, Observation)
        assert hasattr(obs, 'category')
        assert hasattr(obs, 'signal')
        assert hasattr(obs, 'confidence')
        assert hasattr(obs, 'message')
        assert hasattr(obs, 'severity')
        assert hasattr(obs, 'evidence')
        assert hasattr(obs, 'rule_id')
        assert hasattr(obs, 'location')

    def test_make_observation_evidence_line_as_string(self):
        """Test make_observation converts string line to int."""
        evidence = {"file": "app.py", "line": "42"}
        obs = make_observation(
            provider="static",
            category="security",
            signal="issue",
            confidence=0.5,
            message="Test",
            evidence=evidence
        )
        
        assert obs.location.line == 42
        assert isinstance(obs.location.line, int)

    def test_make_observation_multiple_calls_consistency(self):
        """Test multiple calls produce consistent results."""
        obs1 = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection"
        )
        
        obs2 = make_observation(
            provider="static",
            category="security",
            signal="sql_injection",
            confidence=0.9,
            message="SQL injection"
        )
        
        assert obs1.category == obs2.category
        assert obs1.signal == obs2.signal
        assert obs1.message == obs2.message
        assert obs1.rule_id == obs2.rule_id
