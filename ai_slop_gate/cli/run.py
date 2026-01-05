import os
import yaml
import sys

from ai_slop_gate.providers import provider_registry
from ai_slop_gate.providers.k8s_runtime import K8sRuntimeProvider
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.domain.check_mapper import decision_to_check
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter
from ai_slop_gate.cli.utils import load_policy_rules
from ai_slop_gate.domain.policy_engine import evaluate_policy

def run_analysis(
    policy_path: str,
    provider_name: str = "static",
    k8s_manifests: str = None,
    pr_id: int = None,
    github_checks: bool = False,
    github_repo: str = None,
    github_sha: str = None,
    enforcement: str = "advisory",
):
    # --- Resolve provider
    try:
        provider_cls = provider_registry.get(provider_name)
    except KeyError:
        print(f"Unknown provider: {provider_name}")
        sys.exit(1)

    provider = provider_cls() if isinstance(provider_cls, type) else provider_cls
    provider_observation = provider.collect()
    observations = (
        provider_observation.observations
        if hasattr(provider_observation, "observations")
        else provider_observation
    )

    # K8s optional
    if k8s_manifests and provider_name != "k8s-runtime":
        with open(k8s_manifests, "r") as f:
            manifests = list(yaml.safe_load_all(f))
        k8s_provider = provider_registry.get("k8s-runtime")(manifests)
        k8s_result = k8s_provider.collect()
        observations.extend(k8s_result.observations)

    # --- Policy evaluation
    rules = load_policy_rules(policy_path)
    decision = evaluate_policy(observations, rules)

    # --- Domain Mapping
    check_report = decision_to_check(decision)

    # --- GitHub reporting
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token and github_repo:
        if github_checks and github_sha:
            GitHubChecksReporter(
                token=github_token,
                repo=github_repo,
                sha=github_sha,
            ).report(check_report)

        if pr_id:
            GitHubPRReporter(
                token=github_token,
                repo_name=github_repo,
                pr_number=pr_id,
            ).report(check_report)

    # --- Console output
    print(f"\nDecision: {decision.mode.value.upper()}")
    for reason in decision.reasons:
        print(f"- {reason}")

    # --- Enforcement
    if decision.mode == DecisionMode.BLOCKING and enforcement == "blocking":
        sys.exit(1)

    sys.exit(0)
