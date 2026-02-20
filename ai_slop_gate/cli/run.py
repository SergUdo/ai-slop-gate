import os
import sys
import logging
import fnmatch
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
from ai_slop_gate.reporters.gitlab_mr import GitLabMRReporter

from ai_slop_gate.providers.static.static_pipeline import StaticPipelineProvider
from ai_slop_gate.providers.llm import GeminiProvider, GroqProvider, OllamaProvider
from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend
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

def get_providers(
    provider_names: List[str], 
    policy_config=None,
    cache_enabled: bool = True,
    cache_dir: str = ".ai-slop-cache"
) -> List[Any]:
    """
    Build providers with optional caching for LLM providers.
    
    Args:
        provider_names: List of provider names
        policy_config: Policy configuration
        cache_enabled: Whether to wrap LLM providers with cache
        cache_dir: Directory for cache storage
    
    Returns:
        List of instantiated provider objects
    """
    providers = []
    
    for name in provider_names:
        key = name.lower()
        if key not in PROVIDER_MAP:
            raise ValueError(f"Unknown provider: {name}")
        
        # Resolve model
        model = resolve_model(policy_config, key)
        
        # Instantiate provider
        provider = PROVIDER_MAP[key](model=model)
        
        # Wrap LLM providers with cache
        if cache_enabled and hasattr(provider, 'kind') and provider.kind == "llm":
            logger.info(f"  🗄️  Wrapping '{name}' with cache (dir={cache_dir})")
            cache_backend = FileCacheBackend(root=cache_dir)
            provider = CachedProvider(
                provider=provider,
                cache=cache_backend
            )
        
        providers.append(provider)
    
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

def build_exclude_filter(exclude_paths, exclude_secret_files):
    all_patterns = list(exclude_paths) + list(exclude_secret_files)
    
    def is_excluded(file_path: str) -> bool:
        if not file_path or file_path in ("root", "unknown"):
            return False
        fp = file_path.replace(os.sep, "/").lstrip("./")
        for pattern in all_patterns:
            pat = pattern.replace(os.sep, "/").lstrip("./")
            if fnmatch.fnmatch(fp, pat):
                return True
            # "docs/**" — префікс
            if pat.endswith("/**"):
                prefix = pat[:-3]
                if fp == prefix or fp.startswith(prefix + "/"):
                    return True
            # "**/name" — any path ending with name
            if pat.startswith("**/"):
                suffix = pat[3:]
                parts = fp.split("/")
                for i in range(len(parts)):
                    if fnmatch.fnmatch("/".join(parts[i:]), suffix):
                        return True
            # "**/name/**" — any path containing name as a segment
            if not any(c in pat for c in ("*", "?", "[")):
                if fp == pat or fp.endswith("/" + pat):
                    return True
        return False
    return is_excluded

