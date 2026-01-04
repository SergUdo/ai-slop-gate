class CacheBackend:
    def get(self, key):
        raise NotImplementedError

    def set(self, key, value, ttl=None):
        raise NotImplementedError