import os
import re
from typing import List, Dict, Any
from .base import BaseProvider
from ..domain.observation import Observation, Severity, Location

class SupplyChainProvider(BaseProvider):
    def __init__(self, policy: Dict[str, Any]):
        self.policy = policy
        self.forbidden_licenses = policy.get("license_audit", {}).get("forbidden_licenses", ["GPL-3.0"])
        self.enabled = policy.get("enabled", False)

    def collect(self) -> List[Observation]:
        if not self.enabled: 
            return []
        
        observations = []
        base_path = os.path.abspath(os.getcwd())
        
        for root, _, files in os.walk(base_path):
            for file in files:
                if file in ["requirements.txt", "pyproject.toml", ".env"]:
                    full_path = os.path.join(root, file)
                    observations.extend(self._scan_manifest(full_path))
        return observations

    def _scan_manifest(self, filepath: str) -> List[Observation]:
        obs_list = []
        lic_audit = self.policy.get("license_audit", {})
        forbidden = lic_audit.get("forbidden_licenses", ["GPL-3.0"])
        
        try:
            with open(filepath, "r", errors="ignore") as f:
                content = f.read()
                for lic in forbidden:
                    if lic.lower() in content.lower():
                        from ..domain.observation import Observation, Severity, Location
                        obs_list.append(Observation(
                            rule_id="COMPLIANCE-LIC-01",
                            category="compliance",
                            signal="license_violation",
                            message=f"Forbidden license {lic} found in {filepath}",
                            severity=Severity.HIGH,
                            confidence=1.0,
                            location=Location(file=filepath)
                        ))
                
                if "API_KEY" in content.upper() or "SECRET" in content.upper():
                    from ..domain.observation import Observation, Severity, Location
                    obs_list.append(Observation(
                        rule_id="COMPLIANCE-SEC-01",
                        category="compliance",
                        signal="secret_exposed",
                        message=f"Potential secret found in {filepath}",
                        severity=Severity.HIGH,
                        confidence=0.8,
                        location=Location(file=filepath)
                    ))
        except Exception:
            pass
        return obs_list