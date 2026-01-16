from ai_slop_gate.domain.policy_config import ComplianceConfig
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway

def test_eu_strict_blocks_gpl():
    config = ComplianceConfig(enabled=True, profiles=["eu-strict"])
    gateway = ComplianceGateway(config)

    obs = gateway.analyze(".")
    assert len(obs) == 1
    assert obs[0].severity == "high"
