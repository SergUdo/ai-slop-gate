from ai_slop_gate.domain.config import PolicyConfig
from ai_slop_gate.domain.compliance.config import ComplianceConfig, LicenseAuditConfig


def test_compliance_disabled():
    cfg = PolicyConfig(
        enforcement="advisory",
        ai_provider={},
        compliance=ComplianceConfig(
            enabled=False,
            license_audit=LicenseAuditConfig(
                enabled=True,
                forbidden_licenses=["GPL-3.0"]
            ),
        ),
        code_quality={},
        infrastructure_security={},
        ai_slop={},
        rules=[]
    )

    assert cfg.compliance.enabled is False
    assert cfg.compliance.license_audit.forbidden_licenses is not None
    assert "GPL-3.0" in cfg.compliance.license_audit.forbidden_licenses

