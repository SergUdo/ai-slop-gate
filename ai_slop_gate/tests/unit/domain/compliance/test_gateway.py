from ai_slop_gate.domain.compliance.gateway import ComplianceGateway

def test_compliance_gateway_returns_result():
    gateway = ComplianceGateway()
    result = gateway.analyze(".")

    assert result is not None
    assert result.issues == []
    assert result.has_issues is False
