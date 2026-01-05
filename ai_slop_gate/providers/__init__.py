from .registry import ProviderRegistry
from .eslint import ESLintProvider
from .static_pipeline import StaticPipelineProvider
from .k8s_runtime import K8sRuntimeProvider
from .terraform_plan import TerraformPlanProvider

provider_registry = ProviderRegistry()
provider_registry.register_defaults()
