from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.decision import DecisionMode
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.providers.static_pipeline import StaticPipelineProvider
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation

def run_cli(ctx):
    print("=== AI Slop Gate Compliance Report ===")
    policy_config, rules = load_policy(ctx.policy_path)
    observations = []

    if ctx.provider == "static":
        provider = StaticPipelineProvider()
        result = provider.collect()
        observations.extend(result.observations)

    if ctx.compliance_enabled and policy_config.compliance and policy_config.compliance.enabled:
        gateway = ComplianceGateway(policy_config.compliance)
        observations.extend(gateway.analyze(ctx.input_file or "."))

    engine = PolicyEngine(rules)
    decision = engine.evaluate(observations)

    if ctx.github_repo and ctx.pr_id and ctx.github_token:
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
        reporter = GitHubPRReporter(
            token=ctx.github_token,
            repo_name=ctx.github_repo,
            pr_id=ctx.pr_id,
        )
        reporter.report(report)

    print(f"Decision: {decision.mode.name}")
    return 1 if decision.mode == DecisionMode.BLOCKING else 0
