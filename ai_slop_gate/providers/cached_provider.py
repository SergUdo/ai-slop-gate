# ai_slop_gate/providers/cached_provider.py
import json
import hashlib
from typing import Any


class CachedProvider:
    def __init__(self, provider, cache):
        self.provider = provider
        self.cache = cache

    def _normalize_key(self, key: Any) -> str:
        """
        Cache key MUST be a string.
        Lists / dicts are serialized & hashed.
        """
        if isinstance(key, str):
            return key

        try:
            raw = json.dumps(key, sort_keys=True, default=str)
        except Exception:
            raw = str(key)

        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def collect(self):
        if not hasattr(self.provider, "cache_key"):
            return self.provider.collect()

        raw_key = self.provider.cache_key()
        key = self._normalize_key(raw_key) if raw_key else None

        if key:
            cached = self.cache.get(key)
            if cached is not None:
                return cached

        result = self.provider.collect()

        # Payload is a list of observations
        if hasattr(result, "observations"):
            payload = list(result.observations)
        else:
            payload = result

        if key:
            self.cache.set(key, payload)

        return payload
    
    def analyze(self, input_text, policy):
        """
        Cache AI model analysis responses
        """
        if not hasattr(self.provider, "analyze"):
            raise NotImplementedError(f"{self.provider.__class__.__name__} does not implement analyze()")

        # Create cache key
        raw_key = {
            "input_text": input_text,
            "policy": policy,
        }
        key = self._normalize_key(raw_key)

        cached = self.cache.get(key)
        if cached is not None:
            return cached

        result = self.provider.analyze(input_text, policy)

        self.cache.set(key, result)
        return result
        

