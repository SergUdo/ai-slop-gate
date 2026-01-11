# ai_slop_gate/providers/__init__.py

from .registry import provider_registry, ProviderRegistry
from .gemini import GeminiProvider
from .static_pipeline import StaticPipelineProvider
from .k8s_runtime import K8sRuntimeProvider

__all__ = [
    "provider_registry", 
    "ProviderRegistry", 
    "GeminiProvider", 
    "StaticPipelineProvider", 
    "K8sRuntimeProvider"
]