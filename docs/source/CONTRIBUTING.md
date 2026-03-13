# ai-slop-gate — Contribution Guide

Thank you for your interest in **ai-slop-gate** 🙌

**Goal:** prevent "AI slop" — including inside `ai-slop-gate` itself.

> All architectural decisions are defined in `ai_slop_gate_snapshot.json` (v7.5.0).
> If this document conflicts with the snapshot, **the snapshot wins**.

---

## Project Philosophy

- **Advisory-first:** By default, nothing is blocking. Results are recommendations, not verdicts.
- **Short > Clear > Readable:** Output must be concise, signal-like, and actionable.
- **Policy is the source of truth:** All enforcement flows from `policy.yml`.
- **No hidden logic:** Every decision is traceable.

---

## Architectural Principles (Non-Negotiable)

| Component | Does | Does NOT |
|---|---|---|
| `cli/` | Parses args, wires components | Contains analysis logic |
| `engine/` | Orchestrates providers | Formats output |
| `domain/policy_engine.py` | Evaluates observations → Decision | Knows about CI or reporters |
| `providers/` | Collect or analyze data | Make enforcement decisions |
| `reporters/` | Render and deliver output | Know about providers |
| `cache/` | Prevent duplicate LLM calls | Cache static providers |

**Zero dependency on CI platforms.** CLI works locally and in any CI without GitHub/GitLab SDKs.

**Provider-first design.** Everything goes through providers via registry. CLI never imports concrete providers directly.

---

## Canonical Contracts

### BaseProvider

```python
class BaseProvider(ABC):
    name: str
    kind: str  # "llm" | "static" | "infra"

    @abstractmethod
    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        # LLM: analyze PR diff or snippet
        ...

    @abstractmethod
    def collect(self, base_path: str = ".") -> ProviderObservation:
        # Static/infra: scan a directory
        # LLM: delegates to chunked file scanning via LlmProvider
        ...

    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        # Optional: direct PR analysis (LLM providers only)
        # Default raises NotImplementedError
        ...
```

### ProviderObservation

```python
@dataclass(frozen=True)
class ProviderObservation:
    provider: str
    model: str
    observations: List[Any]
    raw_text: str
```

### CachedProvider

Wraps any LLM provider. Caches `collect()` and `analyze()` results.
Must not change provider behavior. CachedProvider is infrastructure, not logic.

```python
class CacheBackend:
    def get(self, key): ...
    def set(self, key, value): ...
```

---

## Adding a New Provider

### LLM Provider

1. Create `ai_slop_gate/providers/llm/<n>.py` extending `LlmProvider` with `kind = "llm"`
2. Implement `analyze(code, input_file)` → `ProviderObservation`
3. Optionally implement `analyze_pr(repo, pr_id, token)`
4. Add prompt file(s) to `ai_slop_gate/providers/llm/prompts/<n>/`
5. Register in `providers/registry.py`
6. Add `--provider <n>` to CLI
7. Write tests in `tests/unit/providers/`

**LLM JSON contract** — prompt must instruct the model to return:
```json
{
  "issues": [
    {
      "category": "security|quality|architecture|...",
      "signal": "snake_case_identifier",
      "message": "non-empty string",
      "severity": "low|medium|high|critical",
      "confidence": 0.85,
      "file": "path/to/file.py",
      "line": 42
    }
  ]
}
```
No markdown, no text outside JSON, no ranges for line numbers.

### Static/Infra Provider

1. Create `ai_slop_gate/providers/static/<n>.py` extending `BaseProvider`
2. Set `kind = "static"` or `"infra"`
3. Implement `collect(base_path)` → `ProviderObservation`
4. Register in `providers/registry.py`
5. Write tests with positive (detects issues) and negative (clean code) examples

---

## Testing Philosophy

Tests lock **architectural contracts**, not implementation.

**Critical invariants:**
- LLM token is not spent twice for the same cache key
- Cache key changes when input or policy changes
- Static providers are never wrapped by CachedProvider

```bash
python -m pytest ai_slop_gate/tests -v
python -m pytest ai_slop_gate/tests --cov=ai_slop_gate --cov-report=term-missing
```

---

## Snapshot Rule

Any architectural change must:

1. Update `ai_slop_gate_snapshot.json`
2. Bump the snapshot version (e.g. `7.4.0` → `7.5.0`)
3. Be aligned with the roadmap

**No snapshot update = not canonical.**

---

## Roadmap

### ✅ Stage 5 — DONE
GitLab support, provider registry, cache contracts, CachedProvider, rate-limit guard, file cache backend.

### ✅ Stage 6 — Runtime & UX (current)
- `init` command (`ai-slop-gate init`)
- Policy examples for static, plan.json, k8s
- Kubernetes runtime: admission-style analysis, advisory-only

### 🔜 Stage 7 — AI Quality Heuristics
LLM as advisor, short outputs, mandatory caching.

### 🔜 Stage 8 — Terraform
Static terraform plan parsing. Advisory mode only.

### 🔜 Stage 9 — Composition & Profiles
Profiles (ci, local, infra) and preset policies.

---

## Working with AI Assistants

ai-slop-gate ships context files for AI-assisted development. Use them — they prevent
the tool from generating "AI slop" in its own codebase.

### GitHub Copilot (VS Code)

`.github/copilot-instructions.md` is loaded automatically by Copilot Chat when you
open the repository in VS Code. It contains the full architectural context:
`BaseProvider` contracts, provider inventory, cache rules, and strict "never do" list.

No setup required. Open the repo, start Copilot Chat with `@workspace`.

### Tessl / Agent Skills Registry

`skills/ai-slop-gate/SKILL.md` is published to the
[Tessl registry](https://tessl.io/registry). It allows any AI agent that supports
the [Agent Skills spec](https://agentskills.io/specification) to automatically load
project context when working in this codebase.

Install locally:
```bash
npx tessl install ai-slop-gate
```

Evaluate or publish:
```bash
npx tessl skill review ./skills/ai-slop-gate
npx tessl skill publish ./skills/ai-slop-gate
```

### Claude (claude.ai or API)

When starting a new conversation with Claude about this project, paste the contents
of `ai_slop_gate_snapshot.json`. It is the single source of truth and gives Claude
full architectural context without relying on README or stale memory.

```
Paste ai_slop_gate_snapshot.json → then describe your task
```

For multi-session work, re-paste the snapshot at the start of each conversation.
Claude has no persistent memory of previous sessions.

### General Rules for AI-Assisted Contributions

- **Always provide the snapshot.** Without it, any model will guess architecture and
  invent missing components.
- **Never accept invented file paths, method names, or SDK methods.** Verify against
  the actual source before committing.
- **Snapshot update is mandatory.** If an AI assistant suggests an architectural
  change, update `ai_slop_gate_snapshot.json` as part of the same PR.
- **AI-generated code goes through the gate.** Run `--provider static` on your own
  diff before opening a PR. The project uses ai-slop-gate on itself via
  `.github/workflows/analyze.yml`.

---

## Not Accepted

- "Smart" decisions without policy
- Auto-blocking by default
- Tight coupling to a single CI platform
- Long LLM essays instead of signals
- Business logic inside CLI
- Provider-specific cache logic