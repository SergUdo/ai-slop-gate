# ai-slop-gate — Copilot Instructions

> Source of truth: `ai_slop_gate_snapshot.json` (v7.4.0). If this file conflicts with the snapshot, the snapshot wins.

## Project Purpose

Vendor-agnostic CI/CD gate combining static analysis and multi-LLM code review to detect low-intent AI-generated code, security issues, and compliance violations. Supports GitHub, GitLab.

## Architectural Principles

- Policy is source of truth — `policy.yml` drives all enforcement
- CLI is thin — argument parsing and wiring only, no business logic
- Engine is pure — no IO, no printing, no exit calls
- Compliance is a sidecar — runs alongside analysis, never inside engine
- Cache is cost control — LLM providers only, prevents duplicate token spend

## Directory Structure

```
ai_slop_gate/
├── cli/              # Thin layer: main.py, run.py, args.py, context.py, logger.py
├── engine/           # provider_factory.py
├── domain/           # PolicyEngine, Observation, Decision, CheckReport
│   └── compliance/   # Compliance sidecar (detector, profiles, rules, enforcement)
├── providers/
│   ├── base.py           # BaseProvider ABC + ProviderObservation
│   ├── registry.py       # Provider registry
│   ├── cached_provider.py # CachedProvider wrapper (LLM only)
│   ├── rate_limit_guard.py
│   ├── llm/              # LLM providers + prompts/
│   └── static/           # Static and infra providers
├── reporters/        # Console, GitHubPR, GitHubChecks, GitLabMR
├── github/           # pr_commenter.py
├── cache/            # File and memory backends
└── tests/unit/ + tests/integration/
```

## Core Contracts

```python
@dataclass(frozen=True)
class ProviderObservation:
    provider: str
    model: str
    observations: List[Any]   # list of Observation objects
    raw_text: str

class BaseProvider(ABC):
    name: str
    kind: str  # "llm" | "static" | "infra"

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation: ...
    def collect(self, base_path: str = ".") -> ProviderObservation: ...
    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        # Default raises NotImplementedError

@dataclass(frozen=True)
class Observation:
    category: str
    signal: str               # snake_case
    confidence: float         # 0.0 – 1.0
    message: str
    severity: Optional[Severity]    # low|medium|high|critical
    evidence: Optional[Dict[str, Any]]
    rule_id: Optional[str]
    location: Optional[Location]    # { file: str, line: Optional[int] }

@dataclass(frozen=True)
class Decision:
    mode: DecisionMode        # allow | advisory | blocking
    reasons: List[str]
    annotations: Optional[List[Annotation]]
```

Exit codes: `allow` → 0, `advisory` → 0, `blocking` → 1.

## Provider Inventory

### LLM Providers (kind = "llm")

| Class | name | Prompts | analyze_pr |
|---|---|---|---|
| `GeminiProvider` | `gemini` | `gemini/deep.prompt` | ✅ |
| `GroqProvider` | `groq` | `groq/deep.prompt`, `groq/fast.prompt` | ✅ |
| `OllamaProvider` | `ollama` | `ollama/qwen.prompt`, `ollama/mistral.prompt` | ❌ |

LLM `collect()` delegates to `LlmProvider.analyze_files()` — chunks repo files and calls `analyze()` per chunk.

### Static Providers (kind = "static")

`StaticProvider`, `StaticSecurityProvider`, `StaticPipelineProvider`, `StaticPythonProvider`, `StaticJSProvider`, `StaticTSJSProvider`, `StaticDockerProvider`, `StaticCppProvider`, `StaticCSharpProvider`, `StaticJavaProvider`, `StaticRubyProvider`, `ESLintProvider`, `KubernetesStaticProvider`, `TerraformStaticProvider`, `TerraformPlanProvider`, `SupplyChainProvider`, `TrivyProvider`, `SBOMProvider`, `DeadCodeProvider`

### Infra Providers (kind = "infra")

`K8sRuntimeProvider`

## LLM JSON Contract

Prompts must instruct the model to return exactly:
```json
{
  "issues": [
    {
      "category": "string",
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
No markdown, no text outside JSON, no line ranges, top-level key must be `issues`.

## Cache Rules

- `CachedProvider` wraps LLM providers only
- Cache key: `provider_id + model + profile + policy_hash + input_fingerprint`
- Same key must NEVER trigger a second LLM call
- Static providers are NEVER cached

## Compliance Sidecar

Enabled by `--compliance` / `--compliance-only` or `policy.compliance.enabled`.
Profiles: `default`, `eu`, `eu-strict`.
Capabilities: forbidden license detection (GPL/AGPL), secret detection, GDPR data residency.

## Strict Rules

**Never:**
- Invent SDK methods, JSON fields, or file paths not in the snapshot
- Create new providers unless explicitly requested
- Modify architecture unless explicitly requested
- Simplify or remove validation logic
- Put business logic inside CLI
- Add provider-specific logic to cache or reporters
- Cache static providers

**Always:**
- Follow provider-agnostic pattern: `ProviderObservation` → `PolicyEngine` → Reporter
- Write tests for new rules and providers
- Use absolute imports
- English only: comments and docstrings

## Adding a New LLM Provider

1. `providers/llm/<n>.py` extending `LlmProvider`, `kind = "llm"`
2. Implement `analyze(code, input_file)` → `ProviderObservation`
3. Add prompt to `providers/llm/prompts/<n>/`
4. Register in `providers/registry.py`
5. Add `--provider <n>` to CLI args
6. Write tests in `tests/unit/providers/`

## Adding a New Static Provider

1. `providers/static/<n>.py` extending `BaseProvider`, `kind = "static"` or `"infra"`
2. Implement `collect(base_path)` → `ProviderObservation`
3. Register in `providers/registry.py`
4. Write tests with positive and negative examples

## Style

- Python 3.12+, PEP8, absolute imports
- English only, Google-style or minimal docstrings
- Follow existing style in the file being edited

## Running Tests

```bash
python -m pytest ai_slop_gate/tests -v
python -m pytest ai_slop_gate/tests --cov=ai_slop_gate --cov-report=term-missing
```