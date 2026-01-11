from typing import Any

from .terraform_static import TerraformStaticProvider
from .k8s_static import KubernetesStaticProvider
from .terraform_plan import TerraformPlanProvider
from .eslint import ESLintProvider
from .static_pipeline import StaticPipelineProvider
from .k8s_runtime import K8sRuntimeProvider
from .supply_chain import SupplyChainProvider

class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, Any] = {}

    def register(self, name: str, provider_cls: Any):
        self._providers[name] = provider_cls

    def get(self, name: str):
        if name not in self._providers:
            raise ValueError(f"Unknown provider: {name}")
        return self._providers[name]

    def register_defaults(self):
        """Register all default providers."""
        self.register("static", StaticPipelineProvider)
        self.register("eslint", ESLintProvider)
        self.register("terraform-plan", TerraformPlanProvider)
        self.register("k8s-runtime", K8sRuntimeProvider)
        self.register("terraform-static", TerraformStaticProvider)
        self.register("k8s-static", KubernetesStaticProvider)
        self.register("supply-chain", SupplyChainProvider)

# --- Singleton instance ---
provider_registry = ProviderRegistry()
provider_registry.register_defaults()