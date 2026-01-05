import argparse
import sys
import yaml
import os

from ai_slop_gate.cli.init import run_init
from ai_slop_gate.cli.logger import logger
from ai_slop_gate.providers.registry import ProviderRegistry
from ai_slop_gate.providers import provider_registry
from ai_slop_gate.domain.policy_engine import evaluate_policy, PolicyRule
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.domain.check_mapper import decision_to_check
from ai_slop_gate.providers.k8s_runtime import K8sRuntimeProvider
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter


def load_policy_rules(path: str) -> list[PolicyRule]:
    """Load policy rules from YAML"""
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


def run_analysis(args: argparse.Namespace) -> None:
    """Main logic's run-command"""
    logger.info(f"Running provider: {args.provider}")

    provider_cls = provider_registry.get(args.provider)
    if isinstance(provider_cls, type):
        provider = provider_cls()
    else:
        provider = provider_cls

    provider_observation = provider.collect()
    observations = (
        provider_observation.observations
        if hasattr(provider_observation, "observations")
        else provider_observation
    )

    # Kubernetes runtime optional
    if args.k8s_manifests and args.provider != "k8s-runtime":
        with open(args.k8s_manifests, "r") as f:
            manifests = list(yaml.safe_load_all(f))
        k8s_provider = provider_registry.get("k8s-runtime")(manifests)
        k8s_result = k8s_provider.collect()
        observations.extend(k8s_result.observations)

    # --- Policy evaluation
    rules = load_policy_rules(args.policy)
    decision = evaluate_policy(observations, rules)

    # --- Domain Mapping (Decision -> CheckReport)
    check_report = decision_to_check(decision)

    # --- GitHub Reporting
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token and args.github_repo:
        if args.github_checks and args.github_sha:
            GitHubChecksReporter(
                token=github_token, repo=args.github_repo, sha=args.github_sha
            ).report(check_report)
        if args.pr_id:
            GitHubPRReporter(
                token=github_token,
                repo_name=args.github_repo,
                pr_number=args.pr_id,
            ).report(check_report)

    # --- Console Output через логер
    logger.info(f"Decision: {decision.mode.value.upper()}")
    for reason in decision.reasons:
        logger.info(f"- {reason}")

    # --- Final Enforcement
    if decision.mode == DecisionMode.BLOCKING and args.enforcement == "blocking":
        sys.exit(1)

    sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser("ai-slop-gate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- init
    init_parser = subparsers.add_parser("init", help="Initialize ai-slop-gate config")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config")
    init_parser.add_argument("--policy", help="Path to policy.yml")
    init_parser.add_argument("--provider", help="Default provider for initial run")

    # --- run
    run_parser = subparsers.add_parser("run", help="Run slop gate analysis")
    run_parser.add_argument("--policy", required=True)
    run_parser.add_argument("--provider", default="static")
    run_parser.add_argument("--k8s-manifests", help="Path to Kubernetes YAML manifests")
    run_parser.add_argument("--github-checks", action="store_true")
    run_parser.add_argument("--github-repo")
    run_parser.add_argument("--github-sha")
    run_parser.add_argument("--pr-id", type=int)
    run_parser.add_argument(
        "--enforcement", choices=["never","blocking","advisory"], default="advisory"
    )

    args = parser.parse_args()
    logger.info(f"Parsed args: {args}")

    if args.command == "init":
        run_init(force=args.force)
        if args.policy:
            logger.info(f"Policy path: {args.policy}")
        if args.provider:
            logger.info(f"Default provider: {args.provider}")
    elif args.command == "run":
        run_analysis(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Starting ai-slop-gate CLI")
    main()
