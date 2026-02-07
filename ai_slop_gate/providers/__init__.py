# ai_slop_gate/providers/__init__.py

# Core registry - always available
from .registry import provider_registry, ProviderRegistry

# Lazy imports for providers to avoid dependency issues
def __getattr__(name):
    if name == "GeminiProvider":
        from .llm import GeminiProvider
        return GeminiProvider
    elif name == "StaticPipelineProvider":
        from .static import StaticPipelineProvider
        return StaticPipelineProvider
    elif name == "K8sRuntimeProvider":
        from .static import K8sRuntimeProvider
        return K8sRuntimeProvider
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "provider_registry", 
    "ProviderRegistry", 
    "GeminiProvider", 
    "StaticPipelineProvider", 
    "K8sRuntimeProvider"
]