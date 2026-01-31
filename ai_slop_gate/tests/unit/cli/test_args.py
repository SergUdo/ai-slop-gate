import pytest
from ai_slop_gate.cli.args import build_parser


class TestBuildParser:
    """Test suite for argument parser configuration."""

    def test_parser_exists(self):
        """Test that parser is created successfully."""
        parser = build_parser()
        assert parser is not None

    def test_init_command_basic(self):
        """Test init command with minimal arguments."""
        parser = build_parser()
        args = parser.parse_args(["init"])
        
        assert args.command == "init"
        assert args.force is False

    def test_init_command_with_force(self):
        """Test init command with --force flag."""
        parser = build_parser()
        args = parser.parse_args(["init", "--force"])
        
        assert args.command == "init"
        assert args.force is True

    def test_run_command_with_provider(self):
        """Test run command with required provider argument."""
        parser = build_parser()
        args = parser.parse_args(["run", "--provider", "static"])
        
        assert args.command == "run"
        assert args.provider == ["static"]

    def test_run_command_with_multiple_providers(self):
        """Test run command with multiple providers."""
        parser = build_parser()
        args = parser.parse_args(["run", "--provider", "static", "gemini"])
        
        assert args.command == "run"
        assert args.provider == ["static", "gemini"]

    def test_run_command_provider_short_flag(self):
        """Test run command with -p short flag."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static"])
        
        assert args.command == "run"
        assert args.provider == ["static"]

    def test_run_command_with_path(self):
        """Test run command with --path argument."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--path", "/custom/path"])
        
        assert args.path == "/custom/path"

    def test_run_command_path_default(self):
        """Test run command --path defaults to current directory."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static"])
        
        assert args.path == "."

    def test_run_command_with_llm_local(self):
        """Test run command with --llm-local flag."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--llm-local"])
        
        assert args.llm_local is True

    def test_run_command_llm_local_default(self):
        """Test run command --llm-local defaults to False."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static"])
        
        assert args.llm_local is False

    def test_run_command_with_github_repo(self):
        """Test run command with --github-repo argument."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--github-repo", "owner/repo"])
        
        assert args.github_repo == "owner/repo"

    def test_run_command_with_pr_id(self):
        """Test run command with --pr-id argument."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--pr-id", "123"])
        
        assert args.pr_id == 123

    def test_run_command_pr_id_is_integer(self):
        """Test that --pr-id converts to integer type."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--pr-id", "456"])
        
        assert isinstance(args.pr_id, int)
        assert args.pr_id == 456

    def test_run_command_with_github_sha(self):
        """Test run command with --github-sha argument."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--github-sha", "abc123def"])
        
        assert args.github_sha == "abc123def"

    def test_run_command_with_github_token(self):
        """Test run command with --github-token argument."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--github-token", "ghp_token123"])
        
        assert args.github_token == "ghp_token123"

    def test_run_command_with_policy_file(self):
        """Test run command with --policy argument."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--policy", "/path/to/policy.yml"])
        
        assert args.policy == "/path/to/policy.yml"

    def test_run_command_policy_default(self):
        """Test run command --policy defaults to policy.yml."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static"])
        
        assert args.policy == "policy.yml"

    def test_run_command_with_verbose(self):
        """Test run command with --verbose flag."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static", "--verbose"])
        
        assert args.verbose is True

    def test_run_command_verbose_default(self):
        """Test run command --verbose defaults to False."""
        parser = build_parser()
        args = parser.parse_args(["run", "-p", "static"])
        
        assert args.verbose is False

    def test_run_command_all_arguments_combined(self):
        """Test run command with all arguments combined."""
        parser = build_parser()
        args = parser.parse_args([
            "run",
            "-p", "static", "gemini",
            "--path", "/project",
            "--llm-local",
            "--github-repo", "org/repo",
            "--pr-id", "42",
            "--github-sha", "deadbeef",
            "--github-token", "secret",
            "--policy", "custom.yml",
            "--verbose"
        ])
        
        assert args.command == "run"
        assert args.provider == ["static", "gemini"]
        assert args.path == "/project"
        assert args.llm_local is True
        assert args.github_repo == "org/repo"
        assert args.pr_id == 42
        assert args.github_sha == "deadbeef"
        assert args.github_token == "secret"
        assert args.policy == "custom.yml"
        assert args.verbose is True

    def test_run_command_requires_provider(self):
        """Test that run command requires --provider argument."""
        parser = build_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["run"])

    def test_command_required(self):
        """Test that a command is required."""
        parser = build_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args([])
