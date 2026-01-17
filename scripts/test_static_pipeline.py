# python -m scripts.test_static_pipeline
# python -m ai_slop_gate.cli run --policy policy.yml --provider static

# scripts/test_static_pipeline.py
from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.cli.utils import load_policy

policy_config, rules = load_policy("policy.yml")

provider = StaticPipelineProvider()
result = provider.collect()

engine = PolicyEngine(rules)
decision = engine.evaluate(result.observations)

print("Decision:", decision.mode.value)
for reason in decision.reasons:
    print("-", reason)

