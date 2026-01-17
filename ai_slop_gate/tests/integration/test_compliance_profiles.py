from ai_slop_gate.domain.compliance.config import PolicyConfig, ComplianceConfig
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway

def test_eu_profile_blocks_gpl():
    config = PolicyConfig(enabled=True, profiles=["eu"])
    gateway = ComplianceGateway(config)

    observations = gateway.analyze(".")

    assert len(observations) == 1
    assert observations[0].license == "GPL-3.0"
