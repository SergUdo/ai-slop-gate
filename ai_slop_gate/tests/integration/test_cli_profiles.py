import subprocess
import sys
from pathlib import Path


def test_cli_verbose_profile_display(tmp_path: Path):
    policy = tmp_path / "policy.yml"
    policy.write_text(
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

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_slop_gate.cli.main",
            "run",
            "--provider",
            "static",
            "--policy",
            str(policy),
            "--verbose",
        ],
        capture_output=True,
        text=True,
    )

    out = result.stdout
    assert "Active profile: eu" in out
    assert "Forbidden licenses: ['GPL-3.0']" in out


