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
            if self.DANGEROUS_EVAL_RE.search(line):
                obs.append(
                    make_observation(
                        provider=self.name,
                        category="security",
                        signal="dangerous_eval",
                        confidence=1.0,
                        message="Use of eval() detected. This is a major AI Slop indicator and security risk.",
                        evidence={"file": filename, "line": i},
                    )
                )

            if self.SECRET_RE.search(line):
                obs.append(
                    make_observation(
                        provider=self.name,
                        category="security",
                        signal="hardcoded_secret",
                        confidence=0.95,
                        message="Hardcoded credential or sensitive URL found in source code.",
                        evidence={"file": filename, "line": i},
                    )
                )

            if "any" in line and ("type" in line or ":" in line):
                obs.append(
                    make_observation(
                        provider=self.name,
                        category="quality",
                        signal="any_type_abuse",
                        confidence=0.7,
                        message="Excessive use of 'any' type. AI often uses this to bypass type checking.",
                        evidence={"file": filename, "line": i},
                    )
                )

            if "catch" in line and ("console.log" in line or "console.error" in line or "{}") and not "throw" in line:
                obs.append(
                    make_observation(
                        provider=self.name,
                        category="quality",
                        signal="silent_catch",
                        confidence=0.8,
                        message="Empty or console-only catch block. Errors are swallowed without proper handling.",
                        evidence={"file": filename, "line": i},
                    )
                )

            if self.LOCAL_STORAGE_SECRET_RE.search(line):
                obs.append(
                    make_observation(
                        provider=self.name,
                        category="security",
                        signal="localstorage_vulnerability",
                        confidence=0.8,
                        message="Storing sensitive tokens or keys in localStorage is insecure.",
                        evidence={"file": filename, "line": i},
                    )
                )

            if self.INSECURE_DEFAULTS_RE.search(line):
                obs.append(
                    make_observation(
                        provider=self.name,
                        category="security",
                        signal="insecure_default",
                        confidence=0.9,
                        message="Insecure default configuration detected.",
                        evidence={"file": filename, "line": i},
                    )
                )

        return obs

    def collect(self) -> ProviderObservation:
        return self.analyze()
