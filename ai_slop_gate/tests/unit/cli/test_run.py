# import pytest
# import os
# from unittest.mock import patch, MagicMock
# from ai_slop_gate.cli.run import run_cli, get_providers, PROVIDER_MAP
# from ai_slop_gate.cli.context import RuntimeContext


# # -------------------------------------------------------------------
# # Helper: Fake policy config for strict-mode model resolver
# # -------------------------------------------------------------------
# class FakePolicy:
#     def __init__(self):
#         self.ai_provider = {
#             "models": {
#                 "static": "static-model",
#                 "gemini": "gemini-2.5-flash",
#                 "groq": "llama-3.3-70b-versatile",
#             }
#         }
#         self.include_paths = []
#         self.compliance = None


# # -------------------------------------------------------------------
# # PROVIDER MAP TESTS
# # -------------------------------------------------------------------
# class TestProviderMap:
#     def test_provider_map_contains_static(self):
#         assert "static" in PROVIDER_MAP
#         assert "static_pipeline" in PROVIDER_MAP

#     def test_provider_map_contains_gemini(self):
#         assert "gemini" in PROVIDER_MAP

#     def test_provider_map_static_and_static_pipeline_same(self):
#         assert PROVIDER_MAP["static"] == PROVIDER_MAP["static_pipeline"]


# # -------------------------------------------------------------------
# # GET PROVIDERS TESTS (strict-mode aware)
# # -------------------------------------------------------------------
# class TestGetProviders:
#     def test_get_providers_single_provider(self):
#         policy = FakePolicy()
#         providers = get_providers(["static"], policy_config=policy)
#         assert len(providers) == 1

#     def test_get_providers_multiple_providers(self):
#         policy = FakePolicy()
#         with patch("ai_slop_gate.cli.run.GeminiProvider") as mock_gemini:
#             mock_gemini.return_value = MagicMock()
#             providers = get_providers(["gemini"], policy_config=policy)
#             assert len(providers) == 1

#     def test_get_providers_case_insensitive(self):
#         policy = FakePolicy()
#         p1 = get_providers(["STATIC"], policy_config=policy)
#         p2 = get_providers(["Static"], policy_config=policy)
#         p3 = get_providers(["static"], policy_config=policy)
#         assert len(p1) == len(p2) == len(p3) == 1

#     def test_get_providers_invalid_provider_raises_error(self):
#         policy = FakePolicy()
#         with pytest.raises(ValueError, match="Unknown provider"):
#             get_providers(["invalid"], policy_config=policy)

#     def test_get_providers_empty_list(self):
#         policy = FakePolicy()
#         providers = get_providers([], policy_config=policy)
#         assert providers == []

#     def test_get_providers_static_pipeline_alias(self):
#         policy = FakePolicy()
#         with patch("ai_slop_gate.cli.run.StaticPipelineProvider") as mock_static:
#             mock_static.return_value = MagicMock()
#             p1 = get_providers(["static"], policy_config=policy)
#             p2 = get_providers(["static_pipeline"], policy_config=policy)
#             assert len(p1) == 1
#             assert len(p2) == 1

#     def test_get_providers_missing_model_strict_mode_llm_only(self):
#         """Strict-mode error should occur ONLY for LLM providers, not static."""
#         policy = FakePolicy()

#         # Remove model for gemini (LLM provider)
#         policy.ai_provider["models"].pop("gemini")

#         with pytest.raises(ValueError, match="STRICT MODE"):
#             get_providers(["gemini"], policy_config=policy)

#     def test_get_providers_missing_model_static_no_error(self):
#         """Static providers do NOT require a model."""
#         policy = FakePolicy()
#         policy.ai_provider["models"].pop("static")  # should NOT raise

#         providers = get_providers(["static"], policy_config=policy)
#         assert len(providers) == 1



# # -------------------------------------------------------------------
# # RUN CLI TESTS
# # -------------------------------------------------------------------
# class TestRunCli:
#     @pytest.fixture
#     def mock_context(self):
#         return RuntimeContext(
#             providers=["static"],
#             path=".",
#             github_token=None,
#             policy_path="policy.yml",
#             verbose=False
#         )

#     @patch("ai_slop_gate.cli.run.load_policy")
#     @patch("ai_slop_gate.cli.run.get_providers")
#     def test_run_cli_basic(self, mock_get_providers, mock_load_policy, mock_context):
#         mock_policy = FakePolicy()
#         mock_load_policy.return_value = (mock_policy, [])
#         mock_get_providers.return_value = [MagicMock(kind="static", collect=lambda base_path: MagicMock(observations=[]))]

#         with patch("ai_slop_gate.cli.run.logging.basicConfig"):
#             with patch("ai_slop_gate.cli.run.logger"):
#                 result = run_cli(mock_context)

#         mock_load_policy.assert_called_once_with("policy.yml")
#         assert result == 0

