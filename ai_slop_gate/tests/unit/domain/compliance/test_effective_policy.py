from pathlib import Path

from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.compliance.config import ComplianceConfig
from ai_slop_gate.domain.config import PolicyConfig


def test_effective_policy_merges_profile_and_license_audit(tmp_path: Path):
    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        """
version: "v1"
compliance:
  enabled: true
  active_profile: eu
  profiles:
    - name: eu
      forbid_licenses: ["GPL-3.0"]

rules: []
"""
    )

    policy_cfg, _ = load_policy(str(policy_path))

    assert "GPL-3.0" in policy_cfg.compliance.forbid_licenses
