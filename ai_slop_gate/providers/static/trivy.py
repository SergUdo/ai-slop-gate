import json
import subprocess
import logging
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class TrivyProvider(BaseProvider):
    def __init__(self, model: str = "trivy-scanner-v1"):
        self.name = "trivy"
        self.kind = "security"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        try:
            cmd = ["trivy", "fs", "--format", "json", "--severity", "CRITICAL,HIGH", base_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Trivy scan failed: {result.stderr}")
                return ProviderObservation(self.name, self.model, [], "Scan Failed")

            data = json.loads(result.stdout)
            
            for result_item in data.get("Results", []):
                target = result_item.get("Target", "unknown")
                for vuln in result_item.get("Vulnerabilities", []):
                    observations.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="vulnerability_detected",
                        confidence=1.0,
                        message=f"Vulnerability detected: {vuln.get('VulnerabilityID')}",
                        severity=vuln.get("Severity", "high").lower(),
                        evidence={
                            "pkg": vuln.get("PkgName"),
                            "installed": vuln.get("InstalledVersion"),
                            "fixed": vuln.get("FixedVersion"),
                            "target": target
                        }
                    ))
        except FileNotFoundError:
            logger.error("Trivy binary not found. Is it installed?")
        except Exception as e:
            logger.error(f"Error during Trivy scan: {e}")

        return ProviderObservation(self.name, self.model, observations, "Trivy Scan Complete")

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "")