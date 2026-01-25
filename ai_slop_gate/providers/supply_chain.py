import os
import logging
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class SupplyChainProvider(BaseProvider):
    def __init__(self, model: str = "manifest-scanner-v1"):
        self.name = "supply-chain"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        target = os.path.abspath(base_path)
        
        manifests = ["requirements.txt", "package.json", "pyproject.toml"]
        
        for root, _, files in os.walk(target):
            if any(x in root for x in [".venv", "node_modules", "htmlcov", ".venv"]): continue
            
            for f in files:
                if f in manifests:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, target)
                    
                    try:
                        with open(full_path, "r") as content:
                            text = content.read()
                            if "GPL" in text.upper():
                                observations.append(make_observation(
                                    provider=self.name,
                                    category="compliance",
                                    signal="copyleft_license",
                                    confidence=1.0,
                                    message=f"GPL-like license detected in {f}",
                                    severity="high",
                                    evidence={"file": rel_path, "line": 1}
                                ))
                    except Exception as e:
                        logger.error(f"Error reading {rel_path}: {e}")
                        
        return ProviderObservation(self.name, self.model, observations, "Supply Chain Audit Done")

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "")
    