from ai_slop_gate.domain.policy_config import ComplianceConfig
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway

def test_eu_profile_blocks_gpl():
    config = ComplianceConfig(enabled=True, profiles=["eu"])
    gateway = ComplianceGateway(config)

    observations = gateway.analyze(".")

    assert len(observations) == 1
    assert observations[0].license == "GPL-3.0"
