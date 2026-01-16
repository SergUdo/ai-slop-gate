import subprocess
import sys
from pathlib import Path

def test_cli_run_static(tmp_path):
    policy = tmp_path / "policy.yml"
    policy.write_text("""
rules:
  - id: todo
    when:
      category: CODE_QUALITY
      signal: TODO
    then:
      action: advisory
      message: Remove TODO
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
