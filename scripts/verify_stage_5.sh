#!/usr/bin/env bash
# ./scripts/verify_stage_5.sh
set -euo pipefail

echo "🔍 Verifying Stage 5: GitLab support & provider registry"

echo "▶️ 1. CLI help"
python -m ai_slop_gate.cli --help >/dev/null

echo "▶️ 2. Registry import"
python - <<'PY'
from ai_slop_gate.providers.registry import ProviderRegistry
r = ProviderRegistry()
print("OK: ProviderRegistry")
PY

echo "▶️ 3. Cache backend"
python - <<'PY'
from ai_slop_gate.cache.file_backend import FileCacheBackend
c = FileCacheBackend(".tmp-cache")
c.set("test", {"ok": True})
assert c.get("test")["ok"] is True
print("OK: FileCacheBackend")
PY

echo "▶️ 4. Cached provider wrapper"
python - <<'PY'
class DummyProvider:
    name = "dummy"
    def analyze(self, x): return {"value": x}
    def cache_key(self, x): return "k"
from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend

cp = CachedProvider(DummyProvider(), FileCacheBackend(".tmp-cache"))
assert cp.analyze(1)["value"] == 1
print("OK: CachedProvider")
PY

echo "▶️ 5. Rate-limit guard"
python - <<'PY'
class P:
    name="p"
    def analyze(self,x): return x
from ai_slop_gate.providers.rate_limit_guard import RateLimitGuard
g = RateLimitGuard(P(), interval_sec=0)
assert g.analyze(1) == 1
print("OK: RateLimitGuard")
PY

echo "▶️ 6. GitLab reporter import"
python - <<'PY'
from ai_slop_gate.reporters.gitlab_merge_request import GitLabMergeRequestReporter
print("OK: GitLabMergeRequestReporter")
PY

echo "✅ Stage 5 verification PASSED"
