from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.decision import DecisionMode


def run_cli(ctx):
    policy_config, rules = load_policy(ctx.policy_path)
    observations = []

    if ctx.compliance_enabled and policy_config.compliance and policy_config.compliance.enabled:
        gateway = ComplianceGateway(policy_config.compliance)
        observations.extend(
            gateway.analyze(ctx.input_file or ".")
        )

    engine = PolicyEngine(rules)
    decision = engine.evaluate(observations)

    print(f"Decision: {decision.mode.name}")

    return 1 if decision.mode == DecisionMode.BLOCKING else 0
