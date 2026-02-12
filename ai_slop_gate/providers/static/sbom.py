import json
import subprocess
import logging
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class SBOMProvider(BaseProvider):
    def __init__(self, model: str = "syft-sbom-v1"):
        self.name = "sbom_generator"
        self.kind = "supply_chain"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        try:
            # Run Syft to generate SBOM in JSON format
            # syft . -o json
            cmd = ["syft", base_path, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return ProviderObservation(self.name, self.model, [], "SBOM Generation Failed")

            data = json.loads(result.stdout)
            
            # Create an observation for the generated SBOM
            pkgs = data.get("artifacts", [])
            observations.append(make_observation(
                provider=self.name,
                category="supply_chain",
                signal="sbom_generated",
                confidence=1.0,
                message=f"Generated SBOM with {len(pkgs)} dependencies.",
                severity="info",
                evidence={"package_count": len(pkgs)}
            ))
            
        except FileNotFoundError:
            logger.error("Syft binary not found. Please install it to use SBOM features.")
        
        return ProviderObservation(self.name, self.model, observations, "SBOM Complete")
    
    def analyze(self, code: str, input_file: str = "inline") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "")