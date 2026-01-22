def test_llm_tokens_not_spent_twice(tmp_path, mocker):
    from ai_slop_gate.providers.cached_provider import CachedProvider
    from ai_slop_gate.cache.file_backend import FileCacheBackend

    provider = mocker.Mock()
    provider.model = "models/gemini-2.5-flash"
    provider.collect.return_value = {"result": "OK"}

    cache = FileCacheBackend(root=tmp_path)
    cached = CachedProvider(provider, cache)

    policy = {"ai_slop": {"detect_llm_quality": {"enabled": True}}}

    cached.collect("code", policy)
    cached.collect("code", policy)

    assert provider.collect.call_count == 1
