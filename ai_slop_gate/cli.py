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

    # --- Provider logic
    if args.provider == "static":
        provider = StaticPipelineProvider()
    else:
        raise ValueError(f"Unknown provider: {args.provider}")

    provider_observation = provider.collect()
    observations = provider_observation.observations

    # --- Policy evaluation
    rules = load_policy_rules(args.policy)
    decision = evaluate_policy(observations, rules)

    # --- Domain Mapping (Decision -> CheckReport)
    check_report = decision_to_check(decision)

    # --- GitHub Reporting
    github_token = os.getenv("GITHUB_TOKEN")
    
    if github_token and args.github_repo:
        # 1. GitHub Checks (Annotations in Files)
        if args.github_checks and args.github_sha:
            GitHubChecksReporter(
                token=github_token,
                repo=args.github_repo,
                sha=args.github_sha,
            ).report(check_report)

        # 2. GitHub PR Comment (Summary in Conversation)
        if args.pr_id:
            GitHubPRReporter(
                token=github_token,
                repo_name=args.github_repo,
                pr_number=args.pr_id,
            ).report(check_report)

    # --- Console Output
    print(f"\nDecision: {decision.mode.value.upper()}")
    for reason in decision.reasons:
        print(f"- {reason}")

    # --- Final Enforcement
    if decision.mode == DecisionMode.BLOCKING and args.enforcement == "blocking":
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()