import argparse
import sys
import yaml
import os
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
from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend

def normalize_path(value: Optional[Union[str, list]]) -> Optional[str]:
    if value is None: return None
    if isinstance(value, list): return value[0] if value else None
    return value

def get_provider_with_cache(provider_name: str, *, k8s_manifests=None):
    """
    Instantiate provider and wrap with cache.
    """
    from ai_slop_gate.providers.registry import provider_registry
    provider_cls = provider_registry.get(provider_name)
    if not provider_cls:
        if provider_name == "gemini":
            from ai_slop_gate.providers.gemini import GeminiProvider
            provider_cls = GeminiProvider
        else:
            raise ValueError(f"Unknown provider: {provider_name}. Check provider_registry.")

    if provider_name == "k8s-runtime":
        if not k8s_manifests:
            raise ValueError("k8s-runtime provider requires --k8s-manifests")
        provider = provider_cls(k8s_manifests)
    elif provider_name == "gemini":
        provider = provider_cls(model="models/gemini-2.5-flash")
    else:
        provider = provider_cls()

    cache_backend = FileCacheBackend()
    return CachedProvider(provider, cache=cache_backend)

def normalize_observations(result):
    if result is None: return []
    if hasattr(result, "observations"): return list(result.observations)
    if isinstance(result, list): return result
    raise TypeError(f"Unsupported provider result type: {type(result)}")

def run_analysis(args):
    try:
        logger.info(f"Running provider: {args.provider}")

        k8s_manifests_arg = normalize_path(getattr(args, "k8s_manifests", None))
        manifests = None
        if k8s_manifests_arg:
            path = Path(k8s_manifests_arg)
            if path.exists():
                with path.open("r") as f:
                    manifests = list(yaml.safe_load_all(f))

        provider = get_provider_with_cache(
            args.provider,
            k8s_manifests=manifests if args.provider == "k8s-runtime" else None,
        )

        # --- Read input content from file or text argument ---
        content = ""
        if args.input_file and os.path.exists(args.input_file):
            with open(args.input_file, "r") as f:
                content = f.read()
        elif args.input_text:
            content = args.input_text

        # --- Pass content to the provider ---
        primary_result = provider.collect(content)
        observations = normalize_observations(primary_result)

        rules = load_policy_rules(args.policy)
        decision = evaluate_policy(observations, rules)
        check_report = decision_to_check(decision)

        github_token = getattr(args, "github_token", None) or os.getenv("GITHUB_TOKEN")
        
        if github_token and args.github_repo:
            if args.github_checks and args.github_sha:
                logger.info("Reporting to GitHub Checks...")
                GitHubChecksReporter(token=github_token, repo=args.github_repo, sha=args.github_sha).report(check_report)
            
            if args.pr_id:
                logger.info(f"Reporting to Pull Request #{args.pr_id}...")
                GitHubPRReporter(token=github_token, repo_name=args.github_repo, pr_id=args.pr_id).report(check_report)

        logger.info(f"Decision: {decision.mode.value.upper()}")
        for reason in decision.reasons:
            logger.info(f"- {reason}")

        if decision.mode == DecisionMode.BLOCKING and args.enforcement == "blocking":
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser("ai-slop-gate")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument("--policy")
    init_parser.add_argument("--provider")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--policy", required=True)
    run_parser.add_argument("--provider", default="static")
    run_parser.add_argument("--pr-id", type=int)
    run_parser.add_argument("--github-checks", action="store_true")
    run_parser.add_argument("--github-repo")
    run_parser.add_argument("--github-sha")
    run_parser.add_argument("--github-token")
    run_parser.add_argument("--enforcement", choices=["never", "blocking", "advisory"], default="advisory")
    run_parser.add_argument("--k8s-manifests")
    run_parser.add_argument("--input-text")
    run_parser.add_argument("--input-file")

    args = parser.parse_args()
    if args.command == "run":
        run_analysis(args)
    elif args.command == "init":
        run_init(force=args.force)

if __name__ == "__main__":
    main()
    