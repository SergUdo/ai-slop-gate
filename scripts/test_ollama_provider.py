# python -m scripts.test_ollama_provider

import time
import random
import os
from pathlib import Path

from ai_slop_gate.providers.llm.ollama import OllamaProvider
from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.reporters.formatter import format_pr_comment


MAX_CHUNK_SIZE = 3000
BASE_DELAY = 1.0        
JITTER = 0.3            


IGNORE_DIRS = {
    ".git", "node_modules", "venv", "__pycache__", ".idea", ".vscode",
    ".ai-slop-cache", ".venv", "dist", "build",
}

ALLOWED_EXTENSIONS = {
    ".py", ".yaml", ".yml", ".js", ".ts", ".go", ".java", ".rb"
}


def should_ignore(path: Path) -> bool:
    parts = set(path.parts)
    if any(d in parts for d in IGNORE_DIRS):
        return True
    if path.suffix not in ALLOWED_EXTENSIONS:
        return True
    return False


def build_file_chunks(repo_path: Path):
    chunks = []
    current = ""

    for file in sorted(repo_path.rglob("*")):
        if not file.is_file() or should_ignore(file):
            continue

        try:
            content = file.read_text(encoding="utf-8")
        except Exception:
            continue

        rel = file.relative_to(repo_path)
        entry = f"### File: {rel}\n```\n{content}\n```\n\n"

        if len(current) + len(entry) > MAX_CHUNK_SIZE:
            if current:
                chunks.append(current)
            current = entry
        else:
            current += entry

    if current:
        chunks.append(current)

    return chunks


def test_ollama_local_repo():
    TEST_REPO = Path("/home/serhiy/slop_test") 

    print(f"📁 [Ollama Mode] Scanning repo: {TEST_REPO}")

    chunks = build_file_chunks(TEST_REPO)
    print(f"🧩 Created {len(chunks)} chunks for analysis\n")

    provider = OllamaProvider(model="qwen2.5-coder:1.5b")

    all_observations = []

    for i, chunk in enumerate(chunks, 1):
        print(f"🚀 Sending chunk {i}/{len(chunks)} to Local Ollama ({provider.model})...")
        start = time.time()

        try:
            result = provider.analyze(code=chunk, input_file=f"chunk_{i}")
            
            if result.raw_text and not result.observations:
                print(f"⚠️ Chunk {i} returned text but no observations:")
                print(result.raw_text[:300])
            
            if result.observations:
                print(f"✅ Chunk {i}: found {len(result.observations)} problems")
                all_observations.extend(result.observations)
            else:
                print(f"✅ Chunk {i}: код чистий")
                
        except Exception as e:
            print(f"❌ Chunk {i} failed: {e}")

        elapsed = time.time() - start
        print(f"⏱️ Chunk {i} response in {elapsed:.2f}s")
        print("-" * 60)

        time.sleep(0.5)

    print(f"\n🧠 Total findings: {len(all_observations)}\n")

    if not all_observations:
        print("✅ No issues found — repo is clean!")
        return

    converted = []
    for obs in all_observations:
        sev = obs.severity
        if isinstance(sev, str):
            try:
                sev_enum = Severity(sev.lower())
            except ValueError:
                sev_enum = Severity.MEDIUM
        else:
            sev_enum = sev

        converted.append(
            Observation(
                category=obs.category,
                signal=obs.signal,
                confidence=obs.confidence,
                message=obs.message,
                severity=sev_enum,
                evidence=getattr(obs, "evidence", None),
                rule_id=getattr(obs, "rule_id", None),
                location=getattr(obs, "location", None),
            )
        )

    decision = Decision(
        mode=DecisionMode.ADVISORY,
        reasons=[f"Local Ollama analysis using {provider.model}"]
    )

    print("📝 Final Local AI Report:\n")
    print(format_pr_comment(decision, converted))


if __name__ == "__main__":
    test_ollama_local_repo()