def extract_location(obs: Observation):
    """Extract file path and line number from an observation."""
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
    gitlab_token = ctx.gitlab_token or os.getenv("GITLAB_TOKEN") or os.getenv("CI_JOB_TOKEN")

    try:
        logger.info(f"Loading policy file: {ctx.policy_path}")
        policy_config, rules, exclude_paths, exclude_secret_files = load_policy(ctx.policy_path)
        exclude_filter = build_exclude_filter(exclude_paths, exclude_secret_files)

        enforcement_override = getattr(ctx, 'enforcement', None)
        if enforcement_override:
            logger.info(f"  ⚠️  Enforcement overridden via CLI: {enforcement_override.upper()}")

        include_filter = None
        if policy_config.include_paths:
            include_filter = build_include_filter(ctx, policy_config.include_paths)

        provider_names = ctx.providers or []
        
        # Cache configuration
        cache_enabled = not getattr(ctx, "no_cache", False)
        cache_dir = getattr(ctx, "cache_dir", ".ai-slop-cache")
        
        # Working mode detection
        is_compliance_only = getattr(ctx, "compliance_only", False)
        is_compliance_flag = getattr(ctx, "compliance", False)
        is_github_pr = bool(ctx.github_repo and ctx.pr_id)
        is_gitlab_mr = bool(getattr(ctx, 'gitlab_project', None) and getattr(ctx, 'mr_iid', None))  # ✅ ДОДАНО
        
        logger.info("=" * 60)
        logger.info("EXECUTION MODE DETECTION:")
        logger.info(f"  Providers requested: {provider_names or '(none)'}")
        logger.info(f"  Cache enabled: {cache_enabled} (dir={cache_dir})")
        logger.info(f"  --compliance flag: {is_compliance_flag}")
        logger.info(f"  --compliance-only flag: {is_compliance_only}")
        logger.info(f"  GitHub PR mode: {is_github_pr}")
        logger.info(f"  GitLab MR mode: {is_gitlab_mr}")
        if is_github_pr:
            logger.info(f"    GitHub repo: {ctx.github_repo}, PR: {ctx.pr_id}")
        if is_gitlab_mr:
            logger.info(f"    GitLab project: {ctx.gitlab_project}, MR: {ctx.mr_iid}")
        logger.info(f"  policy.compliance.enabled: {policy_config.compliance.enabled if policy_config.compliance else 'N/A'}")
        if policy_config.compliance:
            run_in_pr = getattr(policy_config.compliance, 'run_in_pr', False)
            logger.info(f"  policy.compliance.run_in_pr: {run_in_pr}")
        logger.info("=" * 60)

        if not provider_names and not is_compliance_flag and not is_compliance_only:
            logger.error("❌ No analyzers specified. Use --provider, --compliance, or --compliance-only.")
            return 1

        all_observations: List[Observation] = []

        # Step 1: Providers
        if provider_names and not is_compliance_only:
            logger.info(f"▶️  STEP 1: Running {len(provider_names)} provider(s)")
            providers = get_providers(
                provider_names, 
                policy_config=policy_config,
                cache_enabled=cache_enabled,
                cache_dir=cache_dir
            )
            for provider in providers:
                # Handle CachedProvider wrapper
                actual_provider = provider.provider if isinstance(provider, CachedProvider) else provider
                provider_name = actual_provider.name if hasattr(actual_provider, 'name') else actual_provider.__class__.__name__
                provider_kind = actual_provider.kind if hasattr(actual_provider, 'kind') else 'unknown'
                
                logger.info(f"  → Running provider: {provider_name} ({provider_kind})")
                
                if provider_kind == "llm":
                    if is_github_pr:
                        result = actual_provider.analyze_pr(ctx.github_repo, ctx.pr_id, github_token)
                    elif ctx.llm_local:
                        result = actual_provider.analyze_files(ctx.path)
                    else:
                        logger.warning(f"  ⚠️  Skipping LLM provider '{provider_name}': insufficient context.")
                        continue
                else:
                    result = provider.collect(base_path=ctx.path)

                provider_obs_count = 0
                for obs in result.observations:
                    f_path, _ = extract_location(obs)
                    if exclude_filter(f_path):
                        continue
                    if not include_filter or include_filter(f_path):
                        all_observations.append(obs)
                        provider_obs_count += 1
                
                logger.info(f"  ✓ {provider_name}: collected {provider_obs_count} observations")
        else:
            logger.info("⏭️  STEP 1: Skipped (no providers or --compliance-only mode)")

        # Step 2: Compliance
        should_run_compliance = False
        compliance_reason = []
        
        if is_compliance_flag or is_compliance_only:
            should_run_compliance = True
            compliance_reason.append("explicit --compliance flag")
        
        if policy_config.compliance and policy_config.compliance.enabled:
            is_pr_mode = is_github_pr or is_gitlab_mr
            if is_pr_mode:
                run_in_pr = getattr(policy_config.compliance, 'run_in_pr', False)
                if run_in_pr:
                    should_run_compliance = True
                    compliance_reason.append("policy.compliance.enabled=true + run_in_pr=true")
                else:
                    compliance_reason.append("(blocked: run_in_pr=false)")
            else:
                should_run_compliance = True
                compliance_reason.append("policy.compliance.enabled=true (local mode)")

        logger.info("▶️  STEP 2: Compliance check decision")
        logger.info(f"  Should run: {should_run_compliance}")
        logger.info(f"  Reasons: {', '.join(compliance_reason) if compliance_reason else '(none)'}")

        if should_run_compliance:
            logger.info("  → Running compliance pipeline...")
            pipeline = CompliancePipeline(policy_config.compliance)
            compliance_obs = pipeline.run(
                artifacts_path=ctx.path,
                ai_provider_region=policy_config.ai_provider.get("region")
            )

            policy_dir = os.path.dirname(os.path.abspath(ctx.policy_path))
            target_dir = os.path.abspath(ctx.path)

            compliance_obs_count = 0
            for obs in compliance_obs:
                f_path, _ = extract_location(obs)
                if os.path.basename(f_path) == "policy.yml" and policy_dir != target_dir:
                    continue
                if exclude_filter(f_path):
                    continue
                if not include_filter or include_filter(f_path):
                    all_observations.append(obs)
                    compliance_obs_count += 1
            
            logger.info(f"  ✓ Compliance: collected {compliance_obs_count} observations")
        else:
            logger.info("  ⏭️  Compliance skipped")

        # Step 3: Evaluate
        logger.info("▶️  STEP 3: Policy evaluation")
        logger.info(f"  Total observations: {len(all_observations)}")
        
        engine = PolicyEngine(rules)
        decision = engine.evaluate(all_observations)
        logger.info(f"  ✅ Policy Verdict: {decision.mode.value.upper()}")

        # Apply enforcement override
        effective_mode = decision.mode
        if enforcement_override == "never":
            effective_mode = DecisionMode.ADVISORY
        elif enforcement_override == "advisory" and decision.mode == DecisionMode.BLOCKING:
            logger.warning("⚠️  --enforcement=advisory: policy would BLOCK but overridden to ADVISORY")
            effective_mode = DecisionMode.ADVISORY

        # Step 4: Report
        annotations = []
        for obs in all_observations:
            f_path, l_num = extract_location(obs)
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
            summary=f"Verdict: {effective_mode.value.upper()}. Found {len(annotations)} issues.",
            status=effective_mode,
            annotations=annotations,
            reasons=list(dict.fromkeys(decision.reasons)),
        )

        # Step 5: Reporters
        logger.info("▶️  STEP 5: Reporting")
        
        # GitLab MR Reporter
        if is_gitlab_mr and gitlab_token:
            logger.info(f"  Using GitLab MR reporter for {ctx.gitlab_project}!{ctx.mr_iid}")
            GitLabMRReporter(
                gitlab_token, 
                ctx.gitlab_project, 
                ctx.mr_iid,
                gitlab_url=getattr(ctx, 'gitlab_url', 'https://gitlab.com')
            ).report(report)
        # GitHub Reporters
        elif is_github_pr and github_token:
            logger.info(f"  Using GitHub reporters for repo={ctx.github_repo}")
            if ctx.pr_id:
                logger.info(f"  → Posting PR comment to PR #{ctx.pr_id}")
                GitHubPRReporter(github_token, ctx.github_repo, ctx.pr_id).report(report)
            if ctx.github_sha:
                logger.info(f"  → Creating GitHub Check for commit {ctx.github_sha}")
                GitHubChecksReporter(github_token, ctx.github_repo, ctx.github_sha).report(report)
        # Console fallback
        else:
            logger.info("  Using console reporter (no CI/CD context)")
            ConsoleReporter(verbose=ctx.verbose).report(report)

        logger.info("=" * 60)
        logger.info("✅ Execution Completed Successfully")
        logger.info("=" * 60)
        return 0 if effective_mode != DecisionMode.BLOCKING else 1

    except Exception as e:
        logger.error(f"❌ Execution failed: {str(e)}", exc_info=True)
        return 1
    