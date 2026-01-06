# AI Slop Gate — Contribution Guide

Thank you for your interest in **ai-slop-gate** 🙌
This document defines the philosophy, architectural principles, and contribution rules of the project.

**Goal:** prevent “AI slop” — including inside `ai-slop-gate` itself.

#### All architectural decisions are defined in ai_slop_gate_snapshot.json

---

## 🧭 Project Philosophy

* **Advisory-first:** By default, nothing is blocking. Results are recommendations, not verdicts.
* **Short > Clear > Readable:** Long texts are not read. Output must be concise, understandable, and signal-like.
* **Groq-style LLM:** Output should be short, precise, and actionable.

---

## 🧱 Architectural Principles (Non-Negotiable)

### 1. Strict Separation of Responsibilities

| Component | Does | Does NOT |
| :--- | :--- | :--- |
| **init** | Creates local config | Does not analyze |
| **run** | Executes analysis | Does not mutate policies |
| **policy** | Defines rules | Does not perform IO |
| **providers** | Collect / analyze data | Do not decide |
| **decision** | Produces result | Knows nothing about CI |

### 2. Zero Dependency on CI Platforms
CLI must work locally and in any CI without GitHub/GitLab SDKs.

### 3. Provider-first Design
Everything goes through providers via a registry. CLI never imports concrete providers directly.

---

## 📜 Canonical Contracts

### Provider
```python
class Provider:
    def collect(self) -> list[Observation]:
        ...

    # optional
    def analyze(self, input_text, policy):
        ...

    # optional
    def rate_limit_key(self) -> str:
        ...
```

## CachedProvider v2 (CANONICAL)

Wraps any provider. Caches collect() and analyze() results. Must not change provider behavior. CachedProvider is infrastructure, not logic.

### CacheBackend Contract

```
class CacheBackend:
    def get(self, key): 
        ...
    def set(self, key, value): 
        ...
```

## Roadmap

#### ✅ Stage 5 — DONE
* GitLab support, provider registry, Cache contracts, CachedProvider, Rate-limit guard, File cache backend.

* Stage is finalized and frozen.

#### 🚧 Stage 6 — Runtime & UX (current)

* 6.1 — init: ai-slop-gate init (creates .ai-slop-gate.yml).

* 6.2 — Policy examples: for static, plan.json, k8s.

* 6.3 — Kubernetes runtime: admission-style analysis, advisory-only.

####  🔜 Stage 7 — AI Quality Heuristics
* LLM as advisor, short outputs, mandatory caching.

####  🔜 Stage 8 — Terraform
* Static terraform plan parsing. Advisory mode only.

####  🔜 Stage 9 — Composition & Profiles
* Profiles (ci, local, infra) and preset policies.

## 🚫 Not Accepted
* “Smart” decisions without policy.

* Auto-blocking by default.

* Tight coupling to a single CI.

* Long LLM essays instead of signals.

📦 Snapshot Rule (IMPORTANT)
* Any architectural change must:

* Update the CANONICAL SNAPSHOT.

* Bump version (v1.1 -> v1.2).

* Be aligned with the roadmap.

#### No snapshot — not canonical.

