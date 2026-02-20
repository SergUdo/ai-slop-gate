from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation


class DummyProvider:
    def __init__(self):
        self.called = 0
        self.model = "dummy"
    def collect(self, content: str):
        self.called += 1
        obs = make_observation(
            provider="DummyProvider",
            category="quality",
            signal="test",
            confidence=0.9,
            message=content,
        )
        return ProviderObservation(
            provider="DummyProvider",
            model=self.model,
            observations=[obs],
            raw_text=content,
        )


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
