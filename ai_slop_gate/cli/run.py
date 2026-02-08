import os
import sys
import logging
from typing import List, Any
from dotenv import load_dotenv

from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.cli.context import RuntimeContext
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation
from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.decision import DecisionMode

from ai_slop_gate.reporters.console import ConsoleReporter
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter

from ai_slop_gate.providers.static.static_pipeline import StaticPipelineProvider
from ai_slop_gate.providers.llm import GeminiProvider, GroqProvider

from ai_slop_gate.domain.compliance.pipeline import CompliancePipeline

load_dotenv()
logger = logging.getLogger("ai_slop_gate")


PROVIDER_MAP = {
    "static": StaticPipelineProvider,
    "static_pipeline": StaticPipelineProvider,
    "gemini": GeminiProvider,
    "groq": GroqProvider,
}


def resolve_model(policy_config, provider_name: str) -> str | None:
    if provider_name in ("static", "static_pipeline"):
        return None

    ai = policy_config.ai_provider
    models = ai.get("models", {})

    if provider_name in models:
        return models[provider_name]

    if "model" in ai:
        return ai["model"]

    raise ValueError(
        f"[STRICT MODE] No model defined for provider '{provider_name}'. "
        f"Add it under ai_provider.models.{provider_name} in policy.yml"
    )


def get_providers(provider_names: List[str], policy_config=None) -> List[Any]:
    providers = []
    for name in provider_names:
        key = name.lower()
        if key not in PROVIDER_MAP:
            raise ValueError(f"Unknown provider: {name}")
        model = resolve_model(policy_config, key)
        providers.append(PROVIDER_MAP[key](model=model))
    return providers


# -----------------------------
# FIXED include filter
# -----------------------------
def build_include_filter(ctx: RuntimeContext, include_paths: List[str]):
    normalized_include_paths = [
        os.path.abspath(os.path.join(ctx.path, p))
        for p in include_paths
    ]

    def is_included(file_path: str) -> bool:
        if not normalized_include_paths:
            return True

        if not file_path:
            return True

        abs_file = (
            os.path.abspath(os.path.join(ctx.path, file_path))
            if not os.path.isabs(file_path)
            else os.path.abspath(file_path)
        )

        for inc in normalized_include_paths:
            inc = os.path.abspath(inc)
            if abs_file == inc or abs_file.startswith(inc + os.sep):
                return True

        return False

    return is_included


# -----------------------------
# MAIN CLI
# -----------------------------
def run_cli(ctx: RuntimeContext) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
        force=True
    )

    logger.info("--- AI SLOP GATE STARTING ---")

    github_token = ctx.github_token or os.getenv("GITHUB_TOKEN")

    try:
        logger.info(f"Loading policy file: {ctx.policy_path}")
        policy_config, rules = load_policy(ctx.policy_path)

        include_filter = None
        if policy_config.include_paths:
            include_filter = build_include_filter(ctx, policy_config.include_paths)

        provider_names = ctx.providers or []
        providers = get_providers(provider_names, policy_config=policy_config)

        if not providers:
            raise ValueError("No providers specified.")

        logger.info(f"Providers selected: {provider_names}")

        all_observations: List[Observation] = []
        executed_any_provider = False

        has_llm_provider = any(getattr(p, "kind", None) == "llm" for p in providers)
        is_llm_pr_analysis = bool(has_llm_provider and ctx.github_repo and ctx.pr_id)

        # -----------------------------
        # STATIC + LLM PROVIDERS
        # -----------------------------
        for provider in providers:
            logger.info(f"Running provider: {provider.name} ({provider.kind})")

            if provider.kind == "llm":
                if ctx.github_repo and ctx.pr_id:
                    result = provider.analyze_pr(ctx.github_repo, ctx.pr_id, github_token)
                    all_observations.extend(result.observations)
                    executed_any_provider = True
                    continue

                if ctx.llm_local:
                    result = provider.analyze_files(ctx.path)
                    all_observations.extend(result.observations)
                    executed_any_provider = True
                    continue

                logger.info(f"Skipping LLM provider '{provider.name}'")
                continue

            if provider.kind == "static":
                result = provider.collect(base_path=ctx.path)

                if include_filter:
                    filtered = []
                    for obs in result.observations:
                        file_path = None
                        if hasattr(obs, "location") and obs.location:
                            file_path = obs.location.file
                        elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
                            file_path = obs.evidence.get("file")

                        if include_filter(file_path):
                            filtered.append(obs)

                    all_observations.extend(filtered)
                else:
                    all_observations.extend(result.observations)

                executed_any_provider = True
                continue

        if not executed_any_provider:
            logger.error("No analyzers executed.")
            return 1

        # -----------------------------
        # COMPLIANCE PIPELINE
        # -----------------------------
        if not is_llm_pr_analysis:
            if policy_config.compliance and policy_config.compliance.enabled:
                logger.info("Running compliance pipeline...")
                pipeline = CompliancePipeline(policy_config.compliance)
                compliance_obs = pipeline.run(
                    artifacts_path=ctx.path,
                    ai_provider_region=policy_config.ai_provider.get("region")
                )

                policy_dir = os.path.dirname(os.path.abspath(ctx.policy_path))
                target_dir = os.path.abspath(ctx.path)

                filtered = []
                for obs in compliance_obs:
                    if hasattr(obs, "location") and obs.location and obs.location.file:
                        file_path = obs.location.file
                    else:
                        file_path = ctx.path

                    if os.path.basename(file_path) == "policy.yml" and policy_dir != target_dir:
                        continue

                    if include_filter and not include_filter(file_path):
                        continue

                    filtered.append(obs)

                all_observations.extend(filtered)

        # -----------------------------
        # POLICY ENGINE
        # -----------------------------
        engine = PolicyEngine(rules)
        decision = engine.evaluate(all_observations)
        logger.info(f"Policy Verdict: {decision.mode.value.upper()}")

        # -----------------------------
        # ANNOTATIONS
        # -----------------------------
        annotations = []
        for obs in all_observations:
            file_path = "root"
            line_num = 1

            if hasattr(obs, "location") and obs.location:
                file_path = obs.location.file or "root"
                line_num = obs.location.line or 1
            elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
                file_path = obs.evidence.get("file", "root")
                line_num = obs.evidence.get("line", 1)

            level = "failure" if obs.severity in ["high", "critical"] else "warning"

            annotations.append(
                CheckAnnotation(
                    file=file_path,
                    line=line_num,
                    level=level,
                    message=f"[{obs.signal}] {obs.message}"
                )
            )

        # -----------------------------
        # REPORTING
        # -----------------------------
        report = CheckReport(
            title="AI Slop Gate Report",
            summary=f"Verdict: {decision.mode.value.upper()}. Found {len(annotations)} issues.",
            status=decision.mode,
            annotations=annotations,
            reasons=decision.reasons,
        )

        if ctx.github_repo and github_token:
            if ctx.pr_id:
                GitHubPRReporter(github_token, ctx.github_repo, ctx.pr_id).report(report)
            if ctx.github_sha:
                GitHubChecksReporter(github_token, ctx.github_repo, ctx.github_sha).report(report)
        else:
            ConsoleReporter(verbose=ctx.verbose).report(report)

        logger.info("--- Execution Completed Successfully ---")
        return 0 if decision.mode != DecisionMode.BLOCKING else 1

    except Exception as e:
        logger.error(f"Execution failed: {str(e)}", exc_info=True)
        return 1
