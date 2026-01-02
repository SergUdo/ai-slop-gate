import re
from pathlib import Path
from typing import List

from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation


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

REQUIRED_ENV = [
    "process.env.NODE_ENV",
    "process.env.DATABASE_URL",
    "process.env.JWT_SECRET",
]


class StaticJSProvider:
    def collect(self) -> ProviderObservation:
        observations = []
        all_text = ""

        files = self._collect_js_files()

        for file in files:
            text = file.read_text(errors="ignore")
            all_text += text + "\n"

            for i, line in enumerate(text.splitlines(), start=1):
                if SECRET_RE.search(line):
                    observations.append(
                        make_observation(
                            provider="static-js",
                            category="security",
                            signal="hardcoded_secret",
                            confidence=0.95,
                            message="Hardcoded secret detected in JS code",
                            evidence={"file": str(file), "line": i},
                        )
                    )

                if INSECURE_DEFAULTS_RE.search(line):
                    observations.append(
                        make_observation(
                            provider="static-js",
                            category="security",
                            signal="insecure_default",
                            confidence=0.9,
                            message="Insecure default configuration detected",
                            evidence={"file": str(file), "line": i},
                        )
                    )

        for env in REQUIRED_ENV:
            if env not in all_text:
                observations.append(
                    make_observation(
                        provider="static-js",
                        category="security",
                        signal="missing_required",
                        confidence=1.0,
                        message=f"Missing required config: {env}",
                        evidence={"file": None, "line": None},
                    )
                )

        if "process.env.NODE_ENV" in all_text and '"production"' in all_text:
            if "debug" in all_text or "console.log" in all_text:
                observations.append(
                    make_observation(
                        provider="static-js",
                        category="security",
                        signal="dev_in_prod",
                        confidence=1.0,
                        message="Development config detected in production code",
                        evidence={"file": None, "line": None},
                    )
                )

        return ProviderObservation(
            provider="static-js",
            model="regex-v1",
            observations=observations,
            raw_text="",
        )

    def _collect_js_files(self) -> List[Path]:
        files = []
        for path in Path(".").rglob("*"):
            if path.is_file() and path.suffix in JS_EXTENSIONS:
                if not any(p in IGNORE_DIRS for p in path.parts):
                    files.append(path)
        return files
