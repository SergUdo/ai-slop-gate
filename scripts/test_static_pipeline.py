# python -m scripts.test_static_pipeline

from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider
from ai_slop_gate.domain.policy_engine import evaluate_policy
from ai_slop_gate.cli import load_policy_rules

provider = StaticPipelineProvider()
result = provider.collect()

rules = load_policy_rules("policy.yml")
decision = evaluate_policy(result.observations, rules)

print("Decision:", decision.mode.value)
for r in decision.reasons:
    print("-", r)
