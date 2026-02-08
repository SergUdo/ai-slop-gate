# python -m scripts.test_gemini_provider

import time
import random
import os
from pathlib import Path

from ai_slop_gate.providers.llm.gemini import GeminiProvider
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
    parts = set(path.parts)
    return any(d in parts for d in IGNORE_DIRS)


def build_file_chunks(repo_path: Path):
    chunks = []
    current = ""

    for file in repo_path.rglob("*"):
        if not file.is_file():
            continue
        if should_ignore(file):
            continue

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


def call_gemini_with_retry(provider, chunk, chunk_id, max_retries=3):
    delay = BASE_DELAY

    for attempt in range(1, max_retries + 1):
        try:
            return provider.analyze(code=chunk, input_file=f"chunk_{chunk_id}")
        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                print(f"⚠️ 429 Too Many Requests — retry {attempt}/{max_retries} in {delay:.1f}s...")
                time.sleep(delay + random.random() * JITTER)
                delay *= 2
                continue

            print(f"❌ Gemini request failed: {e}")
            return None


def repair_json_text(raw: str) -> str | None:
    """Try to heuristically extract JSON array from LLM output."""
    if not raw:
        return None
    txt = raw.strip()
    # strip code fences
    if "```" in txt:
        try:
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0]
            else:
                txt = txt.split("```")[1].split("```")[0]
        except Exception:
            pass

    # find first [ and last ] to grab array-like content
    start = txt.find("[")
    end = txt.rfind("]")
    if start != -1 and end != -1 and end > start:
        return txt[start:end+1]

    return None


def test_gemini_local_repo():
    TEST_REPO = Path("/home/serhiy/slop_test")

    print(f"📁 Scanning repo: {TEST_REPO}")

    chunks = build_file_chunks(TEST_REPO)
    print(f"🧩 Created {len(chunks)} chunks for analysis\n")

    provider = GeminiProvider(model="models/gemini-2.5-flash")

    all_observations = []

    for i, chunk in enumerate(chunks, 1):
        print(f"🚀 Sending chunk {i}/{len(chunks)} to Gemini...")
        start = time.time()

        result = call_gemini_with_retry(provider, chunk, i)

        print(f"⏱️ Chunk {i} response in {time.time() - start:.2f}s")
        print("-" * 60)

        # If provider returned raw_text but no observations, try to repair JSON and re-parse
        if result and not getattr(result, "observations", None) and getattr(result, "raw_text", None):
            repaired = repair_json_text(result.raw_text)
            if repaired:
                try:
                    # leverage provider analyze parsing by calling analyze on repaired JSON
                    repaired_result = provider.analyze(repaired, input_file=f"chunk_{i}")
                    if repaired_result and repaired_result.observations:
                        result = repaired_result
                except Exception:
                    pass

        if result and result.observations:
            all_observations.extend(result.observations)

        # Always wait a bit between chunks
        time.sleep(BASE_DELAY + random.random() * JITTER)

    if not all_observations:
        print("⚠️ No observations parsed from any chunk.")
        return

    print(f"🧠 Total findings: {len(all_observations)}\n")

    # Normalize severity and convert to domain Observation objects
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
        reasons=["Local Gemini multi-file chunked test"]
    )

    print("📝 Final GitHub-style report:\n")
    print(format_pr_comment(decision, converted))


if __name__ == "__main__":
    test_gemini_local_repo()