from pathlib import Path

from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.compliance.config import ComplianceConfig, LicenseAuditConfig
from ai_slop_gate.domain.config import PolicyConfig


def test_effective_policy_merges_profile_and_license_audit(tmp_path: Path):
    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        """
version: "v1"
compliance:
  enabled: true
  license_audit:
    enabled: true
    forbidden_licenses:
      - GPL-3.0

rules: []
"""
    )

    policy_cfg, _, _, _ = load_policy(str(policy_path))

    assert policy_cfg.compliance.license_audit.forbidden_licenses is not None
    assert "GPL-3.0" in policy_cfg.compliance.license_audit.forbidden_licenses
