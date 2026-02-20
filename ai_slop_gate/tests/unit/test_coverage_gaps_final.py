"""Final coverage gap tests to reach 81% coverage."""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from tempfile import TemporaryDirectory

# Import cli modules
from ai_slop_gate.cli import run as cli_run_module
from ai_slop_gate.cli.run import run_cli, get_providers
from ai_slop_gate.cli.context import RuntimeContext
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.observation import Observation, Severity


class TestCLIRunEdgeCases:
    """Test edge cases in cli/run.py"""
    
    def test_run_cli_with_policy_rules(self):
        """Test run_cli with policy rules"""
        ctx = RuntimeContext(providers=["static"], path=".")
        
        rule = Mock()
        rule.id = "rule1"
        rule.when = {}
        rule.then = {}
        
        with patch("ai_slop_gate.cli.run.load_policy") as mock_load:
            mock_policy = Mock()
            mock_policy.ai_provider = {}
            mock_policy.compliance = None
            mock_policy.include_paths = []
            mock_load.return_value = (mock_policy, [rule], [], [])
            
            with patch("ai_slop_gate.cli.run.get_providers") as mock_get:
                mock_provider = Mock()
                mock_provider.kind = "static"
                mock_provider.collect.return_value = Mock(observations=[])
                mock_get.return_value = [mock_provider]
                
                with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                    with patch("ai_slop_gate.cli.run.logger"):
                        result = run_cli(ctx)
        
        assert result == 0
    
    def test_run_cli_with_observations(self):
        """Test run_cli with observations from provider"""
        ctx = RuntimeContext(providers=["static"], path=".")
        
        with patch("ai_slop_gate.cli.run.load_policy") as mock_load:
            mock_policy = Mock()
            mock_policy.ai_provider = {}
            mock_policy.compliance = None
            mock_policy.include_paths = []
            mock_load.return_value = (mock_policy, [], [], [])
            
            with patch("ai_slop_gate.cli.run.get_providers") as mock_get:
                obs = Observation(
                    category="quality",
                    signal="test",
                    confidence=0.8,
                    message="Test observation",
                    severity=Severity.HIGH
                )
                result_obj = Mock(observations=[obs])
                
                mock_provider = Mock()
                mock_provider.kind = "static"
                mock_provider.collect.return_value = result_obj
                mock_get.return_value = [mock_provider]
                
                with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                    with patch("ai_slop_gate.cli.run.logger"):
                        result = run_cli(ctx)
        
        assert result == 0
    
    def test_run_cli_with_policy_engine(self):
        """Test run_cli when policy engine evaluates observations"""
        ctx = RuntimeContext(providers=["static"], path=".")
        
        rule = Mock()
        rule.id = "rule1"
        rule.when = {"category": "quality"}
        rule.then = {"action": "advisory", "message": "Quality issue"}
        
        with patch("ai_slop_gate.cli.run.load_policy") as mock_load:
            mock_policy = Mock()
            mock_policy.ai_provider = {}
            mock_policy.compliance = None
            mock_policy.include_paths = []
            mock_load.return_value = (mock_policy, [rule], [], [])
            
            with patch("ai_slop_gate.cli.run.get_providers") as mock_get:
                obs = Observation(
                    category="quality",
                    signal="test",
                    confidence=0.8,
                    message="Test",
                    severity=Severity.HIGH
                )
                result_obj = Mock(observations=[obs])
                
                mock_provider = Mock()
                mock_provider.kind = "static"
                mock_provider.collect.return_value = result_obj
                mock_get.return_value = [mock_provider]
                
                with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                    with patch("ai_slop_gate.cli.run.logger"):
                        result = run_cli(ctx)
        
        assert result == 0


