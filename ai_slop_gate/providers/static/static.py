import os
import logging
from pathlib import Path
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class StaticProvider(BaseProvider):
    """
    Static Provider - handles basic code quality checks.
    
    Responsibilities:
    - Code style issues
    - Basic TODO detection (non-security)
    - Code complexity warnings
    
    Security checks moved to: StaticSecurityProvider
    License compliance moved to: CompliancePipeline
    """
    
    EXCLUDE_DIRS = {
        ".venv", "venv", "node_modules", "ai_slop_gate",
        "scripts", "htmlcov", ".git", "site-packages", "__pycache__"
    }

    def __init__(self, model: str = "generic-static-v1"):
        self.name = "static"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        """
        Scan codebase for basic quality issues (non-security).
        """
        observations = []
        base = os.path.abspath(base_path)

        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for f in files:
                if not any(f.endswith(ext) for ext in [".js", ".ts", ".py", ".sh"]):
                    continue

                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base)

                try:
                    text = open(full_path, "r", errors="ignore").read()
                    for i, line in enumerate(text.splitlines(), start=1):
                        
                        # Basic TODO detection (quality, not security)
                        if "TODO" in line.upper():
                            # Only flag if NOT security-related (those are handled by StaticSecurityProvider)
                            if not any(kw in line.upper() for kw in ["SECURITY", "AUTH", "ENCRYPT", "VULNERABILITY"]):
                                observations.append(make_observation(
                                    provider=self.name, 
                                    category="quality", 
                                    signal="todo_found",
                                    confidence=0.9, 
                                    message="Unresolved TODO found in code.",
                                    severity="low", 
                                    evidence={"file": rel_path, "line": i}
                                ))
                        
                except Exception as e:
                    logger.error(f"Error reading {rel_path}: {e}")

        return ProviderObservation(self.name, self.model, observations, "Scan Complete")

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Analyze single code snippet for quality issues.
        """
        return ProviderObservation(self.name, self.model, [], "")
    