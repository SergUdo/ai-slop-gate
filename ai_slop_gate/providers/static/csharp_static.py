import os
import re
import logging
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class StaticCSharpProvider(BaseProvider):
    """
    Improved C# Static Analysis Provider
    
    Uses regex-based pattern matching instead of dotnet script subprocess.
    More reliable and doesn't require external tools.
    """
    
    EXCLUDE_DIRS = {
        "bin", "obj", ".git", "node_modules", "packages",
        ".vs", "TestResults", "Debug", "Release"
    }
    
    # Dangerous method patterns
    DANGEROUS_METHODS = {
        r'Process\.Start\s*\(': 'Process.Start()',
        r'ProcessStartInfo\s*\(': 'ProcessStartInfo',
        r'Environment\.Exit\s*\(': 'Environment.Exit()',
        r'Assembly\.Load\s*\(': 'Assembly.Load()',
        r'Assembly\.LoadFrom\s*\(': 'Assembly.LoadFrom()',
        r'Activator\.CreateInstance\s*\(': 'Activator.CreateInstance()',
        r'Type\.GetType\s*\(': 'Type.GetType()',
        r'Invoke\s*\(': 'Reflection Invoke()',
        r'CodeDomProvider': 'CodeDomProvider',
        r'CSharpCodeProvider': 'CSharpCodeProvider',
    }
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(SqlCommand|OleDbCommand|OdbcCommand)\s*\(\s*["\'].*\+',  # String concatenation
        r'\.ExecuteReader\s*\(\s*["\'].*\+',
        r'\.ExecuteNonQuery\s*\(\s*["\'].*\+',
        r'\.ExecuteScalar\s*\(\s*["\'].*\+',
        r'new\s+SqlCommand\s*\(\s*.*\+.*\)',
    ]
    
    # Deserialization vulnerabilities
    DESERIALIZATION_PATTERNS = [
        r'BinaryFormatter\.Deserialize\s*\(',
        r'NetDataContractSerializer\.Deserialize\s*\(',
        r'SoapFormatter\.Deserialize\s*\(',
        r'ObjectStateFormatter\.Deserialize\s*\(',
        r'JavaScriptSerializer\.Deserialize\s*\(',
    ]
    
    # Hardcoded credentials patterns
    CREDENTIAL_PATTERNS = {
        r'(?:private|public|internal)?\s+(?:static\s+)?(?:readonly\s+)?string\s+(?:ApiKey|API_KEY)\s*=\s*["\']([^"\']{8,})["\']': 'api_key',
        r'(?:private|public|internal)?\s+(?:static\s+)?(?:readonly\s+)?string\s+(?:Password|PASSWORD)\s*=\s*["\']([^"\']{4,})["\']': 'password',
        r'(?:private|public|internal)?\s+(?:static\s+)?(?:readonly\s+)?string\s+(?:Secret|SECRET)\s*=\s*["\']([^"\']{8,})["\']': 'secret',
        r'(?:private|public|internal)?\s+(?:static\s+)?(?:readonly\s+)?string\s+(?:Token|TOKEN)\s*=\s*["\']([^"\']{8,})["\']': 'token',
        r'ConnectionString\s*=\s*["\'].*Password=([^;"\'\s]{4,})': 'connection_string_password',
    }
    
    # Weak crypto patterns
    WEAK_CRYPTO_PATTERNS = [
        r'MD5\.Create\s*\(',
        r'SHA1\.Create\s*\(',
        r'DES\.Create\s*\(',
        r'RC2\.Create\s*\(',
        r'new\s+MD5CryptoServiceProvider',
        r'new\s+SHA1Managed',
        r'Random\s+',  # Not RNGCryptoServiceProvider
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r'File\.Open\s*\(\s*.*\+',
        r'File\.ReadAllText\s*\(\s*.*\+',
        r'File\.WriteAllText\s*\(\s*.*\+',
        r'Directory\.GetFiles\s*\(\s*.*\+',
        r'Path\.Combine\s*\(\s*.*Request',  # Combining with user input
    ]
    
    # XXE patterns
    XXE_PATTERNS = [
        r'XmlDocument\s*\(',
        r'XmlTextReader\s*\(',
        r'XPathDocument\s*\(',
    ]
    
    # Command injection via PowerShell
    POWERSHELL_PATTERNS = [
        r'PowerShell\.Create\s*\(',
        r'AddScript\s*\(\s*.*\+',
        r'Invoke-Expression',
    ]

    def __init__(self, model: str = "csharp-regex-v2"):
        self.name = "static-csharp"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        base = os.path.abspath(base_path)
        
        csharp_files = []

        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for f in files:
                if f.endswith(".cs"):
                    full_path = os.path.join(root, f)
                    csharp_files.append(full_path)

        logger.info(f"[StaticCSharpProvider] Found {len(csharp_files)} C# files to analyze")

        for full_path in csharp_files:
            rel_path = os.path.relpath(full_path, base)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                
                observations.extend(self._analyze_code(code, rel_path))
                
            except Exception as e:
                logger.error(f"[StaticCSharpProvider] Failed to read {rel_path}: {e}")

        logger.info(f"[StaticCSharpProvider] Analysis complete. Found {len(observations)} observations")
        return ProviderObservation(self.name, self.model, observations, "C# Static Analysis Complete")

    def _analyze_code(self, code: str, filename: str) -> List:
        """Analyze C# code using regex patterns"""
        obs = []
        lines = code.split('\n')
        
        # Remove comments
        code_no_comments = self._remove_comments(code)
        
        obs.extend(self._check_dangerous_methods(code_no_comments, lines, filename))
        obs.extend(self._check_sql_injection(code_no_comments, lines, filename))
        obs.extend(self._check_deserialization(code_no_comments, lines, filename))
        obs.extend(self._check_credentials(code, lines, filename))
        obs.extend(self._check_weak_crypto(code_no_comments, lines, filename))
        obs.extend(self._check_path_traversal(code_no_comments, lines, filename))
        obs.extend(self._check_xxe(code_no_comments, lines, filename))
        obs.extend(self._check_powershell(code_no_comments, lines, filename))
        obs.extend(self._check_todos(code, lines, filename))

        return obs

    def _remove_comments(self, code: str) -> str:
        """Remove C# comments (// and /* */)"""
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    def _check_dangerous_methods(self, code: str, lines: List[str], filename: str) -> List:
        """Check for dangerous C# methods"""
        obs = []
        
        for pattern, method_name in self.DANGEROUS_METHODS.items():
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    severity = "high"
                    if "Environment.Exit" in method_name:
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
                        message="Potential SQL injection: String concatenation in SQL command",
                        severity="high",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_deserialization(self, code: str, lines: List[str], filename: str) -> List:
        """Check for unsafe deserialization"""
        obs = []
        
        for pattern in self.DESERIALIZATION_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="unsafe_deserialization",
                        confidence=0.8,
                        message="Unsafe deserialization detected (.NET formatters are vulnerable)",
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
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(1) if match.groups() else ""
                    
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
                    if "Random" in line and "RNGCryptoServiceProvider" not in line:
                        message = "Using Random instead of RNGCryptoServiceProvider"
                    
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
        """Check for XXE vulnerabilities"""
        obs = []
        
        for pattern in self.XXE_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # Check for secure settings
                    secure = False
                    for i in range(max(0, line_num - 1), min(len(lines), line_num + 5)):
                        if 'DtdProcessing.Prohibit' in lines[i] or 'ProhibitDtd = true' in lines[i]:
                            secure = True
                            break
                    
                    if not secure:
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

    def _check_powershell(self, code: str, lines: List[str], filename: str) -> List:
        """Check for PowerShell command injection"""
        obs = []
        
        for pattern in self.POWERSHELL_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="command_injection_risk",
                        confidence=0.8,
                        message="PowerShell command injection risk",
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
        if not value or len(value) < 4:
            return False
        
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
        """Analyze a single C# code snippet"""
        observations = self._analyze_code(code, input_file or "inline.cs")
        return ProviderObservation(
            self.name,
            self.model,
            observations,
            f"Analyzed {len(observations)} patterns"
        )
    