import subprocess
import sys
from pathlib import Path
import pytest
import yaml

# --- Mock provider that simulates GPL violation
class MockComplianceProvider:
    def collect(self):
        # Return a mock observation (Stage 0.1 ignores signal printing)
        return [{"signal": "GPL-3.0", "rule_id": "forbidden_license"}]

@pytest.mark.integration
def test_cli_stage0_gpl_detection(tmp_path, monkeypatch):
    """
    Integration test for Stage 0.1 CLI with compliance.
    Checks that Decision is ADVISORY or BLOCKING when a GPL license is found.
    """

    # Create a minimal policy file for compliance check
    policy_file = tmp_path / "policy.yml"
    policy_content = {
        "rules": [
            {
                "id": "forbidden_license",
                "when": {"category": "SUPPLY_CHAIN", "signal": "GPL-3.0"},
                "then": {"action": "advisory", "message": "GPL violation detected"}
            }
        ]
    }
    policy_file.write_text(yaml.dump(policy_content))

    # Create a fake requirements.txt
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("some-library==1.0.0 # License: GPL-3.0")

    # Patch provider registry to use the mock for "static"
    from ai_slop_gate.providers.registry import provider_registry
    monkeypatch.setattr(provider_registry, "get", lambda key: MockComplianceProvider if key == "static" else None)

    # Run CLI subprocess
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_slop_gate.cli.main",
            "run",
            "--policy",
            str(policy_file),
            "--provider",
            "static",
            "--input-file",
            str(req_file),
        ],
        capture_output=True,
        text=True,
    )

    # --- Assertions ---
    # CLI should run successfully
    assert result.returncode == 0

    # Stage 0.1 CLI prints Decision
    assert "Decision:" in result.stdout

    # Decision should be ADVISORY or BLOCKING (mock triggers advisory)
    assert "ADVISORY" in result.stdout or "BLOCKING" in result.stdout
