from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.decision import DecisionMode


def run_cli(ctx) -> int:
    """
    Canonical Stage 0.6 CLI entrypoint.
    This function is a stable contract for:
    - CLI
    - tests
    - providers
    - registry
    """

    policy_config, rules = load_policy(ctx.policy_path)

    observations = []

    # --- Compliance (optional, advisory input only)
    if ctx.compliance_enabled and policy_config.compliance:
        gateway = ComplianceGateway(policy_config.compliance)
        compliance_obs = gateway.analyze(ctx.repository or ".")
        observations.extend(compliance_obs)

        for obs in compliance_obs:
            print(f"[COMPLIANCE] {obs.license}: {obs.message}")

    # --- Policy evaluation
    engine = PolicyEngine(rules)
    decision = engine.evaluate(observations)

    print(f"Decision: {decision.mode.name}")

    # --- Exit code contract
    if decision.mode == DecisionMode.BLOCKING:
        return 1

    return 0
