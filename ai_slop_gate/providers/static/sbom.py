import json
import os
import subprocess
import logging
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

# SBOM output filenames written alongside the scanned project
_SBOM_FORMATS = [
    ("json",          "sbom.json"),
    ("spdx-json",     "sbom-spdx.json"),
    ("cyclonedx-json","sbom-cyclonedx.json"),
]


class SBOMProvider(BaseProvider):
    def __init__(self, model: str = "syft-sbom-v1"):
        self.name = "sbom_generator"
        self.kind = "supply_chain"
        self.model = model

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations = []

        try:
            # ── 1. Generate all three SBOM formats and save to disk ──────────
            for fmt, filename in _SBOM_FORMATS:
                output_path = os.path.join(base_path, filename)
                cmd = ["syft", base_path, "-o", fmt, "--file", output_path]

                logger.debug(f"[SBOMProvider] Running: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    logger.error(
                        f"[SBOMProvider] Syft failed for format '{fmt}': "
                        f"{result.stderr[:300]}"
                    )
                else:
                    logger.info(f"[SBOMProvider] Saved {filename}")

            # ── 2. Read native JSON for observation + package count ───────────
            native_path = os.path.join(base_path, "sbom.json")
            if not os.path.exists(native_path):
                return ProviderObservation(
                    self.name, self.model, [], "SBOM Generation Failed"
                )

            with open(native_path) as f:
                data = json.load(f)

            pkgs = data.get("artifacts", [])
            pkg_types = sorted({a.get("type", "") for a in pkgs})

            observations.append(
                make_observation(
                    provider=self.name,
                    category="supply_chain",
                    signal="sbom_generated",
                    confidence=1.0,
                    message=f"Generated SBOM with {len(pkgs)} dependencies.",
                    severity="info",
                    evidence={
                        "package_count": len(pkgs),
                        "package_types": pkg_types,
                        "formats": [f for _, f in _SBOM_FORMATS],
                    },
                )
            )

        except FileNotFoundError:
            logger.error(
                "[SBOMProvider] Syft binary not found. "
                "Install: https://github.com/anchore/syft"
            )
        except subprocess.TimeoutExpired:
            logger.error("[SBOMProvider] Syft scan timed out after 120 seconds")
        except Exception as e:
            logger.error(f"[SBOMProvider] Error: {e}", exc_info=True)

        return ProviderObservation(self.name, self.model, observations, "SBOM Complete")

    def analyze(self, code: str, input_file: str = "inline") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "")
    