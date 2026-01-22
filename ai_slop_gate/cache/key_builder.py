import hashlib
import json


class CacheKeyBuilder:
    def build(self, *, provider_name, model, content, policy):
        payload = {
            "provider": provider_name,
            "model": model,
            "content_sha256": self._sha256(content),
            "policy_sha256": self._sha256(policy),
            "contract": "collect@v1",
        }
        return self._sha256(payload)

    def _sha256(self, obj):
        raw = json.dumps(obj, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
