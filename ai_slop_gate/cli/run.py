from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.decision import DecisionMode


def run_cli(ctx):
    # --- Load policy ---
    policy_config, rules = load_policy(ctx.policy)

    observations = []

    # --- Compliance stage (stage-0.7 invariant) ---
    if ctx.compliance and policy_config.compliance and policy_config.compliance.enabled:
        gateway = ComplianceGateway(policy_config.compliance)
        observations.extend(
            gateway.analyze(ctx.input_file or ".")
        )

    # --- Policy evaluation ---
    engine = PolicyEngine(rules)
    decision = engine.evaluate(observations)

    # --- Minimal mode (used by tests) ---
    if not ctx.verbose:
        print(f"Decision: {decision.mode.name}")
        return 1 if decision.mode == DecisionMode.BLOCKING else 0

    # --- Verbose mode ---
    print("=== AI Slop Gate Compliance Report ===\n")

    # Active profile
    if policy_config.compliance and policy_config.compliance.profiles:
        print(f"Active profile: {policy_config.compliance.profiles[0]}")
    else:
        print("Active profile: none")

    # Compliance settings
    if policy_config.compliance:
        print(f"Forbidden licenses: {policy_config.compliance.forbid_licenses or []}")
        print(f"Allowed licenses: {policy_config.compliance.allow_licenses or []}")
    else:
        print("Compliance: disabled")

    print(f"\nRules loaded: {len(rules)}\n")

    # Observations
    print("Observations:")
    if not observations:
        print("  (none)")
    else:
        for obs in observations:
            loc = ""
            if obs.evidence and "file" in obs.evidence:
                loc = f"{obs.evidence['file']}:{obs.evidence.get('line', 1)}"

            license_info = ""
            if obs.evidence and "license" in obs.evidence:
                license_info = f"[{obs.evidence['license']}]"

            print(f"  - {obs.category}/{obs.signal} {license_info} {loc}")

    # Reasons
    print("\nReasons:")
    if not decision.reasons:
        print("  (none)")
    else:
        for r in decision.reasons:
            print(f"  - {r}")

    # Annotations
    print("\nAnnotations:")
    if not decision.annotations:
        print("  (none)")
    else:
        for a in decision.annotations:
            print(f"  - {a.file}:{a.line} → {a.message}")

    print(f"\nDecision: {decision.mode.name}")

    return 1 if decision.mode == DecisionMode.BLOCKING else 0
