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

    def register_defaults(self):
        self.register("eslint", ESLintProvider)
        self.register("static", StaticPipelineProvider)
        self.register("terraform-static", TerraformStaticProvider)
        self.register("terraform-plan", TerraformPlanProvider)
        self.register("k8s-static", KubernetesStaticProvider)
        self.register("k8s-runtime", K8sRuntimeProvider)

    def register(self, name: str, provider: Any):
        self._providers[name] = provider

    def get(self, name: str):
        if name not in self._providers:
            raise ValueError(f"Unknown provider: {name}")
        return self._providers[name]

    def all(self):
        return list(self._providers.values())

provider_registry = ProviderRegistry()
provider_registry.register_defaults()