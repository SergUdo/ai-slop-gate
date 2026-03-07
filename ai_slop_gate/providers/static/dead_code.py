"""
Dead Code Detection Provider

Optional provider for detecting unused code across multiple languages.

Requires external tools:
- Python: vulture (pip install vulture)
- Ruby: debride (gem install debride)
- JavaScript/TypeScript: ts-prune (npm install -g ts-prune)

Usage:
    ai-slop-gate run --policy policy.yml --provider dead-code
"""

import os
import re
import logging
import subprocess
import vulture
from pathlib import Path
from typing import List, Dict, Optional, Set
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class DeadCodeProvider(BaseProvider):
    """
    Multi-language dead code detection provider.
    
    Uses external tools to detect unused:
    - Functions/methods
    - Classes
    - Variables
    - Imports
    """
    
    # Mapping of languages to detection tools
    TOOL_MAP = {
        'python': {
            'tool': 'vulture',
            'install': 'pip install vulture',
            'command': ['vulture', '{path}', '--min-confidence', '80'],
            'extensions': {'.py'}
        },
        'ruby': {
            'tool': 'debride',
            'install': 'gem install debride',
            'command': ['debride', '{path}'],
            'extensions': {'.rb'}
        },
        'javascript': {
            'tool': 'ts-prune',
            'install': 'npm install -g ts-prune',
            'command': ['ts-prune'],
            'extensions': {'.js', '.jsx', '.ts', '.tsx'}
        },
    }
    
    EXCLUDE_DIRS = {
        '.git', '__pycache__', 'node_modules', 'vendor', '.bundle',
        'dist', 'build', 'coverage', 'tmp', 'log', '.venv', 'venv'
    }

    def __init__(self, model: str = "multi-tool-v1"):
        self.name = "dead-code"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        """
        Detect dead code in the project.
        
        Automatically detects project language and uses appropriate tool.
        """
        observations = []
        base = os.path.abspath(base_path)
        
        # Detect language(s) in project
        detected_languages = self._detect_languages(base)
        
        if not detected_languages:
            logger.warning("[DeadCodeProvider] No supported languages detected")
            observations.append(make_observation(
                provider=self.name,
                category="info",
                signal="no_supported_language",
                confidence=1.0,
                message="No supported languages found for dead code detection",
                severity="info",
                evidence={
                    "supported": list(self.TOOL_MAP.keys()),
                    "path": base
                }
            ))
            return ProviderObservation(self.name, self.model, observations, "No supported languages")
        
        logger.info(f"[DeadCodeProvider] Detected languages: {detected_languages}")
        
        # Run detection for each language
        for language in detected_languages:
            lang_observations = self._detect_for_language(base, language)
            observations.extend(lang_observations)
        
        logger.info(f"[DeadCodeProvider] Found {len(observations)} potential dead code issues")
        return ProviderObservation(
            self.name,
            self.model,
            observations,
            f"Analyzed {len(detected_languages)} language(s)"
        )

    def _detect_languages(self, base_path: str) -> Set[str]:
        """Detect which languages are present in the project."""
        detected = set()
        
        for lang, config in self.TOOL_MAP.items():
            extensions = config['extensions']
            
            # Check if any files with these extensions exist
            for root, dirs, files in os.walk(base_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        detected.add(lang)
                        break
                
                if lang in detected:
                    break
        
        return detected

    def _detect_for_language(self, base_path: str, language: str) -> List:
        """Run dead code detection for a specific language."""
        config = self.TOOL_MAP[language]
        tool_name = config['tool']
        
        # Check if tool is installed
        if not self._is_tool_installed(tool_name):
            logger.warning(f"[DeadCodeProvider] {tool_name} not installed for {language}")
            return [make_observation(
                provider=self.name,
                category="info",
                signal="tool_not_installed",
                confidence=1.0,
                message=f"{tool_name} not installed. Dead code detection skipped for {language}.",
                severity="info",
                evidence={
                    "language": language,
                    "tool": tool_name,
                    "install_command": config['install']
                }
            )]
        
        # Run the tool
        try:
            if language == 'python':
                return self._run_vulture(base_path)
            elif language == 'ruby':
                return self._run_debride(base_path)
            elif language == 'javascript':
                return self._run_ts_prune(base_path)
            else:
                return []
        except Exception as e:
            logger.error(f"[DeadCodeProvider] Error running {tool_name}: {e}")
            return [make_observation(
                provider=self.name,
                category="error",
                signal="detection_failed",
                confidence=1.0,
                message=f"Failed to run {tool_name}: {str(e)}",
                severity="low",
                evidence={"language": language, "error": str(e)}
            )]

    def _is_tool_installed(self, tool_name: str) -> bool:
        """Check if a tool is installed."""
        try:
            subprocess.run(
                [tool_name, '--version'],
                capture_output=True,
                timeout=5
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run_vulture(self, base_path: str) -> List:
        """Run vulture for Python dead code detection."""
        observations = []
        
        try:
            # Check for whitelist file
            whitelist_path = os.path.join(base_path, 'vulture_whitelist.py')
            
            cmd = ['vulture', base_path, '--min-confidence', '80']
            if os.path.exists(whitelist_path):
                cmd.append(whitelist_path)
                logger.info("[DeadCodeProvider] Using vulture whitelist")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse vulture output
            # Format: "path/to/file.py:123: unused function 'foo' (90% confidence)"
            for line in result.stdout.strip().split('\n'):
                if not line or ':' not in line:
                    continue
                
                parsed = self._parse_vulture_line(line)
                if parsed:
                    observations.append(make_observation(
                        provider=self.name,
                        category="quality",
                        signal="unused_code",
                        confidence=parsed['confidence'] / 100.0,
                        message=f"Unused {parsed['type']}: {parsed['name']}",
                        severity="low" if parsed['confidence'] < 80 else "medium",
                        evidence={
                            "file": parsed['file'],
                            "line": parsed['line'],
                            "type": parsed['type'],
                            "name": parsed['name'],
                            "language": "python",
                            "tool": "vulture"
                        }
                    ))
            
        except subprocess.TimeoutExpired:
            logger.error("[DeadCodeProvider] vulture timed out")
        except Exception as e:
            logger.error(f"[DeadCodeProvider] vulture failed: {e}")
        
        return observations

    def _parse_vulture_line(self, line: str) -> Optional[Dict]:
        """
        Parse vulture output line.
        
        Format: "path/to/file.py:123: unused function 'foo' (90% confidence)"
        """
        # Pattern: filepath:line: unused TYPE 'NAME' (CONFIDENCE% confidence)
        pattern = r'^(.+?):(\d+):\s+unused\s+(\w+)\s+["\']?(\w+)["\']?\s+\((\d+)%'
        match = re.match(pattern, line)
        
        if match:
            return {
                'file': match.group(1),
                'line': int(match.group(2)),
                'type': match.group(3),  # function, class, variable, etc.
                'name': match.group(4),
                'confidence': int(match.group(5))
            }
        
        return None

    def _run_debride(self, base_path: str) -> List:
        """Run debride for Ruby dead code detection."""
        observations = []
        
        try:
            result = subprocess.run(
                ['debride', base_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse debride output
            # Format varies, typically shows unused methods
            for line in result.stdout.strip().split('\n'):
                if 'unused' in line.lower():
                    # Basic parsing - debride format is less structured
                    observations.append(make_observation(
                        provider=self.name,
                        category="quality",
                        signal="unused_code",
                        confidence=0.7,  # debride has more false positives
                        message=f"Potential unused code: {line.strip()}",
                        severity="low",
                        evidence={
                            "language": "ruby",
                            "tool": "debride",
                            "raw_output": line.strip()
                        }
                    ))
        
        except subprocess.TimeoutExpired:
            logger.error("[DeadCodeProvider] debride timed out")
        except Exception as e:
            logger.error(f"[DeadCodeProvider] debride failed: {e}")
        
        return observations

    def _run_ts_prune(self, base_path: str) -> List:
        """Run ts-prune for JavaScript/TypeScript dead code detection."""
        observations = []
        
        try:
            # ts-prune needs to run from project root where tsconfig.json is
            result = subprocess.run(
                ['ts-prune'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=base_path
            )
            
            # Parse ts-prune output
            # Format: "path/to/file.ts:123 - FunctionName"
            for line in result.stdout.strip().split('\n'):
                if not line or line.startswith('('):
                    continue
                
                parts = line.split(' - ')
                if len(parts) == 2:
                    location, name = parts
                    file_line = location.split(':')
                    
                    observations.append(make_observation(
                        provider=self.name,
                        category="quality",
                        signal="unused_export",
                        confidence=0.8,
                        message=f"Unused export: {name.strip()}",
                        severity="low",
                        evidence={
                            "file": file_line[0] if file_line else location,
                            "line": int(file_line[1]) if len(file_line) > 1 else 0,
                            "name": name.strip(),
                            "language": "javascript",
                            "tool": "ts-prune"
                        }
                    ))
        
        except subprocess.TimeoutExpired:
            logger.error("[DeadCodeProvider] ts-prune timed out")
        except Exception as e:
            logger.error(f"[DeadCodeProvider] ts-prune failed: {e}")
        
        return observations

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Analyze a single code snippet (not supported for dead code detection).
        
        Dead code detection requires analyzing entire project context.
        """
        return ProviderObservation(
            self.name,
            self.model,
            [make_observation(
                provider=self.name,
                category="info",
                signal="not_supported",
                confidence=1.0,
                message="Dead code detection requires full project analysis, not single file",
                severity="info",
                evidence={"file": input_file}
            )],
            "Single file analysis not supported"
        )
    