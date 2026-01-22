# ai_slop_gate/providers/static_ts_js.py
import re
from pathlib import Path
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

class StaticTSJSProvider(BaseProvider):
    JS_EXTENSIONS = {".js", ".ts", ".jsx", ".tsx"}
    IGNORE_DIRS = {"node_modules", "dist", "build"}

    SECRET_RE = re.compile(
        r"(API_KEY|SECRET|TOKEN|PASSWORD|JWT|PRIVATE_KEY)\s*[:=]\s*['\"`][^'\"`]{6,}['\"`]",
        re.IGNORECASE,
    )

    INSECURE_DEFAULTS_RE = re.compile(
        r"(debug\s*[:=]\s*true|"
        r"sslVerify\s*[:=]\s*false|"
        r"rejectUnauthorized\s*[:=]\s*false|"
        r"allowOrigin\s*[:=]\s*['\"]\*['\"])",
        re.IGNORECASE,
    )

    DANGEROUS_EVAL_RE = re.compile(r"\beval\s*\(", re.IGNORECASE)
    LOCAL_STORAGE_SECRET_RE = re.compile(r"localStorage\.setItem\s*\(\s*['\"`].*(token|auth|key).*['\"`]", re.IGNORECASE)

    def __init__(self, model: str = "ts-js-regex-v1"):
        self.name = "static-ts-js"
        self.kind = "scm"
        self.model = model

    def analyze(self, input_data: str = "") -> ProviderObservation:
        observations = []

        if not input_data:
            files = self._collect_js_files()
            for file in files:
                text = file.read_text(errors="ignore")
                observations.extend(self._scan_text(text, str(file)))
        else:
            observations.extend(self._scan_text(input_data, "inline_content"))

        return ProviderObservation(self.name, self.model, observations, "TS/JS Scan Complete")

    def _collect_js_files(self) -> List[Path]:
        files = []
        for path in Path(".").rglob("*"):
            if path.is_file() and path.suffix in self.JS_EXTENSIONS:
                if not any(p in self.IGNORE_DIRS for p in path.parts):
                    files.append(path)
        return files

    def _scan_text(self, text: str, filename: str) -> List:
        obs = []
        lines = text.splitlines()

        for i, line in enumerate(lines, start=1):
            # 1. Eval (Security)
            if self.DANGEROUS_EVAL_RE.search(line):
                obs.append(make_observation(
                    self.name, "security", "dangerous_eval", 1.0, "critical",
                    "Use of eval() detected. This is a major AI Slop indicator and security risk.",
                    {"file": filename, "line": i}
                ))

            # 2. Hardcoded Secrets
            if self.SECRET_RE.search(line):
                obs.append(make_observation(
                    self.name, "security", "hardcoded_secret", 0.95, "high",
                    "Hardcoded credential or sensitive URL found in source code.",
                    {"file": filename, "line": i}
                ))

            # 3. TypeScript "any" abuse (Quality)
            if "any" in line and ("type" in line or ":" in line):
                obs.append(make_observation(
                    self.name, "quality", "any_type_abuse", 0.7, "low",
                    "Excessive use of 'any' type. AI often uses this to bypass type checking.",
                    {"file": filename, "line": i}
                ))

            # 4. Silent Catch (Reliability)
            if "catch" in line and ("console.log" in line or "console.error" in line or "{}") and not "throw" in line:
                obs.append(make_observation(
                    self.name, "quality", "silent_catch", 0.8, "medium",
                    "Empty or console-only catch block. Errors are swallowed without proper handling.",
                    {"file": filename, "line": i}
                ))

            # 5. Sensitive Data in LocalStorage
            if self.LOCAL_STORAGE_SECRET_RE.search(line):
                obs.append(make_observation(
                    self.name, "security", "localstorage_vulnerability", 0.8, "high",
                    "Storing sensitive tokens or keys in localStorage is insecure.",
                    {"file": filename, "line": i}
                ))

            # 6. Insecure Defaults
            if self.INSECURE_DEFAULTS_RE.search(line):
                obs.append(make_observation(
                    self.name, "security", "insecure_default", 0.9, "high",
                    "Insecure default configuration detected.",
                    {"file": filename, "line": i}
                ))

        return obs

    def collect(self) -> ProviderObservation:
        return self.analyze()
