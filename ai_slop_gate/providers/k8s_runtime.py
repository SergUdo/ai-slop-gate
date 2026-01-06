from pathlib import Path
import yaml
from ai_slop_gate.cli.logger import logger
from ai_slop_gate.domain.observation import Observation, Severity

class K8sRuntimeProvider:
    def __init__(self, manifests=None, manifests_path=None):
        self.manifests = manifests
        self.manifests_path = manifests_path

    def collect(self) -> list[Observation]:
        if self.manifests is None and self.manifests_path:
            path = Path(self.manifests_path)
            if not path.exists():
                logger.warning(f"K8s manifests not found: {path}, skipping")
                return []

            with path.open() as f:
                self.manifests = list(yaml.safe_load_all(f))

        if not self.manifests:
            logger.info("No k8s manifests provided, skipping k8s analysis")
            return []

        observations: list[Observation] = []

        for doc in self.manifests:
            if not isinstance(doc, dict):
                continue

            kind = doc.get("kind")
            metadata = doc.get("metadata", {})

            if kind == "Deployment":
                spec = doc.get("spec", {})
                replicas = spec.get("replicas", 1)

                if replicas == 1:
                    observations.append(
                        Observation(
                            rule_id="k8s_single_replica",
                            category="k8s",
                            signal="deployment_replicas",
                            message=f"Deployment {metadata.get('name')} has only 1 replica",
                            severity=Severity.MEDIUM,
                            confidence=0.9,
                            location=None,
                        )
                    )

        return observations
