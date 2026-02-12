import os
import sys
import logging
import json
from typing import List, Any, Optional
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
from ai_slop_gate.providers.llm import GeminiProvider, GroqProvider, OllamaProvider
from ai_slop_gate.domain.compliance.pipeline import CompliancePipeline

load_dotenv()
logger = logging.getLogger("ai_slop_gate")

PROVIDER_MAP = {
    "static": StaticPipelineProvider,
    "static_pipeline": StaticPipelineProvider,
    "gemini": GeminiProvider,
    "groq": GroqProvider,
    "ollama": OllamaProvider
}

def resolve_model(policy_config, provider_name: str) -> str:

    if provider_name in ("static", "static_pipeline"):
        return None

    ai_cfg = policy_config.ai_provider
    models_map = ai_cfg.get("models", {})

    if provider_name in models_map:
        return models_map[provider_name]

    global_model = ai_cfg.get("model")
    if global_model:
        return global_model

    raise ValueError(
        f"[STRICT MODE] No model defined for LLM provider '{provider_name}'. "
        f"Please specify it in 'ai_provider.models.{provider_name}' or set a global 'ai_provider.model'."
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

def build_include_filter(ctx: RuntimeContext, include_paths: List[str]):
    normalized_include_paths = [os.path.abspath(os.path.join(ctx.path, p)) for p in include_paths]
    def is_included(file_path: str) -> bool:
        if not normalized_include_paths or not file_path:
            return True
        abs_file = os.path.abspath(os.path.join(ctx.path, file_path)) if not os.path.isabs(file_path) else os.path.abspath(file_path)
        for inc in normalized_include_paths:
            if abs_file == inc or abs_file.startswith(inc + os.sep):
                return True
        return False
    return is_included

def extract_location(obs: Observation):
    """Extract file path and line number from an observation, handling different possible structures."""
    file_path = "root"
    line_num = 1
    if hasattr(obs, "location") and obs.location:
        file_path = obs.location.file or "root"
        line_num = obs.location.line or 1
    elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
        file_path = obs.evidence.get("file", "root")
        line_num = obs.evidence.get("line", 1)
    return file_path, line_num

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
        
        is_compliance_enabled = getattr(ctx, "compliance", False) or getattr(ctx, "compliance_only", False)

        if not provider_names and not is_compliance_enabled:
            logger.error("No analyzers specified. Use --provider or --compliance.")
            return 1

        all_observations: List[Observation] = []

        # --- Step 1: Run LLM / Static Providers ---
        if provider_names:
            providers = get_providers(provider_names, policy_config=policy_config)
            for provider in providers:
                logger.info(f"Running provider: {provider.name} ({provider.kind})")
                
                if provider.kind == "llm":
                    if ctx.github_repo and ctx.pr_id:
                        result = provider.analyze_pr(ctx.github_repo, ctx.pr_id, github_token)
                    elif ctx.llm_local:
                        result = provider.analyze_files(ctx.path)
                    else:
                        logger.warning(f"Skipping LLM provider '{provider.name}': insufficient context.")
                        continue
                else: # Static
                    result = provider.collect(base_path=ctx.path)

                for obs in result.observations:
                    f_path, _ = extract_location(obs)
                    if not include_filter or include_filter(f_path):
                        all_observations.append(obs)

        # --- Step 2: Compliance Checks ---
        should_run_compliance = is_compliance_enabled or (
            policy_config.compliance and policy_config.compliance.enabled 
            and not (ctx.github_repo and ctx.pr_id)
        )

        if should_run_compliance:
            logger.info("Running compliance pipeline...")
            pipeline = CompliancePipeline(policy_config.compliance)
            compliance_obs = pipeline.run(
                artifacts_path=ctx.path,
                ai_provider_region=policy_config.ai_provider.get("region")
            )

            policy_dir = os.path.dirname(os.path.abspath(ctx.policy_path))
            target_dir = os.path.abspath(ctx.path)

            for obs in compliance_obs:
                f_path, _ = extract_location(obs)
                if os.path.basename(f_path) == "policy.yml" and policy_dir != target_dir:
                    continue
                if not include_filter or include_filter(f_path):
                    all_observations.append(obs)

        # --- Step 3: Evaluate ---
        engine = PolicyEngine(rules)
        decision = engine.evaluate(all_observations)
        logger.info(f"Policy Verdict: {decision.mode.value.upper()}")

        # --- Step 4: Report ---
        annotations = []
        for obs in all_observations:
            f_path, l_num = extract_location(obs)
            # Support both severity levels and signals for determining annotation level
            level = "failure" if obs.severity in ["high", "critical", "failure"] else "warning"
            annotations.append(
                CheckAnnotation(
                    file=f_path,
                    line=l_num,
                    level=level,
                    message=f"[{obs.signal}] {obs.message}"
                )
            )

        report = CheckReport(
            title="AI Slop Gate Report",
            summary=f"Verdict: {decision.mode.value.upper()}. Found {len(annotations)} issues.",
            status=decision.mode,
            annotations=annotations,
            reasons=decision.reasons,
        )

        # --- Step 5: Reporters ---
        if ctx.github_repo and github_token and (ctx.pr_id or ctx.github_sha):
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
    