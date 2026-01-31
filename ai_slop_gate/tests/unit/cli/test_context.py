import pytest
from ai_slop_gate.cli.context import RuntimeContext


class TestRuntimeContext:
    """Test suite for RuntimeContext dataclass."""

    def test_context_creation_minimal(self):
        """Test creating RuntimeContext with minimal required arguments."""
        ctx = RuntimeContext(
            providers=["static"],
            path="/test/path"
        )
        
        assert ctx.providers == ["static"]
        assert ctx.path == "/test/path"
        assert ctx.llm_local is False
        assert ctx.policy_path == "policy.yml"
        assert ctx.verbose is False

    def test_context_creation_with_defaults(self):
        """Test RuntimeContext uses default values."""
        ctx = RuntimeContext(
            providers=["gemini"],
            path="."
        )
        
        assert ctx.github_repo is None
        assert ctx.pr_id is None
        assert ctx.github_sha is None
        assert ctx.github_token is None
        assert ctx.llm_local is False
        assert ctx.policy_path == "policy.yml"
        assert ctx.verbose is False

    def test_context_creation_with_github_params(self):
        """Test RuntimeContext with GitHub PR parameters."""
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            github_repo="owner/repo",
            pr_id=123,
            github_sha="abc123",
            github_token="token"
        )
        
        assert ctx.github_repo == "owner/repo"
        assert ctx.pr_id == 123
        assert ctx.github_sha == "abc123"
        assert ctx.github_token == "token"

    def test_context_creation_with_llm_local(self):
        """Test RuntimeContext with llm_local enabled."""
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            llm_local=True
        )
        
        assert ctx.llm_local is True

    def test_context_creation_with_custom_policy_path(self):
        """Test RuntimeContext with custom policy path."""
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            policy_path="/custom/path/policy.yml"
        )
        
        assert ctx.policy_path == "/custom/path/policy.yml"

    def test_context_creation_with_verbose(self):
        """Test RuntimeContext with verbose flag."""
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            verbose=True
        )
        
        assert ctx.verbose is True

    def test_context_with_multiple_providers(self):
        """Test RuntimeContext with multiple providers."""
        providers = ["static", "gemini"]
        ctx = RuntimeContext(
            providers=providers,
            path="."
        )
        
        assert ctx.providers == providers
        assert len(ctx.providers) == 2

    def test_context_all_parameters(self):
        """Test RuntimeContext with all parameters specified."""
        ctx = RuntimeContext(
            providers=["static", "gemini"],
            path="/project",
            llm_local=True,
            github_repo="org/project",
            pr_id=42,
            github_sha="deadbeefcafe",
            github_token="ghp_secret",
            policy_path="policies/strict.yml",
            verbose=True
        )
        
        assert ctx.providers == ["static", "gemini"]
        assert ctx.path == "/project"
        assert ctx.llm_local is True
        assert ctx.github_repo == "org/project"
        assert ctx.pr_id == 42
        assert ctx.github_sha == "deadbeefcafe"
        assert ctx.github_token == "ghp_secret"
        assert ctx.policy_path == "policies/strict.yml"
        assert ctx.verbose is True

    def test_context_is_dataclass(self):
        """Test that RuntimeContext is a dataclass with proper attributes."""
        ctx = RuntimeContext(
            providers=["static"],
            path="."
        )
        
        # Check that it has __dataclass_fields__
        assert hasattr(ctx, '__dataclass_fields__')

    def test_context_immutability_fields(self):
        """Test that RuntimeContext fields can be accessed and are properly typed."""
        ctx = RuntimeContext(
            providers=["static"],
            path="/test"
        )
        
        # Can access all fields
        assert ctx.providers is not None
        assert ctx.path is not None
        assert ctx.policy_path is not None

    def test_context_pr_id_can_be_none(self):
        """Test that pr_id can be None."""
        ctx = RuntimeContext(
            providers=["static"],
            path="."
        )
        
        assert ctx.pr_id is None

    def test_context_pr_id_can_be_integer(self):
        """Test that pr_id can be an integer."""
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            pr_id=999
        )
        
        assert ctx.pr_id == 999
        assert isinstance(ctx.pr_id, int)

    def test_context_empty_providers_list(self):
        """Test RuntimeContext with empty providers list."""
        ctx = RuntimeContext(
            providers=[],
            path="."
        )
        
        assert ctx.providers == []
        assert len(ctx.providers) == 0

    def test_context_single_provider(self):
        """Test RuntimeContext with single provider."""
        ctx = RuntimeContext(
            providers=["static"],
            path="."
        )
        
        assert len(ctx.providers) == 1
        assert ctx.providers[0] == "static"

    def test_context_github_params_can_be_none(self):
        """Test that GitHub parameters default to None."""
        ctx = RuntimeContext(
            providers=["static"],
            path="."
        )
        
        assert ctx.github_repo is None
        assert ctx.pr_id is None
        assert ctx.github_sha is None
        assert ctx.github_token is None
