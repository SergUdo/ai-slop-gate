class CachedProvider:
    def __init__(self, provider, cache):
        self.provider = provider
        self.cache = cache

    def analyze(self, input_data):
        key = self.provider.cache_key(input_data)
        if key:
            cached = self.cache.get(key)
            if cached:
                return cached

        result = self.provider.analyze(input_data)

        if key:
            self.cache.set(key, result)

        return result
