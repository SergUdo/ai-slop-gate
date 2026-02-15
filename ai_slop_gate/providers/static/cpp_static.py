import os
import re
import logging
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class StaticCppProvider(BaseProvider):
    """
    Improved C++ Static Analysis Provider
    
    Uses regex-based pattern matching instead of Clang AST subprocess.
    More reliable and doesn't require external tools.
    """
    
    EXCLUDE_DIRS = {
        "build", "cmake-build", "cmake-build-debug", "cmake-build-release",
        ".git", "node_modules", "third_party", "external", ".vscode", ".idea"
    }
    
    # Dangerous function patterns
    DANGEROUS_FUNCTIONS = {
        r'\bsystem\s*\(': 'system()',
        r'\bpopen\s*\(': 'popen()',
        r'\bexec[lv][pe]?\s*\(': 'exec*()',
        r'\bgets\s*\(': 'gets()',  # Buffer overflow
        r'\bstrcpy\s*\(': 'strcpy()',  # Buffer overflow
        r'\bstrcat\s*\(': 'strcat()',  # Buffer overflow
        r'\bsprintf\s*\(': 'sprintf()',  # Buffer overflow
        r'\bvsprintf\s*\(': 'vsprintf()',
        r'\bscanf\s*\(': 'scanf()',  # Format string vulnerability
        r'\batoi\s*\(': 'atoi()',  # No error handling
    }
    
    # Memory management issues
    MEMORY_ISSUES = {
        r'malloc\s*\(': 'malloc() without free()',
        r'new\s+\w+': 'new without delete',
        r'new\s+\w+\s*\[': 'new[] without delete[]',
        r'\bdelete\s+': 'manual memory management',
        r'\bfree\s*\(': 'free() manual memory management',
    }
    
    # Unsafe casts
    UNSAFE_CASTS = {
        r'\breinterpret_cast\s*<': 'reinterpret_cast',
        r'\([\w\s\*]+\)\s*\w+': 'C-style cast',
        r'const_cast\s*<': 'const_cast',
    }
    
    # Race conditions / threading issues
    THREADING_PATTERNS = [
        r'pthread_create',
        r'std::thread',
        r'std::async',
    ]
    
    # Hardcoded credentials patterns
    CREDENTIAL_PATTERNS = {
        r'(?:const\s+)?(?:std::)?string\s+(?:api_key|apiKey)\s*=\s*["\']([^"\']{8,})["\']': 'api_key',
        r'(?:const\s+)?(?:std::)?string\s+(?:password|pwd)\s*=\s*["\']([^"\']{4,})["\']': 'password',
        r'(?:const\s+)?(?:std::)?string\s+(?:secret|token)\s*=\s*["\']([^"\']{8,})["\']': 'secret',
        r'#define\s+(?:API_KEY|PASSWORD|SECRET)\s+["\']([^"\']{8,})["\']': 'macro_credential',
    }
    
    # Format string vulnerabilities
    FORMAT_STRING_PATTERNS = [
        r'printf\s*\(\s*\w+\s*\)',  # printf(user_input)
        r'fprintf\s*\([^,]+,\s*\w+\s*\)',
        r'sprintf\s*\([^,]+,\s*\w+\s*\)',
    ]
    
    # SQL injection (if using C++ SQL libraries)
    SQL_INJECTION_PATTERNS = [
        r'exec\s*\(\s*.*\+',
        r'query\s*\(\s*.*\+',
        r'PQexec\s*\(\s*.*\+',  # PostgreSQL
        r'mysql_query\s*\(\s*.*\+',  # MySQL
    ]
    
    # Integer overflow patterns
    INTEGER_OVERFLOW_PATTERNS = [
        r'malloc\s*\(\s*.*\*',  # malloc(size * count)
        r'new\s+\w+\s*\[\s*.*\*',  # new Type[size * count]
    ]

    def __init__(self, model: str = "cpp-regex-v2"):
        self.name = "static-cpp"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        base = os.path.abspath(base_path)
        
        cpp_files = []

        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for f in files:
                if f.endswith((".cpp", ".cc", ".cxx", ".hpp", ".h", ".hxx")):
                    full_path = os.path.join(root, f)
                    cpp_files.append(full_path)

        logger.info(f"[StaticCppProvider] Found {len(cpp_files)} C++ files to analyze")

        for full_path in cpp_files:
            rel_path = os.path.relpath(full_path, base)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                
                observations.extend(self._analyze_code(code, rel_path))
                
            except Exception as e:
                logger.error(f"[StaticCppProvider] Failed to read {rel_path}: {e}")

        logger.info(f"[StaticCppProvider] Analysis complete. Found {len(observations)} observations")
        return ProviderObservation(self.name, self.model, observations, "C++ Static Analysis Complete")

    def _analyze_code(self, code: str, filename: str) -> List:
        """Analyze C++ code using regex patterns"""
        obs = []
        lines = code.split('\n')
        
        # Remove comments
        code_no_comments = self._remove_comments(code)
        
        obs.extend(self._check_dangerous_functions(code_no_comments, lines, filename))
        obs.extend(self._check_memory_issues(code_no_comments, lines, filename))
        obs.extend(self._check_unsafe_casts(code_no_comments, lines, filename))
        obs.extend(self._check_credentials(code, lines, filename))
        obs.extend(self._check_format_strings(code_no_comments, lines, filename))
        obs.extend(self._check_sql_injection(code_no_comments, lines, filename))
        obs.extend(self._check_integer_overflow(code_no_comments, lines, filename))
        obs.extend(self._check_threading(code_no_comments, lines, filename))
        obs.extend(self._check_todos(code, lines, filename))

        return obs

    def _remove_comments(self, code: str) -> str:
        """Remove C++ comments (// and /* */)"""
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    def _check_dangerous_functions(self, code: str, lines: List[str], filename: str) -> List:
        """Check for dangerous C/C++ functions"""
        obs = []
        
        for pattern, func_name in self.DANGEROUS_FUNCTIONS.items():
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    severity = "high"
                    message = f"Dangerous function '{func_name}' detected"
                    
                    if func_name in ['gets()', 'strcpy()', 'strcat()', 'sprintf()']:
                        message += " - Buffer overflow risk"
                    elif func_name in ['system()', 'popen()']:
                        message += " - Command injection risk"
                    
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="dangerous_function",
                        confidence=0.9,
                        message=message,
                        severity=severity,
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "function": func_name,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_memory_issues(self, code: str, lines: List[str], filename: str) -> List:
        """Check for memory management issues"""
        obs = []
        
        # Track allocations and deallocations
        malloc_lines = []
        new_lines = []
        
        for line_num, line in enumerate(lines, 1):
            if re.search(r'\bmalloc\s*\(', line):
                malloc_lines.append(line_num)
            elif re.search(r'\bnew\s+', line) and 'delete' not in line:
                new_lines.append(line_num)
        
        # If there are many allocations, suggest using smart pointers
        if len(malloc_lines) + len(new_lines) > 5:
            obs.append(make_observation(
                provider=self.name,
                category="quality",
                signal="manual_memory_management",
                confidence=0.7,
                message=f"Manual memory management detected ({len(malloc_lines) + len(new_lines)} allocations). Consider using smart pointers.",
                severity="medium",
                evidence={
                    "file": filename,
                    "malloc_count": len(malloc_lines),
                    "new_count": len(new_lines)
                }
            ))
        
        return obs

    def _check_unsafe_casts(self, code: str, lines: List[str], filename: str) -> List:
        """Check for unsafe type casts"""
        obs = []
        
        for pattern, cast_type in self.UNSAFE_CASTS.items():
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="unsafe_cast",
                        confidence=0.7,
                        message=f"Unsafe cast '{cast_type}' detected - Type safety violation",
                        severity="medium",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "cast_type": cast_type,
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

    def _check_format_strings(self, code: str, lines: List[str], filename: str) -> List:
        """Check for format string vulnerabilities"""
        obs = []
        
        for pattern in self.FORMAT_STRING_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="format_string_vulnerability",
                        confidence=0.7,
                        message="Potential format string vulnerability - User input as format string",
                        severity="high",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_sql_injection(self, code: str, lines: List[str], filename: str) -> List:
        """Check for SQL injection"""
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

    def _check_integer_overflow(self, code: str, lines: List[str], filename: str) -> List:
        """Check for integer overflow in memory allocations"""
        obs = []
        
        for pattern in self.INTEGER_OVERFLOW_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="integer_overflow_risk",
                        confidence=0.6,
                        message="Potential integer overflow in memory allocation",
                        severity="medium",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_threading(self, code: str, lines: List[str], filename: str) -> List:
        """Check for threading without synchronization"""
        obs = []
        
        has_threading = False
        has_mutex = False
        
        for line in lines:
            if any(re.search(pattern, line) for pattern in self.THREADING_PATTERNS):
                has_threading = True
            if 'mutex' in line.lower() or 'lock' in line.lower():
                has_mutex = True
        
        if has_threading and not has_mutex:
            obs.append(make_observation(
                provider=self.name,
                category="security",
                signal="race_condition_risk",
                confidence=0.6,
                message="Threading detected without visible synchronization primitives",
                severity="medium",
                evidence={
                    "file": filename,
                    "detail": "No mutex/lock found with threading code"
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
                    'security', 'vuln', 'exploit', 'buffer', 'overflow',
                    'sanitize', 'validate', 'bounds', 'check'
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
        """Analyze a single C++ code snippet"""
        observations = self._analyze_code(code, input_file or "inline.cpp")
        return ProviderObservation(
            self.name,
            self.model,
            observations,
            f"Analyzed {len(observations)} patterns"
        )
    