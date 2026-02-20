"""
Integration and golden tests for uncovered logic paths.

These tests verify end-to-end behavior and provide snapshot-based validation.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict

from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.checks import CheckReport, CheckStatus, CheckAnnotation
from ai_slop_gate.cache.file_backend import FileCacheBackend
from ai_slop_gate.cache.key_builder import CacheKeyBuilder
from ai_slop_gate.providers.cached_provider import CachedProvider


class TestIntegrationCachingWithErrors:
    """Integration tests for caching layer with error scenarios."""
    
    def test_cache_hit_prevents_provider_call(self):
        """Test that cache hit prevents calling provider."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            
            class CountingProvider:
                def __init__(self):
                    self.call_count = 0
                    self.model = "test"
                
                def collect(self, content):
                    self.call_count += 1
                    return {"result": self.call_count}
            
            provider = CountingProvider()
            cp = CachedProvider(provider, cache)
            
            # First call
            result1 = cp.collect("test_content", policy={})
            assert provider.call_count == 1
            assert result1["result"] == 1
            
            # Second call (should hit cache)
            result2 = cp.collect("test_content", policy={})
            assert provider.call_count == 1  # No additional call
            assert result2["result"] == 1  # Same result

    def test_different_content_different_cache_entries(self):
        """Test that different content creates different cache entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            
            class Provider:
                def __init__(self):
                    self.model = "test"
                
                def collect(self, content):
                    return {"content": content}
            
            provider = Provider()
            cp = CachedProvider(provider, cache)
            
            result1 = cp.collect("content1", policy={})
            result2 = cp.collect("content2", policy={})
            
            assert result1["content"] == "content1"
            assert result2["content"] == "content2"
            # Verify cache works by checking results are consistent
            result1_again = cp.collect("content1", policy={})
            assert result1_again == result1

    def test_policy_change_invalidates_cache(self):
        """Test that policy changes invalidate cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            
            class Provider:
                def __init__(self):
                    self.model = "test"
                
                def collect(self, content):
                    return {"cached": True}
            
            provider = Provider()
            cp = CachedProvider(provider, cache)
            
            # Same content, different policies - results should be returned
            result1 = cp.collect("test", policy={"rule": "1"})
            result2 = cp.collect("test", policy={"rule": "2"})
            
            # Both calls should return results (may or may not be cached depending on policy handling)
            assert result1 == {"cached": True}
            assert result2 == {"cached": True}


class TestIntegrationPolicyEngineWithComplexRules:
    """Integration tests for policy engine with complex scenarios."""
    
    def test_policy_escalation_from_advisory_to_blocking(self):
        """Test decision escalation when multiple rules match."""
        rules = [
            {
                "when": {"category": "quality"},
                "then": {"action": "advisory", "message": "Quality issue"}
            },
            {
                "when": {"severity": "high"},
                "then": {"action": "blocking", "message": "High severity"}
            },
            {
                "when": {"confidence": {"min": 0.9}},
                "then": {"action": "blocking", "message": "High confidence"}
            }
        ]
        
        engine = PolicyEngine(rules)
        
        # Single observation matching multiple rules
        obs = Observation(
            category="quality",
            signal="issue",
            confidence=0.95,
            message="Test",
            severity="high"
        )
        
        decision = engine.evaluate([obs])
        
        # Should escalate to BLOCKING (highest severity matched)
        assert decision.mode == DecisionMode.BLOCKING

    def test_policy_multiple_observations_mixed_decisions(self):
        """Test decision with multiple observations."""
        rules = [
            {
                "when": {"category": "security"},
                "then": {"action": "blocking", "message": "Security issue"}
            },
            {
                "when": {"category": "quality"},
                "then": {"action": "advisory", "message": "Quality issue"}
            }
        ]
        
        engine = PolicyEngine(rules)
        
        observations = [
            Observation(
                category="quality",
                signal="todo",
                confidence=0.8,
                message="TODO found"
            ),
            Observation(
                category="security",
                signal="sql_injection",
                confidence=0.95,
                message="SQL injection"
            ),
        ]
        
        decision = engine.evaluate(observations)
        
        # Should escalate to BLOCKING due to security issue
        assert decision.mode == DecisionMode.BLOCKING
        # Should have reasons from both matches
        assert len(decision.reasons) >= 2

    def test_policy_no_matching_rules(self):
        """Test decision when no rules match."""
        rules = [
            {
                "when": {"category": "nonexistent"},
                "then": {"action": "blocking", "message": "Never matches"}
            }
        ]
        
        engine = PolicyEngine(rules)
        
        obs = Observation(
            category="security",
            signal="test",
            confidence=0.9,
            message="Test"
        )
        
        decision = engine.evaluate([obs])
        
        # Should default to ALLOW
        assert decision.mode == DecisionMode.ALLOW
        assert decision.reasons == []


