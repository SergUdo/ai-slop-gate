import pytest
import tempfile
from pathlib import Path
import yaml

from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.providers.k8s_runtime import K8sRuntimeProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend

K8S_YAML = """
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
spec:
  replicas: 1
---
apiVersion: v1
kind: Service
metadata:
  name: test-service
"""

@pytest.fixture
def temp_k8s_file():
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as f:
        f.write(K8S_YAML)
        f.flush()
        yield f.name
    Path(f.name).unlink(missing_ok=True)

@pytest.fixture
def cached_k8s_provider(temp_k8s_file):
    provider = K8sRuntimeProvider(manifests_path=temp_k8s_file)
    cache = FileCacheBackend()
    return CachedProvider(provider, cache=cache)

def test_collect_returns_observations(cached_k8s_provider):
    obs = cached_k8s_provider.collect()
    assert isinstance(obs, list)
    assert any("Deployment" in o.message for o in obs)

def test_collect_cache_hit(cached_k8s_provider):
    obs1 = cached_k8s_provider.collect()
    obs2 = cached_k8s_provider.collect()
    assert obs1 == obs2

def test_analyze_cache_behavior(cached_k8s_provider):
    result = cached_k8s_provider.analyze("dummy input")
    assert isinstance(result, list)
