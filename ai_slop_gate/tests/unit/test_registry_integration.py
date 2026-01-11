from ai_slop_gate.providers.registry import provider_registry
from ai_slop_gate.providers.supply_chain import SupplyChainProvider

def test_supply_chain_registration():
    provider_cls = provider_registry.get("supply-chain")
    assert provider_cls == SupplyChainProvider
    
def test_registry_defaults_contain_supply_chain():
    assert "supply-chain" in provider_registry._providers