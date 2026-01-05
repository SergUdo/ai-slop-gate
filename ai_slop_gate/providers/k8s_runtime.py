from typing import List, Dict, Any
from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.domain.observation_result import ObservationResult


class K8sRuntimeProvider:
    """
    Analyzes Kubernetes manifests (runtime-style, admission-like checks).
    Pure static analysis of YAML, NO cluster access.
    """

    def __init__(self, manifests: List[Dict[str, Any]]):
        self.manifests = manifests

    def collect(self) -> ObservationResult:
        observations: List[Observation] = []

        for doc in self.manifests:
            if not isinstance(doc, dict):
                continue

            kind = doc.get("kind")
            spec = doc.get("spec", {})

            if kind != "Deployment":
                continue

            template = spec.get("template", {})
            pod_spec = template.get("spec", {})
            containers = pod_spec.get("containers", [])

            for container in containers:
                security = container.get("securityContext", {})

                # ❌ runAsUser: 0
                if security.get("runAsUser") == 0:
                    observations.append(
                        Observation(
                            rule_id="k8s-run-as-root",
                            category="security",
                            signal="RUN_AS_ROOT",
                            severity="high",
                            message="Container runs as root user",
                            location="Deployment",
                            confidence=1.0,
                            evidence={
                                "container": container.get("name"),
                            },
                        )
                    )

                # ❌ privileged container
                if security.get("privileged") is True:
                    observations.append(
                        Observation(
                            rule_id="k8s-privileged",
                            category="security",
                            signal="PRIVILEGED_CONTAINER",
                            severity="high",
                            message="Privileged container detected",
                            location="Deployment",
                            confidence=1.0,
                            evidence={
                                "container": container.get("name"),
                            },
                        )
                    )

        return ObservationResult(observations)
