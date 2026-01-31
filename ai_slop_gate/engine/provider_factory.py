from ai_slop_gate.providers.gemini import GeminiProvider
from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend


def build_provider(policy: dict):
    provider_name = policy["ai_provider"]["name"]

    if provider_name == "gemini":
        provider = GeminiProvider(
            model=policy["ai_provider"]["model"]
        )
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

    cache_cfg = policy.get("providers", {}).get("cache", {})

    if cache_cfg.get("enabled", True):
        provider = CachedProvider(
            provider=provider,
            cache=FileCacheBackend(
                root=cache_cfg.get("path", ".ai-slop-cache")
            ),
        )

    return provider
