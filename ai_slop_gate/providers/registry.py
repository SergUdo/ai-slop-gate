from typing import Any

from .terraform_static import TerraformStaticProvider
from .k8s_static import KubernetesStaticProvider
from .terraform_plan import TerraformPlanProvider
from .eslint import ESLintProvider
from .static_pipeline import StaticPipelineProvider
from .k8s_runtime import K8sRuntimeProvider

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

# --- Register all default providers ---
provider_registry = ProviderRegistry()
provider_registry.register("static", StaticPipelineProvider)
provider_registry.register("eslint", ESLintProvider)
provider_registry.register("terraform-plan", TerraformPlanProvider)
provider_registry.register("k8s-runtime", K8sRuntimeProvider)

# Optional static infra providers
provider_registry.register("terraform-static", TerraformStaticProvider)
provider_registry.register("k8s-static", KubernetesStaticProvider)
