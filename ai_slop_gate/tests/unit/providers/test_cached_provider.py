from ai_slop_gate.providers.cached_provider import CachedProvider


class DummyProvider:
    def __init__(self):
        self.called = 0
    def collect(self, content: str):
        self.called += 1
        return {"result": content}


class DummyCache:
    def __init__(self):
        self.store = {}
    def get(self, key):
        return self.store.get(key)
    def set(self, key, value):
        self.store[key] = value


def test_cached_provider_hits_cache():
    prov = DummyProvider()
    cache = DummyCache()
    cp = CachedProvider(prov, cache)

    r1 = cp.collect("abc", policy={})
    r2 = cp.collect("abc", policy={})

    assert r1 == r2
    assert prov.called == 1
