import importlib

MODULES = [
    "ai_slop_gate.providers.static",
    "ai_slop_gate.providers.static_js",
    "ai_slop_gate.providers.static_pipeline",
    "ai_slop_gate.providers.static_python",
    "ai_slop_gate.providers.static_ts_js",
    "ai_slop_gate.providers.static_docker",
    "ai_slop_gate.providers.supply_chain",
    "ai_slop_gate.providers.terraform_plan",
    "ai_slop_gate.providers.terraform_static",
    "ai_slop_gate.providers.k8s_static",
    "ai_slop_gate.providers.k8s_runtime",
    "ai_slop_gate.providers.gemini",
    "ai_slop_gate.providers.registry",
]


def test_import_provider_modules():
    for m in MODULES:
        mod = importlib.import_module(m)
        assert mod is not None
