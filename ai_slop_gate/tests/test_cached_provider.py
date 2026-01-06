import pytest
from ai_slop_gate.providers.cached_provider import CachedProvider


# --- Mock provider з collect() та analyze()
class MockProvider:
    def __init__(self):
        self.collect_called = 0
        self.analyze_called = 0

    def cache_key(self):
        return {"mock": "key"}

    def collect(self):
        self.collect_called += 1
        return ["collect_result"]

    def analyze(self, text, policy=None):
        self.analyze_called += 1
        return [f"analyze_result:{text}"]


# --- Mock cache in memory
class MemoryCache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value


@pytest.fixture
def cached_provider():
    provider = MockProvider()
    cache = MemoryCache()
    return CachedProvider(provider, cache)


def test_collect_cache_hit(cached_provider):
    res1 = cached_provider.collect()
    assert res1 == ["collect_result"]
    assert cached_provider.provider.collect_called == 1

    res2 = cached_provider.collect()
    assert res2 == ["collect_result"]
    assert cached_provider.provider.collect_called == 1


def test_analyze_cache_hit(cached_provider):
    res1 = cached_provider.analyze("hello")
    assert res1 == ["analyze_result:hello"]
    assert cached_provider.provider.analyze_called == 1

    res2 = cached_provider.analyze("hello")
    assert res2 == ["analyze_result:hello"]
    assert cached_provider.provider.analyze_called == 1

    res3 = cached_provider.analyze("world")
    assert res3 == ["analyze_result:world"]
    assert cached_provider.provider.analyze_called == 2
