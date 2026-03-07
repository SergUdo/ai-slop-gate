import json
import os
import subprocess
import logging
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

# VEX output filename written alongside the scanned project
_VEX_FILENAME = "sbom-cyclonedx-vex.json"


class TrivyProvider(BaseProvider):
    """
    Trivy Security Scanner Provider

    Scans for vulnerabilities in:
    - Python dependencies (requirements.txt, pip packages)
    - Node.js dependencies (package.json, node_modules)
    - Container images
    - Infrastructure as Code

    By default scans for HIGH and CRITICAL vulnerabilities.
    Set include_medium=True to also include MEDIUM severity.

    Also saves sbom-cyclonedx-vex.json (CycloneDX + CVE) to base_path,
    so it is available as a workflow artifact without extra steps.
    """

    def __init__(
        self,
        model: str = "trivy-scanner-v1",
        include_medium: bool = False,
        include_low: bool = False,
    ):
        self.name = "trivy"
        self.kind = "security"
        self.model = model
        self.include_medium = include_medium
        self.include_low = include_low

        severities = ["CRITICAL", "HIGH"]
        if include_medium:
            severities.append("MEDIUM")
        if include_low:
            severities.append("LOW")

        self.severity_filter = ",".join(severities)
        logger.info(f"[TrivyProvider] Scanning for severities: {self.severity_filter}")

    def collect(self, base_path: str = ".") -> ProviderObservation:
        """
        Run Trivy filesystem scan, save CycloneDX VEX file,
        and return vulnerability observations.
        """
        observations = []

        try:
            vex_path = os.path.join(base_path, _VEX_FILENAME)

            # ── 1. Save CycloneDX VEX file for artifact upload ───────────────
            vex_cmd = [
                "trivy", "fs",
                "--format", "cyclonedx",
                "--output", vex_path,
                "--severity", self.severity_filter,
                "--exit-code", "0",
                "--quiet",
                base_path,
            ]

            logger.debug(f"[TrivyProvider] Saving VEX: {' '.join(vex_cmd)}")
            vex_result = subprocess.run(
                vex_cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if vex_result.returncode != 0:
                logger.error(
                    f"[TrivyProvider] VEX generation failed: "
                    f"{vex_result.stderr[:300]}"
                )
            else:
                logger.info(f"[TrivyProvider] Saved {_VEX_FILENAME}")

            # ── 2. Scan again in JSON format to parse observations ────────────
            json_cmd = [
                "trivy", "fs",
                "--format", "json",
                "--severity", self.severity_filter,
                "--quiet",
                base_path,
            ]

            logger.debug(f"[TrivyProvider] Running JSON scan: {' '.join(json_cmd)}")
            result = subprocess.run(
                json_cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                logger.error(
                    f"[TrivyProvider] Trivy scan failed with code "
                    f"{result.returncode}: {result.stderr[:500]}"
                )
                return ProviderObservation(
                    self.name,
                    self.model,
                    [],
                    f"Scan Failed (exit code {result.returncode})",
                )

            # ── 3. Parse JSON output → observations ───────────────────────────
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"[TrivyProvider] Failed to parse Trivy JSON: {e}")
                return ProviderObservation(
                    self.name, self.model, [], "JSON Parse Error"
                )

            total_vulns = 0

            for result_item in data.get("Results", []):
                target = result_item.get("Target", "unknown")
                vulnerabilities = result_item.get("Vulnerabilities")

                if not vulnerabilities:
                    continue

                logger.debug(
                    f"[TrivyProvider] Found {len(vulnerabilities)} "
                    f"vulnerabilities in {target}"
                )

                for vuln in vulnerabilities:
                    vuln_id = vuln.get("VulnerabilityID", "UNKNOWN")
                    severity = vuln.get("Severity", "UNKNOWN").lower()
                    pkg_name = vuln.get("PkgName", "unknown")
                    installed_version = vuln.get("InstalledVersion", "unknown")
                    fixed_version = vuln.get("FixedVersion", "")
                    title = vuln.get("Title", "")

                    message = f"Vulnerability {vuln_id} in {pkg_name}@{installed_version}"
                    if title:
                        message += f": {title}"

                    observations.append(
                        make_observation(
                            provider=self.name,
                            category="security",
                            signal="vulnerability_detected",
                            confidence=1.0,
                            message=message,
                            severity=severity,
                            evidence={
                                "cve": vuln_id,
                                "pkg": pkg_name,
                                "installed": installed_version,
                                "fixed": fixed_version if fixed_version else "no fix available",
                                "target": target,
                                "severity": severity.upper(),
                            },
                        )
                    )
                    total_vulns += 1

            status = f"Trivy Scan Complete. Found {total_vulns} vulnerabilities."
            logger.info(f"[TrivyProvider] {status}")

            return ProviderObservation(self.name, self.model, observations, status)

        except FileNotFoundError:
            logger.error(
                "[TrivyProvider] Trivy binary not found. Is it installed?\n"
                "Install: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
            )
            return ProviderObservation(self.name, self.model, [], "Trivy not installed")

        except subprocess.TimeoutExpired:
            logger.error("[TrivyProvider] Trivy scan timed out after 120 seconds")
            return ProviderObservation(self.name, self.model, [], "Scan timeout")

        except Exception as e:
            logger.error(f"[TrivyProvider] Error during Trivy scan: {e}", exc_info=True)
            return ProviderObservation(
                self.name, self.model, [], f"Scan error: {str(e)}"
            )

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Trivy doesn't support inline code analysis.
        Always use collect() method instead.
        """
        return ProviderObservation(
            self.name,
            self.model,
            [],
            "Use collect() method for filesystem scanning",
        )
    