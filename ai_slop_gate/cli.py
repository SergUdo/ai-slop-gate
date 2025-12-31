import argparse
import sys
import yaml

from ai_slop_gate.providers.static import StaticProvider
from ai_slop_gate.domain.policy_engine import PolicyRule, evaluate_policy
from ai_slop_gate.domain.decision import DecisionMode


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

    args = parser.parse_args()

    # --- provider selection (MVP) ---
    if args.provider == "static":
        provider = StaticProvider()
    else:
        raise ValueError(f"Unknown provider: {args.provider}")

    provider_observation = provider.observe()
    observations = provider_observation.observations

    rules = load_policy_rules(args.policy)
    decision = evaluate_policy(observations, rules)

    print(f"\nDecision: {decision.mode.value.upper()}")
    for reason in decision.reasons:
        print(f"- {reason}")

    if decision.mode == DecisionMode.BLOCKING:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
