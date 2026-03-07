# python -m scripts.test_sbom_trivy_providers
#
# Tests SBOMProvider and TrivyProvider locally without Docker/GHCR.
# Runs against a real local repo path and prints a GitHub-style report.
#
# Requirements:
#   syft   — https://github.com/anchore/syft#installation
#   trivy  — https://aquasecurity.github.io/trivy/latest/getting-started/installation/
#
# Quick install (Linux/macOS):
#   curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
#   curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

from ai_slop_gate.providers.static.sbom import SBOMProvider
from ai_slop_gate.providers.static.trivy import TrivyProvider
from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.reporters.formatter import format_pr_comment


TEST_REPO = Path("/home/serhiy/slop_test")
INCLUDE_MEDIUM = False

def check_binary(name: str) -> bool:
    """Check for the presence of syft and trivy (used in Dockerfile) [cite: 4]"""
    if shutil.which(name):
        return True
    print(f"❌ '{name}' not found in PATH.")
    return False

def print_section(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")

def severity_enum(raw) -> Severity:
    if isinstance(raw, Severity):
        return raw
    return Severity.MEDIUM

def show_generated_files(base_path: Path):
    files = [
        "sbom.json",              
        "sbom-spdx.json",         
        "sbom-cyclonedx.json",     
        "sbom-cyclonedx-vex.json",
    ]
    print("\n📂 Status files:")
    for fname in files:
        fpath = base_path / fname
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"   ✅ {fname:<30} {size:>8,} bytes")
        else:
            print(f"   ❌ {fname:<30} Not Found")

def show_sbom_summary(base_path: Path):
    sbom_path = base_path / "sbom.json"
    if not sbom_path.exists(): return
    with open(sbom_path) as f:
        data = json.load(f)
    arts = data.get("artifacts", [])
    print(f"\n📦 Components in SBOM: {len(arts)}")
    for a in arts[:5]:
        print(f"   • {a['name']} {a.get('version', '')} [{a.get('type', '')}]")

def show_vex_summary(base_path: Path):
    """Show VEX summary [cite: 3]"""
    vex_path = base_path / "sbom-cyclonedx-vex.json"
    if not vex_path.exists(): return
    with open(vex_path) as f:
        data = json.load(f)
    vulns = data.get("vulnerabilities", [])
    print(f"\n🔐 Vulnerabilities in VEX (Trivy): {len(vulns)}")
    for v in vulns[:5]:
        print(f"   • {v.get('id', '?'):<20}")

def test_sbom_trivy_local():
    print(f"📁 Test repository: {TEST_REPO}")

    if not TEST_REPO.exists():
        print(f"❌ Path does not exist: {TEST_REPO}")
        sys.exit(1)

    print_section("Preflight: checking binaries")
    if not (check_binary("syft") and check_binary("trivy")):
        sys.exit(1)
    print("✅ Binaries found.")

    all_observations = []

    print_section("Step 1: SBOMProvider (Syft)")
    sbom_provider = SBOMProvider()
    sbom_result = sbom_provider.collect(base_path=str(TEST_REPO))
    print(f"   Result: {sbom_result.raw_text}")
    all_observations.extend(sbom_result.observations)

    print_section("Step 2: TrivyProvider (Trivy)")
    trivy_provider = TrivyProvider(include_medium=INCLUDE_MEDIUM)
    trivy_result = trivy_provider.collect(base_path=str(TEST_REPO))
    print(f"   Result: {trivy_result.raw_text}")
    all_observations.extend(trivy_result.observations)

    print_section("Post-Scan Artifact Verification")
    show_generated_files(TEST_REPO)
    show_sbom_summary(TEST_REPO)
    show_vex_summary(TEST_REPO)

    print_section("Final AI Slop Gate Report")

    converted = [
        Observation(
            category=obs.category,
            signal=obs.signal,
            confidence=obs.confidence,
            message=obs.message,
            severity=severity_enum(obs.severity),
            evidence=getattr(obs, "evidence", None),
            location=obs.location,
        )
        for obs in all_observations
    ]

    decision = Decision(
        mode=DecisionMode.ADVISORY,
        reasons=["Local test of SBOM and VEX generation"],
    )

    print(format_pr_comment(decision, converted))
    print(f"\n✅ Done. Total observations found: {len(converted)}")
if __name__ == "__main__":
    test_sbom_trivy_local()