from ai_slop_gate.providers.registry import provider_registry, ProviderRegistry


def test_provider_registry_defaults():
    # provider_registry should have common providers registered
    assert provider_registry.get("static") is not None
    assert provider_registry.get("eslint") is not None
    # can create a new registry and register a custom provider
    r = ProviderRegistry()
    class Dummy: pass
    r.register("x", Dummy)
    assert r.get("x") is Dummy
