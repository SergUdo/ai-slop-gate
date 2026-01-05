# ai_slop_gate/providers/cached_provider.py
from typing import Any

class CachedProvider:
    """
    Universal CachedProvider that wraps any provider.

    - If the provider has `collect()`, delegate to it with caching.
    - If the provider has `analyze(input_data)`, delegate to it with caching.
    """

    def __init__(self, provider: Any, cache: Any):
        self.provider = provider
        self.cache = cache

    def collect(self, *args, **kwargs):
        """
        For static / infra providers. Returns ProviderObservation or list.
        """
        # Determine cache key
        key = getattr(self.provider, "cache_key", lambda *a, **k: None)(*args, **kwargs)
        if key:
            cached = self.cache.get(key)
            if cached is not None:
                return cached

        # Run actual provider
        if hasattr(self.provider, "collect"):
            result = self.provider.collect(*args, **kwargs)
        elif hasattr(self.provider, "analyze"):
            result = self.provider.analyze(*args, **kwargs)
        else:
            raise ValueError("Provider has no collect() or analyze() method")

        # Save to cache if key exists
        if key:
            self.cache.set(key, result)

        return result

    def analyze(self, input_data: Any):
        """
        Use for providers that implement `analyze(input_data)`.
        """
        if not hasattr(self.provider, "analyze"):
            raise AttributeError(f"{self.provider.__class__.__name__} does not have 'analyze' method")

        key = self.provider.cache_key(input_data) if hasattr(self.provider, "cache_key") else None
        if key:
            cached = self.cache.get(key)
            if cached:
                return cached

        result = self.provider.analyze(input_data)

        if key:
            self.cache.set(key, result)

        return result

    def __getattr__(self, attr):
        """
        Delegate any other attribute access to the wrapped provider.
        """
        return getattr(self.provider, attr)
