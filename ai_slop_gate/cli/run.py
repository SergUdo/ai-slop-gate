import os
import logging
import sys
from typing import Optional, Any
from dotenv import load_dotenv
from contextlib import contextmanager

from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.reporters.github_checks import GitHubChecksReporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation

from ai_slop_gate.providers.gemini import GeminiProvider
from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider

load_dotenv()
logger = logging.getLogger("ai_slop_gate")

@contextmanager
def change_dir(destination):
    cdir = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(cdir)

def get_provider(provider_name: str, model: Optional[str] = None) -> Any:
    """
    Фабрика провайдерів. 
    Повертає StaticPipelineProvider для статики.
    """
    p_name = provider_name.lower()
    
    if p_name == "gemini":
        m = model or os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
        return GeminiProvider(model=m)
    
    if p_name in ["static", "static_pipeline"]:
        return StaticPipelineProvider()
    
    raise ValueError(f"Provider '{provider_name}' is not implemented or supported.")

def run_cli(ctx) -> int:
    """
    Основна точка входу CLI. 
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
        # 1. Завантаження політики
        logger.info(f"Loading policy file: {ctx.policy_path}")
        policy_config, rules = load_policy(ctx.policy_path)
        
        ai_model_name = None
        if hasattr(policy_config, 'ai_provider') and policy_config.ai_provider:
            ai_model_name = policy_config.ai_provider.model

        # 2. Ініціалізація провайдера
        provider = get_provider(ctx.provider, model=ai_model_name)
        logger.info(f"Provider: {provider.name} | Kind: {provider.kind}")

        # 3. Виконання аналізу
        result = None
        if ctx.github_repo and ctx.pr_id:
            if provider.kind == "llm":
                if not github_token:
                    raise ValueError("GITHUB_TOKEN is required for LLM PR analysis")
                result = provider.analyze_pr(ctx.github_repo, ctx.pr_id, github_token)
            else:
                # Статика працює в поточній папці CI
                result = provider.collect(base_path=".")
        else:
            result = provider.collect(base_path=".")

        if not result or not result.observations:
            logger.info("No observations found. Repository is clean.")
            return 0

        # 4. Оцінка політикою
        engine = PolicyEngine(rules)
        decision = engine.evaluate(result.observations)
        logger.info(f"Policy Verdict: {decision.mode.value.upper()}")

        # 5. Трансформація обсервацій в анотації (ВИПРАВЛЕНО unknown)
        annotations = []
        for obs in result.observations:
            # Надійний пошук шляху до файлу
            file_path = "root"
            line_num = 1
            
            # Пріоритет 1: Об'єкт location (створений фабрикою)
            if hasattr(obs, 'location') and obs.location:
                file_path = obs.location.file or "root"
                line_num = obs.location.line or 1
            
            # Пріоритет 2: Словник evidence (якщо location порожній)
            elif hasattr(obs, 'evidence') and isinstance(obs.evidence, dict):
                file_path = obs.evidence.get("file", "root")
                line_num = obs.evidence.get("line", 1)

            # Форматування рівня важливості
            severity = (obs.severity or "medium").lower()
            level = "failure" if severity in ["high", "critical", "failure", "blocking"] else "warning"
            
            annotations.append(
                CheckAnnotation(
                    file=file_path,
                    line=line_num,
                    level=level,
                    message=f"[{obs.signal}] {obs.message}"
                )
            )

        # 6. Репортинг
        if ctx.github_repo and github_token:
            report = CheckReport(
                title=f"AI Slop Gate: {provider.name.upper()} Audit",
                summary=f"Verdict: {decision.mode.value.upper()}. Found {len(annotations)} issues.",
                status=decision.mode,
                annotations=annotations,
            )

            if ctx.pr_id:
                pr_reporter = GitHubPRReporter(github_token, ctx.github_repo, ctx.pr_id)
                pr_reporter.report(report)
                logger.info("Results posted to GitHub PR.")

            if ctx.github_sha:
                checks_reporter = GitHubChecksReporter(github_token, ctx.github_repo, ctx.github_sha)
                checks_reporter.report(report)
                logger.info(f"GitHub Check Run created for SHA: {ctx.github_sha[:7]}")

        logger.info("--- Execution Completed Successfully ---")
        return 0

    except Exception as e:
        logger.error(f"Execution failed: {str(e)}", exc_info=True)
        return 1