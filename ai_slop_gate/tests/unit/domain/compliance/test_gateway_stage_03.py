from ai_slop_gate.domain.compliance.gateway import ComplianceGateway

def test_gateway_returns_observations():
    gateway = ComplianceGateway()
    observations = gateway.analyze(".")

    assert isinstance(observations, list)
