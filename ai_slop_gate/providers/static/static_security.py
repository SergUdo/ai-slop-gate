import os
import re
import logging
from typing import List
from pathlib import Path

from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation import Observation, Location
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class StaticSecurityProvider(BaseProvider):
    """
    Static Security Provider - handles security and PII detection.
    
    Responsibilities:
    - Hardcoded secrets detection (API keys, tokens, passwords)
    - PII detection (emails, SSN, phone numbers)
    - Suspicious TODO comments
    - Non-EU endpoint detection (GDPR compliance)
    
    License compliance is handled by CompliancePipeline.
    """
    
    EXCLUDE_DIRS = {
        ".git", ".venv", "venv", "__pycache__", "node_modules",
        "dist", "build", ".slop", ".idea", ".pytest_cache",
        "site-packages", "ai_slop_gate", "htmlcov", "tests",
    }
    
    SCANNABLE_EXTENSIONS = (
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb",
        ".php", ".cs", ".txt", ".md", ".yaml", ".yml", ".json",
        ".env", ".sh", ".bash", ".sql", ".html", ".css"
    )

    def __init__(
        self, 
        model: str = "static-security-v1",
        detect_secrets: bool = True,
        detect_pii: bool = True,
        detect_todos: bool = True,
        detect_non_eu_endpoints: bool = True,
        severity_email: str = "medium",
        severity_todo: str = "low",
        severity_endpoint: str = "medium"
    ):
        self.name = "static_security"
        self.kind = "static"
        self.model = model
        
        # Feature flags
        self.detect_secrets = detect_secrets
        self.detect_pii = detect_pii
        self.detect_todos = detect_todos
        self.detect_non_eu_endpoints = detect_non_eu_endpoints
        
        # Severity levels
        self.severity_email = severity_email
        self.severity_todo = severity_todo
        self.severity_endpoint = severity_endpoint
        
        # Compiled regex patterns for performance
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance"""
        self.secret_pattern = re.compile(
            r"(api[_-]?key|secret|token|password|passwd|pwd|bearer)\s*[:=]\s*['\"]?[\w\-]{8,}",
            re.IGNORECASE
        )
        
        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )
        
        self.ssn_pattern = re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b"
        )
        
        self.phone_pattern = re.compile(
            r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        )
        
        # Non-EU endpoint - matches URLs without 'eu' in subdomain
        self.non_eu_endpoint_pattern = re.compile(
            r"https?://(?![a-z0-9-]*\.?eu[.-])([a-z0-9-]+\.)+[a-z]{2,}",
            re.IGNORECASE
        )

    def collect(self, base_path: str = ".") -> ProviderObservation:
        """
        Scan entire codebase for security issues and PII.
        """
        observations = []
        base = os.path.abspath(base_path)

        for root, dirs, files in os.walk(base):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for fname in files:
                if not fname.endswith(self.SCANNABLE_EXTENSIONS):
                    continue

                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, base)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    
                    observations.extend(self._scan_file(rel_path, lines))
                    
                except Exception as e:
                    logger.error(f"Error reading {rel_path}: {e}")

        status = f"Security scan complete. Found {len(observations)} issues."
        return ProviderObservation(self.name, self.model, observations, status)

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Analyze a single code snippet for security issues.
        """
        lines = code.splitlines()
        observations = self._scan_file(input_file or "inline_code", lines)
        
        status = f"Analysis complete. Found {len(observations)} issues."
        return ProviderObservation(self.name, self.model, observations, status)

    def _scan_file(self, file_path: str, lines: List[str]) -> List[Observation]:
        """
        Scan a file's content line by line for security issues.
        """
        observations = []
        
        for line_num, line in enumerate(lines, start=1):
            
            # 1. Hardcoded secrets
            if self.detect_secrets and self.secret_pattern.search(line):
                observations.append(
                    Observation(
                        category="security",
                        signal="hardcoded_secret",
                        confidence=0.95,
                        message="Potential hardcoded secret detected (API key, token, or password).",
                        severity="high",
                        location=Location(file=file_path, line=line_num),
                    )
                )

            # 2. Email addresses (PII)
            if self.detect_pii and self.email_pattern.search(line):
                # Avoid false positives from imports and common placeholders
                if not any(skip in line.lower() for skip in ["import", "from", "example.com", "test.com"]):
                    observations.append(
                        Observation(
                            category="security",
                            signal="pii_email",
                            confidence=0.9,
                            message="Email address detected in source code (potential PII leak).",
                            severity=self.severity_email,
                            location=Location(file=file_path, line=line_num),
                        )
                    )

            # 3. SSN (PII)
            if self.detect_pii and self.ssn_pattern.search(line):
                observations.append(
                    Observation(
                        category="security",
                        signal="pii_ssn",
                        confidence=0.95,
                        message="Social Security Number pattern detected (PII leak).",
                        severity="high",
                        location=Location(file=file_path, line=line_num),
                    )
                )

            # 4. Phone numbers (PII)
            if self.detect_pii and self.phone_pattern.search(line):
                # Avoid version numbers and common false positives
                if not any(skip in line.lower() for skip in ["version", "port", "http"]):
                    observations.append(
                        Observation(
                            category="security",
                            signal="pii_phone",
                            confidence=0.7,
                            message="Phone number pattern detected (potential PII).",
                            severity="medium",
                            location=Location(file=file_path, line=line_num),
                        )
                    )

            # 5. Suspicious TODO comments
            if self.detect_todos and "TODO" in line.upper():
                # Flag TODOs related to security
                is_security_todo = any(
                    keyword in line.upper() 
                    for keyword in ["SECURITY", "AUTH", "HACK", "FIX", "VULNERABILITY", "ENCRYPT"]
                )
                
                severity = "medium" if is_security_todo else self.severity_todo
                
                observations.append(
                    Observation(
                        category="quality",
                        signal="suspicious_todo",
                        confidence=1.0,
                        message="Suspicious TODO comment found in code.",
                        severity=severity,
                        location=Location(file=file_path, line=line_num),
                    )
                )

            # 6. Non-EU endpoints (GDPR compliance)
            if self.detect_non_eu_endpoints and self.non_eu_endpoint_pattern.search(line):
                observations.append(
                    Observation(
                        category="compliance",
                        signal="non_eu_endpoint",
                        confidence=0.85,
                        message="Non-EU endpoint detected (potential GDPR violation).",
                        severity=self.severity_endpoint,
                        location=Location(file=file_path, line=line_num),
                    )
                )

        return observations
    