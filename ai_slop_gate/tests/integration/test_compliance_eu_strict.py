from ai_slop_gate.domain.config import PolicyConfig
from ai_slop_gate.domain.compliance.config import ComplianceConfig


def test_eu_strict_blocks_gpl():
    cfg = PolicyConfig(
        compliance=ComplianceConfig(
            enabled=True,
            profiles=["eu-strict"],
            forbid_licenses=["GPL-3.0"],
            enforcement="blocking",
        )
    )

    assert cfg.compliance.enabled is True
    assert "GPL-3.0" in (cfg.compliance.forbid_licenses or [])
