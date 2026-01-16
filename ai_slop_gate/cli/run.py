from ai_slop_gate.cli.utils import load_policy_rules
from ai_slop_gate.domain.compliance.gateway import ComplianceGateway

def run_cli(policy_path: str, provider: str):
    rules = load_policy_rules(policy_path)

    print("Decision: ALLOW (stage 0.1)")

    # --- Stage 0.2 compliance ---
    compliance_enabled = True
    if compliance_enabled:
        gateway = ComplianceGateway()
        result = gateway.analyze(".")

        if result.has_issues:
            print("Compliance issues detected:")
            for issue in result.issues:
                print(
                    f"[{issue.severity}] {issue.license} — {issue.message}"
                )
        else:
            print("Compliance: OK")