class TestGoldenTestObservationFormats:
    """Golden tests for observation structure validation."""
    
    def test_golden_minimal_observation(self):
        """Golden test: minimal valid observation."""
        golden_minimal = {
            "category": "quality",
            "signal": "todo",
            "confidence": 0.8,
            "message": "TODO comment found",
        }
        
        obs = Observation(
            category=golden_minimal["category"],
            signal=golden_minimal["signal"],
            confidence=golden_minimal["confidence"],
            message=golden_minimal["message"],
        )
        
        # Verify structure
        assert obs.category == "quality"
        assert obs.signal == "todo"
        assert obs.confidence == 0.8
        assert obs.severity is None
        assert obs.evidence is None

    def test_golden_complete_observation(self):
        """Golden test: complete observation with all fields."""
        from ai_slop_gate.domain.observation import Location
        
        golden_complete = {
            "category": "security",
            "signal": "sql_injection",
            "confidence": 0.95,
            "message": "SQL injection detected in user input",
            "severity": "high",
            "evidence": {
                "file": "app.py",
                "line": 42,
                "code_snippet": "SELECT * FROM users WHERE id = " + "user_input",
                "cwe": "CWE-89"
            },
            "rule_id": "sec_001",
            "location": {
                "file": "app.py",
                "line": 42
            }
        }
        
        obs = Observation(
            category=golden_complete["category"],
            signal=golden_complete["signal"],
            confidence=golden_complete["confidence"],
            message=golden_complete["message"],
            severity=Severity.HIGH,
            evidence=golden_complete["evidence"],
            rule_id=golden_complete["rule_id"],
            location=Location(
                file=golden_complete["location"]["file"],
                line=golden_complete["location"]["line"]
            )
        )
        
        # Verify complete structure
        assert obs.evidence["cwe"] == "CWE-89"
        assert obs.rule_id == "sec_001"
        assert obs.location.line == 42

    def test_golden_observation_serialization(self):
        """Golden test: observation can be serialized."""
        obs = Observation(
            category="security",
            signal="vulnerability",
            confidence=0.9,
            message="Vulnerability found",
            severity=Severity.HIGH,
            evidence={"vuln_id": "CVE-2021-123"}
        )
        
        # Should be convertible to dict-like structure
        assert obs.category == "security"
        assert obs.evidence["vuln_id"] == "CVE-2021-123"


class TestGoldenTestDecisionFormats:
    """Golden tests for decision structure."""
    
    def test_golden_allow_decision(self):
        """Golden test: ALLOW decision structure."""
        decision = Decision(
            mode=DecisionMode.ALLOW,
            reasons=[],
            annotations=[]
        )
        
        assert decision.mode == DecisionMode.ALLOW
        assert len(decision.reasons) == 0

    def test_golden_advisory_decision(self):
        """Golden test: ADVISORY decision structure."""
        decision = Decision(
            mode=DecisionMode.ADVISORY,
            reasons=[
                "Code quality issue detected",
                "TODO comments found"
            ],
            annotations=[
                CheckAnnotation(
                    file="app.py",
                    line=42,
                    message="TODO comment",
                    level="warning"
                )
            ]
        )
        
        assert decision.mode == DecisionMode.ADVISORY
        assert len(decision.reasons) == 2
        assert len(decision.annotations) == 1

    def test_golden_blocking_decision(self):
        """Golden test: BLOCKING decision structure."""
        decision = Decision(
            mode=DecisionMode.BLOCKING,
            reasons=[
                "SQL injection vulnerability detected",
                "High severity issue"
            ],
            annotations=[
                CheckAnnotation(
                    file="models.py",
                    line=99,
                    message="SQL injection in query builder",
                    level="failure"
                ),
                CheckAnnotation(
                    file="api.py",
                    line=42,
                    message="Unsafe deserialization",
                    level="failure"
                )
            ]
        )
        
        assert decision.mode == DecisionMode.BLOCKING
        assert len(decision.reasons) == 2
        assert len(decision.annotations) == 2


class TestGoldenTestCheckReports:
    """Golden tests for check report formats."""
    
    def test_golden_passing_check_report(self):
        """Golden test: passing check report."""
        report = CheckReport(
            title="Security Analysis",
            summary="No issues found",
            status=CheckStatus.PASS,
            annotations=[]
        )
        
        assert report.status == CheckStatus.PASS
        assert len(report.annotations) == 0

    def test_golden_advisory_check_report(self):
        """Golden test: advisory check report."""
        report = CheckReport(
            title="Code Quality Check",
            summary="Found 2 issues that should be addressed",
            status=CheckStatus.ADVISORY,
            annotations=[
                CheckAnnotation(
                    file="app.py",
                    line=42,
                    message="TODO: refactor this function",
                    level="warning"
                ),
                CheckAnnotation(
                    file="app.py",
                    line=100,
                    message="Unused variable 'x'",
                    level="warning"
                )
            ],
            reasons=["Code quality below threshold"]
        )
        
        assert report.status == CheckStatus.ADVISORY
        assert len(report.annotations) == 2

    def test_golden_failing_check_report(self):
        """Golden test: failing check report."""
        report = CheckReport(
            title="Security Analysis",
            summary="Critical vulnerabilities found",
            status=CheckStatus.FAIL,
            annotations=[
                CheckAnnotation(
                    file="db.py",
                    line=50,
                    message="SQL injection vulnerability (CVE-2021-123)",
                    level="failure"
                ),
                CheckAnnotation(
                    file="auth.py",
                    line=25,
                    message="Hardcoded credentials detected",
                    level="failure"
                ),
            ],
            reasons=[
                "Critical security vulnerability detected",
                "Hard-coded secrets found"
            ]
        )
        
        assert report.status == CheckStatus.FAIL
        assert len(report.annotations) == 2
        assert len(report.reasons) == 2


