import os
import json
import re
from typing import List, Optional

from ai_slop_gate.domain.observation import Observation, Location
from ai_slop_gate.domain.compliance.config import ComplianceConfig


class CompliancePipeline:
    EXCLUDE_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        ".slop",
        ".idea",
        ".pytest_cache",
        "site-packages",
        "ai_slop_gate",
        "htmlcov",
        "tests",
    }

    def __init__(self, cfg: ComplianceConfig):
        self.cfg = cfg

    def run(self, artifacts_path: str, ai_provider_region: Optional[str]) -> List[Observation]:
        observations = []

        observations.extend(self._check_forbidden_licenses(artifacts_path))
        observations.extend(self._scan_source_for_secrets_and_gdpr(artifacts_path))
        observations.extend(self._check_data_residency(ai_provider_region))

        return observations

    # -------------------------------------------------------------------------
    # 1. Forbidden licenses
    # -------------------------------------------------------------------------
    def _check_forbidden_licenses(self, artifacts_path: str) -> List[Observation]:
        forbidden = set(self.cfg.license_audit.forbidden_licenses or [])
        if not forbidden:
            return []

        manifest_path = os.path.join(artifacts_path, ".slop", "supply_chain.json")
        if not os.path.exists(manifest_path):
            return []

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        deps = data.get("dependencies", [])
        observations = []

        for dep in deps:
            lic = dep.get("license")
            name = dep.get("name")

            if lic and lic in forbidden:
                observations.append(
                    Observation(
                        category="compliance",
                        signal="forbidden_license",
                        confidence=1.0,
                        message=f"Dependency '{name}' uses forbidden license '{lic}'.",
                        severity="high",
                        location=Location(file="policy.yml"),
                    )
                )

        return observations

    # -------------------------------------------------------------------------
    # 2. Secrets, PII, TODOs, endpoints
    # -------------------------------------------------------------------------
    def _scan_source_for_secrets_and_gdpr(self, artifacts_path: str) -> List[Observation]:
        observations = []

        detect_secrets = self.cfg.security_audit.detect_secrets
        detect_pii = self.cfg.security_audit.detect_pii
        detect_todos = self.cfg.security_audit.detect_suspicious_todos
        detect_endpoints = self.cfg.security_audit.detect_non_eu_endpoints

        for root, dirs, files in os.walk(artifacts_path):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for fname in files:
                if not fname.endswith((
                    ".py", ".js", ".ts", ".java", ".go", ".rb",
                    ".php", ".cs", ".txt", ".md"
                )):
                    continue

                path = os.path.join(root, fname)

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                except Exception:
                    continue

                for i, line in enumerate(lines, start=1):

                    # Secrets
                    if detect_secrets and re.search(r"(api[_-]?key|secret|token|password)\s*[:=]", line, re.I):
                        observations.append(
                            Observation(
                                category="compliance",
                                signal="hardcoded_secret",
                                confidence=1.0,
                                message="Potential hardcoded secret detected.",
                                severity="high",
                                location=Location(file=path, line=i),
                            )
                        )

                    # Email (PII)
                    if detect_pii and re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", line):
                        observations.append(
                            Observation(
                                category="compliance",
                                signal="pii_email",
                                confidence=1.0,
                                message="Email address detected in source code.",
                                severity=self.cfg.gdpr_detection.severity_email,
                                location=Location(file=path, line=i),
                            )
                        )

                    # TODO suspicious
                    if detect_todos and "TODO" in line.upper():
                        observations.append(
                            Observation(
                                category="compliance",
                                signal="suspicious_todo",
                                confidence=1.0,
                                message="Suspicious TODO comment found.",
                                severity=self.cfg.gdpr_detection.severity_todo,
                                location=Location(file=path, line=i),
                            )
                        )

                    # Non‑EU endpoints
                    if detect_endpoints and re.search(r"https?://(?!eu)([a-z0-9-]+\.)+[a-z]{2,}", line, re.I):
                        observations.append(
                            Observation(
                                category="compliance",
                                signal="non_eu_endpoint",
                                confidence=1.0,
                                message="Non‑EU endpoint detected.",
                                severity=self.cfg.gdpr_detection.severity_non_eu_endpoint,
                                location=Location(file=path, line=i),
                            )
                        )

        return observations

    # -------------------------------------------------------------------------
    # 3. Data residency
    # -------------------------------------------------------------------------
    def _check_data_residency(self, ai_provider_region: Optional[str]) -> List[Observation]:
        required = self.cfg.security_audit.enforce_data_residency
        mode = self.cfg.data_residency_mode  # advisory | blocking

        if not required:
            return []

        if not ai_provider_region:
            return [
                Observation(
                    category="compliance",
                    signal="data_residency_unknown",
                    confidence=1.0,
                    message="AI provider region is not specified.",
                    severity="medium",
                    location=Location(file="policy.yml"),
                )
            ]

        if ai_provider_region.upper() != required.upper():
            severity = "high" if mode == "blocking" else "medium"

            return [
                Observation(
                    category="compliance",
                    signal="data_residency_violation",
                    confidence=1.0,
                    message=(
                        f"AI provider region '{ai_provider_region}' does not satisfy "
                        f"required residency '{required}' (mode: {mode})."
                    ),
                    severity=severity,
                    location=Location(file="policy.yml"),
                )
            ]

        return []
