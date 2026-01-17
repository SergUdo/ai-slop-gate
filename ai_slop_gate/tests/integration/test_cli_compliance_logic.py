import pytest
from subprocess import run, PIPE
from pathlib import Path

@pytest.mark.integration
def test_cli_stage0_gpl_detection(tmp_path):
    """
    CLI should detect GPL-3.0 license violation when compliance enabled.
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
    allow: [MIT, Apache-2.0]
  enforcement: blocking

rules:
  - id: forbid-gpl
    when:
      source: compliance
      license: GPL-3.0
    then:
      decision: block
      reason: "GPL is forbidden by EU compliance"
""")

    input_file = tmp_path / "requirements.txt"
    input_file.write_text("packageA==1.0  # GPL-3.0\n")

    result = run(
        ["python", "-m", "ai_slop_gate.cli.main",
         "run", "--policy", str(policy_file),
         "--provider", "static",
         "--input-file", str(input_file)],
        stdout=PIPE, stderr=PIPE, text=True
    )

    assert "GPL-3.0" in result.stdout or "GPL-3.0" in result.stderr
    assert "Decision" in result.stdout
