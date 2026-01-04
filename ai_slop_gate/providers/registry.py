from ai_slop_gate.providers.terraform_static import TerraformStaticProvider
from ai_slop_gate.providers.k8s_static import KubernetesStaticProvider


class ProviderRegistry:
    def __init__(self):
        self._providers = {}

    def register_defaults(self):
        self.register(TerraformStaticProvider())
        self.register(KubernetesStaticProvider())

    def register(self, provider):
        self._providers[provider.name] = provider

    def get(self, name):
        return self._providers[name]

    def all(self):
        return list(self._providers.values())