#     @patch("ai_slop_gate.cli.run.load_policy")
#     def test_run_cli_loads_policy_file(self, mock_load_policy, mock_context):
#         mock_load_policy.return_value = (FakePolicy(), [])
#         with patch("ai_slop_gate.cli.run.get_providers"):
#             with patch("ai_slop_gate.cli.run.logging.basicConfig"):
#                 with patch("ai_slop_gate.cli.run.logger"):
#                     run_cli(mock_context)
#         mock_load_policy.assert_called_once_with("policy.yml")

#     @patch("ai_slop_gate.cli.run.load_policy")
#     def test_run_cli_custom_policy_path(self, mock_load_policy):
#         mock_load_policy.return_value = (FakePolicy(), [])
#         ctx = RuntimeContext(providers=["static"], path=".", policy_path="custom/policy.yml")

#         with patch("ai_slop_gate.cli.run.get_providers"):
#             with patch("ai_slop_gate.cli.run.logging.basicConfig"):
#                 with patch("ai_slop_gate.cli.run.logger"):
#                     run_cli(ctx)

#         mock_load_policy.assert_called_once_with("custom/policy.yml")

#     @patch("ai_slop_gate.cli.run.load_policy")
#     @patch("ai_slop_gate.cli.run.get_providers")
#     def test_run_cli_gets_providers(self, mock_get_providers, mock_load_policy, mock_context):
#         mock_load_policy.return_value = (FakePolicy(), [])
#         mock_get_providers.return_value = [MagicMock(kind="static", collect=lambda base_path: MagicMock(observations=[]))]

#         with patch("ai_slop_gate.cli.run.logging.basicConfig"):
#             with patch("ai_slop_gate.cli.run.logger"):
#                 run_cli(mock_context)

#         mock_get_providers.assert_called()

#     @patch("ai_slop_gate.cli.run.load_policy")
#     @patch("ai_slop_gate.cli.run.get_providers")
#     @patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"})
#     def test_run_cli_uses_env_github_token(self, mock_get_providers, mock_load_policy, mock_context):
#         mock_load_policy.return_value = (FakePolicy(), [])
#         mock_get_providers.return_value = [MagicMock(kind="static", collect=lambda base_path: MagicMock(observations=[]))]

#         with patch("ai_slop_gate.cli.run.logging.basicConfig"):
#             with patch("ai_slop_gate.cli.run.logger"):
#                 run_cli(mock_context)

#         assert os.getenv("GITHUB_TOKEN") == "env_token"

#     @patch("ai_slop_gate.cli.run.load_policy")
#     @patch("ai_slop_gate.cli.run.get_providers")
#     def test_run_cli_sets_up_logging(self, mock_get_providers, mock_load_policy):
#         mock_load_policy.return_value = (FakePolicy(), [])
#         mock_get_providers.return_value = [MagicMock(kind="static", collect=lambda base_path: MagicMock(observations=[]))]

#         ctx = RuntimeContext(providers=["static"], path=".", verbose=True)

#         with patch("ai_slop_gate.cli.run.logging.basicConfig") as mock_basic:
#             with patch("ai_slop_gate.cli.run.logger"):
#                 run_cli(ctx)

#         mock_basic.assert_called_once()

#     @patch("ai_slop_gate.cli.run.load_policy")
#     @patch("ai_slop_gate.cli.run.get_providers")
#     def test_run_cli_logs_starting_message(self, mock_get_providers, mock_load_policy):
#         mock_load_policy.return_value = (FakePolicy(), [])
#         mock_get_providers.return_value = [MagicMock(kind="static", collect=lambda base_path: MagicMock(observations=[]))]

#         with patch("ai_slop_gate.cli.run.logging.basicConfig"):
#             with patch("ai_slop_gate.cli.run.logger") as mock_logger:
#                 run_cli(RuntimeContext(providers=["static"], path="."))

#         assert mock_logger.info.call_count >= 1

#     @patch("ai_slop_gate.cli.run.load_policy")
#     @patch("ai_slop_gate.cli.run.get_providers")
#     def test_run_cli_github_context_parameters(self, mock_get_providers, mock_load_policy):
#         mock_load_policy.return_value = (FakePolicy(), [])
#         mock_get_providers.return_value = [MagicMock(kind="static", collect=lambda base_path: MagicMock(observations=[]))]

#         ctx = RuntimeContext(
#             providers=["static"],
#             path=".",
#             github_repo="owner/repo",
#             pr_id=123,
#             github_sha="abc123",
#             github_token="token123"
#         )

#         with patch("ai_slop_gate.cli.run.logging.basicConfig"):
#             with patch("ai_slop_gate.cli.run.logger"):
#                 run_cli(ctx)

#         assert ctx.github_repo == "owner/repo"
#         assert ctx.pr_id == 123
#         assert ctx.github_sha == "abc123"
#         assert ctx.github_token == "token123"
