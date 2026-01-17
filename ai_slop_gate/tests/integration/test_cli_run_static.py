import pytest
from subprocess import run, PIPE
from pathlib import Path

@pytest.mark.integration
def test_cli_run_static(tmp_path):
    """
    CLI static provider should produce a decision.
    """
    policy_file = tmp_path / "policy.yml"
    policy_file.write_text("""
version: "v1"
project_name: "ai_slop_gate"
enforcement: advisory
rules: []
""")

    input_file = tmp_path / "requirements.txt"
    input_file.write_text("packageA==1.0\n")

    result = run(
        ["python", "-m", "ai_slop_gate.cli.main",
         "run", "--policy", str(policy_file),
         "--provider", "static",
         "--input-file", str(input_file)],
        stdout=PIPE, stderr=PIPE, text=True
    )

    assert "Decision" in result.stdout
