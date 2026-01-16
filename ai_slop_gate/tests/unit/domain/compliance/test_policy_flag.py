from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.policy_config import ComplianceConfig

def test_compliance_disabled():
    config = ComplianceConfig(enabled=False)
    gateway = ComplianceGateway(config)

    result = gateway.analyze(".")
    assert result == []
