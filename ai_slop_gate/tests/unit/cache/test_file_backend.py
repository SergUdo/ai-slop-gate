"""Unit tests for cache/file_backend module."""
import pytest
import json
import tempfile
from pathlib import Path
from ai_slop_gate.cache.file_backend import FileCacheBackend


class TestFileCacheBackend:
    """Test suite for FileCacheBackend."""

    def test_file_cache_backend_initialization(self):
        """Test FileCacheBackend initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            assert backend.root == Path(tmpdir)
            assert backend.root.exists()

    def test_file_cache_backend_default_root(self):
        """Test FileCacheBackend uses default root."""
        backend = FileCacheBackend()
        assert str(backend.root) == ".ai-slop-cache"

    def test_file_cache_backend_creates_directory(self):
        """Test FileCacheBackend creates root directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "cache"
            assert not cache_dir.exists()
            
            backend = FileCacheBackend(root=str(cache_dir))
            assert cache_dir.exists()

    def test_file_cache_set_and_get(self):
        """Test setting and getting cache values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            
            backend.set("test_key", {"data": "value"})
            result = backend.get("test_key")
            
            assert result == {"data": "value"}

    def test_file_cache_get_nonexistent(self):
        """Test getting nonexistent cache key returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            result = backend.get("nonexistent_key")
            assert result is None

    def test_file_cache_set_string_value(self):
        """Test cache with string value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            backend.set("key", "string_value")
            result = backend.get("key")
            assert result == "string_value"

    def test_file_cache_set_list_value(self):
        """Test cache with list value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            test_list = [1, 2, 3, "four"]
            backend.set("list_key", test_list)
            result = backend.get("list_key")
            assert result == test_list

    def test_file_cache_set_dict_value(self):
        """Test cache with complex dict value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            complex_dict = {
                "nested": {
                    "level": 2,
                    "items": [1, 2, 3]
                },
                "key": "value"
            }
            backend.set("complex", complex_dict)
            result = backend.get("complex")
            assert result == complex_dict

    def test_file_cache_overwrites_existing(self):
        """Test that setting a key overwrites existing value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            
            backend.set("key", "value1")
            assert backend.get("key") == "value1"
            
            backend.set("key", "value2")
            assert backend.get("key") == "value2"

    def test_file_cache_path_generation(self):
        """Test cache path generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            path = backend._path("test_key")
            assert str(path) == str(Path(tmpdir) / "test_key.json")

    def test_file_cache_persists_to_disk(self):
        """Test that cache persists data to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            backend.set("persistent_key", {"data": "persisted"})
            
            # Verify file exists
            cache_file = Path(tmpdir) / "persistent_key.json"
            assert cache_file.exists()
            
            # Verify content
            content = json.loads(cache_file.read_text())
            assert content == {"data": "persisted"}

    def test_file_cache_multiple_keys(self):
        """Test cache with multiple keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            
            backend.set("key1", "value1")
            backend.set("key2", "value2")
            backend.set("key3", "value3")
            
            assert backend.get("key1") == "value1"
            assert backend.get("key2") == "value2"
            assert backend.get("key3") == "value3"

    def test_file_cache_with_special_characters_in_key(self):
        """Test cache key with underscores and numbers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            special_key = "provider_gemini_2024"
            backend.set(special_key, {"test": "value"})
            result = backend.get(special_key)
            assert result == {"test": "value"}

    def test_file_cache_numeric_value(self):
        """Test cache with numeric values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            backend.set("number", 42)
            result = backend.get("number")
            assert result == 42

    def test_file_cache_float_value(self):
        """Test cache with float values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            backend.set("float_val", 3.14159)
            result = backend.get("float_val")
            assert result == 3.14159

    def test_file_cache_boolean_value(self):
        """Test cache with boolean values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            backend.set("bool_true", True)
            backend.set("bool_false", False)
            assert backend.get("bool_true") is True
            assert backend.get("bool_false") is False

    def test_file_cache_null_value(self):
        """Test cache with None value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = FileCacheBackend(root=tmpdir)
            backend.set("null_val", None)
            result = backend.get("null_val")
            assert result is None
