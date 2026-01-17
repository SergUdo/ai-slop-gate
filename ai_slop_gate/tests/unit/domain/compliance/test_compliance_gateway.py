from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.compliance.config import ComplianceConfig
from pathlib import Path


def test_compliance_gateway_detects_forbidden_license(tmp_path):
    policy_cfg = ComplianceConfig(enabled=True, forbid_licenses=["GPL-3.0"])
    gateway = ComplianceGateway(policy_cfg)

    req = tmp_path / "requirements.txt"
    req.write_text("somepkg==1.0  # GPL-3.0\n")

    observations = gateway.analyze(str(tmp_path))

    assert len(observations) == 1
    assert observations[0].license == "GPL-3.0"

