from pathlib import Path
from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.signals import Signal


class TerraformStaticProvider:
    name = "terraform-static"

    def collect(self):
        observations = []

        for tf_file in Path(".").rglob("*.tf"):
            content = tf_file.read_text(errors="ignore")

            if "0.0.0.0/0" in content:
                observations.append(
                    Observation(
                        rule_id="TF001",
                        category="TERRAFORM",
                        signal=Signal.INSECURE_CONFIG,
                        severity="high",
                        message="Open CIDR block (0.0.0.0/0) detected",
                        confidence=0.9,
                        location={
                            "file": str(tf_file),
                            "line": 1,
                        },
                    )
                )

        return observations
