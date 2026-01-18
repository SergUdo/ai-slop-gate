import pytest
from unittest.mock import patch, MagicMock
from ai_slop_gate.cli.main import main

def test_main_init_command(capsys):
    test_args = ["ai-slop-gate", "init", "--force"]

    with patch("sys.argv", test_args), \
         patch("ai_slop_gate.cli.main.argparse.ArgumentParser") as mock_parser, \
         patch("ai_slop_gate.cli.main.run_init") as mock_run_init:

        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.return_value = MagicMock(command="init", force=True)
        mock_run_init.return_value = 0

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 0
        mock_run_init.assert_called_once_with(True)

def test_main_run_command(capsys):
    test_args = ["ai-slop-gate", "run", "--policy", "policy.yml", "--provider", "static"]

    with patch("sys.argv", test_args), \
         patch("ai_slop_gate.cli.main.argparse.ArgumentParser") as mock_parser, \
         patch("ai_slop_gate.cli.main.run_cli") as mock_run_cli:

        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_args = MagicMock(command="run", policy="policy.yml", provider="static")
        mock_parser_instance.parse_args.return_value = mock_args
        mock_run_cli.return_value = 0

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 0
        mock_run_cli.assert_called_once_with(mock_args)

def test_main_invalid_command(capsys):
    test_args = ["ai-slop-gate", "invalid"]

    with patch("sys.argv", test_args), \
         patch("ai_slop_gate.cli.main.argparse.ArgumentParser") as mock_parser:

        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.side_effect = SystemExit(2)

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 2
