# ai_slop_gate/cli/run.py
import os
from dotenv import load_dotenv
from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation
from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider

load_dotenv()

def run_cli(ctx):
    github_token = ctx.github_token or os.getenv("GITHUB_TOKEN")

    policy_config, rules = load_policy(ctx.policy_path)

    provider = StaticPipelineProvider()
    result = provider.collect()
    observations = result.observations

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

    if ctx.github_repo and ctx.pr_id and github_token:
        reporter = GitHubPRReporter(
            token=github_token,
            repo_name=ctx.github_repo,
            pr_id=ctx.pr_id,
        )
        reporter.report(report)
        print(f"Successfully posted PR comment to {ctx.github_repo}#{ctx.pr_id}.")
    else:
        print("GITHUB_TOKEN, GITHUB_REPO, or PR_ID is missing. Skipping PR comment.")

    print(f"Decision: {decision.mode.name}")
    return 0
