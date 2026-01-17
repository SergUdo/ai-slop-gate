import subprocess
import sys
from pathlib import Path


def test_cli_verbose_no_observations(tmp_path: Path):
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
            "--verbose",
        ],
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "=== AI Slop Gate Compliance Report ===" in out
    assert "Active profile: none" in out
    assert "Forbidden licenses: []" in out
    assert "Allowed licenses: []" in out
    assert "Rules loaded: 0" in out
    assert "Observations:" in out
    assert "  (none)" in out
    assert "Reasons:" in out
    assert "  (none)" in out
    assert "Annotations:" in out
    assert "  (none)" in out
    # Stage 0.7: no rules/observations → ALLOW
    assert "Decision: ALLOW" in out
