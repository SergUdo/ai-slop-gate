from ai_slop_gate.cache.key_builder import CacheKeyBuilder
from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation


class CachedProvider:
    def __init__(self, provider, cache, key_builder=None):
        self.provider = provider
        self.cache = cache
        self.key_builder = key_builder or CacheKeyBuilder()

        if hasattr(provider, 'analyze'):
            original_analyze = provider.analyze
            provider.analyze = self._make_cached_analyze(original_analyze)

    def _serialize(self, obs: ProviderObservation) -> dict:
        """Convert ProviderObservation to JSON-serializable dict."""
        return {
            "provider": obs.provider,
            "model": obs.model,
            "raw_text": obs.raw_text,
            "observations": [
                {
                    "category": o.category,
                    "signal": o.signal,
                    "confidence": o.confidence,
                    "message": o.message,
                    "severity": o.severity,
                    "evidence": o.evidence,
                    "rule_id": o.rule_id,
                    "location": (
                        {"file": o.location.file, "line": o.location.line}
                        if o.location else None
                    ),
                }
                for o in obs.observations
            ]
        }

    def _deserialize(self, data: dict) -> ProviderObservation:
        """Restore ProviderObservation from cached dict."""
        if not isinstance(data, dict):
            return None

        observations = []
        for o in data.get("observations", []):
            observations.append(
                make_observation(
                    provider=data["provider"],
                    category=o.get("category", "quality"),
                    signal=o.get("signal", "unknown"),
                    confidence=float(o.get("confidence", 0.7)),
                    message=o.get("message", ""),
                    severity=o.get("severity"),
                    evidence=o.get("evidence"),
                    rule=o.get("rule_id"),
                )
            )

        return ProviderObservation(
            provider=data["provider"],
            model=data["model"],
            observations=observations,
            raw_text=data.get("raw_text", ""),
        )

    def _make_cached_analyze(self, original_analyze):
        def cached_analyze(code: str, input_file: str = ""):
            key = self.key_builder.build(
                provider_name=self.provider.__class__.__name__.lower(),
                model=getattr(self.provider, "model", "unknown"),
                content=code,
                policy={},
            )

            cached = self.cache.get(key)
            if cached is not None:
                result = self._deserialize(cached)
                if result is not None:
                    return result

            result = original_analyze(code, input_file)
            self.cache.set(key, self._serialize(result))
            return result

        return cached_analyze

    def collect(self, content: str, policy: dict):
        key = self.key_builder.build(
            provider_name=self.provider.__class__.__name__.lower(),
            model=getattr(self.provider, "model", "unknown"),
            content=content,
            policy=policy,
        )

        cached = self.cache.get(key)
        if cached is not None:
            result = self._deserialize(cached)
            if result is not None:
                return result

        result = self.provider.collect(content)
        self.cache.set(key, self._serialize(result))
        return result
    