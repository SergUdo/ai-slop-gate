from ai_slop_gate.domain.config import PolicyConfig
from ai_slop_gate.domain.compliance.config import ComplianceConfig


def test_compliance_disabled():
    cfg = PolicyConfig(
        compliance=ComplianceConfig(
            enabled=False,
            forbid_licenses=["GPL-3.0"],
        )
    )

    assert cfg.compliance.enabled is False
    assert "GPL-3.0" in (cfg.compliance.forbid_licenses or [])

