import os
import sys
from pathlib import Path

from ai_slop_gate.cli.logger import logger
from ai_slop_gate.cli.context import RuntimeContext
from ai_slop_gate.cli.utils import load_policy_rules

from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend

from ai_slop_gate.domain.policy_engine import evaluate_policy
from ai_slop_gate.domain.check_mapper import decision_to_check
from ai_slop_gate.domain.decision import DecisionMode

from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter


def run_analysis(ctx: RuntimeContext) -> None:
    from ai_slop_gate.providers.registry import provider_registry
    logger.info(f"Provider: {ctx.provider}")

    provider_cls = provider_registry.get(ctx.provider)
    if not provider_cls:
        raise SystemExit(f"Unknown provider: {ctx.provider}")

    provider = provider_cls()
    provider = CachedProvider(provider, cache=FileCacheBackend())

    content = None
    if ctx.input_file:
        content = Path(ctx.input_file).read_text()
    elif ctx.input_text:
        content = ctx.input_text

    result = provider.collect(content)
    observations = getattr(result, "observations", result)

    rules = load_policy_rules(ctx.policy_path)
    decision = evaluate_policy(observations, rules)
    check = decision_to_check(decision)

    token = ctx.github_token or os.getenv("GITHUB_TOKEN")
    if token and ctx.github_repo:
        if ctx.github_checks and ctx.github_sha:
            GitHubChecksReporter(
                token=token,
                repo=ctx.github_repo,
                sha=ctx.github_sha,
            ).report(check)

        if ctx.pr_id:
            GitHubPRReporter(
                token=token,
                repo_name=ctx.github_repo,
                pr_id=ctx.pr_id,
            ).report(check)

    logger.info(f"Decision: {decision.mode.value.upper()}")
    for r in decision.reasons:
        logger.info(f"- {r}")

    if decision.mode == DecisionMode.BLOCKING and ctx.enforcement == "blocking":
        sys.exit(1)
