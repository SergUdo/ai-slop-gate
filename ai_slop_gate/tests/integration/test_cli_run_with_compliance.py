import pytest
from subprocess import run, PIPE
from pathlib import Path

@pytest.mark.integration
def test_cli_run_includes_compliance_output(tmp_path):
    """
    CLI run should include compliance output when compliance enabled.
    """
    policy_file = tmp_path / "policy.yml"
    policy_file.write_text("""
version: "v1"
project_name: "ai_slop_gate"
enforcement: advisory
compliance:
  enabled: true
  profiles: [eu]
  license:
    forbid: [GPL-3.0]
    allow: [MIT]
  enforcement: advisory
rules: []
""")

    result = run(
        ["python", "-m", "ai_slop_gate.cli.main",
         "run", "--policy", str(policy_file),
         "--provider", "static"],
        stdout=PIPE, stderr=PIPE, text=True
    )

    assert "Compliance" in result.stdout or "Decision" in result.stdout
