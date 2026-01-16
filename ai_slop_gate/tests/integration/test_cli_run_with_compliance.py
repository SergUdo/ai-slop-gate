import subprocess
import sys
from pathlib import Path

def test_cli_run_includes_compliance_output(tmp_path):
    policy = tmp_path / "policy.yml"
    policy.write_text("""
rules: []
""")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_slop_gate.cli.main",
            "run",
            "--policy",
            str(policy),
            "--provider",
            "static",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Decision:" in result.stdout
    assert "Compliance:" in result.stdout
