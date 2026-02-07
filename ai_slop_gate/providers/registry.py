from typing import Any


class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, Any] = {}
        self._defaults_registered = False

    def register(self, name: str, provider_cls: Any):
        self._providers[name] = provider_cls

    def get(self, name: str):
        if not self._defaults_registered:
            self.register_defaults()
        return self._providers.get(name)

    def register_defaults(self):
        """Register all default providers."""
        if self._defaults_registered:
            return
            
        # Lazy imports to avoid dependency issues
        from .static import (
            TerraformStaticProvider,
            KubernetesStaticProvider,
            TerraformPlanProvider,
            ESLintProvider,
            StaticPipelineProvider,
            K8sRuntimeProvider,
            SupplyChainProvider,
            StaticTSJSProvider,
            StaticPythonProvider,
            StaticDockerProvider,
        )
        from .cached_provider import CachedProvider
        
        self.register("static", StaticPipelineProvider)
        self.register("eslint", ESLintProvider)
        self.register("static-ts-js", StaticTSJSProvider)
        self.register("static-python", StaticPythonProvider)
        self.register("static-docker", StaticDockerProvider)
        self.register("terraform-plan", TerraformPlanProvider)
        self.register("k8s-runtime", K8sRuntimeProvider)
        self.register("terraform-static", TerraformStaticProvider)
        self.register("k8s-static", KubernetesStaticProvider)
        self.register("supply-chain", SupplyChainProvider)
        self.register("cached", CachedProvider)
        
        # Try to import LLM providers, but don't fail if dependencies are missing
        try:
            from .llm import GeminiProvider, GroqProvider
            self.register("gemini", GeminiProvider)
            self.register("groq", GroqProvider)
        except ImportError:
            # LLM providers require additional dependencies that may not be installed
            pass
        
        self._defaults_registered = True

provider_registry = ProviderRegistry()