from pathlib import Path
import yaml

from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.signals import Signal


class KubernetesStaticProvider:
    name = "k8s-static"

    def collect(self):
        observations = []

        for yml in Path(".").rglob("*.y*ml"):
            try:
                docs = list(yaml.safe_load_all(yml.read_text()))
            except Exception:
                continue

            for doc in docs:
                if not isinstance(doc, dict):
                    continue

                spec = doc.get("spec", {})
                containers = (
                    spec.get("template", {})
                    .get("spec", {})
                    .get("containers", [])
                )

                for c in containers:
                    if c.get("securityContext", {}).get("privileged") is True:
                        observations.append(
                            Observation(
                                rule_id="K8S001",
                                category="KUBERNETES",
                                signal=Signal.INSECURE_CONFIG,
                                severity="high",
                                message="Privileged container detected",
                                confidence=0.95,
                                location={
                                    "file": str(yml),
                                    "line": 1,
                                },
                            )
                        )

        return observations
