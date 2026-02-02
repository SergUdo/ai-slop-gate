"""Unit tests for rate_limit_guard module."""
import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from ai_slop_gate.providers.rate_limit_guard import RateLimitGuard


class TestRateLimitGuard:
    """Test suite for RateLimitGuard class."""

    def test_rate_limit_guard_initialization(self):
        """Test RateLimitGuard initialization."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        assert guard.provider == mock_provider
        assert guard.interval_sec == 1.0

    def test_rate_limit_guard_key_from_provider_method(self):
        """Test RateLimitGuard gets key from provider method."""
        mock_provider = Mock()
        mock_provider.rate_limit_key = Mock(return_value="custom_key")
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        key = guard._key()
        assert key == "custom_key"
        mock_provider.rate_limit_key.assert_called_once()

    def test_rate_limit_guard_key_from_provider_name(self):
        """Test RateLimitGuard gets key from provider name."""
        mock_provider = Mock()
        mock_provider.name = "gemini_provider"
        # Don't set rate_limit_key method
        del mock_provider.rate_limit_key
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        key = guard._key()
        assert key == "gemini_provider"

    def test_rate_limit_guard_analyze_first_call(self):
        """Test RateLimitGuard analyze on first call."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        result = guard.analyze("arg1", kwarg1="value1")
        
        assert result == "result"
        mock_provider.analyze.assert_called_once_with("arg1", kwarg1="value1")

    def test_rate_limit_guard_with_zero_interval(self):
        """Test RateLimitGuard with zero interval."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        guard = RateLimitGuard(mock_provider, interval_sec=0)
        result = guard.analyze("test")
        
        assert result == "result"
        mock_provider.analyze.assert_called_once()

    def test_rate_limit_guard_with_negative_interval(self):
        """Test RateLimitGuard with negative interval."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        guard = RateLimitGuard(mock_provider, interval_sec=-1.0)
        result = guard.analyze("test")
        
        assert result == "result"
        mock_provider.analyze.assert_called_once()

    def test_rate_limit_guard_tracks_last_call(self):
        """Test RateLimitGuard tracks last call time."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        guard.analyze("test")
        
        key = guard._key()
        assert key in guard._last_call
        assert isinstance(guard._last_call[key], float)

    def test_rate_limit_guard_multiple_keys(self):
        """Test RateLimitGuard with separate instances tracks separately."""
        mock_provider1 = Mock(spec=['name', 'analyze'])
        mock_provider1.name = "provider1"
        mock_provider1.analyze = Mock(return_value="result1")
        
        mock_provider2 = Mock(spec=['name', 'analyze'])
        mock_provider2.name = "provider2"
        mock_provider2.analyze = Mock(return_value="result2")
        
        guard1 = RateLimitGuard(mock_provider1, interval_sec=1.0)
        guard2 = RateLimitGuard(mock_provider2, interval_sec=1.0)
        
        guard1.analyze("test")
        guard2.analyze("test")
        
        # Each guard tracks its own last_call dict
        assert "provider1" in guard1._last_call
        assert "provider2" in guard2._last_call
        # They have separate tracking
        assert guard1._last_call != guard2._last_call

    def test_rate_limit_guard_passes_args_to_provider(self):
        """Test RateLimitGuard passes arguments to provider."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        guard.analyze("arg1", "arg2", key1="value1", key2="value2")
        
        mock_provider.analyze.assert_called_once_with("arg1", "arg2", key1="value1", key2="value2")

    def test_rate_limit_guard_returns_provider_result(self):
        """Test RateLimitGuard returns provider's result."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        expected_result = {"status": "ok", "data": [1, 2, 3]}
        mock_provider.analyze = Mock(return_value=expected_result)
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        result = guard.analyze("test")
        
        assert result == expected_result

    def test_rate_limit_guard_with_exception(self):
        """Test RateLimitGuard when provider raises exception."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(side_effect=ValueError("API Error"))
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        
        with pytest.raises(ValueError, match="API Error"):
            guard.analyze("test")

    def test_rate_limit_guard_interval_seconds(self):
        """Test RateLimitGuard with different interval values."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        for interval in [0.1, 0.5, 1.0, 5.0]:
            guard = RateLimitGuard(mock_provider, interval_sec=interval)
            assert guard.interval_sec == interval

    def test_rate_limit_guard_large_interval(self):
        """Test RateLimitGuard with large interval."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        mock_provider.analyze = Mock(return_value="result")
        
        guard = RateLimitGuard(mock_provider, interval_sec=3600)  # 1 hour
        assert guard.interval_sec == 3600
        
        result = guard.analyze("test")
        assert result == "result"

    def test_rate_limit_guard_last_call_dict_initialization(self):
        """Test RateLimitGuard initializes empty last_call dict."""
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        
        guard = RateLimitGuard(mock_provider, interval_sec=1.0)
        assert isinstance(guard._last_call, dict)
        assert len(guard._last_call) == 0
