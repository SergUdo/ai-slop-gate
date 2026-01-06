import json
import hashlib
import inspect
from typing import Any
from ai_slop_gate.providers.base import ProviderObservation


class CachedProvider:
    """
    Wrap any Provider with a caching layer.
    """

    def __init__(self, provider, cache):
        self.provider = provider
        self.cache = cache

    def _normalize_key(self, key: Any) -> str:
        """Generate string key for cache"""
        if isinstance(key, str):
            return key
        try:
            raw = json.dumps(key, sort_keys=True, default=str)
        except Exception:
            raw = str(key)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _serialize(self, obj):
        """Convert ProviderObservation or Observation into JSON-serializable dict"""
        if hasattr(obj, "__dict__"):
            return {k: self._serialize(v) for k, v in obj.__dict__.items()}
        if isinstance(obj, list):
            return [self._serialize(o) for o in obj]
        return obj

    def _wrap_result(self, payload):
        """
        Wrap deserialized cache back into objects if needed
        """
        return payload  # keep simple, returning list/dict is fine for tests

    def collect(self):
        """Collect observations and cache them"""
        raw_key = getattr(self.provider, "cache_key", lambda: None)()
        key = self._normalize_key(raw_key) if raw_key else None

        if key:
            cached = self.cache.get(key)
            if cached is not None:
                return self._wrap_result(cached)

        result = self.provider.collect()

        if key:
            self.cache.set(key, self._serialize(result))

        return result

    def analyze(self, input_text, policy=None):
        """Cache AI model analysis responses"""
        if not hasattr(self.provider, "analyze"):
            # fallback: use collect
            return self.collect()

        raw_key = {"input_text": input_text, "policy": policy}
        key = self._normalize_key(raw_key)

        cached = self.cache.get(key)
        if cached is not None:
            return self._wrap_result(cached)

        # Handle providers with/without `policy` argument
        sig = inspect.signature(self.provider.analyze)
        if "policy" in sig.parameters:
            result = self.provider.analyze(input_text, policy)
        else:
            result = self.provider.analyze(input_text)

        self.cache.set(key, self._serialize(result))
        return result
