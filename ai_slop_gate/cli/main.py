# ai_slop_gate/cli/main.py
import argparse
import sys
import yaml
from pathlib import Path
from typing import Optional, Union

from ai_slop_gate.cli.logger import logger
from ai_slop_gate.cli.init import run_init
from ai_slop_gate.cli.utils import load_policy_rules

from ai_slop_gate.domain.policy_engine import evaluate_policy
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.domain.check_mapper import decision_to_check

from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter

from ai_slop_gate.providers.registry import provider_registry
from ai_slop_gate.providers.cached_provider import CachedProvider

from ai_slop_gate.cache.file_backend import FileCacheBackend


CONFIG_FILE = ".ai-slop-gate.yml"


def normalize_path(value: Optional[Union[str, list]]) -> Optional[str]:
    """
    argparse / CI / shell may pass arguments as list[str]
    Normalize to single string path.
    """
    if value is None:
        return None
    if isinstance(value, list):
        if not value:
            return None
        return value[0]
    return value


def get_provider_with_cache(provider_name: str, *, k8s_manifests=None):
    """
    Instantiate provider and wrap it with cache.
    Handles providers with constructor arguments (e.g. k8s-runtime).
    """
    provider_cls = provider_registry.get(provider_name)

    # --- provider instantiation
    if provider_name == "k8s-runtime":
        if not k8s_manifests:
            raise ValueError("k8s-runtime provider requires --k8s-manifests")
        provider = provider_cls(k8s_manifests)
    else:
        provider = provider_cls()

    # --- cache wrapper
    cache_backend = FileCacheBackend()
    return CachedProvider(provider, cache=cache_backend)


def normalize_observations(result):
    """
    Providers may return:
    - ProviderObservation(observations=[...])
    - list[Observation] (cached)
    """
    if result is None:
        return []

    if hasattr(result, "observations"):
        return list(result.observations)

    if isinstance(result, list):
        return result

    raise TypeError(f"Unsupported provider result type: {type(result)}")


def run_analysis(args):
    try:
        logger.info(f"Running provider: {args.provider}")

        # --- Normalize k8s-manifests argument
        k8s_manifests_arg = normalize_path(args.k8s_manifests)

        # --- Load K8s manifests early if provided
        manifests = None
        if k8s_manifests_arg:
            path = Path(k8s_manifests_arg)
            if not path.exists():
                raise FileNotFoundError(f"K8s manifests not found: {path}")

            with path.open("r") as f:
                manifests = list(yaml.safe_load_all(f))

        # --- Main provider
        provider = get_provider_with_cache(
            args.provider,
            k8s_manifests=manifests if args.provider == "k8s-runtime" else None,
        )

        primary_result = provider.collect()
        observations = normalize_observations(primary_result)

        # --- Optional k8s-runtime enrichment
        if manifests and args.provider != "k8s-runtime":
            k8s_provider_cls = provider_registry.get("k8s-runtime")
            k8s_provider = k8s_provider_cls(manifests)
            k8s_result = k8s_provider.collect()
            observations.extend(normalize_observations(k8s_result))

        # --- Load policy rules
        rules = load_policy_rules(args.policy)

        # --- Evaluate policy
        decision = evaluate_policy(observations, rules)

        # --- Map decision to check report
        check_report = decision_to_check(decision)

        # --- GitHub reporting
        github_token = getattr(args, "github_token", None)

        if github_token and args.github_repo:
            if args.github_checks and args.github_sha:
                GitHubChecksReporter(
                    token=github_token,
                    repo=args.github_repo,
                    sha=args.github_sha,
                ).report(check_report)

            if args.pr_id:
                GitHubPRReporter(
                    token=github_token,
                    repo_name=args.github_repo,
                    pr_number=args.pr_id,
                ).report(check_report)

        # --- Console output
        logger.info(f"Decision: {decision.mode.value.upper()}")
        for reason in decision.reasons:
            logger.info(f"- {reason}")

        # --- Exit code handling
        if decision.mode == DecisionMode.BLOCKING and args.enforcement == "blocking":
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser("ai-slop-gate")
    subparsers = parser.add_subparsers(dest="command")

    # --- init
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config")
    init_parser.add_argument("--policy", help="Path to policy.yml")
    init_parser.add_argument("--provider", help="Default provider for initial run")

    # --- run
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--policy", required=True)
    run_parser.add_argument("--provider", default="static")
    run_parser.add_argument("--pr-id", type=int)
    run_parser.add_argument("--github-checks", action="store_true")
    run_parser.add_argument("--github-repo")
    run_parser.add_argument("--github-sha")
    run_parser.add_argument(
        "--enforcement",
        choices=["never", "blocking", "advisory"],
        default="advisory",
    )
    run_parser.add_argument("--k8s-manifests", help="Path to Kubernetes YAML manifests")

    args = parser.parse_args()
    logger.info(f"Parsed args: {args}")

    if args.command == "init":
        run_init(force=args.force)
        if args.policy:
            logger.info(f"Policy path: {args.policy}")
        if args.provider:
            logger.info(f"Default provider: {args.provider}")
        return

    if args.command == "run":
        run_analysis(args)
        return

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    logger.info("Starting ai-slop-gate CLI")
    main()
