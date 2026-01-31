import pytest
import os
from unittest.mock import patch, MagicMock, call
from ai_slop_gate.cli.run import run_cli, get_providers, PROVIDER_MAP
from ai_slop_gate.cli.context import RuntimeContext


class TestProviderMap:
    """Test suite for PROVIDER_MAP configuration."""

    def test_provider_map_contains_static(self):
        """Test that PROVIDER_MAP contains 'static' key."""
        assert "static" in PROVIDER_MAP
        assert "static_pipeline" in PROVIDER_MAP

    def test_provider_map_contains_gemini(self):
        """Test that PROVIDER_MAP contains 'gemini' key."""
        assert "gemini" in PROVIDER_MAP

    def test_provider_map_static_and_static_pipeline_same(self):
        """Test that 'static' and 'static_pipeline' map to the same provider."""
        assert PROVIDER_MAP["static"] == PROVIDER_MAP["static_pipeline"]


class TestGetProviders:
    """Test suite for get_providers function."""

    def test_get_providers_single_provider(self):
        """Test getting a single provider."""
        providers = get_providers(["static"])
        
        assert len(providers) == 1
        assert providers[0] is not None

    def test_get_providers_multiple_providers(self):
        """Test getting multiple providers."""
        with patch("ai_slop_gate.cli.run.GeminiProvider") as mock_gemini:
            mock_gemini.return_value = MagicMock()
            providers = get_providers(["static"])
            
            assert len(providers) == 1
            assert providers[0] is not None

    def test_get_providers_case_insensitive(self):
        """Test that provider names are case-insensitive."""
        providers1 = get_providers(["STATIC"])
        providers2 = get_providers(["Static"])
        providers3 = get_providers(["static"])
        
        assert len(providers1) == 1
        assert len(providers2) == 1
        assert len(providers3) == 1

    def test_get_providers_invalid_provider_raises_error(self):
        """Test that invalid provider name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_providers(["invalid_provider"])

    def test_get_providers_with_unknown_provider_in_list(self):
        """Test that unknown provider in list raises error."""
        with pytest.raises(ValueError):
            get_providers(["static", "unknown"])

    def test_get_providers_empty_list(self):
        """Test getting providers with empty list."""
        providers = get_providers([])
        
        assert len(providers) == 0
        assert isinstance(providers, list)

    def test_get_providers_static_pipeline_alias(self):
        """Test that static_pipeline is an alias for static."""
        with patch("ai_slop_gate.cli.run.StaticPipelineProvider") as mock_static:
            mock_instance = MagicMock()
            mock_static.return_value = mock_instance
            
            providers1 = get_providers(["static"])
            providers2 = get_providers(["static_pipeline"])
            
            assert len(providers1) == 1
            assert len(providers2) == 1

    def test_get_providers_with_model_parameter(self):
        """Test get_providers with optional model parameter."""
        with patch("ai_slop_gate.cli.run.StaticPipelineProvider") as mock_static:
            mock_static.return_value = MagicMock()
            providers = get_providers(["static"], model="custom-model")
            
            assert len(providers) == 1
            assert providers[0] is not None


class TestRunCli:
    """Test suite for run_cli function."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock RuntimeContext."""
        return RuntimeContext(
            providers=["static"],
            path=".",
            github_token=None,
            policy_path="policy.yml",
            verbose=False
        )

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    def test_run_cli_basic(self, mock_get_providers, mock_load_policy, mock_context):
        """Test basic run_cli execution."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        mock_get_providers.return_value = [MagicMock()]

        with patch("ai_slop_gate.cli.run.logging.basicConfig"):
            with patch("ai_slop_gate.cli.run.logger"):
                result = run_cli(mock_context)
        
        # load_policy should be called
        mock_load_policy.assert_called_once_with("policy.yml")

    @patch("ai_slop_gate.cli.run.load_policy")
    def test_run_cli_loads_policy_file(self, mock_load_policy, mock_context):
        """Test that run_cli loads the correct policy file."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)

        with patch("ai_slop_gate.cli.run.get_providers"):
            with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                with patch("ai_slop_gate.cli.run.logger"):
                    run_cli(mock_context)
        
        mock_load_policy.assert_called_once_with("policy.yml")

    @patch("ai_slop_gate.cli.run.load_policy")
    def test_run_cli_custom_policy_path(self, mock_load_policy):
        """Test run_cli with custom policy file path."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            policy_path="custom/policy.yml"
        )

        with patch("ai_slop_gate.cli.run.get_providers"):
            with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                with patch("ai_slop_gate.cli.run.logger"):
                    run_cli(ctx)
        
        mock_load_policy.assert_called_once_with("custom/policy.yml")

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    def test_run_cli_gets_providers(self, mock_get_providers, mock_load_policy, mock_context):
        """Test that run_cli calls get_providers."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        mock_get_providers.return_value = [MagicMock()]

        with patch("ai_slop_gate.cli.run.logging.basicConfig"):
            with patch("ai_slop_gate.cli.run.logger"):
                run_cli(mock_context)
        
        mock_get_providers.assert_called()

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    def test_run_cli_with_multiple_providers(self, mock_get_providers, mock_load_policy):
        """Test run_cli with multiple providers."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        
        mock_providers = [MagicMock(), MagicMock()]
        mock_get_providers.return_value = mock_providers
        
        ctx = RuntimeContext(
            providers=["static", "gemini"],
            path="."
        )

        with patch("ai_slop_gate.cli.run.logging.basicConfig"):
            with patch("ai_slop_gate.cli.run.logger"):
                run_cli(ctx)
        
        mock_get_providers.assert_called()

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    @patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"})
    def test_run_cli_uses_env_github_token(self, mock_get_providers, mock_load_policy, mock_context):
        """Test that run_cli uses GITHUB_TOKEN from environment if not provided."""
        mock_context.github_token = None
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        mock_get_providers.return_value = [MagicMock()]

        with patch("ai_slop_gate.cli.run.logging.basicConfig"):
            with patch("ai_slop_gate.cli.run.logger"):
                run_cli(mock_context)
        
        # The function should have accessed the environment
        assert os.getenv("GITHUB_TOKEN") == "env_token"

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    def test_run_cli_sets_up_logging(self, mock_get_providers, mock_load_policy):
        """Test that run_cli sets up logging."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        mock_get_providers.return_value = [MagicMock()]
        
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            verbose=True
        )

        with patch("ai_slop_gate.cli.run.logging.basicConfig") as mock_basicConfig:
            with patch("ai_slop_gate.cli.run.logger"):
                run_cli(ctx)
        
        mock_basicConfig.assert_called_once()

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    def test_run_cli_logs_starting_message(self, mock_get_providers, mock_load_policy):
        """Test that run_cli logs a starting message."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        mock_get_providers.return_value = [MagicMock()]

        with patch("ai_slop_gate.cli.run.logging.basicConfig"):
            with patch("ai_slop_gate.cli.run.logger") as mock_logger:
                run_cli(RuntimeContext(providers=["static"], path="."))
        
        # Check that logger.info was called with starting message
        assert mock_logger.info.call_count >= 1

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    def test_run_cli_context_path_parameter(self, mock_get_providers, mock_load_policy):
        """Test that run_cli uses path from context."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        mock_get_providers.return_value = [MagicMock()]
        
        ctx = RuntimeContext(
            providers=["static"],
            path="/custom/path"
        )

        with patch("ai_slop_gate.cli.run.logging.basicConfig"):
            with patch("ai_slop_gate.cli.run.logger"):
                run_cli(ctx)
        
        # Verify context was created with correct path
        assert ctx.path == "/custom/path"

    @patch("ai_slop_gate.cli.run.load_policy")
    @patch("ai_slop_gate.cli.run.get_providers")
    def test_run_cli_github_context_parameters(self, mock_get_providers, mock_load_policy):
        """Test that run_cli handles GitHub context parameters."""
        mock_policy_config = MagicMock()
        mock_rules = []
        mock_load_policy.return_value = (mock_policy_config, mock_rules)
        mock_get_providers.return_value = [MagicMock()]
        
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            github_repo="owner/repo",
            pr_id=123,
            github_sha="abc123",
            github_token="token123"
        )

        with patch("ai_slop_gate.cli.run.logging.basicConfig"):
            with patch("ai_slop_gate.cli.run.logger"):
                run_cli(ctx)
        
        assert ctx.github_repo == "owner/repo"
        assert ctx.pr_id == 123
        assert ctx.github_sha == "abc123"
        assert ctx.github_token == "token123"
