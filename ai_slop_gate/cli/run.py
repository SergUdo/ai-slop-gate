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

# Reporters
from ai_slop_gate.reporters.console import ConsoleReporter
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter

# Providers
from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider
from ai_slop_gate.providers.gemini import GeminiProvider

# Compliance
from ai_slop_gate.domain.compliance.pipeline import CompliancePipeline

load_dotenv()
logger = logging.getLogger("ai_slop_gate")


# -----------------------------
# Provider Factory
# -----------------------------
PROVIDER_MAP = {
    "static": StaticPipelineProvider,
    "static_pipeline": StaticPipelineProvider,
    "gemini": GeminiProvider,
}


def get_providers(provider_names: List[str], model: str = None) -> List[Any]:
    providers = []
    for name in provider_names:
        key = name.lower()
        if key not in PROVIDER_MAP:
            raise ValueError(f"Unknown provider: {name}")
        providers.append(PROVIDER_MAP[key](model=model))
    return providers


# -----------------------------
# Main CLI Execution
# -----------------------------
def run_cli(ctx: RuntimeContext) -> int:
    """
    Main entry point for AI Slop Gate CLI.
    Handles provider execution, compliance pipeline, policy evaluation, and reporting.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
        force=True
    )

    logger.info("--- AI SLOP GATE STARTING ---")

    github_token = ctx.github_token or os.getenv("GITHUB_TOKEN")

    try:
        # -----------------------------
        # 1. Load policy configuration
        # -----------------------------
        logger.info(f"Loading policy file: {ctx.policy_path}")
        policy_config, rules = load_policy(ctx.policy_path)

        # -----------------------------
        # 2. Initialize providers
        # -----------------------------
        provider_names = ctx.providers or []
        providers = get_providers(provider_names, model=policy_config.ai_provider.get("model"))

        if not providers:
            raise ValueError("No providers specified. Use --provider static or --provider gemini etc.")

        logger.info(f"Providers selected: {provider_names}")

        all_observations: List[Observation] = []
        executed_any_provider = False

        # Determine if ANY provider is LLM
        has_llm_provider = any(getattr(p, "kind", None) == "llm" for p in providers)

        # Determine if we are performing LLM PR analysis (diff-only mode)
        is_llm_pr_analysis = bool(has_llm_provider and ctx.github_repo and ctx.pr_id)

        # -----------------------------
        # 3. Run providers
        # -----------------------------
        for provider in providers:
            logger.info(f"Running provider: {provider.name} ({provider.kind})")

            # -----------------------------
            # LLM PROVIDER LOGIC
            # -----------------------------
            if provider.kind == "llm":

                # --- PR MODE (LLM analyzes GitHub PR diff only) ---
                if ctx.github_repo and ctx.pr_id:
                    logger.info(f"LLM PR analysis: repo={ctx.github_repo}, pr={ctx.pr_id}")
                    result = provider.analyze_pr(ctx.github_repo, ctx.pr_id, github_token)
                    all_observations.extend(result.observations)
                    executed_any_provider = True
                    continue

                # --- LOCAL LLM MODE (LLM analyzes local repository) ---
                if ctx.llm_local:
                    logger.info("LLM local analysis enabled (--llm-local)")
                    result = provider.analyze_files(ctx.path)
                    all_observations.extend(result.observations)
                    executed_any_provider = True
                    continue

                # --- NO VALID LLM MODE ---
                logger.info(
                    f"Skipping LLM provider '{provider.name}': no PR ID and --llm-local not provided."
                )
                continue

            # -----------------------------
            # STATIC PROVIDER LOGIC
            # -----------------------------
            if provider.kind == "static":
                result = provider.collect(base_path=ctx.path)
                all_observations.extend(result.observations)
                executed_any_provider = True
                continue

        # -----------------------------
        # 4. Ensure at least one provider executed
        # -----------------------------
        if not executed_any_provider:
            logger.error(
                "No analyzers were executed. "
                "If you specified only LLM providers, add --llm-local for local analysis "
                "or provide --pr-id for PR analysis."
            )
            return 1

        # -----------------------------
        # 5. Compliance Pipeline
        # -----------------------------
        # IMPORTANT ARCHITECTURAL RULE:
        # - If we are performing LLM PR analysis, we analyze ONLY the diff.
        #   Running compliance pipeline (which scans the local filesystem)
        #   would incorrectly mix local repo findings with PR findings.
        #
        # - For local LLM mode and static providers, compliance pipeline SHOULD run.
        if is_llm_pr_analysis:
            logger.info("Skipping compliance pipeline for LLM PR analysis (diff-only mode).")
        else:
            if policy_config.compliance and policy_config.compliance.enabled:
                logger.info("Running compliance pipeline...")
                pipeline = CompliancePipeline(policy_config.compliance)
                compliance_obs = pipeline.run(
                    artifacts_path=ctx.path,
                    ai_provider_region=policy_config.ai_provider.get("region")
                )
                all_observations.extend(compliance_obs)

        # -----------------------------
        # 6. Policy Engine Evaluation
        # -----------------------------
        engine = PolicyEngine(rules)
        decision = engine.evaluate(all_observations)
        logger.info(f"Policy Verdict: {decision.mode.value.upper()}")

        # -----------------------------
        # 7. Build GitHub-style annotations
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
        # 8. Reporting
        # -----------------------------
        report = CheckReport(
            title="AI Slop Gate Report",
            summary=f"Verdict: {decision.mode.value.upper()}. Found {len(annotations)} issues.",
            status=decision.mode,
            annotations=annotations,
            reasons=decision.reasons,
        )

        # GitHub reporting
        if ctx.github_repo and github_token:
            if ctx.pr_id:
                GitHubPRReporter(github_token, ctx.github_repo, ctx.pr_id).report(report)
                logger.info("Results posted to GitHub PR.")

            if ctx.github_sha:
                GitHubChecksReporter(github_token, ctx.github_repo, ctx.github_sha).report(report)
                logger.info(f"GitHub Check Run created for SHA: {ctx.github_sha[:7]}")

        # Local console reporting
        else:
            ConsoleReporter(verbose=ctx.verbose).report(report)

        logger.info("--- Execution Completed Successfully ---")
        return 0 if decision.mode != DecisionMode.BLOCKING else 1

    except Exception as e:
        logger.error(f"Execution failed: {str(e)}", exc_info=True)
        return 1
