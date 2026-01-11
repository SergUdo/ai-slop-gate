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
from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend
from ai_slop_gate.domain.compliance.engine import evaluate_compliance_risks
from ai_slop_gate.providers.supply_chain import SupplyChainProvider

CONFIG_FILE = ".ai-slop-gate.yml"


def normalize_path(value: Optional[Union[str, list]]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, list):
        return value[0] if value else None
    return value


def get_provider_with_cache(provider_name: str, *, k8s_manifests=None):
    """
    Instantiate provider and wrap with cache.
    Import provider_registry locally to avoid circular import.
    """
    from ai_slop_gate.providers.registry import provider_registry  # локально

    provider_cls = provider_registry.get(provider_name)

    if provider_name == "k8s-runtime":
        if not k8s_manifests:
            raise ValueError("k8s-runtime provider requires --k8s-manifests")
        provider = provider_cls(k8s_manifests)
    else:
        provider = provider_cls()

    cache_backend = FileCacheBackend()
    return CachedProvider(provider, cache=cache_backend)


def normalize_observations(result):
    if result is None:
        return []

    if hasattr(result, "observations"):
        return list(result.observations)

    if isinstance(result, list):
        return result

    raise TypeError(f"Unsupported provider result type: {type(result)}")

def run_compliance_enrichment(args, observations):
    try:
        import yaml
        from ai_slop_gate.providers.supply_chain import SupplyChainProvider
        from ai_slop_gate.domain.compliance.rules import LicenseRule
        from ai_slop_gate.domain.compliance.engine import evaluate_compliance_risks

        with open(args.policy, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        
        comp_cfg = cfg.get("compliance", {})
        # Перевіряємо увімкнення
        is_on = comp_cfg.get("enabled", False) or getattr(args, "compliance", False)
        if getattr(args, "no_compliance", False): is_on = False
        
        if not is_on:
            return []

        # Створюємо провайдер з явною передачею конфігурації
        provider = SupplyChainProvider(policy=comp_cfg)
        found_obs = provider.collect()
        
        if not found_obs:
            # Це допоможе нам в pytest -s
            # print(f"DEBUG: Provider found 0 observations in {os.getcwd()}")
            return []

        # Отримуємо правила
        lic_list = comp_cfg.get("license_audit", {}).get("forbidden_licenses", ["GPL-3.0"])
        rules = [LicenseRule(id="COMP-01", forbidden_licenses=set(lic_list))]
        
        return evaluate_compliance_risks(found_obs, rules, []) 
    except Exception as e:
        # print(f"DEBUG: Error in enrichment: {e}")
        return []


def run_analysis(args):
    try:
        logger.info(f"Running provider: {args.provider}")

        k8s_manifests_arg = normalize_path(getattr(args, "k8s_manifests", None))

        manifests = None
        if k8s_manifests_arg:
            path = Path(k8s_manifests_arg)
            if not path.exists():
                raise FileNotFoundError(f"K8s manifests not found: {path}")
            with path.open("r") as f:
                manifests = list(yaml.safe_load_all(f))

        provider = get_provider_with_cache(
            args.provider,
            k8s_manifests=manifests if args.provider == "k8s-runtime" else None,
        )

        primary_result = provider.collect()
        observations = normalize_observations(primary_result)

        compliance_reasons = run_compliance_enrichment(args, observations)

        rules = load_policy_rules(args.policy)
        decision = evaluate_policy(observations, rules)
        
        if compliance_reasons:
            decision.reasons.extend(compliance_reasons)

        # optional k8s-runtime enrichment
        if manifests and args.provider != "k8s-runtime":
            from ai_slop_gate.providers.registry import provider_registry
            k8s_provider_cls = provider_registry.get("k8s-runtime")
            k8s_provider = k8s_provider_cls(manifests)
            k8s_result = k8s_provider.collect()
            observations.extend(normalize_observations(k8s_result))

        rules = load_policy_rules(args.policy)
        decision = evaluate_policy(observations, rules)
        check_report = decision_to_check(decision)

        github_token = getattr(args, "github_token", None)
        if github_token and args.github_repo:
            if getattr(args, "github_checks", False) and getattr(args, "github_sha", None):
                GitHubChecksReporter(token=github_token, repo=args.github_repo, sha=args.github_sha).report(check_report)
            if getattr(args, "pr_id", None):
                GitHubPRReporter(token=github_token, repo_name=args.github_repo, pr_number=args.pr_id).report(check_report)

        logger.info(f"Decision: {decision.mode.value.upper()}")
        for reason in decision.reasons:
            logger.info(f"- {reason}")

        if decision.mode == DecisionMode.BLOCKING and getattr(args, "enforcement", "advisory") == "blocking":
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser("ai-slop-gate")
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config")
    init_parser.add_argument("--policy", help="Path to policy.yml")
    init_parser.add_argument("--provider", help="Default provider for initial run")

    # run
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--policy", required=True)
    run_parser.add_argument("--provider", default="static")
    run_parser.add_argument("--pr-id", type=int)
    run_parser.add_argument("--github-checks", action="store_true")
    run_parser.add_argument("--github-repo")
    run_parser.add_argument("--github-sha")
    run_parser.add_argument("--enforcement", choices=["never", "blocking", "advisory"], default="advisory")
    run_parser.add_argument("--k8s-manifests", help="Path to Kubernetes YAML manifests")
    run_parser.add_argument("--input-text", help="Text input for AI providers")
    run_parser.add_argument("--input-file", help="File input for AI providers")
    run_parser.add_argument("--compliance", action="store_true", help="Force compliance check")
    run_parser.add_argument("--no-compliance", action="store_true", help="Skip compliance check")

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
