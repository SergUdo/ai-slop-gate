import json
from pathlib import Path
from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.observation_result import ObservationResult
from ai_slop_gate.domain.signals import Signal


class TerraformPlanProvider:
    """
    Static analysis of terraform plan JSON
    (output of: terraform show -json plan.out)
    """

    name = "terraform-plan"

    def __init__(self, plan_path: str = "plan.json"):
        self.plan_path = Path(plan_path)

    def collect(self):
        if not self.plan_path.exists():
            return []

        data = json.loads(self.plan_path.read_text())
        observations = []

        for rc in data.get("resource_changes", []):
            change = rc.get("change", {})
            after = change.get("after", {}) or {}

            # Example: open security group rule
            if "cidr_blocks" in after:
                if "0.0.0.0/0" in after.get("cidr_blocks", []):
                    observations.append(
                        Observation(
                            rule_id="TFPLAN001",
                            category="TERRAFORM",
                            signal=Signal.INSECURE_CONFIG,
                            severity="high",
                            message="Terraform plan exposes resource to 0.0.0.0/0",
                            confidence=0.98,
                            location={
                                "file": rc.get("address", "unknown"),
                                "line": 1,
                            },
                        )
                    )

        return ObservationResult(observations)
