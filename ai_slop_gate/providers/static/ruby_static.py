import os
import re
import logging
from pathlib import Path
from typing import List, Optional
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class StaticRubyProvider(BaseProvider):
    """
    Improved Ruby Static Analysis Provider
    
    Uses regex-based pattern matching instead of Ripper subprocess.
    More reliable and doesn't require Ruby installation.
    """
    
    EXCLUDE_DIRS = {
        ".bundle", "vendor", "node_modules", "tmp", "log",
        "dist", "build", "coverage", ".git", "__pycache__"
    }
    
    # Dangerous function patterns
    DANGEROUS_FUNCTIONS = {
        r'\beval\s*\(': 'eval',
        r'\bexec\s*\(': 'exec',
        r'\bsystem\s*\(': 'system',
        r'\b`[^`]+`': 'backtick_command',
        r'%x\{': 'percent_x_command',
        r'\bsend\s*\(': 'send',
        r'\b__send__\s*\(': '__send__',
        r'\binstance_eval\s*\(': 'instance_eval',
        r'\bclass_eval\s*\(': 'class_eval',
        r'\bmodule_eval\s*\(': 'module_eval',
    }
    
    # Secret patterns
    SECRET_PATTERNS = {
        r'(?:api_key|apikey|api-key)\s*[=:]\s*["\']([^"\']{8,})["\']': 'api_key',
        r'(?:secret|secret_key)\s*[=:]\s*["\']([^"\']{8,})["\']': 'secret',
        r'(?:password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']': 'password',
        r'(?:token|auth_token|access_token)\s*[=:]\s*["\']([^"\']{8,})["\']': 'token',
        r'AWS_[A-Z_]+\s*[=:]\s*["\']([^"\']{8,})["\']': 'aws_credential',
    }
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'\.execute\s*\(\s*["\'].*\#\{.*\}.*["\']',  # String interpolation in SQL
        r'\.query\s*\(\s*["\'].*\#\{.*\}.*["\']',
        r'\.find_by_sql\s*\(\s*["\'].*\#\{.*\}.*["\']',
        r'ActiveRecord::Base\.connection\.execute\s*\(',
    ]
    
    # Non-EU endpoints
    NON_EU_ENDPOINTS = [
        r'https?://(?!.*\.eu)[a-z0-9-]+\.(us|com|net|org)',
        r'https?://[a-z0-9-]*us-[a-z0-9-]+\.',
        r'https?://[a-z0-9-]*ap-[a-z0-9-]+\.',  # Asia Pacific
    ]

    def __init__(self, model: str = "rb-regex-v2"):
        self.name = "static-ruby"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        base = os.path.abspath(base_path)
        
        ruby_files = []

        for root, dirs, files in os.walk(base):
            # Filter excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for f in files:
                if f.endswith(".rb") or f == "Gemfile" or f == "Rakefile":
                    full_path = os.path.join(root, f)
                    ruby_files.append(full_path)

        logger.info(f"[StaticRubyProvider] Found {len(ruby_files)} Ruby files to analyze")

        for full_path in ruby_files:
            rel_path = os.path.relpath(full_path, base)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                
                observations.extend(self._analyze_code(code, rel_path))
                
            except Exception as e:
                logger.error(f"[StaticRubyProvider] Failed to read {rel_path}: {e}")

        logger.info(f"[StaticRubyProvider] Analysis complete. Found {len(observations)} observations")
        return ProviderObservation(self.name, self.model, observations, "Ruby Static Analysis Complete")

    def _analyze_code(self, code: str, filename: str) -> List:
        """Analyze Ruby code using regex patterns"""
        obs = []
        lines = code.split('\n')

        # Check for syntax errors (basic)
        obs.extend(self._check_syntax(code, filename))
        
        # Check for dangerous functions
        obs.extend(self._check_dangerous_functions(code, lines, filename))
        
        # Check for hardcoded secrets
        obs.extend(self._check_secrets(code, lines, filename))
        
        # Check for SQL injection
        obs.extend(self._check_sql_injection(code, lines, filename))
        
        # Check for non-EU endpoints
        obs.extend(self._check_endpoints(code, lines, filename))
        
        # Check for TODOs
        obs.extend(self._check_todos(code, lines, filename))

        return obs

    def _check_syntax(self, code: str, filename: str) -> List:
        """Basic Ruby syntax checks"""
        obs = []
        
        # Check for unmatched quotes
        single_quotes = code.count("'") - code.count("\\'")
        double_quotes = code.count('"') - code.count('\\"')
        
        if single_quotes % 2 != 0:
            obs.append(make_observation(
                provider=self.name,
                category="quality",
                signal="syntax_error",
                confidence=0.8,
                message="Potential syntax error: Unmatched single quotes",
                severity="medium",
                evidence={"file": filename, "detail": "unmatched_quotes"}
            ))
        
        if double_quotes % 2 != 0:
            obs.append(make_observation(
                provider=self.name,
                category="quality",
                signal="syntax_error",
                confidence=0.8,
                message="Potential syntax error: Unmatched double quotes",
                severity="medium",
                evidence={"file": filename, "detail": "unmatched_quotes"}
            ))
        
        return obs

    def _check_dangerous_functions(self, code: str, lines: List[str], filename: str) -> List:
        """Check for dangerous Ruby functions"""
        obs = []
        
        for pattern, func_name in self.DANGEROUS_FUNCTIONS.items():
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="dangerous_function",
                        confidence=0.9,
                        message=f"Dangerous function '{func_name}' detected",
                        severity="high",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "function": func_name,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_secrets(self, code: str, lines: List[str], filename: str) -> List:
        """Check for hardcoded secrets"""
        obs = []
        
        for pattern, secret_type in self.SECRET_PATTERNS.items():
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Don't flag obvious test/example values
                    value = match.group(1) if match.groups() else ""
                    if self._is_likely_real_secret(value):
                        obs.append(make_observation(
                            provider=self.name,
                            category="security",
                            signal="hardcoded_secret",
                            confidence=0.8,
                            message=f"Potential {secret_type} hardcoded in code",
                            severity="high",
                            evidence={
                                "file": filename,
                                "line": line_num,
                                "type": secret_type
                            }
                        ))
        
        return obs

    def _check_sql_injection(self, code: str, lines: List[str], filename: str) -> List:
        """Check for SQL injection vulnerabilities"""
        obs = []
        
        for pattern in self.SQL_INJECTION_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if line.strip().startswith('#'):
                    continue
                
                if re.search(pattern, line):
                    obs.append(make_observation(
                        provider=self.name,
                        category="security",
                        signal="sql_injection_risk",
                        confidence=0.7,
                        message="Potential SQL injection: String interpolation in SQL query",
                        severity="high",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "code_snippet": line.strip()[:100]
                        }
                    ))
        
        return obs

    def _check_endpoints(self, code: str, lines: List[str], filename: str) -> List:
        """Check for non-EU endpoints"""
        obs = []
        
        for pattern in self.NON_EU_ENDPOINTS:
            for line_num, line in enumerate(lines, 1):
                if line.strip().startswith('#'):
                    continue
                
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    url = match.group(0)
                    obs.append(make_observation(
                        provider=self.name,
                        category="compliance",
                        signal="non_eu_endpoint",
                        confidence=0.6,
                        message=f"Non-EU endpoint detected: {url}",
                        severity="medium",
                        evidence={
                            "file": filename,
                            "line": line_num,
                            "url": url
                        }
                    ))
        
        return obs

    def _check_todos(self, code: str, lines: List[str], filename: str) -> List:
        """Check for TODO/FIXME comments"""
        obs = []
        
        todo_pattern = r'#\s*(TODO|FIXME|HACK|XXX|BUG)[\s:](.*)'
        
        for line_num, line in enumerate(lines, 1):
            match = re.search(todo_pattern, line, re.IGNORECASE)
            if match:
                todo_type = match.group(1).upper()
                todo_text = match.group(2).strip()[:100]
                
                # Check if it's security-related
                is_security = any(keyword in todo_text.lower() for keyword in [
                    'security', 'vuln', 'exploit', 'auth', 'password', 
                    'token', 'secret', 'sanitize', 'escape'
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
            r'^(test|example|sample|demo|fake|mock)',
            r'(xxx+|yyy+|zzz+)',
            r'^(your_|my_|replace_)',
            r'(1234|abcd|password)',
        ]
        
        value_lower = value.lower()
        for pattern in test_patterns:
            if re.search(pattern, value_lower):
                return False
        
        return True

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """Analyze a single Ruby code snippet"""
        observations = self._analyze_code(code, input_file or "inline.rb")
        return ProviderObservation(
            self.name,
            self.model,
            observations,
            f"Analyzed {len(observations)} patterns"
        )
    