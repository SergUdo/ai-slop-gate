# ai_slop_gate/cli.py
import argparse
import sys
import yaml
import os

from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider
from ai_slop_gate.domain.policy_engine import evaluate_policy, PolicyRule
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.domain.check_mapper import decision_to_check
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter



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
    parser.add_argument("--pr-id", type=int)
    parser.add_argument("--github-checks", action="store_true")
    parser.add_argument("--github-repo")
    parser.add_argument("--github-sha")
    parser.add_argument(
        "--enforcement",
        choices=["never", "blocking", "advisory"],
        default="advisory",
    )

    args = parser.parse_args()

    # --- Provider
    if args.provider == "static":
        provider = StaticPipelineProvider()
    else:
        raise ValueError(f"Unknown provider: {args.provider}")

    provider_observation = provider.collect()
    observations = provider_observation.observations

    # --- Policy
    rules = load_policy_rules(args.policy)
    decision = evaluate_policy(observations, rules)

    # --- Reporter (safe side-effect)
    # if args.github_repo and args.pr_id:
    #     reporter = GitHubPRReporter(
    #         token=os.environ["GITHUB_TOKEN"],
    #         repo=args.github_repo,
    #         pr_number=args.pr_id,
    #     )
    #     reporter.report(decision, observations)

    check = decision_to_check(decision)

    if args.github_checks:
        GitHubChecksReporter(
            token=os.environ["GITHUB_TOKEN"],
            repo=args.github_repo,
            sha=args.github_sha,
        ).report(check)

    # --- Console output
    print(f"\nDecision: {decision.mode.value.upper()}")
    for reason in decision.reasons:
        print(f"- {reason}")

    # --- Enforcement
    if decision.mode == DecisionMode.BLOCKING and args.enforcement == "blocking":
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
