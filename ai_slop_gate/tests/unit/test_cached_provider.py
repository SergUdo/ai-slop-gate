import pytest
import subprocess
import sys
from pathlib import Path
from ai_slop_gate.providers.cached_provider import CachedProvider

class MockProvider:
    def __init__(self):
        self.collect_called = 0
        self.analyze_called = 0

    def cache_key(self, *args, **kwargs):
        return {"mock": "key", "args": args, "kwargs": kwargs}

    def collect(self, *args, **kwargs):
        self.collect_called += 1
        return ["collect_result"]

    def analyze(self, text, policy=None):
        self.analyze_called += 1
        return [f"analyze_result:{text}"]

# --- Mock cache
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
    res1 = cached_provider.collect("test")
    assert res1 == ["collect_result"]
    assert cached_provider.provider.collect_called == 1

    res2 = cached_provider.collect("test")
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


def test_cli_run_static(tmp_path):
    policy = tmp_path / "policy.yml"
    policy.write_text("""
rules:
  - id: todo
    when:
      category: CODE_QUALITY
      signal: TODO
    then:
      action: advisory
      message: Remove TODO
""")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_slop_gate.cli.main",
            "run",
            "--policy",
            str(policy),
            "--provider",
            "static",
            "--input-text",
            "test"
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    print(result.stderr)

    assert result.returncode == 0
    assert "Decision:" in result.stdout
