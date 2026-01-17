from ai_slop_gate.cli.run import run_cli
from unittest.mock import patch, MagicMock
import argparse

def test_cli_run_static(capsys):
    args = argparse.Namespace(
        command="run",
        policy="policy.yml",
        provider="static",
        compliance=False,
        verbose=False,
    )

    with patch("ai_slop_gate.domain.compliance.gateway.ComplianceGateway.analyze", return_value=[]):
        exit_code = run_cli(args)
        captured = capsys.readouterr()
        assert "Decision: ALLOW" in captured.out
