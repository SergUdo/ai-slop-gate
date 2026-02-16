from ai_slop_gate.cache.key_builder import CacheKeyBuilder


class CachedProvider:
    """
    Canonical cache wrapper.
    Ensures LLM tokens are not spent twice.
    
    Wraps LLM providers and intercepts analyze() calls to cache chunks.
    """

    def __init__(self, provider, cache, key_builder=None):
        self.provider = provider
        self.cache = cache
        self.key_builder = key_builder or CacheKeyBuilder()
        
        # Monkey-patch the provider's analyze() method to add caching
        if hasattr(provider, 'analyze'):
            original_analyze = provider.analyze
            provider.analyze = self._make_cached_analyze(original_analyze)

    def _make_cached_analyze(self, original_analyze):
        """
        Create a cached version of the provider's analyze() method.
        This is where caching actually happens - at the chunk level.
        """
        def cached_analyze(code: str, input_file: str = ""):
            # Build cache key from code content
            key = self.key_builder.build(
                provider_name=self.provider.__class__.__name__.lower(),
                model=getattr(self.provider, "model", "unknown"),
                content=code,  # The chunk being analyzed
                policy={},  # Policy not relevant for chunk-level caching
            )

            # Try cache first
            cached = self.cache.get(key)
            if cached is not None:
                return cached

            # Cache miss - call original
            result = original_analyze(code, input_file)
            self.cache.set(key, result)
            return result
        
        return cached_analyze

    def collect(self, content: str, policy: dict):
        """
        Cache-aware collect method for static providers.
        """
        key = self.key_builder.build(
            provider_name=self.provider.__class__.__name__.lower(),
            model=getattr(self.provider, "model", "unknown"),
            content=content,
            policy=policy,
        )

        cached = self.cache.get(key)
        if cached is not None:
            return cached

        result = self.provider.collect(content)
        self.cache.set(key, result)
        return result