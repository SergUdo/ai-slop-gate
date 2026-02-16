"""
Unit tests for cache system.

Tests verify that:
1. CacheKeyBuilder generates consistent keys
2. FileCacheBackend stores and retrieves data
3. CachedProvider wraps providers correctly
4. Cache hits avoid calling underlying provider
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from ai_slop_gate.cache.key_builder import CacheKeyBuilder
from ai_slop_gate.cache.file_backend import FileCacheBackend
from ai_slop_gate.providers.cached_provider import CachedProvider


class TestCacheKeyBuilder:
    """Test cache key generation."""
    
    def test_deterministic_keys(self):
        """Same input should generate same key."""
        builder = CacheKeyBuilder()
        
        key1 = builder.build(
            provider_name="gemini",
            model="gemini-1.5-pro",
            content="test content",
            policy={"rule": "value"}
        )
        
        key2 = builder.build(
            provider_name="gemini",
            model="gemini-1.5-pro",
            content="test content",
            policy={"rule": "value"}
        )
        
        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex length
    
    def test_different_content_different_keys(self):
        """Different content should generate different keys."""
        builder = CacheKeyBuilder()
        
        key1 = builder.build(
            provider_name="gemini",
            model="gemini-1.5-pro",
            content="content A",
            policy={"rule": "value"}
        )
        
        key2 = builder.build(
            provider_name="gemini",
            model="gemini-1.5-pro",
            content="content B",
            policy={"rule": "value"}
        )
        
        assert key1 != key2
    
    def test_different_policy_different_keys(self):
        """Different policy should generate different keys."""
        builder = CacheKeyBuilder()
        
        key1 = builder.build(
            provider_name="gemini",
            model="gemini-1.5-pro",
            content="test",
            policy={"rule": "A"}
        )
        
        key2 = builder.build(
            provider_name="gemini",
            model="gemini-1.5-pro",
            content="test",
            policy={"rule": "B"}
        )
        
        assert key1 != key2
    
    def test_different_provider_different_keys(self):
        """Different provider should generate different keys."""
        builder = CacheKeyBuilder()
        
        key1 = builder.build(
            provider_name="gemini",
            model="gemini-1.5-pro",
            content="test",
            policy={"rule": "value"}
        )
        
        key2 = builder.build(
            provider_name="groq",
            model="llama-3-70b",
            content="test",
            policy={"rule": "value"}
        )
        
        assert key1 != key2


class TestFileCacheBackend:
    """Test file-based cache storage."""
    
    @pytest.fixture
    def cache_dir(self, tmp_path):
        """Create temporary cache directory."""
        return tmp_path / ".test-cache"
    
    @pytest.fixture
    def cache(self, cache_dir):
        """Create cache backend instance."""
        return FileCacheBackend(root=str(cache_dir))
    
    def test_cache_miss(self, cache):
        """Getting non-existent key returns None."""
        result = cache.get("nonexistent_key")
        assert result is None
    
    def test_cache_set_and_get(self, cache):
        """Set and retrieve data from cache."""
        key = "test_key"
        data = {"result": "success", "count": 42}
        
        cache.set(key, data)
        retrieved = cache.get(key)
        
        assert retrieved == data
    
    def test_cache_persistence(self, cache_dir):
        """Cache persists across instances."""
        cache1 = FileCacheBackend(root=str(cache_dir))
        cache1.set("persistent_key", {"data": "value"})
        
        # Create new instance
        cache2 = FileCacheBackend(root=str(cache_dir))
        retrieved = cache2.get("persistent_key")
        
        assert retrieved == {"data": "value"}
    
    def test_cache_file_format(self, cache, cache_dir):
        """Cache files are valid JSON."""
        key = "format_test"
        data = {"test": "data"}
        
        cache.set(key, data)
        
        # Read file directly
        cache_file = cache_dir / f"{key}.json"
        assert cache_file.exists()
        
        with open(cache_file, 'r') as f:
            file_data = json.load(f)
        
        assert file_data == data
    
    def test_cache_overwrites(self, cache):
        """Setting same key overwrites previous value."""
        key = "overwrite_test"
        
        cache.set(key, {"version": 1})
        cache.set(key, {"version": 2})
        
        result = cache.get(key)
        assert result == {"version": 2}


class TestCachedProvider:
    """Test provider caching wrapper."""
    
    @pytest.fixture
    def mock_provider(self):
        """Create mock provider."""
        provider = Mock()
        provider.__class__.__name__ = "MockProvider"
        provider.model = "mock-model-1"
        return provider
    
    @pytest.fixture
    def mock_cache(self):
        """Create mock cache backend."""
        return Mock()
    
    @pytest.fixture
    def cached_provider(self, mock_provider, mock_cache):
        """Create cached provider instance."""
        return CachedProvider(
            provider=mock_provider,
            cache=mock_cache
        )
    
    def test_cache_miss_calls_provider(self, cached_provider, mock_provider, mock_cache):
        """Cache miss should call underlying provider."""
        mock_cache.get.return_value = None
        mock_provider.collect.return_value = {"result": "from_provider"}
        
        result = cached_provider.collect(
            content="test content",
            policy={"rule": "value"}
        )
        
        # Provider should be called
        mock_provider.collect.assert_called_once_with("test content")
        
        # Result should be cached
        mock_cache.set.assert_called_once()
        
        # Result should be from provider
        assert result == {"result": "from_provider"}
    
    def test_cache_hit_skips_provider(self, cached_provider, mock_provider, mock_cache):
        """Cache hit should NOT call underlying provider."""
        cached_data = {"result": "from_cache"}
        mock_cache.get.return_value = cached_data
        
        result = cached_provider.collect(
            content="test content",
            policy={"rule": "value"}
        )
        
        # Provider should NOT be called
        mock_provider.collect.assert_not_called()
        
        # Cache should not be written (already exists)
        mock_cache.set.assert_not_called()
        
        # Result should be from cache
        assert result == cached_data
    
    def test_cache_key_includes_all_parameters(self, cached_provider, mock_cache):
        """Cache key should include provider, model, content, and policy."""
        mock_cache.get.return_value = None
        
        cached_provider.collect(
            content="test content",
            policy={"rule": "value"}
        )
        
        # Check that cache.get was called with a key
        assert mock_cache.get.call_count == 1
        cache_key = mock_cache.get.call_args[0][0]
        
        # Key should be a hash (64 chars for SHA256)
        assert isinstance(cache_key, str)
        assert len(cache_key) == 64
    
    def test_different_content_different_cache_keys(self, cached_provider, mock_cache):
        """Different content should use different cache keys."""
        mock_cache.get.return_value = None
        
        cached_provider.collect(content="content A", policy={})
        key1 = mock_cache.get.call_args[0][0]
        
        cached_provider.collect(content="content B", policy={})
        key2 = mock_cache.get.call_args[0][0]
        
        assert key1 != key2


class TestCacheIntegration:
    """Integration tests for complete cache flow."""
    
    def test_end_to_end_cache_flow(self, tmp_path):
        """Test complete cache flow with real components."""
        cache_dir = tmp_path / ".cache"
        cache_backend = FileCacheBackend(root=str(cache_dir))
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TestProvider"
        mock_provider.model = "test-model"
        mock_provider.collect.return_value = {
            "observations": [
                {"signal": "test", "message": "test message"}
            ]
        }
        
        cached_provider = CachedProvider(
            provider=mock_provider,
            cache=cache_backend
        )
        
        content = "test content"
        policy = {"rule": "value"}
        
        # First call - cache miss
        result1 = cached_provider.collect(content, policy)
        assert mock_provider.collect.call_count == 1
        
        # Second call - cache hit
        result2 = cached_provider.collect(content, policy)
        assert mock_provider.collect.call_count == 1  # Still 1, not called again
        
        # Results should be identical
        assert result1 == result2
        
        # Verify cache file exists
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) == 1
    
    def test_cache_with_different_policies(self, tmp_path):
        """Different policies should create separate cache entries."""
        cache_dir = tmp_path / ".cache"
        cache_backend = FileCacheBackend(root=str(cache_dir))
        
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TestProvider"
        mock_provider.model = "test-model"
        mock_provider.collect.side_effect = [
            {"result": "policy_A"},
            {"result": "policy_B"}
        ]
        
        cached_provider = CachedProvider(
            provider=mock_provider,
            cache=cache_backend
        )
        
        content = "same content"
        
        # Call with different policies
        result_a = cached_provider.collect(content, {"policy": "A"})
        result_b = cached_provider.collect(content, {"policy": "B"})
        
        # Both should call provider (different cache keys)
        assert mock_provider.collect.call_count == 2
        
        # Results should be different
        assert result_a != result_b
        
        # Should have 2 cache files
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    