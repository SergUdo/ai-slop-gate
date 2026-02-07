# python -m scripts.test_groq_provider

import time
import random
from pathlib import Path

from ai_slop_gate.providers.llm.groq import GroqProvider
from ai_slop_gate.domain.observation import Observation, Severity
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.reporters.formatter import format_pr_comment


MAX_CHUNK_SIZE = 20000  # 20 KB per request
BASE_DELAY = 1.5        # base delay to avoid 429
JITTER = 0.5            # random jitter to avoid rate-window sync


IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
}


def should_ignore(path: Path) -> bool:
    """Skip ignored directories and hidden folders."""
    parts = set(path.parts)
    return any(d in parts for d in IGNORE_DIRS)


def build_file_chunks(repo_path: Path):
    """
    Build multiple unified-diff chunks, each <= MAX_CHUNK_SIZE.
    Each file is wrapped in:
        --- File: <path>
        +++ File: <path>
        <content>
    """
    chunks = []
    current = ""

    for file in repo_path.rglob("*"):
        if not file.is_file():
            continue
        if should_ignore(file):
            continue

        # Skip binary/unreadable files
        try:
            content = file.read_text()
        except Exception:
            continue

        rel = file.relative_to(repo_path)
        entry = f"--- File: {rel}\n+++ File: {rel}\n{content}\n\n"

        if len(current) + len(entry) > MAX_CHUNK_SIZE:
            chunks.append(current)
            current = entry
        else:
            current += entry

    if current:
        chunks.append(current)

    return chunks


def call_groq_with_retry(provider, chunk, chunk_id, max_retries=3):
    """
    Call Groq with retry + exponential backoff + jitter for 429 errors.
    """
    delay = BASE_DELAY

    for attempt in range(1, max_retries + 1):
        try:
            return provider.analyze(
                code=chunk,
                input_file=f"chunk_{chunk_id}"
            )
        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                print(f"⚠️ 429 Too Many Requests — retry {attempt}/{max_retries} in {delay:.1f}s...")
                time.sleep(delay + random.random() * JITTER)
                delay *= 2
                continue

            print(f"❌ Groq request failed: {e}")
            return None


def test_groq_local_repo():
    TEST_REPO = Path("/home/serhiy/slop_test")

    print(f"📁 Scanning repo: {TEST_REPO}")

    chunks = build_file_chunks(TEST_REPO)
    print(f"🧩 Created {len(chunks)} chunks for analysis\n")

    provider = GroqProvider(model="llama-3.3-70b-versatile")

    all_observations = []

    for i, chunk in enumerate(chunks, 1):
        print(f"🚀 Sending chunk {i}/{len(chunks)} to Groq...")
        start = time.time()

        result = call_groq_with_retry(provider, chunk, i)

        print(f"⏱️ Chunk {i} response in {time.time() - start:.2f}s")
        print("-" * 60)

        if result and result.observations:
            all_observations.extend(result.observations)

        # Always wait a bit between chunks
        time.sleep(BASE_DELAY + random.random() * JITTER)

    if not all_observations:
        print("⚠️ No observations parsed from any chunk.")
        return

    print(f"🧠 Total findings: {len(all_observations)}\n")

    # Normalize severity
    converted = []
    for obs in all_observations:
        sev = obs.severity
        if isinstance(sev, str):
            try:
                sev_enum = Severity(sev)
            except Exception:
                try:
                    sev_enum = Severity(sev.upper())
                except Exception:
                    sev_enum = Severity.MEDIUM
        else:
            sev_enum = Severity.MEDIUM

        converted.append(
            Observation(
                category=obs.category,
                signal=obs.signal,
                confidence=obs.confidence,
                message=obs.message,
                severity=sev_enum,
                evidence=getattr(obs, "evidence", None),
                rule_id=getattr(obs, "rule_id", None),
                location=obs.location,
            )
        )

    decision = Decision(
        mode=DecisionMode.ADVISORY,
        reasons=["Local Groq multi-file chunked test"]
    )

    print("📝 Final GitHub-style report:\n")
    print(format_pr_comment(decision, converted))


if __name__ == "__main__":
    test_groq_local_repo()
