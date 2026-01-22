# python -m  scripts/test_full_pipeline
# scripts/test_full_pipeline.py


import os
import logging
from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation
from ai_slop_gate.cli.utils import load_policy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    policy_config, rules = load_policy("policy.yml")

    static_provider = StaticPipelineProvider()
    static_result = static_provider.collect()
    observations = static_result.observations

    engine = PolicyEngine(rules)
    decision = engine.evaluate(observations)

    annotations = [
        CheckAnnotation(
            file=obs.evidence.get("file") if obs.evidence else None,
            line=obs.evidence.get("line") if obs.evidence else None,
            level="warning" if obs.severity == "low" else "failure",
            message=obs.message
        )
        for obs in observations
    ]

    report = CheckReport(
        title="AI Slop Gate Analysis Results",
        summary=f"Decision: {decision.mode.name}",
        status=decision.mode,
        annotations=annotations,
    )

    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = "SergUdo/slop_test"
    pr_id = 1

    if github_token:
        reporter = GitHubPRReporter(
            token=github_token,
            repo_name=github_repo,
            pr_id=pr_id,
        )
        reporter.report(report)
        logger.info("Successfully posted PR comment.")
    else:
        logger.warning("GITHUB_TOKEN is missing. Skipping PR comment.")

    logger.info(f"Decision: {decision.mode.name}")

if __name__ == "__main__":
    main()
