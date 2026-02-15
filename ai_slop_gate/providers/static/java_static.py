import os
import re
import logging
from pathlib import Path
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class StaticJavaProvider(BaseProvider):
    """
    Improved Java Static Analysis Provider
    
    Uses regex-based pattern matching instead of JavaParser subprocess.
    More reliable and doesn't require external tools.
    """
    
    EXCLUDE_DIRS = {
        "target", "build", "out", ".idea", ".git", "node_modules",
        ".gradle", "bin", ".settings", ".vscode"
    }
    
    # Dangerous method patterns
    DANGEROUS_METHODS = {
        r'Runtime\.getRuntime\(\)\.exec\s*\(': 'Runtime.exec()',
        r'ProcessBuilder\s*\(': 'ProcessBuilder',
        r'System\.exit\s*\(': 'System.exit()',
        r'Class\.forName\s*\(': 'Class.forName()',
        r'Method\.invoke\s*\(': 'Method.invoke()',
        r'Constructor\.newInstance\s*\(': 'Constructor.newInstance()',
        r'ScriptEngine\.eval\s*\(': 'ScriptEngine.eval()',
        r'Statement\.execute\s*\(': 'Statement.execute()',
        r'\.setAccessible\s*\(\s*true\s*\)': 'setAccessible(true)',
    }
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'Statement\.execute(?:Query|Update)?\s*\(\s*["\'].*\+',  # String concatenation
        r'createQuery\s*\(\s*["\'].*\+',
        r'\.execute\s*\(\s*["\'].*\+',
        r'PreparedStatement.*\+.*["\']',  # String concat in PreparedStatement
    ]
    
    # Serialization vulnerabilities
    SERIALIZATION_PATTERNS = [
        r'ObjectInputStream\.readObject\s*\(',
        r'XMLDecoder\.readObject\s*\(',
        r'XStream\.fromXML\s*\(',
        r'Serializable.*implements',
    ]
    
    # Hardcoded credentials patterns
    CREDENTIAL_PATTERNS = {
        r'(?:private|public|protected)?\s+(?:static\s+)?(?:final\s+)?String\s+(?:API_KEY|apiKey|api_key)\s*=\s*["\']([^"\']{8,})["\']': 'api_key',
        r'(?:private|public|protected)?\s+(?:static\s+)?(?:final\s+)?String\s+(?:PASSWORD|password|pwd)\s*=\s*["\']([^"\']{4,})["\']': 'password',
        r'(?:private|public|protected)?\s+(?:static\s+)?(?:final\s+)?String\s+(?:SECRET|secret|secretKey)\s*=\s*["\']([^"\']{8,})["\']': 'secret',
        r'(?:private|public|protected)?\s+(?:static\s+)?(?:final\s+)?String\s+(?:TOKEN|token|accessToken)\s*=\s*["\']([^"\']{8,})["\']': 'token',
        r'jdbc:.*://.*:.*@': 'jdbc_credentials',
    }
    
    # Weak crypto patterns
    WEAK_CRYPTO_PATTERNS = [
        r'getInstance\s*\(\s*["\']MD5["\']',
        r'getInstance\s*\(\s*["\']SHA1["\']',
        r'getInstance\s*\(\s*["\']DES["\']',
        r'getInstance\s*\(\s*["\']RC4["\']',
        r'new\s+Random\s*\(',  # Not SecureRandom
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r'new\s+File\s*\(\s*.*\+',  # File path concatenation
        r'Paths\.get\s*\(\s*.*\+',
        r'FileInputStream\s*\(\s*.*\+',
        r'FileOutputStream\s*\(\s*.*\+',
    ]
    
    # XXE (XML External Entity) patterns
    XXE_PATTERNS = [
        r'DocumentBuilderFactory\.newInstance\s*\(\s*\)',
        r'SAXParserFactory\.newInstance\s*\(\s*\)',
        r'XMLInputFactory\.newInstance\s*\(\s*\)',
    ]

    def __init__(self, model: str = "java-regex-v2"):
        self.name = "static-java"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        base = os.path.abspath(base_path)
        
        java_files = []

        for root, dirs, files in os.walk(base):
            # Filter excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for f in files:
                if f.endswith(".java"):
                    full_path = os.path.join(root, f)
                    java_files.append(full_path)

        logger.info(f"[StaticJavaProvider] Found {len(java_files)} Java files to analyze")

        for full_path in java_files:
            rel_path = os.path.relpath(full_path, base)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                
                observations.extend(self._analyze_code(code, rel_path))
                
            except Exception as e:
                logger.error(f"[StaticJavaProvider] Failed to read {rel_path}: {e}")

        logger.info(f"[StaticJavaProvider] Analysis complete. Found {len(observations)} observations")
        return ProviderObservation(self.name, self.model, observations, "Java Static Analysis Complete")

    def _analyze_code(self, code: str, filename: str) -> List:
        """Analyze Java code using regex patterns"""
        obs = []
        lines = code.split('\n')
        
        # Remove comments for cleaner analysis
        code_no_comments = self._remove_comments(code)
        lines_no_comments = code_no_comments.split('\n')

        # Various checks
        obs.extend(self._check_dangerous_methods(code_no_comments, lines, filename))
        obs.extend(self._check_sql_injection(code_no_comments, lines, filename))
        obs.extend(self._check_serialization(code_no_comments, lines, filename))
        obs.extend(self._check_credentials(code, lines, filename))
        obs.extend(self._check_weak_crypto(code_no_comments, lines, filename))
        obs.extend(self._check_path_traversal(code_no_comments, lines, filename))
        obs.extend(self._check_xxe(code_no_comments, lines, filename))
        obs.extend(self._check_todos(code, lines, filename))

        return obs

    def _remove_comments(self, code: str) -> str:
        """Remove Java comments (// and /* */)"""
        # Remove single-line comments
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    def _check_dangerous_methods(self, code: str, lines: List[str], filename: str) -> List:
        """Check for dangerous Java methods"""
        obs = []
        
        for pattern, method_name in self.DANGEROUS_METHODS.items():
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    severity = "high"
                    if "System.exit" in method_name:
                        severity = "medium"
                    
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="dangerous_function",
                        confidence=0.9,
                        message=f"Dangerous method '{method_name}' detected",
                        severity=severity,
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "method": method_name,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_sql_injection(self, code: str, lines: List[str], filename: str) -> List:
        """Check for SQL injection vulnerabilities"""
        obs = []
        
        for pattern in self.SQL_INJECTION_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="sql_injection_risk",
                        confidence=0.8,
                        message="Potential SQL injection: String concatenation in SQL query",
                        severity="high",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_serialization(self, code: str, lines: List[str], filename: str) -> List:
        """Check for unsafe deserialization"""
        obs = []
        
        for pattern in self.SERIALIZATION_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="unsafe_deserialization",
                        confidence=0.7,
                        message="Unsafe deserialization detected",
                        severity="high",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_credentials(self, code: str, lines: List[str], filename: str) -> List:
        """Check for hardcoded credentials"""
        obs = []
        
        for pattern, cred_type in self.CREDENTIAL_PATTERNS.items():
            for line_num, line in enumerate(lines, 1):
                match = re.search(pattern, line)
                if match:
                    # Extract value if available
                    value = match.group(1) if match.groups() else ""
                    
                    # Filter out test/example values
                    if self._is_likely_real_secret(value):
                        obs.append(make_observation(
                            provider=self.name,
                            category="security",
                            signal="hardcoded_secret",
                            confidence=0.8,
                            message=f"Potential {cred_type} hardcoded in code",
                            severity="high",
                            evidence={
                                "file": filename,
                                "line": line_num,
                                "type": cred_type
                            }
                        ))
        
        return obs

    def _check_weak_crypto(self, code: str, lines: List[str], filename: str) -> List:
        """Check for weak cryptography"""
        obs = []
        
        for pattern in self.WEAK_CRYPTO_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    message = "Weak cryptographic algorithm detected"
                    if "Random" in line and "SecureRandom" not in line:
                        message = "Using Random instead of SecureRandom"
                    
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="weak_crypto",
                        confidence=0.8,
                        message=message,
                        severity="medium",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_path_traversal(self, code: str, lines: List[str], filename: str) -> List:
        """Check for path traversal vulnerabilities"""
        obs = []
        
        for pattern in self.PATH_TRAVERSAL_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="path_traversal_risk",
                        confidence=0.6,
                        message="Potential path traversal: Unvalidated file path",
                        severity="medium",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_xxe(self, code: str, lines: List[str], filename: str) -> List:
        """Check for XXE (XML External Entity) vulnerabilities"""
        obs = []
        
        # Check if XXE-prone factories are used without secure configuration
        for pattern in self.XXE_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # Check next few lines for secure configuration
                    secure_config_found = False
                    for i in range(max(0, line_num - 1), min(len(lines), line_num + 5)):
                        if 'setFeature' in lines[i] or 'FEATURE_SECURE_PROCESSING' in lines[i]:
                            secure_config_found = True
                            break
                    
                    if not secure_config_found:
                        obs.append(make_observation(
                            provider=self.name,
                            category="security",
                            signal="xxe_vulnerability",
                            confidence=0.7,
                            message="Potential XXE vulnerability: XML parser without secure configuration",
                            severity="high",
                            evidence={
                                "file": filename,
                                "line": line_num,
                                "code_snippet": line.strip()[:100]
                            }
                        ))
        
        return obs

    def _check_todos(self, code: str, lines: List[str], filename: str) -> List:
        """Check for TODO/FIXME comments"""
        obs = []
        
        todo_pattern = r'//\s*(TODO|FIXME|HACK|XXX|BUG)[\s:](.*)'
        
        for line_num, line in enumerate(lines, 1):
            match = re.search(todo_pattern, line, re.IGNORECASE)
            if match:
                todo_type = match.group(1).upper()
                todo_text = match.group(2).strip()[:100]
                
                # Check if it's security-related
                is_security = any(keyword in todo_text.lower() for keyword in [
                    'security', 'vuln', 'exploit', 'auth', 'password',
                    'token', 'secret', 'sanitize', 'escape', 'validate'
                ])
                
                obs.append(make_observation(
                    provider=self.name,
                    category="quality",
                    signal="suspicious_todo" if is_security else "todo_found",
                    confidence=1.0 if is_security else 0.5,
                    message=f"{todo_type}: {todo_text}",
                    severity="medium" if is_security else "low",
                    evidence={
                        "file": filename,
                        "line": line_num,
                        "type": todo_type
                    }
                ))
        
        return obs

    def _is_likely_real_secret(self, value: str) -> bool:
        """Filter out obvious fake/test secrets"""
        if not value or len(value) < 8:
            return False
        
        # Exclude obvious test values
        test_patterns = [
            r'^(test|example|sample|demo|fake|mock|dummy)',
            r'(xxx+|yyy+|zzz+)',
            r'^(your_|my_|replace_)',
            r'(1234|abcd|password|changeme)',
        ]
        
        value_lower = value.lower()
        for pattern in test_patterns:
            if re.search(pattern, value_lower):
                return False
        
        return True

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """Analyze a single Java code snippet"""
        observations = self._analyze_code(code, input_file or "inline.java")
        return ProviderObservation(
            self.name,
            self.model,
            observations,
            f"Analyzed {len(observations)} patterns"
        )
    