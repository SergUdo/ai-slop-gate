import os
import json
import re
import logging
from typing import List, Dict, Tuple
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class SupplyChainProvider(BaseProvider):
    """
    Supply Chain Provider - scans dependency manifests for license compliance.
    
    Supports:
    - requirements.txt (Python)
    - package.json (Node.js)
    - pyproject.toml (Python Poetry)
    
    Detects GPL, AGPL, and other copyleft licenses.
    """
    
    EXCLUDE_DIRS = {
        ".git", ".venv", "venv", "__pycache__", "node_modules",
        "dist", "build", ".slop", ".idea", ".pytest_cache",
        "site-packages", "ai_slop_gate", "htmlcov", "tests",
    }
    
    # License patterns to detect
    GPL_PATTERNS = [
        r"\bGPL[-\s]?2\.0\b",
        r"\bGPL[-\s]?3\.0\b",
        r"\bGPLv2\b",
        r"\bGPLv3\b",
        r"\bGNU[-\s]?GPL\b",
    ]
    
    AGPL_PATTERNS = [
        r"\bAGPL[-\s]?3\.0\b",
        r"\bAGPLv3\b",
        r"\bAffero[-\s]?GPL\b",
    ]
    
    COPYLEFT_KEYWORDS = [
        "GPL", "AGPL", "GNU General Public", 
        "Affero", "copyleft"
    ]

    def __init__(self, model: str = "manifest-scanner-v1"):
        self.name = "supply-chain"
        self.kind = "static"
        self.model = model
        
        # Compile patterns for performance
        self.gpl_regex = re.compile("|".join(self.GPL_PATTERNS), re.IGNORECASE)
        self.agpl_regex = re.compile("|".join(self.AGPL_PATTERNS), re.IGNORECASE)

    def collect(self, base_path: str = ".") -> ProviderObservation:
        """
        Scan all dependency manifests in the codebase.
        """
        observations = []
        target = os.path.abspath(base_path)

        manifests = {
            "requirements.txt": self._scan_requirements,
            "package.json": self._scan_package_json,
            "pyproject.toml": self._scan_pyproject,
        }

        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for fname in files:
                if fname in manifests:
                    full_path = os.path.join(root, fname)
                    rel_path = os.path.relpath(full_path, target)
                    
                    scanner_func = manifests[fname]
                    obs = scanner_func(full_path, rel_path)
                    observations.extend(obs)

        status = f"Supply Chain Audit Done. Scanned {len(observations)} license issues."
        return ProviderObservation(self.name, self.model, observations, status)

    def analyze(self, code: str, input_file: str = "", base_path: str = ".") -> ProviderObservation:
        """
        Analyze a single manifest file.
        """
        return self.collect(base_path=base_path)

    # -------------------------------------------------------------------------
    # Scanner Functions
    # -------------------------------------------------------------------------

    def _scan_requirements(self, full_path: str, rel_path: str) -> List:
        """
        Scan requirements.txt for GPL/AGPL packages.
        
        Format:
        package-name==1.0.0
        gpl-lib>=2.0.0  # GPL-3.0
        """
        observations = []
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, start=1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    # But check if comment contains license info
                    if line.startswith("#"):
                        obs = self._check_license_in_text(
                            line, full_path, rel_path, line_num, context="comment"
                        )
                        observations.extend(obs)
                    continue
                
                # Extract package name
                package_name = self._extract_package_name(line)
                
                # Check if line contains license info
                obs = self._check_license_in_text(
                    line, full_path, rel_path, line_num, 
                    context=f"package: {package_name}"
                )
                observations.extend(obs)
                
        except Exception as e:
            logger.error(f"Error reading {rel_path}: {e}")
        
        return observations

    def _scan_package_json(self, full_path: str, rel_path: str) -> List:
        """
        Scan package.json for GPL/AGPL packages.
        
        Format:
        {
          "dependencies": {
            "gpl-package": "^1.0.0"
          },
          "licenses": [{"type": "GPL-3.0"}]
        }
        """
        observations = []
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check explicit license field
            if "license" in data:
                license_text = str(data["license"])
                obs = self._check_license_in_text(
                    license_text, full_path, rel_path, 1,
                    context="explicit license field"
                )
                observations.extend(obs)
            
            # Check licenses array
            if "licenses" in data:
                for idx, lic in enumerate(data["licenses"]):
                    license_text = str(lic)
                    obs = self._check_license_in_text(
                        license_text, full_path, rel_path, idx + 1,
                        context="licenses array"
                    )
                    observations.extend(obs)
            
            # Check dependencies
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in data:
                    for package_name in data[dep_type].keys():
                        # Check if package name suggests GPL
                        if any(kw in package_name.lower() for kw in ["gpl", "agpl", "copyleft"]):
                            observations.append(
                                make_observation(
                                    provider=self.name,
                                    category="compliance",
                                    signal="suspicious_package_name",
                                    confidence=0.8,
                                    message=f"Package name suggests copyleft license: {package_name}",
                                    severity="medium",
                                    evidence={"file": rel_path, "package": package_name},
                                )
                            )
            
            # Scan entire file as text (catches comments)
            with open(full_path, "r", encoding="utf-8") as f:
                text = f.read()
                if any(kw.upper() in text.upper() for kw in self.COPYLEFT_KEYWORDS):
                    obs = self._check_license_in_text(
                        text, full_path, rel_path, 1,
                        context="file content scan"
                    )
                    observations.extend(obs)
                    
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {rel_path}: {e}")
        except Exception as e:
            logger.error(f"Error reading {rel_path}: {e}")
        
        return observations

    def _scan_pyproject(self, full_path: str, rel_path: str) -> List:
        """
        Scan pyproject.toml for GPL/AGPL packages.
        
        Format:
        [tool.poetry.dependencies]
        gpl-lib = "^1.0.0"
        
        [project]
        license = {text = "GPL-3.0"}
        """
        observations = []
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple text-based scan (full TOML parsing would require toml library)
            lines = content.split("\n")
            
            for line_num, line in enumerate(lines, start=1):
                line = line.strip()
                
                # Check for license declarations
                if "license" in line.lower():
                    obs = self._check_license_in_text(
                        line, full_path, rel_path, line_num,
                        context="license declaration"
                    )
                    observations.extend(obs)
                
                # Check dependency lines
                if "=" in line and not line.startswith("#"):
                    package_name = line.split("=")[0].strip()
                    if any(kw in package_name.lower() for kw in ["gpl", "agpl", "copyleft"]):
                        observations.append(
                            make_observation(
                                provider=self.name,
                                category="compliance",
                                signal="suspicious_package_name",
                                confidence=0.8,
                                message=f"Package name suggests copyleft license: {package_name}",
                                severity="medium",
                                evidence={"file": rel_path, "package": package_name, "line": line_num},
                            )
                        )
            
            # Full text scan
            obs = self._check_license_in_text(
                content, full_path, rel_path, 1,
                context="file content scan"
            )
            observations.extend(obs)
            
        except Exception as e:
            logger.error(f"Error reading {rel_path}: {e}")
        
        return observations

    # -------------------------------------------------------------------------
    # Helper Functions
    # -------------------------------------------------------------------------

    def _check_license_in_text(
        self, text: str, full_path: str, rel_path: str, 
        line_num: int, context: str = ""
    ) -> List:
        """
        Check if text contains GPL/AGPL license references.
        """
        observations = []
        text_upper = text.upper()
        
        # Check for GPL patterns
        if self.gpl_regex.search(text):
            gpl_match = self.gpl_regex.search(text)
            license_type = gpl_match.group(0) if gpl_match else "GPL"
            
            observations.append(
                make_observation(
                    provider=self.name,
                    category="compliance",
                    signal="gpl_license_detected",
                    confidence=1.0,
                    message=f"GPL license detected in {rel_path} ({context}): {license_type}",
                    severity="high",
                    evidence={
                        "file": rel_path,
                        "line": line_num,
                        "license": license_type,
                        "context": context
                    },
                )
            )
        
        # Check for AGPL patterns
        if self.agpl_regex.search(text):
            agpl_match = self.agpl_regex.search(text)
            license_type = agpl_match.group(0) if agpl_match else "AGPL"
            
            observations.append(
                make_observation(
                    provider=self.name,
                    category="compliance",
                    signal="agpl_license_detected",
                    confidence=1.0,
                    message=f"AGPL license detected in {rel_path} ({context}): {license_type}",
                    severity="high",
                    evidence={
                        "file": rel_path,
                        "line": line_num,
                        "license": license_type,
                        "context": context
                    },
                )
            )
        
        # Generic copyleft detection (lower confidence)
        if not observations and any(kw in text_upper for kw in ["COPYLEFT", "GNU GENERAL PUBLIC"]):
            observations.append(
                make_observation(
                    provider=self.name,
                    category="compliance",
                    signal="copyleft_license",
                    confidence=0.9,
                    message=f"Copyleft license indicator detected in {rel_path} ({context})",
                    severity="high",
                    evidence={
                        "file": rel_path,
                        "line": line_num,
                        "context": context
                    },
                )
            )
        
        return observations

    def _extract_package_name(self, line: str) -> str:
        """
        Extract package name from dependency line.
        Examples:
        - package-name==1.0.0 -> package-name
        - package-name>=2.0,<3.0 -> package-name
        - package-name[extra]==1.0 -> package-name
        """
        # Remove inline comments
        if "#" in line:
            line = line.split("#")[0].strip()
        
        # Extract package name before version specifier
        for sep in ["==", ">=", "<=", "~=", ">", "<", "[", " "]:
            if sep in line:
                line = line.split(sep)[0]
        
        return line.strip()
    