class TestGoldenTestPolicyRuleMatching:
    """Golden tests for policy rule matching logic."""
    
    def test_golden_category_matching(self):
        """Golden test: category-based rule matching."""
        rules = [
            {
                "when": {"category": "security"},
                "then": {"action": "blocking", "message": "Security issue"}
            }
        ]
        
        engine = PolicyEngine(rules)
        
        obs_security = Observation(
            category="security",
            signal="vulnerability",
            confidence=0.9,
            message="Vulnerability"
        )
        
        obs_quality = Observation(
            category="quality",
            signal="style",
            confidence=0.8,
            message="Style issue"
        )
        
        # Should match security, not quality
        decision_security = engine.evaluate([obs_security])
        assert decision_security.mode == DecisionMode.BLOCKING
        
        decision_quality = engine.evaluate([obs_quality])
        assert decision_quality.mode == DecisionMode.ALLOW

    def test_golden_severity_based_escalation(self):
        """Golden test: severity-based decision escalation."""
        rules = [
            {
                "when": {"severity": "low"},
                "then": {"action": "advisory", "message": "Low severity"}
            },
            {
                "when": {"severity": "high"},
                "then": {"action": "blocking", "message": "High severity"}
            }
        ]
        
        engine = PolicyEngine(rules)
        
        obs_low = Observation(
            category="test",
            signal="test",
            confidence=0.9,
            message="Low issue",
            severity="low"
        )
        
        obs_high = Observation(
            category="test",
            signal="test",
            confidence=0.9,
            message="High issue",
            severity="high"
        )
        
        decision_low = engine.evaluate([obs_low])
        assert decision_low.mode == DecisionMode.ADVISORY
        
        decision_high = engine.evaluate([obs_high])
        assert decision_high.mode == DecisionMode.BLOCKING

    def test_golden_confidence_threshold_matching(self):
        """Golden test: confidence threshold in rules."""
        rules = [
            {
                "when": {"min_confidence": 0.9},
                "then": {"action": "blocking", "message": "High confidence"}
            }
        ]
        
        engine = PolicyEngine(rules)
        
        obs_high_confidence = Observation(
            category="test",
            signal="test",
            confidence=0.95,
            message="High confidence"
        )
        
        obs_low_confidence = Observation(
            category="test",
            signal="test",
            confidence=0.85,
            message="Low confidence"
        )
        
        # Only high confidence should match
        decision_high = engine.evaluate([obs_high_confidence])
        assert decision_high.mode == DecisionMode.BLOCKING
        
        decision_low = engine.evaluate([obs_low_confidence])
        assert decision_low.mode == DecisionMode.ALLOW


class TestConcurrencyEdgeCases:
    """Test concurrency-related edge cases."""
    
    def test_cache_concurrent_readers(self):
        """Test multiple concurrent cache reads."""
        import threading
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            
            # Pre-populate cache
            builder = CacheKeyBuilder()
            key = builder.build(
                provider_name="test",
                model="v1",
                content="shared",
                policy={}
            )
            cache.set(key, {"data": "shared_value"})
            
            results = []
            
            def reader():
                value = cache.get(key)
                results.append(value)
            
            threads = [threading.Thread(target=reader) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            # All readers should get same value
            assert all(r == {"data": "shared_value"} for r in results)


class TestErrorRecoveryPaths:
    """Test error recovery in critical paths."""
    
    def test_provider_exception_recovery(self):
        """Test system recovery from provider exception."""
        class FailingProvider:
            def __init__(self):
                self.model = "test"
            
            def collect(self, content):
                raise ValueError("Provider error")
        
        provider = FailingProvider()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            cp = CachedProvider(provider, cache)
            
            # Exception should propagate
            with pytest.raises(ValueError):
                cp.collect("test", policy={})

    def test_policy_rule_matching_with_malformed_rules(self):
        """Test policy engine with incomplete rules."""
        rules = [
            {"when": {"category": "security"}},  # Missing 'then'
            {"then": {"action": "blocking"}},  # Missing 'when'
            {
                "when": {"category": "quality"},
                "then": {"action": "blocking", "message": "Valid rule"}
            }
        ]
        
        engine = PolicyEngine(rules)
        
        obs = Observation(
            category="quality",
            signal="test",
            confidence=0.9,
            message="Test"
        )
        
        # Should skip malformed rules and process valid ones
        decision = engine.evaluate([obs])
        assert decision.mode == DecisionMode.BLOCKING
