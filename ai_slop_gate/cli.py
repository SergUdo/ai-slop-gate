import argparse
import sys
import yaml
import os
from dataclasses import dataclass

from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider
from ai_slop_gate.domain.policy_engine import PolicyRule, evaluate_policy
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.github.pr_commenter import publish_pr_comment

@dataclass(frozen=True)
class PolicyRule:
    id: str
    category: str
    signal: str
    min_confidence: float
    action: str
    message: str

def load_policy_rules(path: str) -> list[PolicyRule]:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    rules = []
    for rule in raw.get("rules", []):
        rules.append(
            PolicyRule(
                id=rule["id"],
                category=rule["when"]["category"],
                signal=rule["when"]["signal"],
                min_confidence=rule["when"].get("min_confidence", 0.0),
                action=rule["then"]["action"],
                message=rule["then"]["message"],
            )
        )

    return rules

def main() -> None:
    parser = argparse.ArgumentParser("ai-slop-gate")
    parser.add_argument("--policy", required=True)
    parser.add_argument("--provider", default="static")
    parser.add_argument("--advisory-only", action="store_true")

    args = parser.parse_args()

    if args.provider == "static":
        provider = StaticPipelineProvider()
    else:
        raise ValueError(f"Unknown provider: {args.provider}")

    provider_observation = provider.collect()
    observations = provider_observation.observations

    rules = load_policy_rules(args.policy)
    decision = evaluate_policy(observations, rules)

    print(f"\nDecision: {decision.mode.value.upper()}")
    for reason in decision.reasons:
        print(f"- {reason}")

    if os.getenv("AI_SLOP_GATE_TOKEN") and os.getenv("GITHUB_REPOSITORY"):
        publish_pr_comment(decision)

    if decision.mode == DecisionMode.BLOCKING and not args.advisory_only:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
