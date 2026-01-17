import subprocess
import sys
from pathlib import Path


def test_cli_minimal_mode(tmp_path: Path):
    policy = tmp_path / "policy.yml"
    policy.write_text(
        """
rules: []
compliance:
  enabled: false
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
        ],
        capture_output=True,
        text=True,
    )

    out = result.stdout.strip()
    # Stage 0.7: no rules → ALLOW
    assert out == "Decision: ALLOW"
