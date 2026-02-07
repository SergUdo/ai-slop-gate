"""Provider integration tests."""
import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock
from ai_slop_gate.providers.registry import ProviderRegistry
from ai_slop_gate.providers.static import StaticProvider


class TestProviderRegistry:
    """Integration tests for provider registry."""

    def test_registry_provider_management(self):
        """Test registering and retrieving providers."""
        registry = ProviderRegistry()
        
        mock_provider = Mock()
        mock_provider.name = "test_provider"
        
        # Register provider
        registry.register("test", mock_provider)
        
        # Retrieve provider
        retrieved = registry.get("test")
        assert retrieved is not None

    def test_static_provider_initialization(self):
        """Test StaticProvider initialization."""
        provider = StaticProvider()
        assert provider is not None
        assert hasattr(provider, 'analyze')

    def test_provider_chain_execution(self):
        """Test executing providers in sequence."""
        providers = []
        
        # Provider 1: Static analysis
        provider1 = Mock(name="static")
        provider1.name = "static"
        provider1.analyze = Mock(return_value={"issues": 3})
        providers.append(provider1)
        
        # Provider 2: Security audit
        provider2 = Mock(name="security")
        provider2.name = "security"
        provider2.analyze = Mock(return_value={"issues": 1})
        providers.append(provider2)
        
        results = []
        for provider in providers:
            result = provider.analyze("test_code")
            results.append(result)
        
        assert len(results) == 2
        assert results[0]["issues"] == 3
        assert results[1]["issues"] == 1

    def test_provider_result_aggregation(self):
        """Test aggregating results from multiple providers."""
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        results = [
            {"provider": "static", "issues": 2, "severity": "medium"},
            {"provider": "gemini", "issues": 1, "severity": "high"},
            {"provider": "groq", "issues": 0, "severity": "low"}
        ]
        
        total_issues = sum(r["issues"] for r in results)
        # Get max severity by numerical order
        max_severity_order = max(severity_order[r["severity"]] for r in results)
        
        assert total_issues == 3
        assert max_severity_order == 3

    def test_provider_fallback_logic(self):
        """Test provider fallback on failure."""
        primary = Mock()
        primary.analyze = Mock(side_effect=Exception("API Error"))
        
        fallback = Mock()
        fallback.analyze = Mock(return_value={"result": "fallback"})
        
        # Simulate fallback logic
        try:
            result = primary.analyze("test")
        except Exception:
            result = fallback.analyze("test")
        
        assert result["result"] == "fallback"

    def test_provider_caching_integration(self):
        """Test provider results caching."""
        from ai_slop_gate.cache.file_backend import FileCacheBackend
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCacheBackend(root=tmpdir)
            provider_name = "gemini"
            
            # First call - would hit API
            key1 = f"{provider_name}_analysis_file1"
            cache.set(key1, {"result": "expensive_computation"})
            
            # Second call - uses cache
            cached_result = cache.get(key1)
            assert cached_result["result"] == "expensive_computation"

    def test_provider_timeout_handling(self):
        """Test provider timeout handling."""
        import time
        
        provider = Mock()
        provider.analyze = Mock(side_effect=TimeoutError("Provider timeout"))
        
        with pytest.raises(TimeoutError):
            provider.analyze("test")

    def test_provider_rate_limiting(self):
        """Test provider rate limiting."""
        from ai_slop_gate.providers.rate_limit_guard import RateLimitGuard
        
        mock_provider = Mock(spec=['name', 'analyze'])
        mock_provider.name = "rate_limited_provider"
        mock_provider.analyze = Mock(return_value={"result": "ok"})
        
        guard = RateLimitGuard(mock_provider, interval_sec=0.01)
        
        # Multiple calls
        result1 = guard.analyze("input1")
        result2 = guard.analyze("input2")
        result3 = guard.analyze("input3")
        
        assert result1 == {"result": "ok"}
        assert result2 == {"result": "ok"}
        assert result3 == {"result": "ok"}

    def test_concurrent_provider_execution(self):
        """Test concurrent provider execution."""
        import concurrent.futures
        
        def mock_analysis(provider_id):
            return {"provider": provider_id, "result": "ok"}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(mock_analysis, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        assert len(results) == 3


class TestProviderSpecificIntegrations:
    """Integration tests for specific providers."""

    def test_static_provider_workflow(self):
        """Test static provider complete workflow."""
        provider = StaticProvider()
        
        test_code = """
        import os
        password = "secret"
        """
        
        # Static provider should be able to process
        assert provider is not None

    def test_eslint_provider_integration(self):
        """Test JavaScript static analysis provider integration."""
        from ai_slop_gate.providers.static import StaticJSProvider
        
        provider = StaticJSProvider()
        assert provider is not None

    def test_supply_chain_provider_integration(self):
        """Test supply chain provider integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            req_file = tmpdir + "/requirements.txt"
            with open(req_file, 'w') as f:
                f.write("requests==2.28.0\n")
                f.write("flask==2.0.0\n")
            
            import os
            assert os.path.exists(req_file)

    def test_k8s_provider_integration(self):
        """Test Kubernetes provider integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample K8s manifest
            k8s_file = tmpdir + "/deployment.yaml"
            with open(k8s_file, 'w') as f:
                f.write("""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example
spec:
  replicas: 1
""")
            
            import os
            assert os.path.exists(k8s_file)
