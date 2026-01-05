from pathlib import Path
import yaml
from ai_slop_gate.providers.base import BaseProvider
from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.cli.logger import logger


class K8sRuntimeProvider(BaseProvider):
    """
    Analyzes Kubernetes manifests for runtime risks.
    """

    def __init__(self, manifests: str | list | None = None):
        self.manifests_path: str | None = None
        self.manifests: list | None = None

        if isinstance(manifests, (str, Path)):
            self.manifests_path = str(manifests)
        elif isinstance(manifests, list):
            self.manifests = manifests

    def cache_key(self):
        return {
            "provider": "k8s-runtime",
            "manifests_path": self.manifests_path or "inline",
        }

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
                            source="k8s-runtime",
                            level="warning",
                            message=f"Deployment {metadata.get('name')} has only 1 replica",
                        )
                    )

        return observations

