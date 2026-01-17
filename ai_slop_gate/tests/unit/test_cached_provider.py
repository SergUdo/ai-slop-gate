# ai_slop_gate/tests/unit/test_cached_provider.py
from ai_slop_gate.cli.run import run_cli
from unittest.mock import patch

def test_cli_run_static(capsys):
    with patch("ai_slop_gate.domain.compliance.gateway.ComplianceGateway.analyze", return_value=[]):
        run_cli("policy.yml", "static")
        captured = capsys.readouterr()
        assert "Decision: ALLOW" in captured.out
