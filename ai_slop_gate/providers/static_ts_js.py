import re
import os
import logging
from pathlib import Path
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class StaticTSJSProvider(BaseProvider):
    JS_EXTENSIONS = {".js", ".ts", ".jsx", ".tsx"}
    IGNORE_DIRS = {"node_modules", "dist", "build", ".next", "htmlcov", ".venv"}

    DANGEROUS_EVAL_RE = re.compile(r"\beval\s*\(", re.IGNORECASE)
    LOCAL_STORAGE_SECRET_RE = re.compile(r"localStorage\.setItem\s*\(\s*['\"`].*(token|auth|key|secret).*['\"`]", re.IGNORECASE)

    def __init__(self, model: str = "ts-js-regex-v1"):
        self.name = "static-ts-js"
        self.kind = "static"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []
        target_dir = Path(base_path).absolute()
        
        try:
            for file in target_dir.rglob("*"):
                if file.is_file() and file.suffix in self.JS_EXTENSIONS:
                    if not any(p in file.parts for p in self.IGNORE_DIRS):
                        # Отримуємо відносний шлях
                        rel_path = os.path.relpath(file, target_dir)
                        try:
                            text = file.read_text(errors="ignore")
                            observations.extend(self._scan_text(text, rel_path))
                        except Exception as e:
                            logger.error(f"Error reading {rel_path}: {e}")
        except Exception as e:
            logger.error(f"Error during TS/JS scan: {e}")

        return ProviderObservation(self.name, self.model, observations, "TS/JS Scan Complete")

    def _scan_text(self, text: str, filename: str) -> List:
        obs = []
        lines = text.splitlines()

        for i, line in enumerate(lines, start=1):
            if self.DANGEROUS_EVAL_RE.search(line):
                obs.append(make_observation(
                    provider=self.name, category="security", signal="dangerous_eval",
                    confidence=1.0, message="Use of eval() detected. Possible AI-generated slop.",
                    severity="high", evidence={"file": filename, "line": i}
                ))

            if self.LOCAL_STORAGE_SECRET_RE.search(line):
                obs.append(make_observation(
                    provider=self.name, category="security", signal="localstorage_vulnerability",
                    confidence=0.9, message="Storing tokens/keys in localStorage is insecure.",
                    severity="high", evidence={"file": filename, "line": i}
                ))

            if "catch" in line and ("console." in line or "{}" in line) and "throw" not in line:
                obs.append(make_observation(
                    provider=self.name, category="quality", signal="silent_catch",
                    confidence=0.8, message="Empty or console-only catch block. Errors are swallowed.",
                    severity="medium", evidence={"file": filename, "line": i}
                ))
        return obs

    def analyze(self, code: str, input_file: str = "inline") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, self._scan_text(code, input_file), "")