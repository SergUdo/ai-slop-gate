from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.compliance.config import PolicyConfig, ComplianceConfig


def test_compliance_disabled():
    config = PolicyConfig(enabled=False)
    gateway = ComplianceGateway(config)

    result = gateway.analyze(".")
    assert result == []
