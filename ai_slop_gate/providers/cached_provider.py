from ai_slop_gate.cache.key_builder import CacheKeyBuilder


class CachedProvider:
    """
    Canonical cache wrapper.
    Ensures LLM tokens are not spent twice.
    """

    def __init__(self, provider, cache, key_builder=None):
        self.provider = provider
        self.cache = cache
        self.key_builder = key_builder or CacheKeyBuilder()

    def collect(self, content: str, policy: dict):
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
