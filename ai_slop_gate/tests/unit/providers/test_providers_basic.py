import importlib

MODULES = [
    "ai_slop_gate.providers.static.static",
    "ai_slop_gate.providers.static.static_js",
    "ai_slop_gate.providers.static.static_pipeline",
    "ai_slop_gate.providers.static.static_python",
    "ai_slop_gate.providers.static.static_ts_js",
    "ai_slop_gate.providers.static.static_docker",
    "ai_slop_gate.providers.static.supply_chain",
    "ai_slop_gate.providers.static.terraform_plan",
    "ai_slop_gate.providers.static.terraform_static",
    "ai_slop_gate.providers.static.k8s_static",
    "ai_slop_gate.providers.static.k8s_runtime",
    "ai_slop_gate.providers.registry",
]

# LLM modules that require optional dependencies
LLM_MODULES = [
    "ai_slop_gate.providers.llm.gemini",
]


def test_import_provider_modules():
    for m in MODULES:
        mod = importlib.import_module(m)
        assert mod is not None


def test_import_llm_provider_modules():
    """Test LLM provider imports - skip if optional dependencies are missing."""
    for m in LLM_MODULES:
        try:
            mod = importlib.import_module(m)
            assert mod is not None
        except ModuleNotFoundError as e:
            # Skip LLM modules if optional dependencies are not installed
            if "github" in str(e) or "genai" in str(e):
                pass
            else:
                raise
