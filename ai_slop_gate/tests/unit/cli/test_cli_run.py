import pytest
from unittest.mock import MagicMock, patch
from ai_slop_gate.cli.run import run_cli
from ai_slop_gate.domain.decision import DecisionMode

@pytest.fixture
def mock_args():
    args = MagicMock()
    args.policy = "tests/fixtures/policy.yml"
    args.provider = "static"
    args.input_file = None
    args.compliance = False
    args.verbose = False
    return args

def test_run_cli_minimal_mode(mock_args):
    with patch("ai_slop_gate.cli.run.load_policy") as mock_load_policy, \
         patch("ai_slop_gate.cli.run.PolicyEngine") as mock_policy_engine:

        mock_load_policy.return_value = (MagicMock(), MagicMock())
        mock_engine = MagicMock()
        mock_policy_engine.return_value = mock_engine
        mock_decision = MagicMock(mode=DecisionMode.ALLOW, reasons=[])
        mock_engine.evaluate.return_value = mock_decision

        result = run_cli(mock_args)

        mock_load_policy.assert_called_once_with(mock_args.policy)
        mock_policy_engine.assert_called_once()
        mock_engine.evaluate.assert_called_once_with([])
        assert result == 0

def test_run_cli_blocking_decision(mock_args):
    with patch("ai_slop_gate.cli.run.load_policy") as mock_load_policy, \
         patch("ai_slop_gate.cli.run.PolicyEngine") as mock_policy_engine:

        mock_load_policy.return_value = (MagicMock(), MagicMock())
        mock_engine = MagicMock()
        mock_policy_engine.return_value = mock_engine
        mock_decision = MagicMock(mode=DecisionMode.BLOCKING, reasons=["Test reason"])
        mock_engine.evaluate.return_value = mock_decision

        result = run_cli(mock_args)

        assert result == 1

def test_run_cli_verbose_mode(mock_args):
    mock_args.verbose = True

    with patch("ai_slop_gate.cli.run.load_policy") as mock_load_policy, \
         patch("ai_slop_gate.cli.run.PolicyEngine") as mock_policy_engine, \
         patch("builtins.print") as mock_print:

        mock_load_policy.return_value = (MagicMock(compliance=MagicMock(enabled=False)), MagicMock())
        mock_engine = MagicMock()
        mock_policy_engine.return_value = mock_engine
        mock_decision = MagicMock(mode=DecisionMode.ALLOW, reasons=[])
        mock_engine.evaluate.return_value = mock_decision

        result = run_cli(mock_args)

        assert mock_print.call_count > 0
        assert result == 0

def test_run_cli_compliance_enabled():
    args = MagicMock()
    args.policy = "tests/fixtures/policy.yml"
    args.provider = "static"
    args.input_file = "."
    args.compliance = True
    args.verbose = False

    with patch("ai_slop_gate.cli.run.load_policy") as mock_load_policy, \
         patch("ai_slop_gate.cli.run.ComplianceGateway") as mock_gateway, \
         patch("ai_slop_gate.cli.run.PolicyEngine") as mock_policy_engine:

        mock_config = MagicMock()
        mock_config.compliance.enabled = True
        mock_load_policy.return_value = (mock_config, MagicMock())
        mock_gateway_instance = MagicMock()
        mock_gateway.return_value = mock_gateway_instance
        mock_gateway_instance.analyze.return_value = [MagicMock()]

        mock_engine = MagicMock()
        mock_policy_engine.return_value = mock_engine
        mock_decision = MagicMock(mode=DecisionMode.ALLOW, reasons=[])
        mock_engine.evaluate.return_value = mock_decision

        result = run_cli(args)

        mock_gateway.assert_called_once()
        mock_gateway_instance.analyze.assert_called_once_with(".")
        assert result == 0
