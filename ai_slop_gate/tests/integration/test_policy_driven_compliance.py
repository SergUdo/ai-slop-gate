from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.policy_config import ComplianceConfig

def test_forbidden_license_emits_observation():
    config = ComplianceConfig(
        enabled=True,
        forbid_licenses=["GPL-3.0"],
    )

    gateway = ComplianceGateway(config)
    observations = gateway.analyze(".")

    assert len(observations) == 1
    assert observations[0].license == "GPL-3.0"
