import json
import hashlib
import inspect
from typing import Any


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
        """Wrap deserialized cache back into objects if needed"""
        return payload  # simple: list/dict is fine for tests

    def collect(self, *args, **kwargs):
        """
        Collect observations with caching.
        Passes arguments to provider.collect only if provider supports them.
        """
        raw_key_func = getattr(self.provider, "cache_key", None)
        raw_key = raw_key_func(*args, **kwargs) if raw_key_func else None
        key = self._normalize_key(raw_key) if raw_key else None

        # check cache
        if key:
            cached = self.cache.get(key)
            if cached is not None:
                return self._wrap_result(cached)

        # check if provider.collect supports args/kwargs
        sig = inspect.signature(self.provider.collect)
        if len(sig.parameters) > 1:  # self + others
            result = self.provider.collect(*args, **kwargs)
        else:
            result = self.provider.collect()

        # save to cache
        if key:
            self.cache.set(key, self._serialize(result))

        return result

    def analyze(self, *args, **kwargs):
        """
        Cache AI model analysis responses.
        Passes all arguments to the wrapped provider if supported.
        """
        if not hasattr(self.provider, "analyze"):
            return self.collect(*args, **kwargs)

        raw_key = {"args": args, "kwargs": kwargs}
        key = self._normalize_key(raw_key)

        cached = self.cache.get(key)
        if cached is not None:
            return self._wrap_result(cached)

        sig = inspect.signature(self.provider.analyze)
        if "policy" in sig.parameters:
            result = self.provider.analyze(*args, **kwargs)
        else:
            kwargs_no_policy = {k: v for k, v in kwargs.items() if k != "policy"}
            result = self.provider.analyze(*args, **kwargs_no_policy)

        self.cache.set(key, self._serialize(result))
        return result