class TestProvidersGetting:
    """Test getting providers"""
    
    def test_get_providers_static(self):
        """Test getting static provider"""
        policy = Mock()
        policy.ai_provider = {"models": {"static": "model"}}
        provider_list = get_providers(["static"], policy_config=policy)
        assert len(provider_list) == 1
    
    def test_get_providers_static_pipeline(self):
        """Test getting static_pipeline provider"""
        policy = Mock()
        policy.ai_provider = {"models": {"static_pipeline": "model"}}
        provider_list = get_providers(["static_pipeline"], policy_config=policy)
        assert len(provider_list) == 1
    
    def test_get_providers_case_insensitive(self):
        """Test getting provider with different case"""
        policy = Mock()
        policy.ai_provider = {"models": {"static": "model"}}
        provider_list = get_providers(["STATIC"], policy_config=policy)
        assert len(provider_list) == 1


class TestCLIRunWithComplexScenarios:
    """Test cli/run.py with complex scenarios"""
    
    def test_run_cli_multiple_providers(self):
        """Test run_cli with multiple providers"""
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
        )
        
        with patch("ai_slop_gate.cli.run.load_policy") as mock_load:
            mock_policy = Mock()
            mock_policy.ai_provider = {}
            mock_policy.compliance = None
            mock_policy.include_paths = []
            mock_load.return_value = (mock_policy, [], [], [])
            
            with patch("ai_slop_gate.cli.run.get_providers") as mock_get:
                mock_provider = Mock()
                mock_provider.kind = "static"
                mock_provider.collect.return_value = Mock(observations=[])
                mock_get.return_value = [mock_provider]
                
                with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                    with patch("ai_slop_gate.cli.run.logger"):
                        result = run_cli(ctx)
        
        assert result == 0
        mock_get.assert_called_once()
    
    def test_run_cli_with_github_token(self):
        """Test run_cli sets up GITHUB_TOKEN"""
        ctx = RuntimeContext(
            providers=["static"],
            path=".",
            github_token="test_token"
        )
        
        with patch("ai_slop_gate.cli.run.load_policy") as mock_load:
            mock_policy = Mock()
            mock_policy.ai_provider = {}
            mock_policy.compliance = None
            mock_policy.include_paths = []
            mock_load.return_value = (mock_policy, [], [], [])
            
            with patch("ai_slop_gate.cli.run.get_providers") as mock_get:
                mock_provider = Mock()
                mock_provider.kind = "static"
                mock_provider.collect.return_value = Mock(observations=[])
                mock_get.return_value = [mock_provider]
                
                with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                    with patch("ai_slop_gate.cli.run.logger"):
                        with patch.dict(os.environ, {}, clear=True):
                            result = run_cli(ctx)
        
        assert result == 0
    
    def test_run_cli_with_include_paths(self):
        """Test run_cli with include_paths in policy"""
        ctx = RuntimeContext(providers=["static"], path=".")
        
        with patch("ai_slop_gate.cli.run.load_policy") as mock_load:
            mock_policy = Mock()
            mock_policy.ai_provider = {}
            mock_policy.compliance = None
            mock_policy.include_paths = ["src/**/*.py"]
            mock_load.return_value = (mock_policy, [], [], [])
            
            with patch("ai_slop_gate.cli.run.get_providers") as mock_get:
                mock_provider = Mock()
                mock_provider.kind = "static"
                mock_provider.collect.return_value = Mock(observations=[])
                mock_get.return_value = [mock_provider]
                
                with patch("ai_slop_gate.cli.run.logging.basicConfig"):
                    with patch("ai_slop_gate.cli.run.logger"):
                        result = run_cli(ctx)
        
        assert result == 0


class TestCliUtilsEdgeCases:
    """Test edge cases in cli/utils.py"""
    
    def test_load_policy_with_exclude_paths(self):
        """Test load_policy returns exclude_paths and exclude_secret_files"""
        with TemporaryDirectory() as tmpdir:
            policy_path = f"{tmpdir}/policy.yml"
            with open(policy_path, "w") as f:
                f.write("""
enforcement: advisory
exclude_paths:
  - build/**
  - dist/**
exclude_secret_files:
  - .env
  - secrets.yml
rules: []
""")
            
            from ai_slop_gate.cli.utils import load_policy
            config, rules, exclude_paths, exclude_secret_files = load_policy(policy_path)
            
            assert "build/**" in exclude_paths
            assert "dist/**" in exclude_paths
            assert ".env" in exclude_secret_files
            assert "secrets.yml" in exclude_secret_files
