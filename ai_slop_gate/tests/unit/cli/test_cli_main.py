import pytest
from unittest.mock import patch, MagicMock
from ai_slop_gate.cli.main import main

def test_main_init_command():
    with patch("ai_slop_gate.cli.main.build_parser") as mock_build_parser, \
         patch("ai_slop_gate.cli.main.run_init") as mock_run_init:

        mock_args = MagicMock()
        mock_args.command = "init"
        mock_args.force = True
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser
        
        mock_run_init.return_value = 0

        result = main()

        assert result == 0
        mock_run_init.assert_called_once_with(force=True)

def test_main_run_command():
    with patch("ai_slop_gate.cli.main.build_parser") as mock_build_parser, \
         patch("ai_slop_gate.cli.main.RuntimeContext") as mock_ctx_class, \
         patch("ai_slop_gate.cli.main.run_cli") as mock_run_cli:

        mock_args = MagicMock(command="run", input_text="test", input_file=None, repo=".", 
                              policy="p.yml", enforcement=True, provider="static", 
                              compliance=False, eu_only=False, license_policy=None,
                              github_repo=None, github_sha=None, pr_id=None, 
                              github_checks=None, github_token=None)
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser
        
        mock_run_cli.return_value = 0

        result = main()

        assert result == 0
        mock_run_cli.assert_called_once()